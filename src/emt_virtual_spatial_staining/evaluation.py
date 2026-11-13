from __future__ import annotations

import math

import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr
from sklearn.metrics import average_precision_score, mean_absolute_error, r2_score


def _correlation(function, truth: np.ndarray, predicted: np.ndarray) -> float:
    if len(truth) < 3 or np.std(truth) <= 1e-12 or np.std(predicted) <= 1e-12:
        return float("nan")
    return float(function(truth, predicted).statistic)


def evaluate_predictions(
    truth: pd.DataFrame,
    predictions: pd.DataFrame,
    targets: list[str],
) -> pd.DataFrame:
    merged = truth.merge(predictions, on="spot_uid", how="inner", suffixes=("", "_prediction"))
    rows = []
    for split, split_frame in merged.groupby("split_prediction" if "split_prediction" in merged.columns else "split"):
        for target in targets:
            observed = pd.to_numeric(split_frame[target], errors="coerce")
            estimated = pd.to_numeric(split_frame[f"pred_{target}"], errors="coerce")
            valid = observed.notna() & estimated.notna()
            y = observed[valid].to_numpy(dtype=float)
            yhat = estimated[valid].to_numpy(dtype=float)
            if len(y) == 0:
                continue
            rows.append(
                {
                    "split": split,
                    "target": target,
                    "n": len(y),
                    "pearson": _correlation(pearsonr, y, yhat),
                    "spearman": _correlation(spearmanr, y, yhat),
                    "mae": float(mean_absolute_error(y, yhat)),
                    "r2": float(r2_score(y, yhat)) if len(y) >= 2 else float("nan"),
                    "prediction_mean": float(np.mean(yhat)),
                    "truth_mean": float(np.mean(y)),
                }
            )
    return pd.DataFrame(rows)


def selective_risk_summary(
    truth: pd.DataFrame,
    predictions: pd.DataFrame,
    target: str = "partial_emt_score",
) -> pd.DataFrame:
    merged = truth.merge(predictions, on="spot_uid", how="inner")
    error = np.abs(merged[target].to_numpy(dtype=float) - merged[f"pred_{target}"].to_numpy(dtype=float))
    uncertainty = merged[f"uncertainty_{target}"].to_numpy(dtype=float)
    rows = []
    for retained_fraction in [1.0, 0.9, 0.8, 0.6, 0.4]:
        keep = max(1, int(math.ceil(len(merged) * retained_fraction)))
        selected = np.argsort(uncertainty)[:keep]
        rows.append(
            {
                "target": target,
                "retained_fraction": retained_fraction,
                "n": keep,
                "mae": float(error[selected].mean()),
                "mean_uncertainty": float(uncertainty[selected].mean()),
            }
        )
    return pd.DataFrame(rows)


def partial_emt_safety_metrics(
    truth: pd.DataFrame,
    predictions: pd.DataFrame,
) -> pd.DataFrame:
    merged = truth.merge(predictions, on="spot_uid", how="inner", suffixes=("", "_prediction"))
    split_column = "split_prediction" if "split_prediction" in merged.columns else "split"
    test = merged.loc[merged[split_column].astype(str).eq("test")].copy()
    if test.empty:
        return pd.DataFrame()
    measured = pd.to_numeric(test["partial_emt_score"], errors="coerce")
    measured_high = measured >= measured.quantile(0.75)
    predicted = pd.to_numeric(test["pred_partial_emt_gated_probability"], errors="coerce").clip(0, 1)
    malignant = test.get("tumor_cell_emt_candidate", pd.Series(True, index=test.index)).fillna(False).astype(bool)
    stroma = pd.to_numeric(test["stromal_contamination_risk"], errors="coerce") >= 0.75
    malignant_valid = malignant & measured.notna() & predicted.notna()
    auprc = float("nan")
    prevalence = float("nan")
    if malignant_valid.sum() >= 5 and measured_high[malignant_valid].nunique() > 1:
        auprc = float(average_precision_score(measured_high[malignant_valid], predicted[malignant_valid]))
        prevalence = float(measured_high[malignant_valid].mean())
    stroma_valid = stroma & predicted.notna()
    stroma_fpr = float((predicted[stroma_valid] >= 0.5).mean()) if stroma_valid.any() else float("nan")

    bins = pd.cut(predicted, bins=np.linspace(0, 1, 11), include_lowest=True, duplicates="drop")
    calibration = pd.DataFrame({"predicted": predicted, "observed": measured_high.astype(float), "bin": bins}).dropna()
    ece = 0.0
    for _, group in calibration.groupby("bin", observed=True):
        ece += len(group) / max(len(calibration), 1) * abs(group["predicted"].mean() - group["observed"].mean())
    return pd.DataFrame(
        [
            {
                "split": "test",
                "malignant_partial_emt_auprc": auprc,
                "malignant_partial_emt_prevalence": prevalence,
                "auprc_above_prevalence": auprc - prevalence if np.isfinite(auprc) and np.isfinite(prevalence) else float("nan"),
                "pure_stroma_false_positive_rate": stroma_fpr,
                "partial_emt_expected_calibration_error": float(ece),
                "test_spots": len(test),
                "malignant_test_spots": int(malignant_valid.sum()),
                "stroma_test_spots": int(stroma_valid.sum()),
            }
        ]
    )


def go_no_go(
    metrics: pd.DataFrame,
    safety: pd.DataFrame | None = None,
    selective: pd.DataFrame | None = None,
) -> pd.DataFrame:
    test = metrics.loc[metrics["split"].astype(str).eq("test")]
    median_spearman = float(test["spearman"].median()) if len(test) else float("nan")
    programs_over_035 = int((test["spearman"] >= 0.35).sum()) if len(test) else 0
    rows = [
        {
            "criterion": "test_metrics_present",
            "threshold": ">= 1 test target",
            "observed": len(test),
            "passed": bool(len(test)),
        },
        {
            "criterion": "median_test_spearman",
            "threshold": ">= 0.35",
            "observed": median_spearman,
            "passed": bool(np.isfinite(median_spearman) and median_spearman >= 0.35),
        },
        {
            "criterion": "programs_with_spearman_0_35",
            "threshold": ">= 4",
            "observed": programs_over_035,
            "passed": programs_over_035 >= 4,
        },
    ]
    if safety is not None and not safety.empty:
        row = safety.iloc[0]
        rows.extend(
            [
                {
                    "criterion": "partial_emt_auprc_above_prevalence",
                    "threshold": ">= 0.15",
                    "observed": row["auprc_above_prevalence"],
                    "passed": bool(pd.notna(row["auprc_above_prevalence"]) and row["auprc_above_prevalence"] >= 0.15),
                },
                {
                    "criterion": "pure_stroma_false_positive_rate",
                    "threshold": "< 0.15",
                    "observed": row["pure_stroma_false_positive_rate"],
                    "passed": bool(pd.notna(row["pure_stroma_false_positive_rate"]) and row["pure_stroma_false_positive_rate"] < 0.15),
                },
                {
                    "criterion": "partial_emt_calibration_error",
                    "threshold": "< 0.10",
                    "observed": row["partial_emt_expected_calibration_error"],
                    "passed": bool(pd.notna(row["partial_emt_expected_calibration_error"]) and row["partial_emt_expected_calibration_error"] < 0.10),
                },
            ]
        )
    if selective is not None and not selective.empty:
        full = selective.loc[selective["retained_fraction"].eq(1.0), "mae"]
        retained = selective.loc[selective["retained_fraction"].eq(0.8), "mae"]
        improvement = float((full.iloc[0] - retained.iloc[0]) / full.iloc[0]) if len(full) and len(retained) and full.iloc[0] else float("nan")
        rows.append(
            {
                "criterion": "uncertainty_abstention_error_improvement",
                "threshold": ">= 0.15",
                "observed": improvement,
                "passed": bool(np.isfinite(improvement) and improvement >= 0.15),
            }
        )
    return pd.DataFrame(rows)
