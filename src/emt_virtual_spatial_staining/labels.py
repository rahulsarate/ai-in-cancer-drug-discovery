from __future__ import annotations

import numpy as np
import pandas as pd


PRIMARY_TARGETS = [
    "epithelial",
    "mesenchymal",
    "partial_emt_score",
    "caf",
    "tam_spp1",
    "hypoxia",
    "ecm_remodeling",
    "stromal_contamination_risk",
]


def _percentile(series: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce")
    return numeric.rank(method="average", pct=True).fillna(0.5)


def add_virtual_stain_labels(frame: pd.DataFrame) -> pd.DataFrame:
    """Add risk-aware supervision without converting weak proxies to truth."""
    out = frame.copy()
    missing = [column for column in PRIMARY_TARGETS if column not in out.columns]
    if missing:
        raise ValueError(f"Missing virtual-stain targets: {', '.join(missing)}")

    epithelial_pct = _percentile(out["epithelial"])
    mesenchymal_pct = _percentile(out["mesenchymal"])
    stromal_pct = _percentile(out["stromal_contamination_risk"])
    partial_pct = _percentile(out["partial_emt_score"])

    malignant_evidence = epithelial_pct * (1.0 - stromal_pct)
    dual_program = np.minimum(epithelial_pct, mesenchymal_pct)
    out["tumor_content_proxy"] = malignant_evidence.clip(0.0, 1.0)
    out["partial_emt_gated_target"] = (dual_program * partial_pct * malignant_evidence).clip(0.0, 1.0)
    out["stromal_inflated_partial_emt"] = (
        (partial_pct >= 0.75) & (stromal_pct >= 0.75)
    )

    strength = out.get("label_strength", pd.Series("weak_proxy", index=out.index)).astype(str)
    confidence = strength.map(
        {
            "pathologist_confirmed": 1.0,
            "strong_proxy": 0.80,
            "weak_proxy": 0.55,
            "contamination_risk": 0.35,
        }
    ).fillna(0.45)
    if "low_library_risk" in out.columns:
        confidence *= np.where(out["low_library_risk"].fillna(False), 0.65, 1.0)
    if "low_complexity_risk" in out.columns:
        confidence *= np.where(out["low_complexity_risk"].fillna(False), 0.65, 1.0)
    out["label_confidence"] = confidence.clip(0.05, 1.0)
    out["label_tier"] = pd.cut(
        out["label_confidence"],
        bins=[-np.inf, 0.40, 0.60, 0.85, np.inf],
        labels=["D", "C", "B", "A"],
    ).astype(str)
    out["supervised_eligible"] = out["label_tier"].ne("D")
    return out


def derive_prediction_gates(
    predictions: pd.DataFrame,
    reference_stats: dict[str, dict[str, float]],
) -> pd.DataFrame:
    out = predictions.copy()

    def logistic_percentile(column: str) -> np.ndarray:
        stats = reference_stats[column]
        scale = max(float(stats["std"]), 1e-6)
        z = (pd.to_numeric(out[f"pred_{column}"], errors="coerce").fillna(stats["mean"]) - stats["mean"]) / scale
        return 1.0 / (1.0 + np.exp(-np.clip(z.to_numpy(), -20, 20)))

    epithelial = logistic_percentile("epithelial")
    mesenchymal = logistic_percentile("mesenchymal")
    stroma = logistic_percentile("stromal_contamination_risk")
    out["pred_tumor_content_proxy"] = epithelial * (1.0 - stroma)
    out["pred_partial_emt_gated_probability"] = np.minimum(epithelial, mesenchymal) * (1.0 - stroma)
    out["pred_stromal_inflated_emt_risk"] = mesenchymal * stroma
    return out
