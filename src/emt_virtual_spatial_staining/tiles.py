from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd
from PIL import Image, ImageFilter


Image.MAX_IMAGE_PIXELS = None


def find_image(spatial_dir: str | Path) -> Path:
    root = Path(spatial_dir)
    names = [
        "tissue_hires_image.png",
        "aligned_tissue_image.jpg",
        "detected_tissue_image.jpg",
        "tissue_lowres_image.png",
    ]
    for name in names:
        candidate = root / name
        if candidate.exists():
            return candidate
    raise FileNotFoundError(f"No aligned H&E image found under {root}")


def coordinate_scale(spatial_dir: str | Path, image_path: str | Path) -> float:
    root = Path(spatial_dir)
    factors = root / "scalefactors_json.json"
    if factors.exists():
        data = json.loads(factors.read_text(encoding="utf-8"))
        if Path(image_path).name == "tissue_lowres_image.png":
            return float(data.get("tissue_lowres_scalef", 1.0))
        return float(data.get("tissue_hires_scalef", 1.0))
    return 1.0


def _center(row: pd.Series, scale: float) -> tuple[int, int]:
    if pd.notna(row.get("pixel_x")) and pd.notna(row.get("pixel_y")):
        return int(round(float(row["pixel_x"]) * scale)), int(round(float(row["pixel_y"]) * scale))
    return int(round(float(row["x"]))), int(round(float(row["y"])))


def crop_tile(image: Image.Image, x: int, y: int, tile_px: int) -> Image.Image:
    half = tile_px // 2
    canvas = Image.new("RGB", (tile_px, tile_px), color=(255, 255, 255))
    left, upper, right, lower = x - half, y - half, x + half, y + half
    clipped = image.crop((max(0, left), max(0, upper), min(image.width, right), min(image.height, lower)))
    canvas.paste(clipped, (max(0, -left), max(0, -upper)))
    return canvas


def _entropy(values: np.ndarray, bins: int = 32) -> float:
    hist, _ = np.histogram(values, bins=bins, range=(0.0, 1.0), density=False)
    probabilities = hist.astype(float) / max(hist.sum(), 1)
    probabilities = probabilities[probabilities > 0]
    return float(-(probabilities * np.log2(probabilities)).sum())


def handcrafted_features(tile: Image.Image, prefix: str) -> dict[str, float]:
    rgb = np.asarray(tile.convert("RGB"), dtype=np.float32) / 255.0
    gray = rgb.mean(axis=2)
    hsv = np.asarray(tile.convert("HSV"), dtype=np.float32) / 255.0
    blurred = np.asarray(tile.convert("L").filter(ImageFilter.GaussianBlur(radius=1)), dtype=np.float32) / 255.0
    edge = np.abs(gray - blurred)
    features: dict[str, float] = {}
    for index, channel in enumerate(["red", "green", "blue"]):
        values = rgb[:, :, index]
        features[f"{prefix}_{channel}_mean"] = float(values.mean())
        features[f"{prefix}_{channel}_std"] = float(values.std())
        features[f"{prefix}_{channel}_q25"] = float(np.quantile(values, 0.25))
        features[f"{prefix}_{channel}_q75"] = float(np.quantile(values, 0.75))
    features[f"{prefix}_brightness_mean"] = float(gray.mean())
    features[f"{prefix}_brightness_std"] = float(gray.std())
    features[f"{prefix}_hematoxylin_proxy"] = float((rgb[:, :, 2] - rgb[:, :, 0]).mean())
    features[f"{prefix}_eosin_proxy"] = float((rgb[:, :, 0] - rgb[:, :, 2]).mean())
    features[f"{prefix}_saturation_mean"] = float(hsv[:, :, 1].mean())
    features[f"{prefix}_dark_fraction"] = float((gray < 0.75).mean())
    features[f"{prefix}_white_fraction"] = float((gray > 0.92).mean())
    features[f"{prefix}_edge_mean"] = float(edge.mean())
    features[f"{prefix}_edge_high_fraction"] = float((edge > 0.08).mean())
    features[f"{prefix}_entropy"] = _entropy(gray)
    return features


def _load_encoder(backend: str) -> tuple[Callable[[list[Image.Image]], np.ndarray] | None, str]:
    if backend == "handcrafted":
        return None, "handcrafted"

    import torch
    from torchvision.models import ResNet50_Weights, resnet50

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    if backend == "resnet50":
        weights = ResNet50_Weights.DEFAULT
        model = resnet50(weights=weights)
        model.fc = torch.nn.Identity()
        transform = weights.transforms()
        model.to(device).eval()

        def encode(images: list[Image.Image]) -> np.ndarray:
            batch = torch.stack([transform(image) for image in images]).to(device)
            with torch.inference_mode():
                return model(batch).detach().cpu().numpy()

        return encode, "torchvision_resnet50_imagenet1k_v2"

    if backend == "h_optimus_0":
        import timm
        from torchvision import transforms

        try:
            model = timm.create_model(
                "hf-hub:bioptimus/H-optimus-0",
                pretrained=True,
                init_values=1e-5,
                dynamic_img_size=False,
            )
        except Exception as exc:
            raise RuntimeError(
                "H-Optimus-0 weights require accepted HuggingFace terms and an HF_TOKEN; "
                "use --backend resnet50 or handcrafted until credentials are configured."
            ) from exc
        model.to(device).eval()
        transform = transforms.Compose(
            [
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=(0.707223, 0.578729, 0.703617), std=(0.211883, 0.230117, 0.177517)),
            ]
        )

        def encode(images: list[Image.Image]) -> np.ndarray:
            batch = torch.stack([transform(image) for image in images]).to(device)
            with torch.inference_mode():
                output = model(batch)
                if isinstance(output, (tuple, list)):
                    output = output[0]
                return output.detach().cpu().numpy()

        return encode, "bioptimus/H-optimus-0"

    if backend == "phikon_v2":
        import torch
        from transformers import AutoImageProcessor, AutoModel

        processor = AutoImageProcessor.from_pretrained("owkin/phikon-v2")
        model = AutoModel.from_pretrained("owkin/phikon-v2")
        model.to(device).eval()

        def encode(images: list[Image.Image]) -> np.ndarray:
            inputs = {key: value.to(device) for key, value in processor(images=images, return_tensors="pt").items()}
            with torch.inference_mode():
                output = model(**inputs).last_hidden_state[:, 0, :]
                return output.detach().cpu().numpy()

        return encode, "owkin/phikon-v2"

    raise ValueError(f"Unsupported embedding backend: {backend}")


def extract_embeddings(
    pairs: pd.DataFrame,
    backend: str = "handcrafted",
    tile_px: int = 224,
    context_px: int = 448,
    batch_size: int = 8,
) -> tuple[pd.DataFrame, dict]:
    encoder, resolved_backend = _load_encoder(backend)
    records: list[dict[str, float | str | bool]] = []
    qc_rows = []

    for spatial_dir, group in pairs.groupby("spatial_dir", sort=False):
        try:
            image_path = find_image(spatial_dir)
            image = Image.open(image_path).convert("RGB")
            scale = coordinate_scale(spatial_dir, image_path)
        except Exception as exc:
            for _, row in group.iterrows():
                records.append({"spot_uid": row["spot_uid"], "embedding_qc_pass": False})
            qc_rows.append({"spatial_dir": spatial_dir, "status": "image_error", "detail": str(exc)})
            continue

        group = group.reset_index(drop=True)
        for start in range(0, len(group), batch_size):
            chunk = group.iloc[start : start + batch_size]
            centers = [_center(row, scale) for _, row in chunk.iterrows()]
            center_tiles = [crop_tile(image, x, y, tile_px) for x, y in centers]
            context_tiles = [crop_tile(image, x, y, context_px).resize((tile_px, tile_px)) for x, y in centers]

            if encoder is None:
                for (_, row), center, context in zip(chunk.iterrows(), center_tiles, context_tiles):
                    features = handcrafted_features(center, "center")
                    features.update(handcrafted_features(context, "context"))
                    records.append({"spot_uid": row["spot_uid"], "embedding_qc_pass": True, **features})
            else:
                center_vector = encoder(center_tiles)
                context_vector = encoder(context_tiles)
                matrix = np.concatenate([center_vector, context_vector], axis=1)
                for (_, row), vector in zip(chunk.iterrows(), matrix):
                    features = {f"embedding_{index:04d}": float(value) for index, value in enumerate(vector)}
                    records.append({"spot_uid": row["spot_uid"], "embedding_qc_pass": True, **features})

        qc_rows.append(
            {
                "spatial_dir": spatial_dir,
                "image_path": str(image_path),
                "image_width": image.width,
                "image_height": image.height,
                "coordinate_scale": scale,
                "spots": len(group),
                "status": "ok",
            }
        )

    embeddings = pd.DataFrame(records)
    metadata = {
        "requested_backend": backend,
        "resolved_backend": resolved_backend,
        "tile_px": tile_px,
        "context_px": context_px,
        "batch_size": batch_size,
        "spots": len(embeddings),
        "features": len([column for column in embeddings.columns if column not in {"spot_uid", "embedding_qc_pass"}]),
        "qc": qc_rows,
    }
    return embeddings, metadata
