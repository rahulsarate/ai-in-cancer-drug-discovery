from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from emt_state_atlas.signatures import SIGNATURES


REQUIRED_COORD_COLUMNS = {"spot_id", "x", "y"}
DEMO_DRIVER_GENES = {
    "AXL",
    "GAS6",
    "TGFB1",
    "TGFBR1",
    "TGFBR2",
    "CXCL12",
    "CXCR4",
    "SPP1",
    "ITGAV",
    "CD44",
    "VEGFA",
    "KDR",
    "CSF1",
    "CSF1R",
}


def read_spatial_expression(path: str | Path) -> pd.DataFrame:
    """Read a spot x gene expression table.

    The first column may be named spot_id/sample_id/cell_id. Gene columns are
    normalized to uppercase symbols to stay compatible with EMT signatures.
    """
    frame = pd.read_csv(path, sep=None, engine="python")
    first = frame.columns[0]
    if first.lower() not in {"spot_id", "sample_id", "cell_id"}:
        raise ValueError("Expression table first column must identify spots.")
    frame = frame.rename(columns={first: "spot_id"})
    frame["spot_id"] = frame["spot_id"].astype(str)
    frame.columns = ["spot_id"] + [str(col).upper() for col in frame.columns[1:]]
    return frame


def read_spatial_metadata(path: str | Path) -> pd.DataFrame:
    frame = pd.read_csv(path, sep=None, engine="python")
    lower = {col.lower(): col for col in frame.columns}
    rename = {}
    for wanted in ["spot_id", "sample_id", "x", "y", "cohort", "cancer_type", "section_id"]:
        if wanted in lower:
            rename[lower[wanted]] = wanted
    frame = frame.rename(columns=rename)
    missing = REQUIRED_COORD_COLUMNS - set(frame.columns)
    if missing:
        raise ValueError(f"Spatial metadata missing required columns: {sorted(missing)}")
    frame["spot_id"] = frame["spot_id"].astype(str)
    return frame


def write_spatial_manifest(rows: list[dict], out: str | Path) -> pd.DataFrame:
    manifest = pd.DataFrame(rows)
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    manifest.to_csv(out, sep="\t", index=False)
    return manifest


def qc_spots(expression: pd.DataFrame, metadata: pd.DataFrame) -> pd.DataFrame:
    genes = [col for col in expression.columns if col != "spot_id"]
    counts = expression[genes].apply(pd.to_numeric, errors="coerce").fillna(0)
    qc = pd.DataFrame(
        {
            "spot_id": expression["spot_id"],
            "total_counts": counts.sum(axis=1),
            "detected_genes": (counts > 0).sum(axis=1),
        }
    )
    qc["low_library_risk"] = qc["total_counts"] <= qc["total_counts"].quantile(0.05)
    qc["low_complexity_risk"] = qc["detected_genes"] <= qc["detected_genes"].quantile(0.05)
    return metadata.merge(qc, on="spot_id", how="left")


def make_demo_spatial_dataset(out_dir: str | Path, n: int = 144, seed: int = 7) -> tuple[Path, Path]:
    """Create a synthetic Visium-like grid with EMT and stromal niches."""
    rng = np.random.default_rng(seed)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    side = int(np.sqrt(n))
    if side * side != n:
        raise ValueError("n must be a perfect square for the demo grid.")

    genes = sorted({gene for values in SIGNATURES.values() for gene in values} | DEMO_DRIVER_GENES)
    coords = []
    rows = []
    center = np.array([side * 0.62, side * 0.45])
    hypoxia_center = np.array([side * 0.42, side * 0.7])
    for i in range(side):
        for j in range(side):
            spot_id = f"SPOT_{i:02d}_{j:02d}"
            xy = np.array([i, j], dtype=float)
            niche = np.exp(-np.linalg.norm(xy - center) ** 2 / (2 * (side * 0.18) ** 2))
            hypoxia = np.exp(-np.linalg.norm(xy - hypoxia_center) ** 2 / (2 * (side * 0.16) ** 2))
            tumor = 1.0 if j < side * 0.72 else 0.35
            stromal = 1.0 - tumor + 0.65 * niche
            immune = 0.25 + 0.55 * np.exp(-np.linalg.norm(xy - np.array([side * 0.75, side * 0.75])) ** 2 / 9)
            expr = {"spot_id": spot_id}
            for gene in genes:
                value = rng.normal(2.0, 0.35)
                if gene in SIGNATURES["epithelial"]:
                    value += 2.2 * tumor * (1 - niche)
                if gene in SIGNATURES["mesenchymal"] or gene in SIGNATURES["partial_emt_anchor"]:
                    value += 2.6 * niche
                if gene in SIGNATURES["stromal_fibroblast"] or gene in SIGNATURES["caf"]:
                    value += 2.8 * stromal
                if gene in SIGNATURES["tam_spp1"] or gene in SIGNATURES["immune_total"]:
                    value += 2.2 * immune
                if gene in SIGNATURES["hypoxia"]:
                    value += 2.4 * hypoxia
                if gene in {"AXL", "GAS6", "TGFB1", "TGFBR1", "TGFBR2", "SPP1", "ITGAV", "CD44"}:
                    value += 2.3 * niche
                if gene in {"CXCL12", "CSF1", "CSF1R"}:
                    value += 1.8 * stromal
                if gene in {"VEGFA", "KDR"}:
                    value += 1.6 * hypoxia
                expr[gene] = round(max(value, 0.0), 4)
            rows.append(expr)
            coords.append(
                {
                    "spot_id": spot_id,
                    "sample_id": "demo_slide_001",
                    "section_id": "demo_section_A",
                    "cohort": "synthetic",
                    "cancer_type": "demo_breast",
                    "x": float(i),
                    "y": float(j),
                    "pathologist_region": "invasive_edge" if niche > 0.55 else "tumor_core" if tumor > 0.8 else "stroma",
                    "weak_label_source": "synthetic_distance_to_invasive_edge",
                }
            )

    expression_path = out / "demo_spatial_expression.tsv"
    metadata_path = out / "demo_spatial_metadata.tsv"
    pd.DataFrame(rows).to_csv(expression_path, sep="\t", index=False)
    pd.DataFrame(coords).to_csv(metadata_path, sep="\t", index=False)
    return expression_path, metadata_path
