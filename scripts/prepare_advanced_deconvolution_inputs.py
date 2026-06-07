from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from spatial_emt_niche_gnn.data import read_spatial_expression, read_spatial_metadata


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Prepare Tangram/cell2location/RCTD-ready inputs from spatial tables and a cell-type reference.")
    p.add_argument("--expression", required=True)
    p.add_argument("--metadata", required=True)
    p.add_argument("--reference", required=True)
    p.add_argument("--out-dir", required=True)
    return p


def write_anndata(expression: pd.DataFrame, metadata: pd.DataFrame, out: Path) -> tuple[bool, str]:
    try:
        import anndata as ad
        import numpy as np
    except Exception as exc:
        return False, f"anndata import failed: {type(exc).__name__}: {exc}"
    genes = [col for col in expression.columns if col != "spot_id"]
    expr = expression[expression["spot_id"].isin(set(metadata["spot_id"].astype(str)))].copy()
    meta = metadata.set_index("spot_id").loc[expr["spot_id"].astype(str)].copy()
    x = expr[genes].apply(pd.to_numeric, errors="coerce").fillna(0).to_numpy(dtype="float32")
    adata = ad.AnnData(X=x, obs=meta, var=pd.DataFrame(index=genes))
    adata.obsm["spatial"] = meta[["x", "y"]].apply(pd.to_numeric, errors="coerce").fillna(0).to_numpy(dtype="float32")
    adata.write_h5ad(out)
    return True, str(out)


def write_reference_anndata(reference: pd.DataFrame, out: Path) -> tuple[bool, str]:
    try:
        import anndata as ad
    except Exception as exc:
        return False, f"anndata import failed: {type(exc).__name__}: {exc}"
    genes = [col for col in reference.columns if col != "cell_type"]
    x = reference[genes].apply(pd.to_numeric, errors="coerce").fillna(0).to_numpy(dtype="float32")
    cell_types = reference["cell_type"].map(str).tolist()
    obs = pd.DataFrame({"cell_type": cell_types}, index=cell_types, dtype=object)
    obs.index.name = "pseudo_cell_id"
    adata = ad.AnnData(X=x, obs=obs, var=pd.DataFrame(index=genes))
    adata.write_h5ad(out)
    return True, str(out)


def main() -> None:
    args = parser().parse_args()
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    expression = read_spatial_expression(args.expression)
    metadata = read_spatial_metadata(args.metadata)
    reference = pd.read_csv(args.reference, sep="\t")
    genes = [col for col in expression.columns if col != "spot_id" and col in reference.columns]
    expression_shared = expression[["spot_id", *genes]].copy()
    reference_shared = reference[["cell_type", *genes]].copy()

    expression_shared.to_csv(out / "spatial_counts_for_deconvolution.tsv", sep="\t", index=False)
    metadata.to_csv(out / "spatial_metadata_for_deconvolution.tsv", sep="\t", index=False)
    reference_shared.to_csv(out / "scrna_reference_for_deconvolution.tsv", sep="\t", index=False)

    spatial_ok, spatial_msg = write_anndata(expression_shared, metadata, out / "spatial_counts_for_deconvolution.h5ad")
    ref_ok, ref_msg = write_reference_anndata(reference_shared, out / "scrna_reference_pseudocells_for_deconvolution.h5ad")
    rows = [
        {
            "adapter": "Tangram",
            "input_ready": spatial_ok and ref_ok,
            "spatial_input": str(out / "spatial_counts_for_deconvolution.h5ad"),
            "reference_input": str(out / "scrna_reference_pseudocells_for_deconvolution.h5ad"),
            "note": "Reference is cell-type pseudo-cells; true Tangram mapping improves with cell-level scRNA matrix.",
        },
        {
            "adapter": "cell2location",
            "input_ready": spatial_ok and ref_ok,
            "spatial_input": str(out / "spatial_counts_for_deconvolution.h5ad"),
            "reference_input": str(out / "scrna_reference_pseudocells_for_deconvolution.h5ad"),
            "note": "Use pseudo-cells for smoke testing; publication run should use cell-level scRNA counts and labels.",
        },
        {
            "adapter": "RCTD/spacexr",
            "input_ready": True,
            "spatial_input": str(out / "spatial_counts_for_deconvolution.tsv"),
            "reference_input": str(out / "scrna_reference_for_deconvolution.tsv"),
            "note": "TSV inputs are ready for R conversion into SpatialRNA and Reference objects.",
        },
    ]
    pd.DataFrame(rows).to_csv(out / "advanced_deconvolution_input_manifest.tsv", sep="\t", index=False)
    pd.DataFrame(
        [
            {"check": "shared_genes", "value": len(genes), "status": "ok" if genes else "failed"},
            {"check": "spatial_h5ad", "value": spatial_msg, "status": "ok" if spatial_ok else "failed"},
            {"check": "reference_h5ad", "value": ref_msg, "status": "ok" if ref_ok else "failed"},
            {"check": "spots", "value": len(expression_shared), "status": "ok"},
            {"check": "reference_cell_types", "value": len(reference_shared), "status": "ok"},
        ]
    ).to_csv(out / "advanced_deconvolution_input_qc.tsv", sep="\t", index=False)
    print(f"Wrote advanced deconvolution inputs to {out}")


if __name__ == "__main__":
    main()
