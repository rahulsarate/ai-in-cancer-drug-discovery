from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.optimize import nnls


COMPARTMENT_COLUMNS = {
    "tumor_epithelial": ["epithelial"],
    "tumor_mesenchymal": ["emt_score", "partial_emt_score"],
    "caf": ["caf", "stromal_fibroblast"],
    "tam": ["tam_spp1"],
    "t_cell": ["t_cell_cytotoxic"],
    "hypoxic_zone": ["hypoxia"],
    "ecm_rich_zone": ["stromal_fibroblast", "caf"],
    "ferroptosis_window": ["ferroptosis_window"],
}


def estimate_marker_proxy_compartments(scored: pd.DataFrame) -> pd.DataFrame:
    """Create reference-free compartment proportions from signature scores.

    This is not a replacement for cell2location/RCTD/Tangram. It is a
    transparent first-pass proxy that lets downstream heterogeneous graphs run
    before matched scRNA-seq references are available.
    """
    values = pd.DataFrame({"spot_id": scored["spot_id"].astype(str)})
    raw = []
    for compartment, cols in COMPARTMENT_COLUMNS.items():
        present = [col for col in cols if col in scored.columns]
        if not present:
            values[compartment] = 0.0
        else:
            values[compartment] = scored[present].apply(pd.to_numeric, errors="coerce").mean(axis=1).fillna(0.0)
        raw.append(compartment)
    matrix = values[raw].to_numpy(dtype=float)
    matrix = matrix - np.nanmin(matrix, axis=1, keepdims=True)
    matrix = np.nan_to_num(matrix, nan=0.0)
    denom = matrix.sum(axis=1, keepdims=True)
    denom[denom == 0] = 1.0
    values[raw] = matrix / denom
    values["dominant_compartment"] = values[raw].idxmax(axis=1)
    values["deconvolution_method"] = "marker_proxy_reference_free"
    return values


def nnls_reference_deconvolution(expression: pd.DataFrame, reference: pd.DataFrame) -> pd.DataFrame:
    """Estimate spot proportions against a cell-type x gene reference matrix."""
    expr = expression.copy()
    ref = reference.copy()
    if "cell_type" not in ref.columns:
        raise ValueError("Reference table must contain a cell_type column.")
    genes = [col for col in ref.columns if col != "cell_type" and col in expr.columns]
    if not genes:
        raise ValueError("No shared genes between expression and reference.")
    ref_matrix = ref[genes].apply(pd.to_numeric, errors="coerce").fillna(0.0).to_numpy(dtype=float).T
    cell_types = ref["cell_type"].astype(str).tolist()
    rows = []
    for _, spot in expr.iterrows():
        y = spot[genes].apply(pd.to_numeric, errors="coerce").fillna(0.0).to_numpy(dtype=float)
        weights, residual = nnls(ref_matrix, y)
        total = weights.sum()
        proportions = weights / total if total > 0 else weights
        rows.append(
            {
                "spot_id": spot["spot_id"],
                **{cell_type: float(value) for cell_type, value in zip(cell_types, proportions)},
                "nnls_residual": float(residual),
                "deconvolution_method": "nnls_reference",
            }
        )
    return pd.DataFrame(rows)
