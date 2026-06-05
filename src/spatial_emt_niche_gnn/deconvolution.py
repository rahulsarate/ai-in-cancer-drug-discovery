from __future__ import annotations

import numpy as np
import pandas as pd


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
