from __future__ import annotations

import gzip
import shutil
import tarfile
from pathlib import Path
from urllib.request import Request, urlopen

import numpy as np
import pandas as pd
from scipy.io import mmread

from .signatures import required_genes


GSE225857_URL = "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE225nnn/GSE225857/suppl/GSE225857_RAW.tar"
GEOMX_URL = "https://zenodo.org/api/records/7520789/files/Counts.csv/content"

VISIUM_SECTIONS = {
    "GSM7058756_C1": {"site": "primary_crc", "sample_label": "C1", "patient_id": "not_disclosed_C1"},
    "GSM7058757_C2": {"site": "primary_crc", "sample_label": "C2", "patient_id": "not_disclosed_C2"},
    "GSM7058758_C3": {"site": "primary_crc", "sample_label": "C3", "patient_id": "not_disclosed_C3"},
    "GSM7058759_C4": {"site": "primary_crc", "sample_label": "C4", "patient_id": "not_disclosed_C4"},
    "GSM7058760_L1": {"site": "liver_metastasis", "sample_label": "L1", "patient_id": "not_disclosed_L1"},
    "GSM7058761_L2": {"site": "liver_metastasis", "sample_label": "L2", "patient_id": "not_disclosed_L2"},
}


def download(url: str, output: Path) -> Path:
    if output.exists() and output.stat().st_size > 0:
        return output
    output.parent.mkdir(parents=True, exist_ok=True)
    request = Request(url, headers={"User-Agent": "crc-liver-invasion-front/0.1"})
    with urlopen(request, timeout=300) as response, open(output, "wb") as handle:
        shutil.copyfileobj(response, handle)
    return output


def safe_extract(archive: Path, output_dir: Path) -> Path:
    marker = output_dir / ".extracted"
    if marker.exists():
        return output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    base = output_dir.resolve()
    with tarfile.open(archive, "r") as tar:
        for member in tar.getmembers():
            target = (output_dir / member.name).resolve()
            if target != base and base not in target.parents:
                raise RuntimeError(f"Unsafe archive member: {member.name}")
        tar.extractall(output_dir)
    marker.write_text("ok\n", encoding="utf-8")
    return output_dir


def _read_gzip_rows(path: Path) -> list[list[str]]:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        return [line.rstrip("\n").split("\t") for line in handle]


def _find(extract_dir: Path, prefix: str, suffix: str) -> Path:
    matches = list(extract_dir.glob(f"{prefix}*{suffix}"))
    if not matches:
        raise FileNotFoundError(f"Missing {prefix}*{suffix} in {extract_dir}")
    return matches[0]


def load_visium_section(extract_dir: Path, section_id: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    features_path = _find(extract_dir, section_id, "features.tsv.gz")
    barcodes_path = _find(extract_dir, section_id, "barcodes.tsv.gz")
    matrix_path = _find(extract_dir, section_id, "matrix.mtx.gz")
    positions_path = _find(extract_dir, section_id, "tissue_positions_list.csv.gz")

    features = _read_gzip_rows(features_path)
    barcodes = [row[0] for row in _read_gzip_rows(barcodes_path)]
    matrix = mmread(matrix_path).tocsr()
    if matrix.shape[0] != len(features):
        matrix = matrix.T.tocsr()
    totals = np.asarray(matrix.sum(axis=0)).ravel()
    totals[totals <= 0] = 1.0

    wanted = required_genes()
    gene_rows: dict[str, int] = {}
    for index, row in enumerate(features):
        symbol = (row[1] if len(row) > 1 else row[0]).upper()
        if symbol in wanted and symbol not in gene_rows:
            gene_rows[symbol] = index
    genes = sorted(gene_rows)
    subset = matrix[[gene_rows[gene] for gene in genes], :].T.toarray().astype(np.float32)
    subset = np.log1p(subset / totals[:, None] * 10_000.0)
    spot_ids = [f"{section_id}::{barcode}" for barcode in barcodes]
    expression = pd.DataFrame(subset, columns=genes)
    expression.insert(0, "spot_id", spot_ids)

    positions = pd.read_csv(positions_path, header=None)
    if positions.shape[1] < 6:
        raise ValueError(f"Unexpected tissue positions format: {positions_path}")
    positions = positions.iloc[:, :6]
    positions.columns = ["barcode", "in_tissue", "array_row", "array_col", "pixel_y", "pixel_x"]
    positions["spot_id"] = section_id + "::" + positions["barcode"].astype(str)
    positions = positions[positions["in_tissue"].astype(int).eq(1)].copy()
    section = VISIUM_SECTIONS[section_id]
    positions["section_id"] = section_id
    positions["sample_label"] = section["sample_label"]
    positions["patient_id"] = section["patient_id"]
    positions["site"] = section["site"]
    positions["is_liver_metastasis"] = section["site"] == "liver_metastasis"
    positions["x"] = pd.to_numeric(positions["array_col"], errors="coerce")
    positions["y"] = pd.to_numeric(positions["array_row"], errors="coerce")
    metadata_columns = [
        "spot_id", "barcode", "section_id", "sample_label", "patient_id", "site",
        "is_liver_metastasis", "x", "y", "array_row", "array_col", "pixel_x", "pixel_y",
    ]
    metadata = positions[metadata_columns]
    expression = expression[expression["spot_id"].isin(metadata["spot_id"])].reset_index(drop=True)
    return expression, metadata.reset_index(drop=True)


def prepare_gse225857(raw_dir: str | Path, output_dir: str | Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    raw = Path(raw_dir)
    out = Path(output_dir)
    expression_path = out / "gse225857_signature_expression.tsv.gz"
    metadata_path = out / "gse225857_spatial_metadata.tsv"
    manifest_path = out / "spatial_data_manifest.tsv"
    if expression_path.exists() and metadata_path.exists() and manifest_path.exists():
        return (
            pd.read_csv(expression_path, sep="\t"),
            pd.read_csv(metadata_path, sep="\t"),
            pd.read_csv(manifest_path, sep="\t"),
        )
    archive = download(GSE225857_URL, raw / "GSE225857_RAW.tar")
    extracted = safe_extract(archive, raw / "extract")
    expression_parts: list[pd.DataFrame] = []
    metadata_parts: list[pd.DataFrame] = []
    manifest_rows: list[dict[str, object]] = []
    for section_id, section in VISIUM_SECTIONS.items():
        expression, metadata = load_visium_section(extracted, section_id)
        expression_parts.append(expression)
        metadata_parts.append(metadata)
        manifest_rows.append(
            {
                "dataset_id": "GSE225857",
                "section_id": section_id,
                "sample_label": section["sample_label"],
                "site": section["site"],
                "spots_under_tissue": len(metadata),
                "source_url": "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE225857",
                "study_doi": "10.1126/sciadv.adf5464",
                "patient_pairing": "not available for public Visium section IDs",
            }
        )
    expression = pd.concat(expression_parts, ignore_index=True)
    metadata = pd.concat(metadata_parts, ignore_index=True)
    manifest = pd.DataFrame(manifest_rows)
    out.mkdir(parents=True, exist_ok=True)
    expression.to_csv(expression_path, sep="\t", index=False, compression="gzip")
    metadata.to_csv(metadata_path, sep="\t", index=False)
    manifest.to_csv(manifest_path, sep="\t", index=False)
    return expression, metadata, manifest


def fetch_geomx_validation(raw_dir: str | Path, output_dir: str | Path) -> pd.DataFrame:
    raw_path = download(GEOMX_URL, Path(raw_dir) / "Counts.csv")
    frame = pd.read_csv(raw_path, index_col=0)
    availability = pd.DataFrame(
        [
            {
                "dataset_id": "Zenodo_7520789",
                "platform": "NanoString GeoMx CTA",
                "patients": 4,
                "aois": frame.shape[1],
                "genes": frame.shape[0],
                "role": "orthogonal matched primary/metastasis evidence",
                "status": "downloaded_not_region_labeled",
                "limitation": "public count table lacks a machine-readable AOI-to-tissue annotation",
                "doi": "10.5281/zenodo.7520789",
            }
        ]
    )
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    availability.to_csv(output / "geomx_validation_availability.tsv", sep="\t", index=False)
    return availability
