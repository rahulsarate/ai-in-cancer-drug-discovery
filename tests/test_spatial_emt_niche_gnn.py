from __future__ import annotations

import pandas as pd

from spatial_emt_niche_gnn.data import make_demo_spatial_dataset, read_spatial_expression, read_spatial_metadata
from spatial_emt_niche_gnn.graph import build_spatial_graph
from spatial_emt_niche_gnn.model import train_graph_logistic
from spatial_emt_niche_gnn.scoring import score_spatial_niches


def test_demo_spatial_scoring_creates_risk_labels(tmp_path):
    expression_path, metadata_path = make_demo_spatial_dataset(tmp_path, n=36)
    expression = read_spatial_expression(expression_path)
    metadata = read_spatial_metadata(metadata_path)

    scored = score_spatial_niches(expression, metadata)

    assert "emt_niche_label" in scored.columns
    assert "stromal_inflated_emt_candidate" in scored.columns
    assert scored["emt_niche_label"].sum() > 0


def test_spatial_graph_and_model_produce_predictions(tmp_path):
    expression_path, metadata_path = make_demo_spatial_dataset(tmp_path, n=36)
    scored = score_spatial_niches(read_spatial_expression(expression_path), read_spatial_metadata(metadata_path))

    edges = build_spatial_graph(scored, k=4, radius=2.5)
    predictions, metrics = train_graph_logistic(scored, edges, epochs=50)

    assert not edges.empty
    assert set(predictions["split"]).issubset({"train", "test"})
    assert predictions["emt_niche_probability"].between(0, 1).all()
    assert pd.notna(metrics["train_accuracy"])


def test_spatial_graph_does_not_connect_different_samples(tmp_path):
    expression_path, metadata_path = make_demo_spatial_dataset(tmp_path, n=36)
    scored = score_spatial_niches(read_spatial_expression(expression_path), read_spatial_metadata(metadata_path))
    duplicate = scored.copy()
    duplicate["sample_id"] = "second_slide"
    duplicate["spot_id"] = "second|" + duplicate["spot_id"].astype(str)
    combined = pd.concat([scored, duplicate], ignore_index=True)

    edges = build_spatial_graph(combined, k=4, radius=2.5)
    sample_by_spot = combined.set_index("spot_id")["sample_id"].to_dict()
    cross_edges = [
        row
        for _, row in edges.iterrows()
        if sample_by_spot[row["source"]] != sample_by_spot[row["target"]]
    ]

    assert cross_edges == []
