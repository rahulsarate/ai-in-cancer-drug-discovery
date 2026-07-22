from __future__ import annotations

import pandas as pd


def group_small_cohort_warnings(group_summary: pd.DataFrame, min_samples: int = 50) -> pd.DataFrame:
    if group_summary.empty or "cancer_group" not in group_summary.columns:
        return pd.DataFrame()
    rows = []
    for _, row in group_summary.iterrows():
        warnings = []
        n = int(row.get("sample_count", 0) or 0)
        if n < min_samples:
            warnings.append(f"small_cohort_n_{n}")
        if row.get("high_confidence_fraction", 0) < 0.2:
            warnings.append("low_high-confidence_fraction")
        if row.get("stromal_dominant_fraction", 0) > 0.25:
            warnings.append("high_stromal_dominant_fraction")
        rows.append({"cancer_group": row["cancer_group"], "app_warning": ";".join(warnings) if warnings else "ok"})
    return pd.DataFrame(rows)


def state_comparison_table(scores: pd.DataFrame) -> pd.DataFrame:
    required = {"cancer_group", "consensus_emt_state"}
    if scores.empty or not required.issubset(scores.columns):
        return pd.DataFrame()
    metrics = [col for col in ["emt_score", "partial_emt_score", "stromal_contamination_risk", "hypoxia", "caf_tam_niche"] if col in scores.columns]
    grouped = (
        scores.groupby(["cancer_group", "consensus_emt_state"], dropna=False)
        .agg(samples=("sample_id", "count"), **{f"{metric}_mean": (metric, "mean") for metric in metrics})
        .reset_index()
    )
    total = scores.groupby("cancer_group")["sample_id"].count().rename("group_samples").reset_index()
    grouped = grouped.merge(total, on="cancer_group", how="left")
    grouped["state_fraction"] = grouped["samples"] / grouped["group_samples"].replace(0, pd.NA)
    return grouped.sort_values(["cancer_group", "state_fraction"], ascending=[True, False]).reset_index(drop=True)
