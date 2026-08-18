from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, average_precision_score, brier_score_loss, roc_auc_score


ROOT = Path(__file__).resolve().parents[1]


def metric_bundle(y_true: np.ndarray, y_score: np.ndarray) -> dict[str, float]:
    pred = (y_score >= 0.5).astype(int)
    out = {
        "accuracy": float(accuracy_score(y_true, pred)),
        "brier": float(brier_score_loss(y_true, y_score)),
    }
    if len(np.unique(y_true)) > 1:
        out["auroc"] = float(roc_auc_score(y_true, y_score))
        out["auprc"] = float(average_precision_score(y_true, y_score))
    else:
        out["auroc"] = np.nan
        out["auprc"] = np.nan
    return out


def bootstrap_predictions(predictions: pd.DataFrame, n_bootstrap: int, seed: int) -> pd.DataFrame:
    rows = []
    rng = np.random.default_rng(seed)
    for keys, group in predictions.groupby(["dataset_id", "feature_set", "calibration_method"], dropna=False):
        y_true = (group["standard_response"] == "residual_or_poor_response").astype(int).to_numpy()
        y_score = pd.to_numeric(group["residual_or_poor_response_probability"], errors="coerce").to_numpy(dtype=float)
        valid = ~np.isnan(y_score)
        y_true = y_true[valid]
        y_score = y_score[valid]
        if y_true.size == 0:
            continue
        point = metric_bundle(y_true, y_score)
        boot = {metric: [] for metric in ["auroc", "accuracy", "brier"]}
        for _ in range(n_bootstrap):
            idx = rng.integers(0, y_true.size, size=y_true.size)
            sampled_y = y_true[idx]
            sampled_score = y_score[idx]
            sampled_pred = (sampled_score >= 0.5).astype(int)
            boot["accuracy"].append(float((sampled_pred == sampled_y).mean()))
            boot["brier"].append(float(np.mean((sampled_score - sampled_y) ** 2)))
            if len(np.unique(sampled_y)) > 1:
                boot["auroc"].append(float(roc_auc_score(sampled_y, sampled_score)))
        row = {"dataset_id": keys[0], "feature_set": keys[1], "calibration_method": keys[2], "samples": int(y_true.size)}
        for metric, value in point.items():
            row[f"{metric}_point"] = value
            vals = np.array(boot.get(metric, []), dtype=float)
            row[f"{metric}_q025"] = float(np.quantile(vals, 0.025)) if vals.size else np.nan
            row[f"{metric}_q975"] = float(np.quantile(vals, 0.975)) if vals.size else np.nan
        rows.append(row)
    return pd.DataFrame(rows)


def write_report(intervals: pd.DataFrame, out_path: Path) -> None:
    lines = [
        "# TNBC External Response Metric Robustness",
        "",
        "## Bootstrap Intervals",
        "",
        intervals.to_markdown(index=False) if not intervals.empty else "No intervals available.",
        "",
        "## Interpretation",
        "",
        "- Intervals are nonparametric bootstrap intervals over external validation samples.",
        "- Wide intervals reflect limited external cohort size and should be reported with all AUROC/AUPRC values.",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Bootstrap external TNBC response-model metrics.")
    p.add_argument("--predictions", default="data/processed/tnbc_digital_twin/external_validation/gse163882/external_validation_predictions.tsv")
    p.add_argument("--out-dir", default="data/processed/tnbc_digital_twin/response_model_robustness")
    p.add_argument("--bootstrap-samples", type=int, default=200)
    p.add_argument("--seed", type=int, default=20260614)
    return p


def main() -> None:
    args = parser().parse_args()
    out_dir = ROOT / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    predictions = pd.read_csv(ROOT / args.predictions, sep="\t")
    intervals = bootstrap_predictions(predictions, args.bootstrap_samples, args.seed)
    intervals.to_csv(out_dir / "gse163882_external_metric_bootstrap_intervals.tsv", sep="\t", index=False)
    write_report(intervals, out_dir / "gse163882_external_metric_bootstrap_report.md")
    print(intervals.to_string(index=False))


if __name__ == "__main__":
    main()
