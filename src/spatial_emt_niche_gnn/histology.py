from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image


def find_histology_image(spatial_dir: str | Path) -> Path:
    root = Path(spatial_dir)
    for name in ["tissue_hires_image.png", "tissue_lowres_image.png", "detected_tissue_image.jpg"]:
        path = root / name
        if path.exists():
            return path
    raise FileNotFoundError(f"No supported 10x histology image found in {root}")


def hires_scale(spatial_dir: str | Path) -> float:
    path = Path(spatial_dir) / "scalefactors_json.json"
    if not path.exists():
        return 1.0
    data = json.loads(path.read_text(encoding="utf-8"))
    return float(data.get("tissue_hires_scalef", data.get("tissue_lowres_scalef", 1.0)))


def extract_tile_features(metadata: pd.DataFrame, spatial_dir: str | Path, tile_px: int = 48) -> pd.DataFrame:
    image_path = find_histology_image(spatial_dir)
    scale = hires_scale(spatial_dir)
    image = Image.open(image_path).convert("RGB")
    arr = np.asarray(image, dtype=np.float32) / 255.0
    half = tile_px // 2
    rows = []
    for _, row in metadata.iterrows():
        if "pixel_x" in row and "pixel_y" in row and pd.notna(row["pixel_x"]) and pd.notna(row["pixel_y"]):
            x = int(float(row["pixel_x"]) * scale)
            y = int(float(row["pixel_y"]) * scale)
        else:
            x = int(float(row["x"]))
            y = int(float(row["y"]))
        x0, x1 = max(0, x - half), min(arr.shape[1], x + half)
        y0, y1 = max(0, y - half), min(arr.shape[0], y + half)
        tile = arr[y0:y1, x0:x1]
        if tile.size == 0:
            stats = {name: np.nan for name in feature_names()}
        else:
            red, green, blue = tile[:, :, 0], tile[:, :, 1], tile[:, :, 2]
            gray = tile.mean(axis=2)
            hematoxylin_proxy = blue - red
            eosin_proxy = red - blue
            stats = {
                "tile_red_mean": float(red.mean()),
                "tile_green_mean": float(green.mean()),
                "tile_blue_mean": float(blue.mean()),
                "tile_brightness_mean": float(gray.mean()),
                "tile_brightness_std": float(gray.std()),
                "hematoxylin_proxy_mean": float(hematoxylin_proxy.mean()),
                "eosin_proxy_mean": float(eosin_proxy.mean()),
                "tissue_dark_fraction": float((gray < 0.75).mean()),
            }
        rows.append({"spot_id": row["spot_id"], **stats})
    return pd.DataFrame(rows)


def feature_names() -> list[str]:
    return [
        "tile_red_mean",
        "tile_green_mean",
        "tile_blue_mean",
        "tile_brightness_mean",
        "tile_brightness_std",
        "hematoxylin_proxy_mean",
        "eosin_proxy_mean",
        "tissue_dark_fraction",
    ]


def summarize_histology_features(features: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col in feature_names():
        if col in features.columns:
            rows.append(
                {
                    "feature": col,
                    "mean": features[col].mean(),
                    "median": features[col].median(),
                    "std": features[col].std(ddof=0),
                    "missing": int(features[col].isna().sum()),
                }
            )
    return pd.DataFrame(rows)
