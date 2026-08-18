from __future__ import annotations

import argparse
import csv
import gzip
import re
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import numpy as np
import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from emt_state_atlas.signatures import SIGNATURES  # noqa: E402


USER_AGENT = "EMT-Metastasis-AI-TNBC-Digital-Twin/0.1"


def request_download(url: str, local: Path, force: bool = False, timeout: int = 180) -> str:
    local.parent.mkdir(parents=True, exist_ok=True)
    if local.exists() and local.stat().st_size > 0 and not force:
        return "exists"
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=timeout) as response, open(local, "wb") as handle:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            handle.write(chunk)
    return "downloaded"


def geo_platform_prefix(platform_id: str) -> str:
    match = re.fullmatch(r"GPL(\d+)", platform_id.upper())
    if not match:
        raise ValueError(f"Unsupported GEO platform id: {platform_id}")
    number = int(match.group(1))
    if number < 1000:
        return "GPLnnn"
    return f"GPL{number // 1000}nnn"


def platform_soft_url(platform_id: str) -> str:
    return (
        f"https://ftp.ncbi.nlm.nih.gov/geo/platforms/{geo_platform_prefix(platform_id)}/"
        f"{platform_id}/soft/{platform_id}_family.soft.gz"
    )


def platform_annot_url(platform_id: str) -> str:
    return (
        f"https://ftp.ncbi.nlm.nih.gov/geo/platforms/{geo_platform_prefix(platform_id)}/"
        f"{platform_id}/annot/{platform_id}.annot.gz"
    )


def open_text(path: Path):
    return gzip.open(path, "rt", encoding="utf-8", errors="replace") if path.suffix == ".gz" else open(path, "rt", encoding="utf-8", errors="replace")


def parse_platform_ids(matrix_path: Path) -> list[str]:
    platforms: list[str] = []
    with open_text(matrix_path) as handle:
        for line in handle:
            if line.startswith("!series_matrix_table_begin"):
                break
            if line.startswith("!Series_platform_id"):
                row = next(csv.reader([line], delimiter="\t"))
                platforms.extend(value.strip().strip('"') for value in row[1:] if value.strip())
    return sorted(set(platforms))


def load_target_genes(config_path: Path) -> set[str]:
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    genes: set[str] = set()

    def collect(value):
        if isinstance(value, list):
            for item in value:
                if isinstance(item, str):
                    genes.add(item.upper())
        elif isinstance(value, dict):
            for nested in value.values():
                collect(nested)

    collect(config.get("signature_blocks", {}))
    for signature_genes in SIGNATURES.values():
        genes.update(gene.upper() for gene in signature_genes)
    return genes


def iter_platform_table_rows(soft_path: Path):
    header = None
    in_table = False
    with open_text(soft_path) as handle:
        for line in handle:
            if line.startswith("!platform_table_begin"):
                in_table = True
                continue
            if line.startswith("!platform_table_end"):
                break
            if not in_table:
                continue
            row = next(csv.reader([line.rstrip("\n")], delimiter="\t"))
            if header is None:
                header = [col.strip() for col in row]
            else:
                if len(row) < len(header):
                    row.extend([""] * (len(header) - len(row)))
                yield header, row[: len(header)]


def iter_annotation_rows(annotation_path: Path):
    header = None
    with open_text(annotation_path) as handle:
        for line in handle:
            if not line.strip() or line.startswith("#") or line.startswith("!"):
                continue
            row = next(csv.reader([line.rstrip("\n")], delimiter="\t"))
            if header is None:
                header = [col.strip() for col in row]
                continue
            if len(row) < len(header):
                row.extend([""] * (len(header) - len(row)))
            yield header, row[: len(header)]


def symbols_from_value(value: object, target_genes: set[str]) -> list[str]:
    text = str(value)
    if not text or text.lower() in {"nan", "null", "---", "na"}:
        return []
    symbols: list[str] = []

    for part in re.split(r"///|//|;|,|\|", text):
        token = part.strip()
        if not token:
            continue
        # Affymetrix assignment columns often contain "accession // SYMBOL // description".
        words = re.findall(r"[A-Za-z][A-Za-z0-9.-]{1,20}", token)
        for word in words:
            gene = word.upper()
            if gene in target_genes:
                symbols.append(gene)
        if token.upper() in target_genes:
            symbols.append(token.upper())

    return sorted(set(symbols))


def build_probe_map_from_soft(soft_path: Path, target_genes: set[str]) -> tuple[pd.DataFrame, int]:
    first_rows = []
    row_count = 0
    header = None
    for header, row in iter_platform_table_rows(soft_path):
        row_count += 1
        if len(first_rows) < 5000:
            first_rows.append(row)
    if header is None or "ID" not in header:
        return pd.DataFrame(columns=["probe_id", "gene_symbol", "source_column"]), row_count

    candidate_columns = [
        col
        for col in header
        if col != "ID"
        and any(token in col.lower() for token in ["gene symbol", "gene_symbol", "symbol", "gene_assignment", "mrna_assignment", "gene assignment"])
    ]
    if not candidate_columns:
        candidate_columns = [col for col in header if col != "ID"]

    col_index = {col: i for i, col in enumerate(header)}
    scored: list[tuple[int, str]] = []
    for col in candidate_columns:
        idx = col_index[col]
        hits = sum(len(symbols_from_value(row[idx], target_genes)) for row in first_rows if idx < len(row))
        scored.append((hits, col))
    scored.sort(reverse=True)

    used_columns = [col for hits, col in scored if hits > 0][:3]
    if not used_columns and scored:
        used_columns = [scored[0][1]]
    used_indices = [(col, col_index[col]) for col in used_columns]

    rows = []
    id_idx = col_index["ID"]
    for header, row in iter_platform_table_rows(soft_path):
        probe = str(row[id_idx]).strip().strip('"') if id_idx < len(row) else ""
        if not probe:
            continue
        for col, idx in used_indices:
            value = row[idx] if idx < len(row) else ""
            for symbol in symbols_from_value(value, target_genes):
                rows.append({"probe_id": probe, "gene_symbol": symbol, "source_column": col})
    if not rows:
        return pd.DataFrame(columns=["probe_id", "gene_symbol", "source_column"]), row_count
    return pd.DataFrame(rows).drop_duplicates(), row_count


def build_probe_map_from_rows(row_iter_factory, target_genes: set[str]) -> tuple[pd.DataFrame, int]:
    first_rows = []
    row_count = 0
    header = None
    for header, row in row_iter_factory():
        row_count += 1
        if len(first_rows) < 5000:
            first_rows.append(row)
    if header is None:
        return pd.DataFrame(columns=["probe_id", "gene_symbol", "source_column"]), row_count
    id_col = "ID" if "ID" in header else header[0]
    candidate_columns = [
        col
        for col in header
        if col != id_col
        and any(token in col.lower() for token in ["gene symbol", "gene_symbol", "symbol", "gene_assignment", "mrna_assignment", "gene assignment"])
    ]
    if not candidate_columns:
        candidate_columns = [col for col in header if col != id_col]
    col_index = {col: i for i, col in enumerate(header)}
    scored: list[tuple[int, str]] = []
    for col in candidate_columns:
        idx = col_index[col]
        hits = sum(len(symbols_from_value(row[idx], target_genes)) for row in first_rows if idx < len(row))
        scored.append((hits, col))
    scored.sort(reverse=True)
    used_columns = [col for hits, col in scored if hits > 0][:3]
    if not used_columns and scored:
        used_columns = [scored[0][1]]
    used_indices = [(col, col_index[col]) for col in used_columns]
    id_idx = col_index[id_col]
    rows = []
    for header, row in row_iter_factory():
        probe = str(row[id_idx]).strip().strip('"') if id_idx < len(row) else ""
        if not probe:
            continue
        for col, idx in used_indices:
            value = row[idx] if idx < len(row) else ""
            for symbol in symbols_from_value(value, target_genes):
                rows.append({"probe_id": probe, "gene_symbol": symbol, "source_column": col})
    if not rows:
        return pd.DataFrame(columns=["probe_id", "gene_symbol", "source_column"]), row_count
    return pd.DataFrame(rows).drop_duplicates(), row_count


def read_series_expression(matrix_path: Path, keep_probes: set[str]) -> pd.DataFrame:
    header = None
    rows = []
    in_table = False
    with open_text(matrix_path) as handle:
        for line in handle:
            if line.startswith("!series_matrix_table_begin"):
                in_table = True
                continue
            if line.startswith("!series_matrix_table_end"):
                break
            if not in_table:
                continue
            row = next(csv.reader([line.rstrip("\n")], delimiter="\t"))
            if header is None:
                header = [value.strip().strip('"') for value in row]
                continue
            if len(row) < 2:
                continue
            probe_id = row[0].strip().strip('"')
            if keep_probes and probe_id not in keep_probes:
                continue
            values = pd.to_numeric(pd.Series(row[1:], index=header[1:]), errors="coerce")
            rows.append((probe_id, values))
    if header is None or not rows:
        return pd.DataFrame()
    expr = pd.DataFrame({probe: values for probe, values in rows}).T
    expr.index.name = "probe_id"
    return expr


def collapse_to_genes(probe_expr: pd.DataFrame, probe_map: pd.DataFrame) -> pd.DataFrame:
    if probe_expr.empty or probe_map.empty:
        return pd.DataFrame()
    present = probe_map[probe_map["probe_id"].isin(probe_expr.index)].copy()
    if present.empty:
        return pd.DataFrame()
    mapped = probe_expr.loc[present["probe_id"].unique()].copy()
    probe_to_genes = present.groupby("probe_id")["gene_symbol"].apply(list)

    gene_frames = []
    for probe_id, genes in probe_to_genes.items():
        for gene in genes:
            series = mapped.loc[probe_id].copy()
            series.name = gene
            gene_frames.append(series)
    expanded = pd.DataFrame(gene_frames)
    gene_expr = expanded.groupby(expanded.index).median(numeric_only=True).T
    gene_expr.index.name = "sample_id"
    return gene_expr.reset_index()


def write_markdown_report(platform_audit: pd.DataFrame, expression_audit: pd.DataFrame, out_path: Path) -> None:
    lines = [
        "# TNBC NAC Gene Expression Build Report",
        "",
        "## Platform Annotation Audit",
        "",
        platform_audit.to_markdown(index=False),
        "",
        "## Gene Expression Audit",
        "",
        expression_audit.to_markdown(index=False),
        "",
        "## Notes",
        "",
        "- Expression outputs are compact sample-by-gene matrices restricted to configured EMT, TME, and TNBC resistance signatures.",
        "- Probe-level values are collapsed to gene symbols by median across mapped probes.",
        "- RNA-seq/single-cell GEO matrices without embedded expression rows are preserved as metadata resources and skipped here.",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Map TNBC NAC GEO probe matrices to compact gene-level expression tables.")
    p.add_argument("--audit", default="data/processed/tnbc_digital_twin/tnbc_nac_geo_download_audit.tsv")
    p.add_argument("--config", default="configs/tnbc_digital_twin.yml")
    p.add_argument("--raw-dir", default="data/raw/tnbc_nac")
    p.add_argument("--out-dir", default="data/processed/tnbc_digital_twin")
    p.add_argument("--force", action="store_true")
    p.add_argument("--timeout", type=int, default=180)
    return p


def main() -> None:
    args = parser().parse_args()
    audit = pd.read_csv(ROOT / args.audit, sep="\t")
    raw_dir = ROOT / args.raw_dir
    out_dir = ROOT / args.out_dir
    expression_dir = out_dir / "gene_expression"
    platform_dir = raw_dir / "platforms"
    expression_dir.mkdir(parents=True, exist_ok=True)
    target_genes = load_target_genes(ROOT / args.config)

    matrix_rows = []
    platform_ids: set[str] = set()
    for _, row in audit.iterrows():
        if row.get("download_status") == "failed":
            continue
        if "expression_feature_count" in audit.columns and int(float(row.get("expression_feature_count", 0) or 0)) <= 0:
            continue
        matrix_path = ROOT / str(row["local_path"])
        if not matrix_path.exists():
            continue
        platforms = parse_platform_ids(matrix_path)
        platform_ids.update(platforms)
        matrix_rows.append({"dataset_id": row["dataset_id"], "matrix_path": matrix_path, "platform_ids": platforms})

    platform_audit_rows = []
    probe_maps = {}
    for platform_id in sorted(platform_ids):
        annotation_path = platform_dir / platform_id / f"{platform_id}.annot.gz"
        soft_path = platform_dir / platform_id / f"{platform_id}_family.soft.gz"
        status = "not_attempted"
        error = ""
        try:
            status = request_download(platform_annot_url(platform_id), annotation_path, force=args.force, timeout=args.timeout)
            probe_map, platform_rows = build_probe_map_from_rows(lambda: iter_annotation_rows(annotation_path), target_genes)
            source_file = annotation_path
            if probe_map.empty:
                status = request_download(platform_soft_url(platform_id), soft_path, force=args.force, timeout=args.timeout)
                probe_map, platform_rows = build_probe_map_from_soft(soft_path, target_genes)
                source_file = soft_path
            probe_maps[platform_id] = probe_map
            probe_map.to_csv(out_dir / f"{platform_id}_signature_probe_map.tsv", sep="\t", index=False)
            platform_audit_rows.append(
                {
                    "platform_id": platform_id,
                    "download_status": status,
                    "platform_rows": platform_rows,
                    "probe_gene_links": probe_map.shape[0],
                    "mapped_genes": probe_map["gene_symbol"].nunique() if not probe_map.empty else 0,
                    "source_columns": ";".join(sorted(probe_map["source_column"].dropna().unique())) if not probe_map.empty else "",
                    "annotation_file": str(source_file.relative_to(ROOT)),
                    "error": "",
                }
            )
        except (HTTPError, URLError, TimeoutError, OSError, ValueError, csv.Error) as exc:
            platform_audit_rows.append(
                {
                    "platform_id": platform_id,
                    "download_status": "failed",
                    "platform_rows": 0,
                    "probe_gene_links": 0,
                    "mapped_genes": 0,
                    "source_columns": "",
                    "annotation_file": "",
                    "error": str(exc),
                }
            )

    expression_audit_rows = []
    for item in matrix_rows:
        dataset_id = str(item["dataset_id"])
        matrix_path = item["matrix_path"]
        platforms = item["platform_ids"]
        if len(platforms) != 1 or platforms[0] not in probe_maps:
            expression_audit_rows.append(
                {
                    "dataset_id": dataset_id,
                    "status": "skipped",
                    "reason": f"unsupported platform set: {';'.join(platforms)}",
                    "samples": 0,
                    "genes": 0,
                    "out_path": "",
                }
            )
            continue
        keep_probes = set(probe_maps[platforms[0]]["probe_id"]) if not probe_maps[platforms[0]].empty else set()
        probe_expr = read_series_expression(matrix_path, keep_probes=keep_probes)
        gene_expr = collapse_to_genes(probe_expr, probe_maps[platforms[0]])
        if gene_expr.empty:
            expression_audit_rows.append(
                {
                    "dataset_id": dataset_id,
                    "status": "skipped",
                    "reason": "no expression rows or no mapped signature probes",
                    "samples": 0,
                    "genes": 0,
                    "out_path": "",
                }
            )
            continue
        out_path = expression_dir / f"{dataset_id}_signature_gene_expression.tsv"
        gene_expr.to_csv(out_path, sep="\t", index=False)
        expression_audit_rows.append(
            {
                "dataset_id": dataset_id,
                "status": "written",
                "reason": "",
                "samples": gene_expr.shape[0],
                "genes": gene_expr.shape[1] - 1,
                "out_path": str(out_path.relative_to(ROOT)),
            }
        )

    platform_audit = pd.DataFrame(platform_audit_rows)
    expression_audit = pd.DataFrame(expression_audit_rows)
    platform_audit.to_csv(out_dir / "tnbc_nac_platform_annotation_audit.tsv", sep="\t", index=False)
    expression_audit.to_csv(out_dir / "tnbc_nac_gene_expression_audit.tsv", sep="\t", index=False)
    write_markdown_report(platform_audit, expression_audit, out_dir / "tnbc_nac_gene_expression_build_report.md")
    print(expression_audit.to_string(index=False))


if __name__ == "__main__":
    main()
