from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, balanced_accuracy_score, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from .interface import MALIGNANT_TYPES


BASE_FEATURE_GROUPS = {
    "malignant_state": ["partial_emt"],
    "myeloid": ["mrc1_ccl18_macrophage", "damaged_hepatocyte"],
    "fibroblast_ecm": ["activated_fibroblast", "ecm_remodeling"],
    "endothelial": ["endothelial"],
    "metabolism": ["glycolysis", "hypoxia"],
}


def _model(random_state: int = 47) -> Pipeline:
    return Pipeline(
        [
            ("scale", StandardScaler()),
            (
                "classifier",
                LogisticRegression(
                    C=0.5,
                    class_weight="balanced",
                    max_iter=5000,
                    random_state=random_state,
                ),
            ),
        ]
    )


def model_feature_groups(message_features: pd.DataFrame) -> dict[str, list[str]]:
    columns = set(message_features.columns)
    groups = {name: [feature for feature in features if feature in columns] for name, features in BASE_FEATURE_GROUPS.items()}
    groups["spatial_context"] = [column for column in message_features.columns if column.startswith("spatial_neighbor_")]
    groups["heterogeneous_contact"] = [column for column in message_features.columns if column.startswith("contact_neighbor_")]
    groups["ligand_receptor_context"] = [column for column in message_features.columns if column.startswith("lr_neighbor_")]
    groups["gradient_context"] = [
        column for column in message_features.columns
        if column.startswith("ecm_gradient_neighbor_") or column.startswith("glycolysis_gradient_neighbor_")
    ]
    return {name: features for name, features in groups.items() if features}


def _cross_section_predictions(x: np.ndarray, y: np.ndarray, groups: np.ndarray, random_state: int) -> np.ndarray:
    probabilities = np.full(len(y), np.nan, dtype=float)
    for held_out in np.unique(groups):
        train = groups != held_out
        test = groups == held_out
        if len(np.unique(y[train])) < 2:
            continue
        estimator = _model(random_state)
        estimator.fit(x[train], y[train])
        probabilities[test] = estimator.predict_proba(x[test])[:, 1]
    return probabilities


def fit_interface_model(
    scored: pd.DataFrame,
    message_features: pd.DataFrame,
    n_permutations: int = 100,
    random_state: int = 47,
) -> tuple[Pipeline, pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, object]]:
    data = scored.merge(message_features, on="spot_id", how="left", suffixes=("", "_message"))
    data = data[
        data["is_liver_metastasis"].astype(bool)
        & data["dominant_compartment"].isin(MALIGNANT_TYPES)
        & ~data["stromal_inflated_emt_risk"].astype(bool)
    ].copy()
    feature_groups = model_feature_groups(message_features)
    features = list(dict.fromkeys(feature for group in feature_groups.values() for feature in group))
    x = data[features].apply(pd.to_numeric, errors="coerce").fillna(0.0).to_numpy(dtype=float)
    y = data["is_tumour_front"].astype(int).to_numpy()
    groups = data["section_id"].astype(str).to_numpy()
    if len(np.unique(groups)) < 2 or len(np.unique(y)) < 2:
        raise ValueError("Interface modeling requires at least two liver sections and both front/core labels.")
    probabilities = _cross_section_predictions(x, y, groups, random_state)
    valid = np.isfinite(probabilities)
    observed_auc = float(roc_auc_score(y[valid], probabilities[valid]))
    observed_ap = float(average_precision_score(y[valid], probabilities[valid]))
    predicted = (probabilities >= 0.5).astype(int)

    rng = np.random.default_rng(random_state)
    null_aucs: list[float] = []
    for _ in range(n_permutations):
        permuted = y.copy()
        for section in np.unique(groups):
            indices = np.flatnonzero(groups == section)
            permuted[indices] = rng.permutation(permuted[indices])
        null_probabilities = _cross_section_predictions(x, permuted, groups, random_state)
        null_valid = np.isfinite(null_probabilities)
        if len(np.unique(permuted[null_valid])) == 2:
            null_aucs.append(float(roc_auc_score(permuted[null_valid], null_probabilities[null_valid])))

    final_model = _model(random_state)
    final_model.fit(x, y)
    coefficients = final_model.named_steps["classifier"].coef_[0]
    importance = pd.DataFrame(
        {
            "feature": features,
            "coefficient": coefficients,
            "absolute_coefficient": np.abs(coefficients),
            "direction": np.where(coefficients >= 0, "tumour_front_enriched", "tumour_core_enriched"),
        }
    ).sort_values("absolute_coefficient", ascending=False)
    predictions = data[
        ["spot_id", "section_id", "dominant_compartment", "interface_band", "x", "y"]
    ].copy()
    predictions["observed_label"] = y
    predictions["interface_probability"] = probabilities
    predictions["predicted_label"] = predicted

    ablation_rows: list[dict[str, object]] = []
    for removed_group, removed_features in {"none": [], **feature_groups}.items():
        retained = [feature for feature in features if feature not in removed_features]
        if not retained:
            continue
        retained_indices = [features.index(feature) for feature in retained]
        ablated_probabilities = _cross_section_predictions(x[:, retained_indices], y, groups, random_state)
        ablated_valid = np.isfinite(ablated_probabilities)
        auc = float(roc_auc_score(y[ablated_valid], ablated_probabilities[ablated_valid]))
        ablation_rows.append(
            {
                "removed_feature_group": removed_group,
                "features_retained": len(retained),
                "cross_section_roc_auc": auc,
                "auc_drop_vs_full": observed_auc - auc,
            }
        )
    ablations = pd.DataFrame(ablation_rows).sort_values("auc_drop_vs_full", ascending=False)
    metrics = {
        "model": "standardized_logistic_typed_message_passing_baseline",
        "validation": "leave_one_liver_section_out",
        "liver_sections": int(len(np.unique(groups))),
        "malignant_spots": int(len(data)),
        "tumour_front_spots": int(y.sum()),
        "features": len(features),
        "roc_auc": observed_auc,
        "average_precision": observed_ap,
        "balanced_accuracy": float(balanced_accuracy_score(y[valid], predicted[valid])),
        "permutation_p": float((1 + np.sum(np.asarray(null_aucs) >= observed_auc)) / (1 + len(null_aucs))),
        "permutations": len(null_aucs),
        "null_auc_mean": float(np.mean(null_aucs)) if null_aucs else None,
        "label_type": "marker_plus_spatial_weak_label",
        "intended_use": "research hypothesis generation only",
    }
    return final_model, predictions, importance, ablations, metrics


def compare_front_to_core(scored: pd.DataFrame) -> pd.DataFrame:
    programs = [
        "partial_emt", "mrc1_ccl18_macrophage", "activated_fibroblast", "endothelial",
        "ecm_remodeling", "glycolysis", "hypoxia", "damaged_hepatocyte",
    ]
    liver = scored[
        scored["is_liver_metastasis"].astype(bool)
        & scored["dominant_compartment"].isin(MALIGNANT_TYPES)
    ]
    rows: list[dict[str, object]] = []
    for program in programs:
        front = liver.loc[liver["is_tumour_front"], program].dropna().to_numpy(dtype=float)
        core = liver.loc[liver["interface_band"].eq("tumour_core"), program].dropna().to_numpy(dtype=float)
        if len(front) < 2 or len(core) < 2:
            continue
        statistic, p_value = mannwhitneyu(front, core, alternative="two-sided")
        rows.append(
            {
                "program": program,
                "front_spots": len(front),
                "core_spots": len(core),
                "mean_front": float(front.mean()),
                "mean_core": float(core.mean()),
                "front_minus_core": float(front.mean() - core.mean()),
                "rank_biserial_effect": float(2 * statistic / (len(front) * len(core)) - 1),
                "mannwhitney_p": float(p_value),
            }
        )
    result = pd.DataFrame(rows).sort_values("mannwhitney_p")
    if result.empty:
        return result
    ranks = np.arange(1, len(result) + 1)
    adjusted = np.minimum.accumulate((result["mannwhitney_p"].to_numpy() * len(result) / ranks)[::-1])[::-1]
    result["fdr_bh"] = np.clip(adjusted, 0, 1)
    return result


def save_model(model: Pipeline, metrics: dict[str, object], output_dir: str | Path) -> tuple[Path, Path]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    model_path = output / "crc_liver_interface_model.joblib"
    metrics_path = output / "model_metrics.json"
    joblib.dump(model, model_path)
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    return model_path, metrics_path
