from __future__ import annotations

import argparse
import shutil
from pathlib import Path
from urllib.request import Request, urlopen

import pandas as pd

from spatial_emt_niche_gnn.tenx_visium import (
    GEO_METASTATIC_PDAC_GSE274557,
    extract_tarball,
    load_filtered_signature_h5,
    load_spatial_metadata,
)


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Prepare a matched-site GSE274557 metastatic PDAC Visium subset.")
    p.add_argument("--raw-dir", default="data/raw/spatial/geo/GSE274557")
    p.add_argument("--out-dir", default="data/processed/spatial_emt_niche_gnn_geo_met_pdac_gse274557")
    p.add_argument("--patients", nargs="*", default=["Pt-1"], help="Patient prefixes to download, e.g. Pt-1 Pt-3.")
    p.add_argument("--all-patients", action="store_true", help="Download all non-PDX patients. This is large.")
    return p


def download(url: str, out: Path) -> None:
    if out.exists():
        return
    out.parent.mkdir(parents=True, exist_ok=True)
    safe_url = url.replace("ftp://ftp.ncbi.nlm.nih.gov", "https://ftp.ncbi.nlm.nih.gov")
    request = Request(safe_url, headers={"User-Agent": "Mozilla/5.0 spatial-emt-niche-gnn/0.1"})
    with urlopen(request, timeout=240) as response, open(out, "wb") as handle:
        shutil.copyfileobj(response, handle)


def fetch_soft(raw_dir: Path) -> Path:
    path = raw_dir / "GSE274557_samples.soft"
    download(GEO_METASTATIC_PDAC_GSE274557["soft_url"], path)
    return path


def parse_soft(path: Path) -> pd.DataFrame:
    samples = []
    current: dict[str, str] | None = None
    for raw_line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw_line.strip()
        if line.startswith("^SAMPLE = "):
            if current:
                samples.append(current)
            current = {"geo_accession": line.split("=", 1)[1].strip()}
        elif current is None:
            continue
        elif line.startswith("!Sample_title = "):
            current["sample_title"] = line.split("=", 1)[1].strip()
        elif line.startswith("!Sample_source_name_ch1 = "):
            current["source_name"] = line.split("=", 1)[1].strip()
        elif line.startswith("!Sample_characteristics_ch1 = tissue: "):
            current["tissue"] = line.split("tissue:", 1)[1].strip()
        elif line.startswith("!Sample_characteristics_ch1 = age: "):
            current["age"] = line.split("age:", 1)[1].strip()
        elif line.startswith("!Sample_characteristics_ch1 = Sex: "):
            current["sex"] = line.split("Sex:", 1)[1].strip()
        elif line.startswith("!Sample_characteristics_ch1 = treatment: "):
            current["treatment"] = line.split("treatment:", 1)[1].strip()
        elif line.startswith("!Sample_supplementary_file_1 = "):
            current["h5_url"] = line.split("=", 1)[1].strip()
        elif line.startswith("!Sample_supplementary_file_2 = "):
            current["spatial_url"] = line.split("=", 1)[1].strip()
        elif line.startswith("!Sample_supplementary_file_3 = "):
            current["histology_url"] = line.split("=", 1)[1].strip()
    if current:
        samples.append(current)
    frame = pd.DataFrame(samples)
    frame["patient_id"] = frame["sample_title"].str.extract(r"^(Pt-\d+)", expand=False)
    frame["is_pdx"] = frame["sample_title"].str.contains("PDX", case=False, na=False)
    frame["site_label"] = frame["tissue"].fillna(frame["source_name"]).map(site_label)
    frame["progression_label"] = frame["site_label"].map(lambda value: "primary" if value == "primary" else ("pdx" if value == "pdx" else "metastasis"))
    return frame


def site_label(tissue: str) -> str:
    text = str(tissue).lower()
    if "pdx" in text:
        return "pdx"
    if "primary" in text:
        return "primary"
    if "liver" in text:
        return "liver_metastasis"
    if "lung" in text:
        return "lung_metastasis"
    if "peritoneal" in text:
        return "peritoneal_metastasis"
    if "metastasis" in text:
        return "metastasis_other"
    return "unknown"


def selected_samples(manifest: pd.DataFrame, patients: list[str], all_patients: bool) -> pd.DataFrame:
    non_pdx = manifest[~manifest["is_pdx"]].copy()
    if all_patients:
        return non_pdx
    return non_pdx[non_pdx["patient_id"].isin(set(patients))].copy()


def prepare_subset(selected: pd.DataFrame, raw_dir: Path, out_dir: Path) -> tuple[Path, Path]:
    expression_tables = []
    metadata_tables = []
    for _, sample in selected.iterrows():
        sample_id = f"{sample['geo_accession']}_{sample['sample_title']}"
        sample_dir = raw_dir / str(sample["geo_accession"])
        h5_path = sample_dir / Path(sample["h5_url"]).name
        spatial_tar = sample_dir / Path(sample["spatial_url"]).name
        download(sample["h5_url"], h5_path)
        download(sample["spatial_url"], spatial_tar)
        spatial_dir = sample_dir / "spatial"
        extract_tarball(spatial_tar, spatial_dir)

        expression = load_filtered_signature_h5(h5_path)
        metadata = load_spatial_metadata(spatial_dir, sample_id)
        metadata["raw_barcode"] = metadata["spot_id"]
        metadata["spot_id"] = sample_id + "|" + metadata["raw_barcode"].astype(str)
        metadata["sample_id"] = sample_id
        metadata["geo_accession"] = sample["geo_accession"]
        metadata["sample_title"] = sample["sample_title"]
        metadata["patient_id"] = sample["patient_id"]
        metadata["cohort"] = "geo_met_pdac_gse274557"
        metadata["cancer_type"] = "pancreatic_cancer"
        metadata["disease"] = GEO_METASTATIC_PDAC_GSE274557["disease"]
        metadata["site_label"] = sample["site_label"]
        metadata["progression_label"] = sample["progression_label"]
        metadata["source_page"] = GEO_METASTATIC_PDAC_GSE274557["source_page"]

        expression["spot_id"] = sample_id + "|" + expression["spot_id"].astype(str)
        expression = expression[expression["spot_id"].isin(set(metadata["spot_id"]))].copy()
        expression_tables.append(expression)
        metadata_tables.append(metadata)

    out_dir.mkdir(parents=True, exist_ok=True)
    expression_path = out_dir / "geo_met_pdac_gse274557_signature_expression.tsv"
    metadata_path = out_dir / "geo_met_pdac_gse274557_spatial_metadata.tsv"
    pd.concat(expression_tables, ignore_index=True).to_csv(expression_path, sep="\t", index=False)
    pd.concat(metadata_tables, ignore_index=True).to_csv(metadata_path, sep="\t", index=False)
    return expression_path, metadata_path


def main() -> None:
    args = parser().parse_args()
    raw_dir = Path(args.raw_dir)
    out_dir = Path(args.out_dir)
    raw_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest = parse_soft(fetch_soft(raw_dir))
    manifest.to_csv(out_dir / "gse274557_sample_manifest.tsv", sep="\t", index=False)
    selected = selected_samples(manifest, args.patients, args.all_patients)
    if selected.empty:
        raise SystemExit("No GSE274557 samples selected.")
    selected.to_csv(out_dir / "gse274557_selected_samples.tsv", sep="\t", index=False)
    expression_path, metadata_path = prepare_subset(selected, raw_dir, out_dir)
    (out_dir / "dataset_source.tsv").write_text(
        "field\tvalue\n" + "\n".join(f"{key}\t{value}" for key, value in GEO_METASTATIC_PDAC_GSE274557.items()) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {expression_path}")
    print(f"Wrote {metadata_path}")


if __name__ == "__main__":
    main()
