from __future__ import annotations

import numpy as np
import pandas as pd

from emt_state_atlas.scoring import score_expression
from emt_state_atlas.summaries import add_state_flags


SPATIAL_SCORE_COLUMNS = [
    "emt_score",
    "partial_emt_score",
    "stromal_contamination_risk",
    "immune_context",
    "caf_tam_niche",
    "hypoxia",
    "ecm_remodeling",
    "angiogenesis",
    "ferroptosis_window",
]

DRIVER_GENES = [
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
]


def score_spatial_niches(expression: pd.DataFrame, metadata: pd.DataFrame) -> pd.DataFrame:
    genes = [col for col in expression.columns if col != "spot_id"]
    expr = expression.set_index("spot_id")[genes].apply(pd.to_numeric, errors="coerce").fillna(0.0)
    scores = add_state_flags(score_expression(expr)).rename(columns={"sample_id": "spot_id"})
    for gene in DRIVER_GENES:
        if gene in expr.columns:
            scores[gene] = expr[gene].to_numpy()
    merged = scores.merge(metadata, on="spot_id", how="left")
    return add_spatial_proxy_labels(merged)


def add_spatial_proxy_labels(frame: pd.DataFrame) -> pd.DataFrame:
    """Create transparent weak labels for model development.

    These are not ground truth EMT labels. They combine tumor-cell EMT candidate
    status with spatial niche context so downstream models can be benchmarked
    before pathologist-reviewed annotations are available.
    """
    out = frame.copy()
    niche_cols = [
        col
        for col in ["caf_tam_niche", "hypoxia", "ecm_remodeling", "angiogenesis", "stromal_contamination_risk"]
        if col in out.columns
    ]
    niche = out[niche_cols].rank(pct=True).mean(axis=1)
    partial = out["partial_emt_score"].rank(pct=True)
    tumor_emt = out["tumor_cell_emt_candidate"].astype(float)
    out["emt_niche_proxy_score"] = (0.45 * tumor_emt + 0.35 * partial + 0.20 * niche).clip(0, 1)
    out["emt_niche_label"] = out["emt_niche_proxy_score"] >= out["emt_niche_proxy_score"].quantile(0.75)
    out["label_strength"] = np.where(out["tumor_cell_emt_candidate"], "strong_proxy", "weak_proxy")
    out.loc[out["stromal_inflated_emt_candidate"], "label_strength"] = "contamination_risk"
    return out


def summarize_niches(scored: pd.DataFrame) -> pd.DataFrame:
    group_cols = [col for col in ["cohort", "cancer_type", "sample_id", "section_id"] if col in scored.columns]
    if not group_cols:
        group_cols = ["sample_id"]
        scored = scored.copy()
        scored["sample_id"] = "unknown"
    summary = scored.groupby(group_cols, dropna=False).agg(
        spots=("spot_id", "count"),
        emt_niche_fraction=("emt_niche_label", "mean"),
        stromal_inflated_fraction=("stromal_inflated_emt_candidate", "mean"),
        tumor_cell_emt_fraction=("tumor_cell_emt_candidate", "mean"),
        mean_partial_emt=("partial_emt_score", "mean"),
        mean_caf_tam=("caf_tam_niche", "mean"),
        mean_hypoxia=("hypoxia", "mean"),
        mean_ecm_remodeling=("ecm_remodeling", "mean"),
        mean_angiogenesis=("angiogenesis", "mean"),
    )
    return summary.reset_index()
