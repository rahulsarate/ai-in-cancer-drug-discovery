from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from .graph import graph_features


MODEL_FEATURES = [
    "emt_score",
    "partial_emt_score",
    "stromal_contamination_risk",
    "immune_context",
    "caf_tam_niche",
    "hypoxia",
    "ecm_remodeling",
    "angiogenesis",
    "ferroptosis_window",
]


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(x, -40, 40)))


def standardize(train: np.ndarray, test: np.ndarray | None = None) -> tuple[np.ndarray, np.ndarray | None, dict]:
    mean = train.mean(axis=0)
    scale = train.std(axis=0)
    scale[scale == 0] = 1.0
    ztrain = (train - mean) / scale
    ztest = None if test is None else (test - mean) / scale
    return ztrain, ztest, {"mean": mean.tolist(), "scale": scale.tolist()}


def train_graph_logistic(
    scored: pd.DataFrame,
    edges: pd.DataFrame,
    label_col: str = "emt_niche_label",
    cohort_col: str = "cohort",
    holdout_cohort: str | None = None,
    epochs: int = 1200,
    lr: float = 0.08,
    l2: float = 0.01,
) -> tuple[pd.DataFrame, dict]:
    """Train a dependency-light graph-aware logistic model.

    This is the MVP baseline: features are spot scores plus message-passed
    neighbor scores. It is not a replacement for a PyTorch Geometric GNN, but it
    establishes the graph-learning workflow and robust validation outputs.
    """
    feature_cols = [col for col in MODEL_FEATURES if col in scored.columns]
    features = graph_features(scored, edges, feature_cols)
    feature_names = [col for col in features.columns if col != "spot_id"]
    table = scored[["spot_id", label_col] + ([cohort_col] if cohort_col in scored.columns else [])].merge(
        features, on="spot_id", how="left"
    )
    table[feature_names] = table[feature_names].apply(pd.to_numeric, errors="coerce").fillna(0.0)
    y = table[label_col].astype(int).to_numpy()

    if holdout_cohort and cohort_col in table.columns:
        train_mask = table[cohort_col].astype(str).ne(holdout_cohort).to_numpy()
    else:
        rng = np.random.default_rng(11)
        train_mask = rng.random(len(table)) < 0.8
    if train_mask.sum() == 0 or (~train_mask).sum() == 0:
        train_mask = np.arange(len(table)) % 5 != 0

    x = table[feature_names].to_numpy(dtype=float)
    x_train, x_test, scaler = standardize(x[train_mask], x[~train_mask])
    y_train = y[train_mask]
    x_train = np.c_[np.ones(len(x_train)), x_train]
    x_test_aug = np.c_[np.ones(len(x_test)), x_test]
    weights = np.zeros(x_train.shape[1])
    for _ in range(epochs):
        pred = sigmoid(x_train @ weights)
        grad = x_train.T @ (pred - y_train) / len(y_train)
        grad[1:] += l2 * weights[1:]
        weights -= lr * grad

    mean = np.array(scaler["mean"], dtype=float)
    scale = np.array(scaler["scale"], dtype=float)
    all_z = (x - mean) / scale
    all_aug = np.c_[np.ones(len(all_z)), all_z]
    table["emt_niche_probability"] = sigmoid(all_aug @ weights)
    table["split"] = np.where(train_mask, "train", "test")
    metrics = {
        "model": "graph_logistic_message_passing_baseline",
        "feature_names": ["intercept"] + feature_names,
        "weights": weights.tolist(),
        "scaler": scaler,
        "train_accuracy": accuracy(y_train, sigmoid(x_train @ weights)),
        "test_accuracy": accuracy(y[~train_mask], sigmoid(x_test_aug @ weights)) if (~train_mask).sum() else None,
        "holdout_cohort": holdout_cohort or "",
        "risk_controls": [
            "neighbor message passing uses typed spatial graph",
            "weak labels remain explicit in scored table",
            "leave-cohort-out validation supported through --holdout-cohort",
        ],
    }
    return table[["spot_id", "split", label_col, "emt_niche_probability"]], metrics


def accuracy(y: np.ndarray, probability: np.ndarray) -> float:
    if len(y) == 0:
        return float("nan")
    return float(((probability >= 0.5).astype(int) == y.astype(int)).mean())


def write_model_outputs(predictions: pd.DataFrame, metrics: dict, out_dir: str | Path) -> None:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    predictions.to_csv(out / "emt_niche_predictions.tsv", sep="\t", index=False)
    (out / "model_metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
