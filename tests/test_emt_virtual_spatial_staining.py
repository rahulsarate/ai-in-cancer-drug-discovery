from __future__ import annotations

import json

import numpy as np
import pandas as pd
from PIL import Image

from emt_virtual_spatial_staining.data import deterministic_group_split
from emt_virtual_spatial_staining.evaluation import go_no_go, partial_emt_safety_metrics, selective_risk_summary
from emt_virtual_spatial_staining.labels import PRIMARY_TARGETS, add_virtual_stain_labels
from emt_virtual_spatial_staining.modeling import EMTVistaEnsemble
from emt_virtual_spatial_staining.tiles import extract_embeddings


def _label_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "spot_id": ["tumor", "stroma", "epithelial", "mixed"],
            "epithelial": [1.2, -0.5, 1.5, 1.0],
            "mesenchymal": [1.1, 1.4, -1.0, 0.9],
            "partial_emt_score": [1.0, 1.2, -0.8, 0.8],
            "caf": [0.1, 1.5, -0.4, 0.3],
            "tam_spp1": [0.2, 0.8, -0.3, 0.4],
            "hypoxia": [0.5, 0.2, -0.2, 0.4],
            "ecm_remodeling": [0.2, 1.7, -0.5, 0.4],
            "stromal_contamination_risk": [0.1, 0.95, 0.05, 0.3],
            "label_strength": ["strong_proxy", "contamination_risk", "weak_proxy", "strong_proxy"],
            "low_library_risk": [False, False, False, False],
            "low_complexity_risk": [False, False, False, False],
        }
    )


def test_partial_emt_gate_penalizes_stromal_mixture() -> None:
    scored = add_virtual_stain_labels(_label_frame())
    tumor = scored.set_index("spot_id").loc["tumor"]
    stroma = scored.set_index("spot_id").loc["stroma"]
    assert tumor["partial_emt_gated_target"] > stroma["partial_emt_gated_target"]
    assert bool(stroma["stromal_inflated_partial_emt"])
    assert stroma["label_tier"] == "D"


def test_group_split_keeps_named_holdout_separate() -> None:
    frame = pd.DataFrame({"sample_id": np.repeat(["a", "b", "c", "lung", "crc"], 4)})
    split = deterministic_group_split(frame, test_groups={"lung", "crc"})
    assert set(split.loc[frame["sample_id"].isin(["lung", "crc"])]) == {"test"}
    assert not split.loc[~frame["sample_id"].isin(["lung", "crc"])].eq("test").any()
    assert split.loc[frame["sample_id"].eq("a")].nunique() == 1
    assert split.eq("train").any()


def test_handcrafted_embedding_uses_aligned_coordinates(tmp_path) -> None:
    spatial = tmp_path / "spatial"
    spatial.mkdir()
    image = Image.new("RGB", (200, 200), color=(245, 245, 245))
    pixels = np.asarray(image).copy()
    pixels[60:140, 60:140] = (90, 40, 120)
    Image.fromarray(pixels).save(spatial / "tissue_hires_image.png")
    (spatial / "scalefactors_json.json").write_text(json.dumps({"tissue_hires_scalef": 1.0}), encoding="utf-8")
    pairs = pd.DataFrame(
        {
            "spot_uid": ["sample::inside", "sample::outside"],
            "spatial_dir": [str(spatial), str(spatial)],
            "pixel_x": [100, 15],
            "pixel_y": [100, 15],
            "x": [0, 1],
            "y": [0, 1],
        }
    )
    embeddings, metadata = extract_embeddings(pairs, backend="handcrafted", tile_px=48, context_px=96)
    indexed = embeddings.set_index("spot_uid")
    assert indexed.loc["sample::inside", "center_dark_fraction"] > indexed.loc["sample::outside", "center_dark_fraction"]
    assert metadata["resolved_backend"] == "handcrafted"
    assert metadata["features"] >= 30


def test_multitask_ensemble_exports_uncertainty_and_gates() -> None:
    rng = np.random.default_rng(4)
    rows = 80
    x1 = rng.normal(size=rows)
    x2 = rng.normal(size=rows)
    frame = pd.DataFrame(
        {
            "spot_uid": [f"s::{index}" for index in range(rows)],
            "spot_id": [str(index) for index in range(rows)],
            "sample_id": np.repeat(["a", "b", "c", "d"], rows // 4),
            "dataset_id": np.repeat(["a", "b", "c", "d"], rows // 4),
            "split": ["train"] * 60 + ["test"] * 20,
            "x": np.arange(rows),
            "y": np.arange(rows) % 10,
            "center_feature_1": x1,
            "context_feature_2": x2,
            "label_confidence": np.ones(rows),
        }
    )
    for index, target in enumerate(PRIMARY_TARGETS):
        frame[target] = (index + 1) * 0.1 * x1 + 0.2 * x2
    model = EMTVistaEnsemble(n_models=3, max_components=2, alpha=0.1).fit(frame.iloc[:60])
    predictions = model.predict(frame)
    assert len(predictions) == rows
    assert "uncertainty_partial_emt_score" in predictions.columns
    assert "pred_partial_emt_gated_probability" in predictions.columns
    assert predictions["pred_partial_emt_gated_probability"].between(0, 1).all()


def test_safety_metrics_are_explicit_when_partial_emt_is_stromal() -> None:
    truth = pd.DataFrame(
        {
            "spot_uid": [f"s::{index}" for index in range(12)],
            "split": ["test"] * 12,
            "partial_emt_score": np.linspace(-1, 1, 12),
            "stromal_contamination_risk": [0.9] * 6 + [0.1] * 6,
            "tumor_cell_emt_candidate": [False] * 6 + [True] * 6,
        }
    )
    predictions = pd.DataFrame(
        {
            "spot_uid": truth["spot_uid"],
            "split": truth["split"],
            "pred_partial_emt_gated_probability": np.linspace(0.05, 0.95, 12),
            "pred_partial_emt_score": np.linspace(-0.8, 0.8, 12),
            "uncertainty_partial_emt_score": np.linspace(0.1, 0.4, 12),
        }
    )
    safety = partial_emt_safety_metrics(truth, predictions)
    selective = selective_risk_summary(truth, predictions)
    gates = go_no_go(pd.DataFrame(columns=["split", "target", "spearman"]), safety=safety, selective=selective)
    assert "pure_stroma_false_positive_rate" in safety.columns
    assert "partial_emt_calibration_error" in set(gates["criterion"])
