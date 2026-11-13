from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, average_precision_score, brier_score_loss, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]


FEATURE_SETS = {
    "emt_core": [
        "epithelial",
        "mesenchymal",
        "emt_score",
        "partial_emt_score",
        "partial_emt_balance",
    ],
    "tme_resistance": [
        "stromal_fibroblast",
        "caf",
        "immune_total",
        "t_cell_cytotoxic",
        "tam_spp1",
        "hypoxia",
        "caf_tam_niche",
        "tnbc_axl_tam",
        "tnbc_tgfb",
        "tnbc_yap_taz",
        "tnbc_hypoxia",
        "tnbc_stemness_persister",
        "tnbc_persister_tumor_refined",
        "tnbc_persister_stress_tolerance",
        "tnbc_persister_niche",
        "tnbc_immune_checkpoint",
    ],
    "digital_twin": [
        "epithelial_fraction_estimate",
        "hybrid_fraction_estimate",
        "mesenchymal_fraction_estimate",
        "persister_fraction_estimate",
        "plasticity_index",
        "resistant_fraction_estimate",
        "therapy_selection_pressure",
        "residual_disease_probability_proxy",
        "prediction_confidence_proxy",
    ],
}


def available_features(df: pd.DataFrame, feature_names: list[str]) -> list[str]:
    return [feature for feature in feature_names if feature in df.columns and pd.to_numeric(df[feature], errors="coerce").notna().any()]


def deduplicate_samples(df: pd.DataFrame) -> pd.DataFrame:
    priority = {"GSE25055": 0, "GSE25065": 0, "GSE18864": 0, "GSE45898": 0, "GSE25066": 1}
    out = df.copy()
    out["_dataset_priority"] = out["dataset_id"].map(priority).fillna(2)
    out = out.sort_values(["sample_id", "_dataset_priority", "dataset_id"]).drop_duplicates("sample_id", keep="first")
    return out.drop(columns=["_dataset_priority"])


def make_pipeline() -> Pipeline:
    return Pipeline(
        [
            ("impute", SimpleImputer(strategy="median", keep_empty_features=True)),
            ("scale", StandardScaler()),
            ("model", LogisticRegression(max_iter=2000, class_weight="balanced", solver="liblinear")),
        ]
    )


def metrics(y_true: pd.Series, y_score: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    result = {
        "samples": float(len(y_true)),
        "positive_rate": float(np.mean(y_true)),
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "brier": float(brier_score_loss(y_true, y_score)),
    }
    if len(set(y_true)) > 1:
        result["auroc"] = float(roc_auc_score(y_true, y_score))
        result["auprc"] = float(average_precision_score(y_true, y_score))
    else:
        result["auroc"] = np.nan
        result["auprc"] = np.nan
    return result


def evaluate_cv(df: pd.DataFrame, feature_set: str, features: list[str]) -> dict[str, float]:
    y = (df["standard_response"] == "residual_or_poor_response").astype(int)
    X = df[features].apply(pd.to_numeric, errors="coerce")
    min_class = int(y.value_counts().min())
    splits = max(2, min(5, min_class))
    cv = StratifiedKFold(n_splits=splits, shuffle=True, random_state=13)
    model = make_pipeline()
    scores = cross_val_predict(model, X, y, cv=cv, method="predict_proba")[:, 1]
    preds = (scores >= 0.5).astype(int)
    row = metrics(y, scores, preds)
    row.update({"evaluation": "stratified_cv", "feature_set": feature_set, "feature_count": len(features), "train_dataset": "all_deduplicated", "test_dataset": "all_deduplicated"})
    return row


def evaluate_train_test(df: pd.DataFrame, feature_set: str, features: list[str], train_dataset: str, test_dataset: str) -> tuple[dict[str, float] | None, pd.DataFrame]:
    train = df[df["dataset_id"] == train_dataset]
    test = df[df["dataset_id"] == test_dataset]
    if train.empty or test.empty:
        return None, pd.DataFrame()
    y_train = (train["standard_response"] == "residual_or_poor_response").astype(int)
    y_test = (test["standard_response"] == "residual_or_poor_response").astype(int)
    if y_train.nunique() < 2 or y_test.nunique() < 2:
        return None, pd.DataFrame()
    X_train = train[features].apply(pd.to_numeric, errors="coerce")
    X_test = test[features].apply(pd.to_numeric, errors="coerce")
    model = make_pipeline()
    model.fit(X_train, y_train)
    scores = model.predict_proba(X_test)[:, 1]
    preds = (scores >= 0.5).astype(int)
    row = metrics(y_test, scores, preds)
    row.update({"evaluation": "train_test", "feature_set": feature_set, "feature_count": len(features), "train_dataset": train_dataset, "test_dataset": test_dataset})

    coef = model.named_steps["model"].coef_[0]
    importance = pd.DataFrame({"feature_set": feature_set, "feature": features, "coefficient": coef}).sort_values("coefficient", key=lambda s: s.abs(), ascending=False)
    return row, importance


def write_report(metrics_df: pd.DataFrame, importance: pd.DataFrame, cohort_summary: pd.DataFrame, out_path: Path) -> None:
    lines = [
        "# TNBC NAC Response Model Report",
        "",
        "## Cohort Summary",
        "",
        cohort_summary.to_markdown(index=False),
        "",
        "## Model Metrics",
        "",
        metrics_df.to_markdown(index=False),
        "",
        "## Top Discovery-to-Validation Coefficients",
        "",
        importance.head(25).to_markdown(index=False) if not importance.empty else "No coefficient table generated.",
        "",
        "## Interpretation Rules",
        "",
        "- Positive label is residual disease or poor response.",
        "- These are first-pass research models, not clinical decision tools.",
        "- `GSE25066` is a superseries overlapping `GSE25055` and `GSE25065`; deduplicated modeling keeps subseries rows first.",
        "- The strongest immediate validation comparison is train on `GSE25055` and test on `GSE25065`.",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Train first TNBC NAC pCR/residual-disease models from EMT digital-twin features.")
    p.add_argument("--model-table", default="data/processed/tnbc_digital_twin/tnbc_nac_emt_digital_twin_tnbc_response_model_table.tsv")
    p.add_argument("--out-dir", default="data/processed/tnbc_digital_twin")
    return p


def main() -> None:
    args = parser().parse_args()
    out_dir = ROOT / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    raw = pd.read_csv(ROOT / args.model_table, sep="\t")
    raw = raw[raw["standard_response"].isin(["pcr_or_good_response", "residual_or_poor_response"])].copy()
    dedup = deduplicate_samples(raw)

    cohort_summary = (
        dedup.groupby(["dataset_id", "standard_response"], dropna=False)
        .size()
        .reset_index(name="samples")
    )

    metric_rows = []
    importance_frames = []
    feature_sets = {
        "emt_core": FEATURE_SETS["emt_core"],
        "emt_tme_resistance": FEATURE_SETS["emt_core"] + FEATURE_SETS["tme_resistance"],
        "digital_twin": FEATURE_SETS["digital_twin"],
        "combined": FEATURE_SETS["emt_core"] + FEATURE_SETS["tme_resistance"] + FEATURE_SETS["digital_twin"],
    }
    for name, feature_names in feature_sets.items():
        features = available_features(dedup, feature_names)
        if len(features) < 2:
            continue
        metric_rows.append(evaluate_cv(dedup, name, features))
        train_test, importance = evaluate_train_test(dedup, name, features, "GSE25055", "GSE25065")
        if train_test is not None:
            metric_rows.append(train_test)
        if not importance.empty:
            importance_frames.append(importance)

    metrics_df = pd.DataFrame(metric_rows)
    importance_df = pd.concat(importance_frames, ignore_index=True) if importance_frames else pd.DataFrame()
    dedup.to_csv(out_dir / "tnbc_nac_response_model_table_deduplicated.tsv", sep="\t", index=False)
    metrics_df.to_csv(out_dir / "tnbc_nac_response_model_metrics.tsv", sep="\t", index=False)
    importance_df.to_csv(out_dir / "tnbc_nac_response_model_feature_importance.tsv", sep="\t", index=False)
    write_report(metrics_df, importance_df, cohort_summary, out_dir / "tnbc_nac_response_model_report.md")
    print(metrics_df.to_string(index=False))


if __name__ == "__main__":
    main()
