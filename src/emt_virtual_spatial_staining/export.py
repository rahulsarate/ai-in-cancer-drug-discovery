from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .tiles import coordinate_scale, find_image


MAP_COLUMNS = [
    "pred_epithelial",
    "pred_mesenchymal",
    "pred_partial_emt_gated_probability",
    "pred_caf",
    "pred_tam_spp1",
    "pred_hypoxia",
    "pred_ecm_remodeling",
    "pred_stromal_inflated_emt_risk",
    "mean_prediction_uncertainty",
]


def export_geojson(predictions: pd.DataFrame, out_path: str | Path, top_fraction: float = 0.10) -> Path:
    score = pd.to_numeric(predictions["pred_partial_emt_gated_probability"], errors="coerce")
    threshold = float(score.quantile(1.0 - top_fraction))
    selected = predictions.loc[score >= threshold]
    features = []
    for _, row in selected.iterrows():
        x = float(row.get("pixel_x", row.get("x", 0.0)))
        y = float(row.get("pixel_y", row.get("y", 0.0)))
        properties = {
            "spot_uid": str(row["spot_uid"]),
            "partial_emt_gated_probability": float(row["pred_partial_emt_gated_probability"]),
            "stromal_inflated_emt_risk": float(row["pred_stromal_inflated_emt_risk"]),
            "uncertainty": float(row["mean_prediction_uncertainty"]),
            "abstain": bool(row["abstain"]),
        }
        features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [x, y]},
                "properties": properties,
            }
        )
    destination = Path(out_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps({"type": "FeatureCollection", "features": features}, indent=2), encoding="utf-8")
    return destination


def export_map_panel(predictions: pd.DataFrame, out_path: str | Path) -> Path:
    available = [column for column in MAP_COLUMNS if column in predictions.columns]
    columns = 3
    rows = int(np.ceil(len(available) / columns))
    figure, axes = plt.subplots(rows, columns, figsize=(4.5 * columns, 4.0 * rows), squeeze=False)
    x = pd.to_numeric(predictions.get("x", predictions.get("pixel_x")), errors="coerce")
    y = pd.to_numeric(predictions.get("y", predictions.get("pixel_y")), errors="coerce")
    for axis, column in zip(axes.flat, available):
        values = pd.to_numeric(predictions[column], errors="coerce")
        scatter = axis.scatter(x, -y, c=values, s=8, cmap="viridis", linewidths=0)
        axis.set_title(column.replace("pred_", "").replace("_", " "))
        axis.set_aspect("equal")
        axis.axis("off")
        figure.colorbar(scatter, ax=axis, fraction=0.046, pad=0.04)
    for axis in axes.flat[len(available) :]:
        axis.axis("off")
    figure.tight_layout()
    destination = Path(out_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(destination, dpi=180, bbox_inches="tight")
    plt.close(figure)
    return destination


def export_he_overlay(predictions: pd.DataFrame, out_path: str | Path) -> Path | None:
    if "spatial_dir" not in predictions.columns or predictions["spatial_dir"].dropna().empty:
        return None
    spatial_dir = str(predictions["spatial_dir"].dropna().iloc[0])
    try:
        image_path = find_image(spatial_dir)
    except FileNotFoundError:
        return None
    image = plt.imread(image_path)
    scale = coordinate_scale(spatial_dir, image_path)
    x = pd.to_numeric(predictions["pixel_x"], errors="coerce") * scale
    y = pd.to_numeric(predictions["pixel_y"], errors="coerce") * scale
    columns = [
        "pred_partial_emt_gated_probability",
        "pred_caf",
        "pred_hypoxia",
        "pred_stromal_inflated_emt_risk",
    ]
    figure, axes = plt.subplots(2, 2, figsize=(12, 10), squeeze=False)
    for axis, column in zip(axes.flat, columns):
        axis.imshow(image)
        values = pd.to_numeric(predictions[column], errors="coerce")
        scatter = axis.scatter(x, y, c=values, s=10, cmap="magma", alpha=0.72, linewidths=0)
        axis.set_title(column.replace("pred_", "").replace("_", " "))
        axis.axis("off")
        figure.colorbar(scatter, ax=axis, fraction=0.046, pad=0.04)
    figure.tight_layout()
    destination = Path(out_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(destination, dpi=180, bbox_inches="tight")
    plt.close(figure)
    return destination


def slide_summary(predictions: pd.DataFrame) -> pd.DataFrame:
    group_cols = [column for column in ["dataset_id", "sample_id"] if column in predictions.columns]
    if not group_cols:
        predictions = predictions.assign(dataset_id="unknown")
        group_cols = ["dataset_id"]
    return (
        predictions.groupby(group_cols, dropna=False)
        .agg(
            spots=("spot_uid", "count"),
            mean_partial_emt=("pred_partial_emt_gated_probability", "mean"),
            p90_partial_emt=("pred_partial_emt_gated_probability", lambda values: values.quantile(0.90)),
            mean_stromal_risk=("pred_stromal_inflated_emt_risk", "mean"),
            mean_uncertainty=("mean_prediction_uncertainty", "mean"),
            abstained_fraction=("abstain", "mean"),
        )
        .reset_index()
    )
