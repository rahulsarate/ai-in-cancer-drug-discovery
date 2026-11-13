from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
SCRIPTS = ROOT / "scripts"
for path in [SRC, SCRIPTS]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from emt_state_atlas.scoring import score_expression  # noqa: E402
from score_tnbc_nac_digital_twin_features import add_digital_twin_features, load_tnbc_signatures  # noqa: E402
from train_tnbc_nac_response_model import FEATURE_SETS, available_features, deduplicate_samples, make_pipeline, metrics  # noqa: E402


RESPONSE_VALUES = ["pcr_or_good_response", "residual_or_poor_response"]
EXTERNAL_FEATURE_SETS = {
    "emt_core": FEATURE_SETS["emt_core"],
    "emt_tme_resistance": FEATURE_SETS["emt_core"] + FEATURE_SETS["tme_resistance"],
    "digital_twin": FEATURE_SETS["digital_twin"],
    "combined": FEATURE_SETS["emt_core"] + FEATURE_SETS["tme_resistance"] + FEATURE_SETS["digital_twin"],
}


def empirical_percentile(reference: pd.Series, values: pd.Series) -> pd.Series:
    ref = pd.to_numeric(reference, errors="coerce").dropna().to_numpy(dtype=float)
    vals = pd.to_numeric(values, errors="coerce").to_numpy(dtype=float)
    if ref.size == 0:
        return pd.Series(np.nan, index=values.index)
    ref = np.sort(ref)
    pct = np.searchsorted(ref, vals, side="right") / ref.size
    pct[np.isnan(vals)] = np.nan
    return pd.Series(pct, index=values.index)


def build_feature_matrices(
    internal: pd.DataFrame,
    external: pd.DataFrame,
    features: list[str],
    calibration_method: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    x_train = internal[features].apply(pd.to_numeric, errors="coerce")
    x_external = external[features].apply(pd.to_numeric, errors="coerce")
    if calibration_method == "raw":
        return x_train, x_external
    if calibration_method == "internal_percentile":
        train_cal = pd.DataFrame(index=x_train.index)
        external_cal = pd.DataFrame(index=x_external.index)
        for feature in features:
            train_cal[feature] = empirical_percentile(x_train[feature], x_train[feature])
            external_cal[feature] = empirical_percentile(x_train[feature], x_external[feature])
        return train_cal, external_cal
    if calibration_method == "external_zscore_to_internal":
        external_cal = pd.DataFrame(index=x_external.index)
        for feature in features:
            internal_values = x_train[feature]
            external_values = x_external[feature]
            internal_mean = internal_values.mean()
            internal_std = internal_values.std(ddof=0)
            external_mean = external_values.mean()
            external_std = external_values.std(ddof=0)
            if pd.isna(external_std) or external_std == 0 or pd.isna(internal_std):
                external_cal[feature] = external_values
            else:
                external_cal[feature] = ((external_values - external_mean) / external_std) * internal_std + internal_mean
        return x_train, external_cal
    if calibration_method == "external_quantile_to_internal":
        external_cal = pd.DataFrame(index=x_external.index)
        for feature in features:
            ref = pd.to_numeric(x_train[feature], errors="coerce").dropna().sort_values().to_numpy(dtype=float)
            vals = pd.to_numeric(x_external[feature], errors="coerce")
            if ref.size == 0:
                external_cal[feature] = vals
                continue
            ranks = vals.rank(pct=True, method="average")
            external_cal[feature] = ranks.apply(lambda q: np.nan if pd.isna(q) else float(np.quantile(ref, min(max(q, 0.0), 1.0))))
        return x_train, external_cal
    raise ValueError(f"Unsupported calibration method: {calibration_method}")


def write_templates(out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    scored_template = pd.DataFrame(
        [
            {
                "dataset_id": "EXTERNAL_TNBC_NAC_001",
                "sample_id": "sample_001",
                "standard_response": "residual_or_poor_response",
                "tnbc_confirmed_or_likely": True,
                "epithelial": 0.0,
                "mesenchymal": 0.0,
                "emt_score": 0.0,
                "partial_emt_score": 0.0,
                "tnbc_axl_tam": 0.0,
                "tnbc_tgfb": 0.0,
                "tnbc_yap_taz": 0.0,
                "tnbc_hypoxia": 0.0,
                "tnbc_stemness_persister": 0.0,
                "tnbc_persister_tumor_refined": 0.0,
                "tnbc_persister_stress_tolerance": 0.0,
                "tnbc_persister_niche": 0.0,
                "epithelial_fraction_estimate": 0.25,
                "hybrid_fraction_estimate": 0.25,
                "mesenchymal_fraction_estimate": 0.25,
                "persister_fraction_estimate": 0.25,
                "plasticity_index": 0.5,
                "resistant_fraction_estimate": 0.75,
                "therapy_selection_pressure": 0.5,
                "residual_disease_probability_proxy": 0.5,
            }
        ]
    )
    expression_template = pd.DataFrame(
        [
            {
                "sample_id": "sample_001",
                "CDH1": 7.2,
                "EPCAM": 6.8,
                "VIM": 5.1,
                "FN1": 4.6,
                "AXL": 3.2,
                "GAS6": 2.1,
                "HIF1A": 4.0,
                "YAP1": 3.9,
                "FTH1": 6.4,
                "FTL": 6.1,
            }
        ]
    )
    metadata_template = pd.DataFrame(
        [
            {
                "dataset_id": "EXTERNAL_TNBC_NAC_001",
                "sample_id": "sample_001",
                "standard_response": "residual_or_poor_response",
                "tnbc_confirmed_or_likely": True,
                "standard_timepoint": "T0",
                "notes": "Use pcr_or_good_response or residual_or_poor_response.",
            }
        ]
    )
    scored_template.to_csv(out_dir / "external_scored_feature_template.tsv", sep="\t", index=False)
    expression_template.to_csv(out_dir / "external_expression_template.tsv", sep="\t", index=False)
    metadata_template.to_csv(out_dir / "external_metadata_template.tsv", sep="\t", index=False)
    lines = [
        "# External TNBC NAC Validation Input Templates",
        "",
        "This folder contains templates for independent TNBC neoadjuvant chemotherapy validation cohorts.",
        "",
        "## Option A: Already-Scored Feature Table",
        "",
        "Use `external_scored_feature_template.tsv` when an external cohort already has EMT/digital-twin scores.",
        "",
        "Required columns:",
        "",
        "- `sample_id`",
        "- `standard_response`: `pcr_or_good_response` or `residual_or_poor_response`",
        "- Feature columns matching at least one feature set in the internal response model.",
        "",
        "## Option B: Expression Plus Metadata",
        "",
        "Use `external_expression_template.tsv` plus `external_metadata_template.tsv` when the cohort is a sample-by-gene matrix.",
        "",
        "Expression requirements:",
        "",
        "- Rows are samples.",
        "- `sample_id` is required.",
        "- Gene-symbol columns should be uppercase HGNC symbols where possible.",
        "",
        "Metadata requirements:",
        "",
        "- `sample_id`",
        "- `standard_response`",
        "- Optional: `dataset_id`, `tnbc_confirmed_or_likely`, `standard_timepoint`.",
    ]
    (out_dir / "external_validation_input_templates.md").write_text("\n".join(lines), encoding="utf-8")


def load_internal_training(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, sep="\t")
    df = df[df["standard_response"].isin(RESPONSE_VALUES)].copy()
    return deduplicate_samples(df)


def score_external_expression(expression_path: Path, metadata_path: Path, config_path: Path) -> pd.DataFrame:
    expr = pd.read_csv(expression_path, sep="\t")
    if "sample_id" not in expr.columns:
        raise SystemExit("External expression table must include `sample_id`.")
    metadata = pd.read_csv(metadata_path, sep="\t", dtype=str)
    if "sample_id" not in metadata.columns or "standard_response" not in metadata.columns:
        raise SystemExit("External metadata table must include `sample_id` and `standard_response`.")
    expr = expr.set_index("sample_id")
    expr.columns = [str(col).upper() for col in expr.columns]
    scored = score_expression(expr.apply(pd.to_numeric, errors="coerce"), signatures=load_tnbc_signatures(config_path))
    scored = add_digital_twin_features(scored)
    return scored.merge(metadata, on="sample_id", how="left")


def load_external(args: argparse.Namespace) -> pd.DataFrame:
    if args.external_scored_table:
        external = pd.read_csv(ROOT / args.external_scored_table, sep="\t")
    elif args.external_expression and args.external_metadata:
        external = score_external_expression(ROOT / args.external_expression, ROOT / args.external_metadata, ROOT / args.config)
    else:
        return pd.DataFrame()
    if "dataset_id" not in external.columns:
        external.insert(0, "dataset_id", args.external_dataset_id)
    external = external[external["standard_response"].isin(RESPONSE_VALUES)].copy()
    return external


def evaluate_external(internal: pd.DataFrame, external: pd.DataFrame, calibration_methods: list[str]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    metric_rows = []
    prediction_frames = []
    feature_rows = []
    y_train = (internal["standard_response"] == "residual_or_poor_response").astype(int)
    y_external = (external["standard_response"] == "residual_or_poor_response").astype(int)
    for name, feature_names in EXTERNAL_FEATURE_SETS.items():
        internal_features = available_features(internal, feature_names)
        features = [feature for feature in internal_features if feature in external.columns and pd.to_numeric(external[feature], errors="coerce").notna().any()]
        feature_rows.append(
            {
                "feature_set": name,
                "requested_features": len(feature_names),
                "available_internal_features": len(internal_features),
                "available_external_features": len(features),
                "features": ",".join(features),
            }
        )
        if len(features) < 2:
            continue
        for calibration_method in calibration_methods:
            model = make_pipeline()
            x_train, x_external = build_feature_matrices(internal, external, features, calibration_method)
            model.fit(x_train, y_train)
            scores = model.predict_proba(x_external)[:, 1]
            preds = (scores >= 0.5).astype(int)
            row = metrics(y_external, scores, preds)
            row.update(
                {
                    "evaluation": "external_validation",
                    "calibration_method": calibration_method,
                    "feature_set": name,
                    "feature_count": len(features),
                    "train_dataset": "internal_geo_deduplicated",
                    "test_dataset": ",".join(sorted(external["dataset_id"].astype(str).unique())),
                }
            )
            metric_rows.append(row)
            pred = external[["dataset_id", "sample_id", "standard_response"]].copy()
            pred["feature_set"] = name
            pred["calibration_method"] = calibration_method
            pred["residual_or_poor_response_probability"] = scores
            pred["predicted_response"] = np.where(preds == 1, "residual_or_poor_response", "pcr_or_good_response")
            prediction_frames.append(pred)
    return (
        pd.DataFrame(metric_rows),
        pd.concat(prediction_frames, ignore_index=True) if prediction_frames else pd.DataFrame(),
        pd.DataFrame(feature_rows),
    )


def write_report(metrics_df: pd.DataFrame, predictions: pd.DataFrame, feature_availability: pd.DataFrame, out_path: Path) -> None:
    lines = [
        "# External TNBC NAC Response Validation Report",
        "",
        "## Feature Availability",
        "",
        feature_availability.to_markdown(index=False) if not feature_availability.empty else "No external dataset supplied. Templates were generated only.",
        "",
        "## External Metrics",
        "",
        metrics_df.to_markdown(index=False) if not metrics_df.empty else "No metrics generated.",
        "",
        "## Prediction Preview",
        "",
        predictions.head(20).to_markdown(index=False) if not predictions.empty else "No predictions generated.",
        "",
        "## Interpretation Rules",
        "",
        "- External validation must use locked response labels and a held-out dataset not used in model fitting.",
        "- Positive label is `residual_or_poor_response`.",
        "- `raw` uses feature values directly; `internal_percentile` maps train and external features to empirical percentiles relative to the internal training distribution.",
        "- If the external cohort has only one response class, AUROC/AUPRC are not interpretable.",
        "- Results are research validation metrics, not clinical decision support.",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Evaluate internal TNBC NAC response models on an independent external cohort.")
    p.add_argument("--internal-model-table", default="data/processed/tnbc_digital_twin/tnbc_nac_emt_digital_twin_tnbc_response_model_table.tsv")
    p.add_argument("--external-scored-table")
    p.add_argument("--external-expression")
    p.add_argument("--external-metadata")
    p.add_argument("--external-dataset-id", default="EXTERNAL_TNBC_NAC")
    p.add_argument("--config", default="configs/tnbc_digital_twin.yml")
    p.add_argument("--out-dir", default="data/processed/tnbc_digital_twin/external_validation")
    p.add_argument("--calibration", choices=["raw", "internal_percentile", "external_zscore_to_internal", "external_quantile_to_internal", "all", "both"], default="all")
    return p


def main() -> None:
    args = parser().parse_args()
    out_dir = ROOT / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    write_templates(out_dir)

    external = load_external(args)
    if external.empty:
        empty = pd.DataFrame()
        empty.to_csv(out_dir / "external_validation_metrics.tsv", sep="\t", index=False)
        empty.to_csv(out_dir / "external_validation_predictions.tsv", sep="\t", index=False)
        empty.to_csv(out_dir / "external_validation_feature_availability.tsv", sep="\t", index=False)
        write_report(empty, empty, empty, out_dir / "external_validation_report.md")
        print(f"templates_written={out_dir}")
        return

    internal = load_internal_training(ROOT / args.internal_model_table)
    if args.calibration == "both":
        calibration_methods = ["raw", "internal_percentile"]
    elif args.calibration == "all":
        calibration_methods = ["raw", "internal_percentile", "external_zscore_to_internal", "external_quantile_to_internal"]
    else:
        calibration_methods = [args.calibration]
    metrics_df, predictions, feature_availability = evaluate_external(internal, external, calibration_methods)
    external.to_csv(out_dir / "external_validation_scored_input.tsv", sep="\t", index=False)
    metrics_df.to_csv(out_dir / "external_validation_metrics.tsv", sep="\t", index=False)
    predictions.to_csv(out_dir / "external_validation_predictions.tsv", sep="\t", index=False)
    feature_availability.to_csv(out_dir / "external_validation_feature_availability.tsv", sep="\t", index=False)
    write_report(metrics_df, predictions, feature_availability, out_dir / "external_validation_report.md")
    print(metrics_df.to_string(index=False) if not metrics_df.empty else "No external metrics generated.")


if __name__ == "__main__":
    main()
