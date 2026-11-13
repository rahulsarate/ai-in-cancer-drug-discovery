from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


def read_table(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path, sep="\t")


def write_same_platform_report(internal_metrics: pd.DataFrame, out_path: Path) -> None:
    same_platform = internal_metrics.copy()
    if not same_platform.empty:
        same_platform["validation_scope"] = same_platform["evaluation"].map(
            {
                "train_test": "same_platform_train_gse25055_test_gse25065",
                "stratified_cv": "internal_deduplicated_cv",
            }
        ).fillna("internal")
        cols = ["validation_scope", "feature_set", "samples", "positive_rate", "auroc", "auprc", "accuracy", "brier", "train_dataset", "test_dataset"]
        same_platform = same_platform[[col for col in cols if col in same_platform.columns]]
    lines = [
        "# Same-Platform TNBC NAC Response Model Report",
        "",
        "## Scope",
        "",
        "This report separates internal same-platform response modeling from cross-platform external validation. The strongest same-platform comparison remains training on `GSE25055` and testing on `GSE25065`.",
        "",
        "## Metrics",
        "",
        same_platform.to_markdown(index=False) if not same_platform.empty else "No same-platform metrics available.",
        "",
        "## Interpretation",
        "",
        "- These metrics estimate internal retrospective performance across GEO cohorts already used in model development.",
        "- Same-platform results should not be mixed with RNA-seq external validation metrics.",
        "- Positive label is `residual_or_poor_response`.",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")


def write_cross_platform_report(external_metrics: pd.DataFrame, platform_shift: pd.DataFrame, out_path: Path) -> None:
    metrics = external_metrics.copy()
    if not metrics.empty:
        cols = ["test_dataset", "calibration_method", "feature_set", "samples", "positive_rate", "auroc", "auprc", "accuracy", "brier"]
        metrics = metrics[[col for col in cols if col in metrics.columns]]
    shift = platform_shift.copy()
    if not shift.empty:
        cols = ["feature", "standardized_mean_shift", "ks_statistic", "ks_pvalue"]
        shift = shift[[col for col in cols if col in shift.columns]].head(12)
    lines = [
        "# Cross-Platform External TNBC NAC Validation Report",
        "",
        "## Scope",
        "",
        "This report is restricted to held-out external validation where the training data and test data come from different cohorts/platform contexts. Current external cohort: `GSE163882_TNBC_TPM` RNA-seq TPM data.",
        "",
        "## Raw Versus Percentile-Calibrated Metrics",
        "",
        metrics.to_markdown(index=False) if not metrics.empty else "No external metrics available.",
        "",
        "## Largest Platform/Feature Shifts",
        "",
        shift.to_markdown(index=False) if not shift.empty else "No platform-shift diagnostics available.",
        "",
        "## Interpretation",
        "",
        "- `raw` validation uses feature values directly.",
        "- `internal_percentile` maps features to empirical percentiles relative to the internal training distribution.",
        "- Performance that changes substantially after percentile calibration is likely sensitive to platform/cohort distribution shift.",
        "- These are external research-validation metrics, not clinical decision-support performance claims.",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Build separated same-platform and cross-platform TNBC response-model reports.")
    p.add_argument("--processed-dir", default="data/processed/tnbc_digital_twin")
    return p


def main() -> None:
    args = parser().parse_args()
    processed = ROOT / args.processed_dir
    internal_metrics = read_table(processed / "tnbc_nac_response_model_metrics.tsv")
    external_metrics = read_table(processed / "external_validation" / "gse163882" / "external_validation_metrics.tsv")
    platform_shift = read_table(processed / "platform_normalization" / "tnbc_platform_feature_shift_diagnostics.tsv")
    write_same_platform_report(internal_metrics, processed / "tnbc_same_platform_response_model_report.md")
    write_cross_platform_report(external_metrics, platform_shift, processed / "tnbc_cross_platform_external_validation_report.md")
    print(f"wrote {processed / 'tnbc_same_platform_response_model_report.md'}")
    print(f"wrote {processed / 'tnbc_cross_platform_external_validation_report.md'}")


if __name__ == "__main__":
    main()
