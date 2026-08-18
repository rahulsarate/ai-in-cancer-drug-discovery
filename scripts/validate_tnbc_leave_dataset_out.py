from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from train_tnbc_nac_response_model import FEATURE_SETS, available_features, deduplicate_samples, make_pipeline, metrics  # noqa: E402
from validate_tnbc_external_response_dataset import build_feature_matrices  # noqa: E402


FEATURE_GROUPS = {
    "emt_core": FEATURE_SETS["emt_core"],
    "emt_tme_resistance": FEATURE_SETS["emt_core"] + FEATURE_SETS["tme_resistance"],
    "digital_twin": FEATURE_SETS["digital_twin"],
    "combined": FEATURE_SETS["emt_core"] + FEATURE_SETS["tme_resistance"] + FEATURE_SETS["digital_twin"],
}


def evaluate_lodo(df: pd.DataFrame, holdout_datasets: list[str], calibration_methods: list[str]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    metric_rows = []
    prediction_frames = []
    availability_rows = []
    df = deduplicate_samples(df[df["standard_response"].isin(["pcr_or_good_response", "residual_or_poor_response"])].copy())

    for holdout in holdout_datasets:
        test = df[df["dataset_id"] == holdout].copy()
        train = df[df["dataset_id"] != holdout].copy()
        if test.empty or train.empty:
            continue
        y_train = (train["standard_response"] == "residual_or_poor_response").astype(int)
        y_test = (test["standard_response"] == "residual_or_poor_response").astype(int)
        if y_train.nunique() < 2 or y_test.nunique() < 2:
            continue
        for group, requested in FEATURE_GROUPS.items():
            train_features = available_features(train, requested)
            features = [
                feature
                for feature in train_features
                if feature in test.columns and pd.to_numeric(test[feature], errors="coerce").notna().any()
            ]
            availability_rows.append(
                {
                    "holdout_dataset": holdout,
                    "feature_set": group,
                    "requested_features": len(requested),
                    "available_train_features": len(train_features),
                    "available_holdout_features": len(features),
                    "features": ",".join(features),
                }
            )
            if len(features) < 2:
                continue
            for calibration in calibration_methods:
                x_train, x_test = build_feature_matrices(train, test, features, calibration)
                model = make_pipeline()
                model.fit(x_train, y_train)
                scores = model.predict_proba(x_test)[:, 1]
                preds = (scores >= 0.5).astype(int)
                row = metrics(y_test, scores, preds)
                row.update(
                    {
                        "evaluation": "leave_dataset_out",
                        "calibration_method": calibration,
                        "feature_set": group,
                        "feature_count": len(features),
                        "train_dataset": "all_except_" + holdout,
                        "test_dataset": holdout,
                    }
                )
                metric_rows.append(row)
                pred = test[["dataset_id", "sample_id", "standard_response"]].copy()
                pred["feature_set"] = group
                pred["calibration_method"] = calibration
                pred["residual_or_poor_response_probability"] = scores
                pred["predicted_response"] = np.where(preds == 1, "residual_or_poor_response", "pcr_or_good_response")
                prediction_frames.append(pred)
    return (
        pd.DataFrame(metric_rows),
        pd.concat(prediction_frames, ignore_index=True) if prediction_frames else pd.DataFrame(),
        pd.DataFrame(availability_rows),
    )


def write_report(metrics_df: pd.DataFrame, predictions: pd.DataFrame, availability: pd.DataFrame, out_path: Path) -> None:
    lines = [
        "# Leave-Dataset-Out TNBC NAC Validation",
        "",
        "## Purpose",
        "",
        "This analysis adds independent same-project validation checks by holding out each small TNBC NAC response cohort from model fitting, then testing on that held-out cohort. It is not a substitute for a large external prospective cohort, but it prevents label reuse for the held-out test set.",
        "",
        "## Feature Availability",
        "",
        availability.to_markdown(index=False) if not availability.empty else "No feature availability rows generated.",
        "",
        "## Metrics",
        "",
        metrics_df.to_markdown(index=False) if not metrics_df.empty else "No metrics generated.",
        "",
        "## Prediction Preview",
        "",
        predictions.head(30).to_markdown(index=False) if not predictions.empty else "No predictions generated.",
        "",
        "## Interpretation",
        "",
        "- Positive label is `residual_or_poor_response`.",
        "- `GSE18864` and `GSE45898` are small TNBC NAC cohorts, so uncertainty is high.",
        "- Use this as a sensitivity/robustness layer alongside the larger `GSE163882` RNA-seq external validation.",
        "- Do not use these results for individual patient decision-making.",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Run leave-dataset-out validation for TNBC NAC response cohorts.")
    p.add_argument("--model-table", default="data/processed/tnbc_digital_twin/response_label_curation/tnbc_curated_response_model_table.tsv")
    p.add_argument("--holdout-datasets", nargs="+", default=["GSE18864", "GSE45898"])
    p.add_argument("--out-dir", default="data/processed/tnbc_digital_twin/leave_dataset_out_validation")
    p.add_argument("--calibration", choices=["raw", "internal_percentile", "external_zscore_to_internal", "external_quantile_to_internal", "all"], default="all")
    return p


def main() -> None:
    args = parser().parse_args()
    out_dir = ROOT / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(ROOT / args.model_table, sep="\t")
    if args.calibration == "all":
        calibration_methods = ["raw", "internal_percentile", "external_zscore_to_internal", "external_quantile_to_internal"]
    else:
        calibration_methods = [args.calibration]
    metrics_df, predictions, availability = evaluate_lodo(df, args.holdout_datasets, calibration_methods)
    metrics_df.to_csv(out_dir / "tnbc_leave_dataset_out_metrics.tsv", sep="\t", index=False)
    predictions.to_csv(out_dir / "tnbc_leave_dataset_out_predictions.tsv", sep="\t", index=False)
    availability.to_csv(out_dir / "tnbc_leave_dataset_out_feature_availability.tsv", sep="\t", index=False)
    write_report(metrics_df, predictions, availability, out_dir / "tnbc_leave_dataset_out_validation_report.md")
    print(metrics_df.to_string(index=False) if not metrics_df.empty else "No leave-dataset-out metrics generated.")


if __name__ == "__main__":
    main()
