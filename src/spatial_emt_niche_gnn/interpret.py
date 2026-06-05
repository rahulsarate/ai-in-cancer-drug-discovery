from __future__ import annotations

import numpy as np
import pandas as pd

from .graph import edge_type_summary
from .model import train_graph_logistic


def edge_ablation_report(scored: pd.DataFrame, edges: pd.DataFrame, label_col: str = "emt_niche_label") -> pd.DataFrame:
    rows = []
    _, full_metrics = train_graph_logistic(scored, edges, label_col=label_col)
    full_acc = full_metrics.get("test_accuracy") or 0.0
    rows.append({"ablation": "none", "test_accuracy": full_acc, "delta_from_full": 0.0})
    for edge_type in sorted(edges["edge_type"].dropna().unique()) if not edges.empty else []:
        reduced = edges[edges["edge_type"].ne(edge_type)]
        _, metrics = train_graph_logistic(scored, reduced, label_col=label_col)
        acc = metrics.get("test_accuracy") or 0.0
        rows.append({"ablation": f"remove:{edge_type}", "test_accuracy": acc, "delta_from_full": acc - full_acc})
    return pd.DataFrame(rows)


def feature_perturbation_report(
    scored: pd.DataFrame,
    predictions: pd.DataFrame,
    features: list[str],
) -> pd.DataFrame:
    """Rank features by simple correlation with predicted niche probability."""
    merged = scored.merge(predictions[["spot_id", "emt_niche_probability"]], on="spot_id", how="inner")
    rows = []
    for feature in features:
        if feature not in merged.columns:
            continue
        values = pd.to_numeric(merged[feature], errors="coerce").fillna(0.0)
        if values.std(ddof=0) == 0:
            corr = 0.0
        else:
            corr = float(np.corrcoef(values, merged["emt_niche_probability"])[0, 1])
        rows.append({"feature": feature, "association_with_prediction": corr, "abs_association": abs(corr)})
    return pd.DataFrame(rows).sort_values("abs_association", ascending=False)


def niche_driver_summary(scored: pd.DataFrame, edges: pd.DataFrame, predictions: pd.DataFrame) -> dict[str, pd.DataFrame]:
    features = [
        "emt_score",
        "partial_emt_score",
        "stromal_contamination_risk",
        "caf_tam_niche",
        "hypoxia",
        "immune_context",
        "ferroptosis_window",
    ]
    return {
        "edge_type_summary": edge_type_summary(edges),
        "edge_ablation": edge_ablation_report(scored, edges),
        "feature_perturbation": feature_perturbation_report(scored, predictions, features),
    }
