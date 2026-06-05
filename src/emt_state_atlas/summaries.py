from __future__ import annotations

import pandas as pd


SCORE_COLUMNS = [
    "emt_score",
    "partial_emt_score",
    "stromal_fibroblast",
    "stromal_contamination_risk",
    "immune_total",
    "caf_tam_niche",
    "hypoxia",
    "ferroptosis_window",
]


def add_state_flags(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    out["emt_high"] = out["emt_score"] >= out["emt_score"].quantile(0.75)
    out["partial_emt_high"] = out["partial_emt_score"] >= out["partial_emt_score"].quantile(0.75)
    out["stromal_high"] = out["stromal_contamination_risk"] >= 0.75
    out["tumor_cell_emt_candidate"] = out["emt_high"] & ~out["stromal_high"]
    out["stromal_inflated_emt_candidate"] = out["emt_high"] & out["stromal_high"]
    out["ferroptosis_window_high"] = out["ferroptosis_window"] >= out["ferroptosis_window"].quantile(0.75)
    return out


def cancer_type_summary(frame: pd.DataFrame, cancer_type_col: str = "cancer_type") -> pd.DataFrame:
    available = [col for col in SCORE_COLUMNS if col in frame.columns]
    if cancer_type_col not in frame.columns:
        frame = frame.copy()
        frame[cancer_type_col] = "unknown"

    grouped = frame.groupby(cancer_type_col, dropna=False)
    summary = grouped[available].agg(["count", "mean", "median"]).reset_index()
    summary.columns = [
        "_".join(str(part) for part in col if part) if isinstance(col, tuple) else str(col)
        for col in summary.columns
    ]
    summary = summary.rename(columns={f"{cancer_type_col}_": cancer_type_col})
    if "emt_score_mean" in summary.columns:
        summary = summary.sort_values("emt_score_mean", ascending=False)
    return summary.reset_index(drop=True)


def validate_outputs(frame: pd.DataFrame, required: list[str]) -> pd.DataFrame:
    rows = []
    for column in required:
        rows.append(
            {
                "column": column,
                "present": column in frame.columns,
                "missing_values": int(frame[column].isna().sum()) if column in frame.columns else None,
            }
        )
    return pd.DataFrame(rows)

