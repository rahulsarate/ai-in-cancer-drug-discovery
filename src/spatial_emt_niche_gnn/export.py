from __future__ import annotations

from pathlib import Path

import h5py
import numpy as np
import pandas as pd


def write_lightweight_h5ad(expression: pd.DataFrame, metadata: pd.DataFrame, out: str | Path) -> Path:
    """Write a small AnnData-compatible HDF5 skeleton without requiring anndata.

    This stores the core fields we need for reproducibility: X, obs names,
    variable names, and spatial coordinates. Full AnnData objects can be
    regenerated later when `anndata` is installed.
    """
    path = Path(out)
    path.parent.mkdir(parents=True, exist_ok=True)
    expr = expression.copy()
    meta = metadata.copy()
    genes = [col for col in expr.columns if col != "spot_id"]
    expr = expr[expr["spot_id"].isin(set(meta["spot_id"].astype(str)))].copy()
    meta = meta.set_index("spot_id").loc[expr["spot_id"].astype(str)].reset_index()
    x = expr[genes].apply(pd.to_numeric, errors="coerce").fillna(0).to_numpy(dtype=np.float32)
    spatial = meta[["x", "y"]].apply(pd.to_numeric, errors="coerce").fillna(0).to_numpy(dtype=np.float32)
    with h5py.File(path, "w") as handle:
        handle.create_dataset("X", data=x, compression="gzip")
        handle.create_dataset("obs/_index", data=np.array(meta["spot_id"].astype(str), dtype="S"))
        handle.create_dataset("var/_index", data=np.array(genes, dtype="S"))
        handle.create_dataset("obsm/spatial", data=spatial)
        obs = handle.create_group("obs/columns")
        for col in ["sample_id", "section_id", "cohort", "cancer_type", "disease", "weak_label_source"]:
            if col in meta.columns:
                obs.create_dataset(col, data=np.array(meta[col].fillna("").astype(str), dtype="S"))
        handle.attrs["encoding-type"] = "spatial_emt_lightweight_h5ad"
        handle.attrs["note"] = "Core AnnData-like fields only; use anndata for full h5ad conversion."
    return path
