from __future__ import annotations

import gzip
import shutil
import tarfile
from pathlib import Path
from urllib.request import Request, urlopen

import pandas as pd
from scipy.io import mmread
from scipy.sparse import csc_matrix

from emt_state_atlas.signatures import SIGNATURES
from .data import DEMO_DRIVER_GENES


TENX_BREAST_CANCER = {
    "dataset_id": "Visium_FFPE_Human_Breast_Cancer",
    "dataset_name": "10x Visium FFPE Human Breast Cancer",
    "matrix_url": "https://cf.10xgenomics.com/samples/spatial-exp/1.3.0/Visium_FFPE_Human_Breast_Cancer/Visium_FFPE_Human_Breast_Cancer_filtered_feature_bc_matrix.tar.gz",
    "spatial_url": "https://cf.10xgenomics.com/samples/spatial-exp/1.3.0/Visium_FFPE_Human_Breast_Cancer/Visium_FFPE_Human_Breast_Cancer_spatial.tar.gz",
    "source_page": "https://www.10xgenomics.com/datasets/human-breast-cancer-ductal-carcinoma-in-situ-invasive-carcinoma-ffpe-1-standard-1-3-0",
    "cancer_type": "breast_cancer",
    "disease": "Invasive Ductal Carcinoma",
}

TENX_LUNG_LUSC = {
    "dataset_id": "CytAssist_FFPE_Human_Lung_Squamous_Cell_Carcinoma",
    "dataset_name": "10x CytAssist FFPE Human Lung Squamous Cell Carcinoma",
    "matrix_url": "https://cf.10xgenomics.com/samples/spatial-exp/2.0.0/CytAssist_FFPE_Human_Lung_Squamous_Cell_Carcinoma/CytAssist_FFPE_Human_Lung_Squamous_Cell_Carcinoma_filtered_feature_bc_matrix.tar.gz",
    "spatial_url": "https://cf.10xgenomics.com/samples/spatial-exp/2.0.0/CytAssist_FFPE_Human_Lung_Squamous_Cell_Carcinoma/CytAssist_FFPE_Human_Lung_Squamous_Cell_Carcinoma_spatial.tar.gz",
    "source_page": "https://cf.10xgenomics.com/samples/spatial-exp/2.0.0/CytAssist_FFPE_Human_Lung_Squamous_Cell_Carcinoma/CytAssist_FFPE_Human_Lung_Squamous_Cell_Carcinoma_web_summary.html",
    "cancer_type": "lung_cancer",
    "disease": "Lung Squamous Cell Carcinoma",
}

TENX_PROSTATE = {
    "dataset_id": "Visium_FFPE_Human_Prostate_Cancer",
    "dataset_name": "10x Visium FFPE Human Prostate Cancer",
    "matrix_url": "https://cf.10xgenomics.com/samples/spatial-exp/1.3.0/Visium_FFPE_Human_Prostate_Cancer/Visium_FFPE_Human_Prostate_Cancer_filtered_feature_bc_matrix.tar.gz",
    "spatial_url": "https://cf.10xgenomics.com/samples/spatial-exp/1.3.0/Visium_FFPE_Human_Prostate_Cancer/Visium_FFPE_Human_Prostate_Cancer_spatial.tar.gz",
    "source_page": "https://www.10xgenomics.com/datasets/human-prostate-cancer-1-standard",
    "cancer_type": "prostate_cancer",
    "disease": "Prostate Cancer",
}

TENX_OVARIAN = {
    "dataset_id": "Visium_FFPE_Human_Ovarian_Cancer",
    "dataset_name": "10x Visium FFPE Human Ovarian Cancer",
    "matrix_url": "https://cf.10xgenomics.com/samples/spatial-exp/1.3.0/Visium_FFPE_Human_Ovarian_Cancer/Visium_FFPE_Human_Ovarian_Cancer_filtered_feature_bc_matrix.tar.gz",
    "spatial_url": "https://cf.10xgenomics.com/samples/spatial-exp/1.3.0/Visium_FFPE_Human_Ovarian_Cancer/Visium_FFPE_Human_Ovarian_Cancer_spatial.tar.gz",
    "source_page": "https://www.10xgenomics.com/datasets/human-ovarian-cancer-1-standard",
    "cancer_type": "ovarian_cancer",
    "disease": "Ovarian Cancer",
}

TENX_COLORECTAL = {
    "dataset_id": "Visium_FFPE_Human_Intestinal_Cancer",
    "dataset_name": "10x Visium FFPE Human Intestinal/Colorectal Cancer",
    "matrix_url": "https://cf.10xgenomics.com/samples/spatial-exp/1.3.0/Visium_FFPE_Human_Intestinal_Cancer/Visium_FFPE_Human_Intestinal_Cancer_filtered_feature_bc_matrix.tar.gz",
    "spatial_url": "https://cf.10xgenomics.com/samples/spatial-exp/1.3.0/Visium_FFPE_Human_Intestinal_Cancer/Visium_FFPE_Human_Intestinal_Cancer_spatial.tar.gz",
    "source_page": "https://www.10xgenomics.com/datasets/human-intestine-cancer-1-standard",
    "cancer_type": "colorectal_cancer",
    "disease": "Large Intestine Colorectal Cancer",
}

GEO_PDAC_GSE274103 = {
    "dataset_id": "GSE274103",
    "dataset_name": "GEO GSE274103 treatment-naive PDAC Visium FFPE",
    "raw_url": "https://www.ncbi.nlm.nih.gov/geo/download/?acc=GSE274103&format=file",
    "source_page": "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE274103",
    "disease": "Pancreatic Ductal Adenocarcinoma",
}

GEO_BRAIN_MET_GSE179572 = {
    "dataset_id": "GSE179572",
    "dataset_name": "GEO GSE179572 human brain metastasis Visium",
    "raw_url": "https://www.ncbi.nlm.nih.gov/geo/download/?acc=GSE179572&format=file",
    "source_page": "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE179572",
    "cancer_type": "brain_metastasis",
    "disease": "Brain Metastasis",
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


def _decode_array(values) -> list[str]:
    out = []
    for value in values:
        if isinstance(value, bytes):
            out.append(value.decode("utf-8"))
        else:
            out.append(str(value))
    return out


def load_filtered_signature_h5(path: Path) -> pd.DataFrame:
    import h5py

    wanted = required_genes()
    with h5py.File(path, "r") as handle:
        matrix_group = handle["matrix"]
        features = matrix_group["features"]
        names = [name.upper() for name in _decode_array(features["name"][:])]
        barcodes = _decode_array(matrix_group["barcodes"][:])
        gene_rows = {}
        for idx, symbol in enumerate(names):
            if symbol in wanted and symbol not in gene_rows:
                gene_rows[symbol] = idx
        if not gene_rows:
            raise RuntimeError(f"No EMT/signature genes found in {path}")
        matrix = csc_matrix(
            (
                matrix_group["data"][:],
                matrix_group["indices"][:],
                matrix_group["indptr"][:],
            ),
            shape=tuple(matrix_group["shape"][:]),
        )
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


def prepare_10x_public_dataset(config: dict, raw_dir: str | Path, out_dir: str | Path, output_prefix: str) -> tuple[Path, Path]:
    raw = Path(raw_dir)
    out = Path(out_dir)
    dataset_id = config["dataset_id"]
    dataset_raw = raw / dataset_id
    matrix_tar = dataset_raw / "filtered_feature_bc_matrix.tar.gz"
    spatial_tar = dataset_raw / "spatial.tar.gz"
    download(config["matrix_url"], matrix_tar)
    download(config["spatial_url"], spatial_tar)
    extract_tarball(matrix_tar, dataset_raw)
    extract_tarball(spatial_tar, dataset_raw)

    expression = load_filtered_signature_matrix(dataset_raw, dataset_id)
    metadata = load_spatial_metadata(dataset_raw, dataset_id)
    metadata["disease"] = config.get("disease", metadata.get("disease", ""))
    metadata["cancer_type"] = config.get("cancer_type", metadata.get("cancer_type", ""))
    metadata["source_page"] = config.get("source_page", "")
    expression = expression[expression["spot_id"].isin(set(metadata["spot_id"]))].copy()
    out.mkdir(parents=True, exist_ok=True)
    expression_path = out / f"{output_prefix}_signature_expression.tsv"
    metadata_path = out / f"{output_prefix}_spatial_metadata.tsv"
    expression.to_csv(expression_path, sep="\t", index=False)
    metadata.to_csv(metadata_path, sep="\t", index=False)
    return expression_path, metadata_path


def prepare_10x_breast_cancer(raw_dir: str | Path, out_dir: str | Path) -> tuple[Path, Path]:
    return prepare_10x_public_dataset(TENX_BREAST_CANCER, raw_dir, out_dir, "10x_breast_cancer")


def prepare_10x_lung_lusc(raw_dir: str | Path, out_dir: str | Path) -> tuple[Path, Path]:
    return prepare_10x_public_dataset(TENX_LUNG_LUSC, raw_dir, out_dir, "10x_lung_lusc")


def prepare_10x_prostate(raw_dir: str | Path, out_dir: str | Path) -> tuple[Path, Path]:
    return prepare_10x_public_dataset(TENX_PROSTATE, raw_dir, out_dir, "10x_prostate")


def prepare_10x_ovarian(raw_dir: str | Path, out_dir: str | Path) -> tuple[Path, Path]:
    return prepare_10x_public_dataset(TENX_OVARIAN, raw_dir, out_dir, "10x_ovarian")


def prepare_10x_colorectal(raw_dir: str | Path, out_dir: str | Path) -> tuple[Path, Path]:
    return prepare_10x_public_dataset(TENX_COLORECTAL, raw_dir, out_dir, "10x_colorectal")


def prepare_geo_pdac_gse274103(raw_dir: str | Path, out_dir: str | Path, max_samples: int | None = None) -> tuple[Path, Path]:
    return prepare_geo_h5_visium(
        GEO_PDAC_GSE274103,
        raw_dir,
        out_dir,
        "geo_pdac_gse274103",
        "pancreatic_cancer",
        max_samples=max_samples,
    )


def prepare_geo_brain_met_gse179572(raw_dir: str | Path, out_dir: str | Path, max_samples: int | None = None) -> tuple[Path, Path]:
    return prepare_geo_h5_visium(
        GEO_BRAIN_MET_GSE179572,
        raw_dir,
        out_dir,
        "geo_brain_met_gse179572",
        "brain_metastasis",
        max_samples=max_samples,
    )


def prepare_geo_h5_visium(
    config: dict,
    raw_dir: str | Path,
    out_dir: str | Path,
    output_prefix: str,
    cancer_type: str,
    max_samples: int | None = None,
) -> tuple[Path, Path]:
    raw = Path(raw_dir)
    out = Path(out_dir)
    dataset_id = config["dataset_id"]
    dataset_raw = raw / dataset_id
    dataset_raw.mkdir(parents=True, exist_ok=True)
    raw_tar = dataset_raw / f"{dataset_id}_RAW.tar"
    download(config["raw_url"], raw_tar)
    extract_dir = dataset_raw / "extract"
    marker = extract_dir / f".extracted_{dataset_id}_RAW"
    if not marker.exists():
        extract_dir.mkdir(parents=True, exist_ok=True)
        with tarfile.open(raw_tar, "r") as archive:
            base = extract_dir.resolve()
            for member in archive.getmembers():
                target = (extract_dir / member.name).resolve()
                if base not in target.parents and target != base:
                    raise RuntimeError(f"Unsafe path in tar archive: {member.name}")
            archive.extractall(extract_dir)
        marker.write_text("ok\n", encoding="utf-8")

    h5_files = sorted(extract_dir.glob("*_filtered_feature_bc_matrix.h5"))
    if max_samples:
        h5_files = h5_files[:max_samples]
    expression_tables = []
    metadata_tables = []
    for h5_path in h5_files:
        sample_id = h5_path.name.replace("_filtered_feature_bc_matrix.h5", "")
        spatial_matches = sorted(extract_dir.glob(f"{sample_id}*spatial.tar.gz"))
        spatial_tar = spatial_matches[0] if spatial_matches else extract_dir / f"{sample_id}_spatial.tar.gz"
        sample_spatial = extract_dir / f"{sample_id}_spatial"
        extract_tarball(spatial_tar, sample_spatial)
        expression = load_filtered_signature_h5(h5_path)
        metadata = load_spatial_metadata(sample_spatial, sample_id)
        metadata["raw_barcode"] = metadata["spot_id"]
        metadata["spot_id"] = sample_id + "|" + metadata["raw_barcode"].astype(str)
        metadata["sample_id"] = sample_id
        metadata["cohort"] = output_prefix
        metadata["cancer_type"] = cancer_type
        metadata["disease"] = config["disease"]
        metadata["source_page"] = config["source_page"]
        expression["spot_id"] = sample_id + "|" + expression["spot_id"].astype(str)
        expression = expression[expression["spot_id"].isin(set(metadata["spot_id"]))].copy()
        expression_tables.append(expression)
        metadata_tables.append(metadata)

    out.mkdir(parents=True, exist_ok=True)
    expression_path = out / f"{output_prefix}_signature_expression.tsv"
    metadata_path = out / f"{output_prefix}_spatial_metadata.tsv"
    pd.concat(expression_tables, ignore_index=True).to_csv(expression_path, sep="\t", index=False)
    pd.concat(metadata_tables, ignore_index=True).to_csv(metadata_path, sep="\t", index=False)
    return expression_path, metadata_path
