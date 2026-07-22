from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class ConsensusThresholds:
    epithelial_high_quantile: float = 0.67
    mesenchymal_high_quantile: float = 0.67
    hybrid_min_quantile: float = 0.50
    stromal_warning_quantile: float = 0.75
    immune_inflamed_quantile: float = 0.75
    hypoxia_high_quantile: float = 0.75
    minimum_signature_gene_coverage: float = 0.60
    minimum_cancer_type_samples_for_survival: int = 30


REQUIRED_SCORE_COLUMNS = ["epithelial", "mesenchymal", "emt_score", "partial_emt_score"]


STATE_EXPLANATIONS = {
    "epithelial": "Epithelial program is dominant and mesenchymal activity is relatively low.",
    "hybrid_e_m": "Both epithelial and mesenchymal programs are active, consistent with a partial or hybrid EMT state.",
    "mesenchymal": "Mesenchymal and EMT-axis activity are high without a dominant stromal warning.",
    "stromal_dominant": "EMT-like activity is high, but fibroblast/stromal signal may explain much of the score.",
    "immune_inflamed_emt": "EMT activity is high together with immune or TAM-context signal.",
    "hypoxic_emt": "EMT activity is high together with hypoxia or angiogenic pressure.",
    "uncertain": "Available scores do not support a confident EMT state assignment.",
}


def _percentile(series: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce")
    if numeric.notna().sum() == 0:
        return pd.Series(np.nan, index=series.index)
    return numeric.rank(pct=True, method="average")


def _state_vote(row: pd.Series) -> str:
    if bool(row.get("stromal_warning", False)) and bool(row.get("emt_axis_high", False)):
        return "stromal_dominant"
    if bool(row.get("emt_axis_high", False)) and bool(row.get("immune_context_high", False)):
        return "immune_inflamed_emt"
    if bool(row.get("emt_axis_high", False)) and bool(row.get("hypoxia_high", False)):
        return "hypoxic_emt"
    if bool(row.get("hybrid_program_high", False)):
        return "hybrid_e_m"
    if bool(row.get("mesenchymal_program_high", False)) and bool(row.get("emt_axis_high", False)):
        return "mesenchymal"
    if bool(row.get("epithelial_program_high", False)) and not bool(row.get("mesenchymal_program_mid", False)):
        return "epithelial"
    return "uncertain"


def _broad_state(state: str) -> str:
    if state in {"stromal_dominant", "immune_inflamed_emt", "hypoxic_emt", "mesenchymal"}:
        return "mesenchymal_like"
    if state == "hybrid_e_m":
        return "hybrid"
    if state == "epithelial":
        return "epithelial"
    return "uncertain"


def _confidence(row: pd.Series, thresholds: ConsensusThresholds) -> tuple[str, str]:
    reasons: list[str] = []
    present_fraction = float(row.get("required_score_fraction_present", 0.0))
    if present_fraction < 1.0:
        reasons.append("missing_required_scores")

    coverage = row.get("signature_gene_coverage", np.nan)
    if pd.notna(coverage) and float(coverage) < thresholds.minimum_signature_gene_coverage:
        reasons.append("low_gene_coverage")

    if bool(row.get("stromal_warning", False)):
        reasons.append("stromal_dominant_signal")

    if float(row.get("method_agreement", 0.0)) < 0.50:
        reasons.append("method_disagreement")

    if pd.notna(row.get("cancer_type_sample_count", np.nan)) and int(row["cancer_type_sample_count"]) < thresholds.minimum_cancer_type_samples_for_survival:
        reasons.append("small_cohort")

    if row.get("consensus_emt_state") == "uncertain":
        reasons.append("uncertain_state")

    if "missing_required_scores" in reasons or "uncertain_state" in reasons:
        return "low", ";".join(dict.fromkeys(reasons))
    if "stromal_dominant_signal" in reasons or "method_disagreement" in reasons or "low_gene_coverage" in reasons:
        return "medium", ";".join(dict.fromkeys(reasons))
    return "high", "score_consensus"


def add_consensus_states(
    frame: pd.DataFrame,
    thresholds: ConsensusThresholds | None = None,
    cancer_type_col: str = "cancer_type",
) -> pd.DataFrame:
    """Add interpretable EMT state labels and confidence fields.

    The classifier is intentionally transparent and percentile-based. It is a
    decision-support layer for reports/cards, not a clinical diagnostic model.
    """

    thresholds = thresholds or ConsensusThresholds()
    out = frame.copy()

    present_required = [col for col in REQUIRED_SCORE_COLUMNS if col in out.columns]
    out["required_score_fraction_present"] = len(present_required) / len(REQUIRED_SCORE_COLUMNS)

    for col in [
        "epithelial",
        "mesenchymal",
        "emt_score",
        "partial_emt_score",
        "stromal_contamination_risk",
        "immune_total",
        "immune_context",
        "caf_tam_niche",
        "hypoxia",
    ]:
        if col in out.columns:
            out[f"{col}_percentile"] = _percentile(out[col])

    immune_pct = None
    for col in ["immune_total_percentile", "immune_context_percentile", "caf_tam_niche_percentile"]:
        if col in out.columns:
            immune_pct = out[col] if immune_pct is None else pd.concat([immune_pct, out[col]], axis=1).max(axis=1)
    if immune_pct is not None:
        out["immune_context_percentile_consensus"] = immune_pct

    out["epithelial_program_high"] = out.get("epithelial_percentile", pd.Series(False, index=out.index)) >= thresholds.epithelial_high_quantile
    out["mesenchymal_program_high"] = out.get("mesenchymal_percentile", pd.Series(False, index=out.index)) >= thresholds.mesenchymal_high_quantile
    out["mesenchymal_program_mid"] = out.get("mesenchymal_percentile", pd.Series(False, index=out.index)) >= thresholds.hybrid_min_quantile
    out["epithelial_program_mid"] = out.get("epithelial_percentile", pd.Series(False, index=out.index)) >= thresholds.hybrid_min_quantile
    out["emt_axis_high"] = out.get("emt_score_percentile", pd.Series(False, index=out.index)) >= thresholds.mesenchymal_high_quantile
    out["partial_emt_program_high"] = out.get("partial_emt_score_percentile", pd.Series(False, index=out.index)) >= thresholds.hybrid_min_quantile
    out["hybrid_program_high"] = out["epithelial_program_mid"] & out["mesenchymal_program_mid"] & out["partial_emt_program_high"]
    out["stromal_warning"] = out.get("stromal_contamination_risk_percentile", pd.Series(False, index=out.index)) >= thresholds.stromal_warning_quantile
    if "stromal_high" in out.columns:
        out["stromal_warning"] = out["stromal_warning"] | out["stromal_high"].fillna(False).astype(bool)
    out["immune_context_high"] = out.get("immune_context_percentile_consensus", pd.Series(False, index=out.index)) >= thresholds.immune_inflamed_quantile
    out["hypoxia_high"] = out.get("hypoxia_percentile", pd.Series(False, index=out.index)) >= thresholds.hypoxia_high_quantile

    axis_vote = np.where(out["emt_axis_high"], "mesenchymal_like", np.where(out["epithelial_program_high"], "epithelial", "uncertain"))
    program_vote = np.where(
        out["hybrid_program_high"],
        "hybrid",
        np.where(out["mesenchymal_program_high"], "mesenchymal_like", np.where(out["epithelial_program_high"], "epithelial", "uncertain")),
    )
    context_vote = np.where(
        out["stromal_warning"] | out["immune_context_high"] | out["hypoxia_high"],
        "mesenchymal_like",
        "uncertain",
    )
    votes = pd.DataFrame({"axis": axis_vote, "program": program_vote, "context": context_vote}, index=out.index)

    out["consensus_emt_state"] = out.apply(_state_vote, axis=1)
    out["consensus_broad_state"] = out["consensus_emt_state"].map(_broad_state)
    out["method_agreement"] = [
        float((row[row != "uncertain"] == broad).sum()) / max(int((row != "uncertain").sum()), 1)
        if broad != "uncertain"
        else 0.0
        for (_, row), broad in zip(votes.iterrows(), out["consensus_broad_state"])
    ]

    if cancer_type_col in out.columns:
        counts = out.groupby(cancer_type_col, dropna=False)["sample_id"].transform("count") if "sample_id" in out.columns else out.groupby(cancer_type_col, dropna=False)[cancer_type_col].transform("count")
        out["cancer_type_sample_count"] = counts

    confidence = out.apply(lambda row: _confidence(row, thresholds), axis=1)
    out["confidence_label"] = [item[0] for item in confidence]
    out["confidence_reason"] = [item[1] for item in confidence]
    out["state_explanation"] = out["consensus_emt_state"].map(STATE_EXPLANATIONS)

    return out


def consensus_cancer_type_summary(frame: pd.DataFrame, cancer_type_col: str = "cancer_type") -> pd.DataFrame:
    if "consensus_emt_state" not in frame.columns:
        frame = add_consensus_states(frame, cancer_type_col=cancer_type_col)
    data = frame.copy()
    if cancer_type_col not in data.columns:
        data[cancer_type_col] = "unknown"
    data[cancer_type_col] = data[cancer_type_col].fillna("unknown").replace("", "unknown")

    rows = []
    for cancer_type, group in data.groupby(cancer_type_col, dropna=False):
        total = len(group)
        state_counts = group["consensus_emt_state"].value_counts()
        row = {
            cancer_type_col: cancer_type,
            "sample_count": total,
            "emt_score_mean": group["emt_score"].mean() if "emt_score" in group.columns else np.nan,
            "hybrid_fraction": float(state_counts.get("hybrid_e_m", 0) / total) if total else np.nan,
            "mesenchymal_like_fraction": float(group["consensus_broad_state"].eq("mesenchymal_like").mean()) if total else np.nan,
            "stromal_dominant_fraction": float(state_counts.get("stromal_dominant", 0) / total) if total else np.nan,
            "high_confidence_fraction": float(group["confidence_label"].eq("high").mean()) if "confidence_label" in group.columns and total else np.nan,
        }
        for state in sorted(data["consensus_emt_state"].dropna().unique()):
            row[f"{state}_count"] = int(state_counts.get(state, 0))
        rows.append(row)

    summary = pd.DataFrame(rows)
    if "mesenchymal_like_fraction" in summary.columns:
        summary = summary.sort_values(["mesenchymal_like_fraction", "hybrid_fraction"], ascending=False)
    return summary.reset_index(drop=True)
