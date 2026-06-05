from __future__ import annotations

import pandas as pd

from .io import orient_expression
from .scoring import score_expression
from .signatures import SIGNATURES
from .summaries import add_state_flags


def score_single_cell_expression(expression: pd.DataFrame, metadata: pd.DataFrame | None = None) -> pd.DataFrame:
    known_genes = {gene.upper() for genes in SIGNATURES.values() for gene in genes}
    expr = orient_expression(expression, known_genes)
    scores = add_state_flags(score_expression(expr))
    if metadata is None:
        return scores
    meta = metadata.copy()
    if "cell_id" in meta.columns and "sample_id" not in meta.columns:
        meta = meta.rename(columns={"cell_id": "sample_id"})
    if "sample_id" not in meta.columns:
        meta = meta.rename(columns={meta.columns[0]: "sample_id"})
    meta["sample_id"] = meta["sample_id"].astype(str)
    return scores.merge(meta, on="sample_id", how="left")


def summarize_single_cell_states(
    scores: pd.DataFrame,
    group_cols: list[str] | None = None,
) -> pd.DataFrame:
    group_cols = group_cols or [col for col in ["dataset", "cell_type", "malignant_status"] if col in scores.columns]
    if not group_cols:
        group_cols = ["all_cells"]
        scores = scores.copy()
        scores["all_cells"] = "all"

    metrics = [
        "emt_score",
        "partial_emt_score",
        "stromal_fibroblast",
        "immune_total",
        "caf_tam_niche",
        "hypoxia",
        "ferroptosis_window",
    ]
    metrics = [metric for metric in metrics if metric in scores.columns]
    summary = scores.groupby(group_cols, dropna=False)[metrics].agg(["count", "mean", "median"]).reset_index()
    summary.columns = [
        "_".join(str(part) for part in col if part) if isinstance(col, tuple) else str(col)
        for col in summary.columns
    ]
    return summary

