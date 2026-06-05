from __future__ import annotations

import gzip
import shutil
import tarfile
from pathlib import Path
from urllib.request import Request, urlopen

import pandas as pd
from scipy.io import mmread

from emt_state_atlas.signatures import SIGNATURES
from .data import DEMO_DRIVER_GENES


TENX_BREAST_CANCER = {
    "dataset_id": "Visium_FFPE_Human_Breast_Cancer",
    "dataset_name": "10x Visium FFPE Human Breast Cancer",
    "matrix_url": "https://cf.10xgenomics.com/samples/spatial-exp/1.3.0/Visium_FFPE_Human_Breast_Cancer/Visium_FFPE_Human_Breast_Cancer_filtered_feature_bc_matrix.tar.gz",
    "spatial_url": "https://cf.10xgenomics.com/samples/spatial-exp/1.3.0/Visium_FFPE_Human_Breast_Cancer/Visium_FFPE_Human_Breast_Cancer_spatial.tar.gz",
    "source_page": "https://www.10xgenomics.com/datasets/human-breast-cancer-ductal-carcinoma-in-situ-invasive-carcinoma-ffpe-1-standard-1-3-0",
    "disease": "Invasive Ductal Carcinoma",
}


def required_genes() -> set[str]:
    return {gene.upper() for genes in SIGNATURES.values() for gene in genes} | DEMO_DRIVER_GENES


def download(url: str, out: Path) -> None:
    if out.exists():
        return
    out.parent.mkdir(parents=True, exist_ok=True)
    request = Request(url, headers={"User-Agent": "Mozilla/5.0 spatial-emt-niche-gnn/0.1"})
    with urlopen(request, timeout=180) as response, open(out, "wb") as handle:
        shutil.copyfileobj(response, handle)


def extract_tarball(tar_path: Path, out_dir: Path) -> None:
    marker = out_dir / f".extracted_{tar_path.stem.replace('.', '_')}"
    if marker.exists():
        return
    out_dir.mkdir(parents=True, exist_ok=True)
    with tarfile.open(tar_path, "r:gz") as archive:
        base = out_dir.resolve()
        for member in archive.getmembers():
            target = (out_dir / member.name).resolve()
            if base not in target.parents and target != base:
                raise RuntimeError(f"Unsafe path in tar archive: {member.name}")
        archive.extractall(out_dir)
    marker.write_text("ok\n", encoding="utf-8")


def find_file(root: Path, name: str) -> Path:
    matches = list(root.rglob(name))
    if not matches:
        raise FileNotFoundError(f"Could not find {name} under {root}")
    return matches[0]


def read_gzip_lines(path: Path) -> list[list[str]]:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        return [line.rstrip("\n").split("\t") for line in handle]


def load_filtered_signature_matrix(root: Path, dataset_id: str) -> pd.DataFrame:
    matrix_path = find_file(root, "matrix.mtx.gz")
    features_path = find_file(root, "features.tsv.gz")
    barcodes_path = find_file(root, "barcodes.tsv.gz")
    features = read_gzip_lines(features_path)
    barcodes = [row[0] for row in read_gzip_lines(barcodes_path)]

    wanted = required_genes()
    gene_rows: dict[str, int] = {}
    for idx, row in enumerate(features):
        symbol = row[1].upper() if len(row) > 1 else row[0].upper()
        if symbol in wanted and symbol not in gene_rows:
            gene_rows[symbol] = idx
    if not gene_rows:
        raise RuntimeError("No EMT/signature genes found in 10x matrix.")

    matrix = mmread(str(matrix_path)).tocsr()
    subset = matrix[list(gene_rows.values()), :].toarray().T
    expression = pd.DataFrame(subset, columns=list(gene_rows.keys()))
    expression.insert(0, "spot_id", barcodes)
    return expression


def load_spatial_metadata(root: Path, dataset_id: str) -> pd.DataFrame:
    candidates = list(root.rglob("tissue_positions*.csv"))
    if not candidates:
        candidates = list(root.rglob("tissue_positions_list.csv"))
    if not candidates:
        raise FileNotFoundError("Could not find tissue_positions CSV.")
    path = candidates[0]
    first = path.read_text(encoding="utf-8").splitlines()[0].split(",")[0]
    if first == "barcode":
        pos = pd.read_csv(path)
    else:
        pos = pd.read_csv(
            path,
            header=None,
            names=["barcode", "in_tissue", "array_row", "array_col", "pxl_row_in_fullres", "pxl_col_in_fullres"],
        )
    pos = pos[pos["in_tissue"].astype(int).eq(1)].copy()
    pos["spot_id"] = pos["barcode"].astype(str)
    pos["sample_id"] = dataset_id
    pos["section_id"] = "section_B1"
    pos["cohort"] = "10x_public"
    pos["cancer_type"] = "breast_cancer"
    pos["disease"] = TENX_BREAST_CANCER["disease"]
    pos["x"] = pd.to_numeric(pos["array_col"], errors="coerce")
    pos["y"] = pd.to_numeric(pos["array_row"], errors="coerce")
    pos["pixel_x"] = pd.to_numeric(pos.get("pxl_col_in_fullres"), errors="coerce")
    pos["pixel_y"] = pd.to_numeric(pos.get("pxl_row_in_fullres"), errors="coerce")
    pos["weak_label_source"] = "emt_partial_emt_tme_proxy_no_pathologist_spot_labels"
    return pos[
        [
            "spot_id",
            "sample_id",
            "section_id",
            "cohort",
            "cancer_type",
            "disease",
            "x",
            "y",
            "pixel_x",
            "pixel_y",
            "weak_label_source",
        ]
    ]


def prepare_10x_breast_cancer(raw_dir: str | Path, out_dir: str | Path) -> tuple[Path, Path]:
    raw = Path(raw_dir)
    out = Path(out_dir)
    dataset_id = TENX_BREAST_CANCER["dataset_id"]
    dataset_raw = raw / dataset_id
    matrix_tar = dataset_raw / "filtered_feature_bc_matrix.tar.gz"
    spatial_tar = dataset_raw / "spatial.tar.gz"
    download(TENX_BREAST_CANCER["matrix_url"], matrix_tar)
    download(TENX_BREAST_CANCER["spatial_url"], spatial_tar)
    extract_tarball(matrix_tar, dataset_raw)
    extract_tarball(spatial_tar, dataset_raw)

    expression = load_filtered_signature_matrix(dataset_raw, dataset_id)
    metadata = load_spatial_metadata(dataset_raw, dataset_id)
    expression = expression[expression["spot_id"].isin(set(metadata["spot_id"]))].copy()
    out.mkdir(parents=True, exist_ok=True)
    expression_path = out / "10x_breast_cancer_signature_expression.tsv"
    metadata_path = out / "10x_breast_cancer_spatial_metadata.tsv"
    expression.to_csv(expression_path, sep="\t", index=False)
    metadata.to_csv(metadata_path, sep="\t", index=False)
    return expression_path, metadata_path
