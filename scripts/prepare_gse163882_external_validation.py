from __future__ import annotations

import argparse
import csv
import gzip
import sys
from pathlib import Path
from urllib.request import Request, urlopen

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
SCRIPTS = ROOT / "scripts"
for path in [SRC, SCRIPTS]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from score_tnbc_nac_digital_twin_features import load_tnbc_signatures  # noqa: E402

USER_AGENT = "TNBC-Digital-Twin-GSE163882/0.1"
GSE163882_TPM_URL = "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE163nnn/GSE163882/suppl/GSE163882_all.data.tpms_222Samples.csv.gz"
HGNC_URL = "https://storage.googleapis.com/public-download-files/hgnc/tsv/tsv/hgnc_complete_set.txt"


def download(url: str, out_path: Path, force: bool = False) -> str:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.exists() and out_path.stat().st_size > 0 and not force:
        return "exists"
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=180) as response, open(out_path, "wb") as handle:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            handle.write(chunk)
    return "downloaded"


def load_ensembl_symbol_map(hgnc_path: Path) -> dict[str, str]:
    hgnc = pd.read_csv(hgnc_path, sep="\t", dtype=str)
    hgnc = hgnc[["symbol", "ensembl_gene_id"]].dropna()
    hgnc["ensembl_gene_id"] = hgnc["ensembl_gene_id"].str.replace(r"\.\d+$", "", regex=True)
    hgnc["symbol"] = hgnc["symbol"].str.upper()
    return dict(zip(hgnc["ensembl_gene_id"], hgnc["symbol"]))


def target_genes(config_path: Path) -> set[str]:
    signatures = load_tnbc_signatures(config_path)
    return {gene.upper() for genes in signatures.values() for gene in genes}


def load_tpm_matrix(tpm_path: Path, ensembl_to_symbol: dict[str, str], targets: set[str]) -> pd.DataFrame:
    rows_by_symbol: dict[str, tuple[float, list[float]]] = {}
    with gzip.open(tpm_path, "rt", encoding="utf-8", errors="replace", newline="") as handle:
        reader = csv.reader(handle)
        header = next(reader)
        has_annotation = header[-1].strip().lower() in {"annotation", "gene", "symbol", "gene_symbol"} or not header[-1].startswith("BA")
        sample_descriptions = header[1:-1] if has_annotation else header[1:]
        for row in reader:
            if not row:
                continue
            ensembl_id = row[0].split(".", 1)[0]
            symbol = ensembl_to_symbol.get(ensembl_id)
            if not symbol and has_annotation and len(row) == len(header):
                symbol = row[-1].upper()
            if not symbol or symbol not in targets:
                continue
            value_slice = row[1:-1] if has_annotation else row[1:]
            values = [float(value) if value not in {"", "NA", "nan"} else 0.0 for value in value_slice]
            mean_value = float(np.mean(values)) if values else 0.0
            if symbol not in rows_by_symbol or mean_value > rows_by_symbol[symbol][0]:
                rows_by_symbol[symbol] = (mean_value, values)
    records = []
    symbols = sorted(rows_by_symbol)
    for sample_idx, sample_description in enumerate(sample_descriptions):
        record = {"sample_id": sample_description, "sample_description": sample_description}
        for symbol in symbols:
            record[symbol] = rows_by_symbol[symbol][1][sample_idx]
        records.append(record)
    return pd.DataFrame(records)


def build_external_tables(expr: pd.DataFrame, metadata_path: Path, out_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    metadata = pd.read_csv(metadata_path, sep="\t", dtype=str)
    metadata = metadata[metadata["dataset_id"].eq("GSE163882")].copy()
    metadata = metadata[
        metadata["tnbc_confirmed_or_likely"].astype(str).str.lower().eq("true")
        & metadata["standard_response"].isin(["pcr_or_good_response", "residual_or_poor_response"])
    ].copy()
    metadata = metadata[["sample_id", "sample_description", "standard_response", "tnbc_confirmed_or_likely", "standard_timepoint", "response_to_nac"]]
    merged = metadata.merge(expr, on="sample_description", how="inner", suffixes=("_geo", ""))
    if "sample_id_geo" in merged.columns:
        merged = merged.rename(columns={"sample_id_geo": "sample_id"})
    gene_cols = [col for col in merged.columns if col not in {"sample_id", "sample_description", "standard_response", "tnbc_confirmed_or_likely", "standard_timepoint", "response_to_nac"}]
    expression = merged[["sample_id"] + gene_cols].copy()
    expression[gene_cols] = np.log2(expression[gene_cols].apply(pd.to_numeric, errors="coerce").fillna(0.0) + 1.0)
    external_metadata = merged[["sample_id", "standard_response", "tnbc_confirmed_or_likely", "standard_timepoint", "response_to_nac"]].copy()
    external_metadata.insert(0, "dataset_id", "GSE163882_TNBC_TPM")
    audit = pd.DataFrame(
        [
            {
                "dataset_id": "GSE163882_TNBC_TPM",
                "source": "GSE163882_all.data.tpms_222Samples.csv.gz",
                "total_geo_samples": int((pd.read_csv(metadata_path, sep="\t", dtype=str)["dataset_id"] == "GSE163882").sum()),
                "tnbc_response_labeled_samples": int(metadata.shape[0]),
                "samples_with_expression": int(expression.shape[0]),
                "genes_mapped_to_hgnc": int(len(gene_cols)),
                "pcr_or_good_response": int((external_metadata["standard_response"] == "pcr_or_good_response").sum()),
                "residual_or_poor_response": int((external_metadata["standard_response"] == "residual_or_poor_response").sum()),
            }
        ]
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    expression.to_csv(out_dir / "gse163882_tnbc_external_expression_log2tpm.tsv", sep="\t", index=False)
    external_metadata.to_csv(out_dir / "gse163882_tnbc_external_metadata.tsv", sep="\t", index=False)
    audit.to_csv(out_dir / "gse163882_external_preparation_audit.tsv", sep="\t", index=False)
    return expression, external_metadata, audit


def write_report(audit: pd.DataFrame, out_path: Path) -> None:
    lines = [
        "# GSE163882 External TNBC NAC Validation Preparation",
        "",
        "## Source",
        "",
        "- GEO: `GSE163882`.",
        "- Expression file: `GSE163882_all.data.tpms_222Samples.csv.gz`.",
        "- Input expression scale for validation: `log2(TPM + 1)`.",
        "- Gene mapping: HGNC complete-set `ensembl_gene_id` to approved symbol.",
        "",
        "## Audit",
        "",
        audit.to_markdown(index=False),
        "",
        "## Intended Use",
        "",
        "This prepared table is used as a held-out external-style TNBC NAC response validation cohort. It is not included in the internal `GSE25055`/`GSE25065` response-model training benchmark.",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Prepare GSE163882 TNBC TPM data for external response validation.")
    p.add_argument("--raw-dir", default="data/raw/tnbc_nac/geo/GSE163882")
    p.add_argument("--metadata", default="data/processed/tnbc_digital_twin/tnbc_nac_geo_sample_metadata.tsv")
    p.add_argument("--config", default="configs/tnbc_digital_twin.yml")
    p.add_argument("--out-dir", default="data/processed/tnbc_digital_twin/external_validation/gse163882")
    p.add_argument("--force-download", action="store_true")
    return p


def main() -> None:
    args = parser().parse_args()
    raw_dir = ROOT / args.raw_dir
    out_dir = ROOT / args.out_dir
    tpm_path = raw_dir / "GSE163882_all.data.tpms_222Samples.csv.gz"
    hgnc_path = raw_dir / "hgnc_complete_set.txt"
    tpm_status = download(GSE163882_TPM_URL, tpm_path, force=args.force_download)
    hgnc_status = download(HGNC_URL, hgnc_path, force=args.force_download)
    mapping = load_ensembl_symbol_map(hgnc_path)
    expr = load_tpm_matrix(tpm_path, mapping, target_genes(ROOT / args.config))
    _, _, audit = build_external_tables(expr, ROOT / args.metadata, out_dir)
    audit["tpm_download_status"] = tpm_status
    audit["hgnc_download_status"] = hgnc_status
    audit.to_csv(out_dir / "gse163882_external_preparation_audit.tsv", sep="\t", index=False)
    write_report(audit, out_dir / "gse163882_external_preparation_report.md")
    print(audit.to_string(index=False))


if __name__ == "__main__":
    main()
