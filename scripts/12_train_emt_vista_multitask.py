from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from emt_virtual_spatial_staining.evaluation import (
    evaluate_predictions,
    go_no_go,
    partial_emt_safety_metrics,
    selective_risk_summary,
)
from emt_virtual_spatial_staining.labels import PRIMARY_TARGETS
from emt_virtual_spatial_staining.modeling import EMTVistaEnsemble, add_neighbor_features, embedding_columns


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Train graph-refined EMT-ViSTA multitask ensemble.")
    p.add_argument("--pairs", required=True)
    p.add_argument("--embeddings", required=True)
    p.add_argument("--out-dir", required=True)
    p.add_argument("--alpha", type=float, default=10.0)
    p.add_argument("--models", type=int, default=5)
    p.add_argument("--components", type=int, default=48)
    p.add_argument("--k-neighbors", type=int, default=6)
    return p


def main() -> None:
    args = parser().parse_args()
    pairs = pd.read_csv(args.pairs, sep="\t", low_memory=False)
    embeddings = pd.read_csv(args.embeddings, sep="\t", low_memory=False)
    table = pairs.merge(embeddings, on="spot_uid", how="inner")
    base_features = embedding_columns(table)
    table = add_neighbor_features(table, base_features, k_neighbors=args.k_neighbors, group_col="dataset_id")
    all_features = embedding_columns(table)
    train = table.loc[table["split"].eq("train") & table["supervised_eligible"].astype(bool)].copy()
    model = EMTVistaEnsemble(alpha=args.alpha, n_models=args.models, max_components=args.components).fit(
        train, feature_cols=all_features
    )
    model.metadata.update({"graph_refinement": "k-neighbor mean embedding", "k_neighbors": args.k_neighbors})
    predictions = model.predict(table)
    metrics = evaluate_predictions(table, predictions, PRIMARY_TARGETS)
    selective = selective_risk_summary(table, predictions)
    safety = partial_emt_safety_metrics(table, predictions)
    gates = go_no_go(metrics, safety=safety, selective=selective)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    model.save(out_dir / "emt_vista_multitask.joblib")
    pd.DataFrame(
        {
            "feature": all_features,
            "source": ["image" if feature in base_features else "spatial_neighbor" for feature in all_features],
        }
    ).to_csv(out_dir / "graph_feature_manifest.tsv", sep="\t", index=False)
    predictions.to_csv(out_dir / "emt_vista_predictions.tsv", sep="\t", index=False)
    metrics.to_csv(out_dir / "emt_vista_metrics.tsv", sep="\t", index=False)
    selective.to_csv(out_dir / "emt_vista_selective_risk.tsv", sep="\t", index=False)
    safety.to_csv(out_dir / "emt_vista_partial_emt_safety.tsv", sep="\t", index=False)
    gates.to_csv(out_dir / "emt_vista_go_no_go.tsv", sep="\t", index=False)
    (out_dir / "emt_vista_model_metadata.json").write_text(json.dumps(model.metadata, indent=2), encoding="utf-8")
    print(gates.to_string(index=False))


if __name__ == "__main__":
    main()
