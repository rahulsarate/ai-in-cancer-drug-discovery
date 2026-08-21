from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from emt_virtual_spatial_staining.evaluation import evaluate_predictions, selective_risk_summary
from emt_virtual_spatial_staining.labels import PRIMARY_TARGETS
from emt_virtual_spatial_staining.modeling import EMTVistaEnsemble, embedding_columns


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Train the EMT-ViSTA image-only multitask baseline.")
    p.add_argument("--pairs", required=True)
    p.add_argument("--embeddings", required=True)
    p.add_argument("--out-dir", required=True)
    p.add_argument("--alpha", type=float, default=10.0)
    p.add_argument("--models", type=int, default=5)
    p.add_argument("--components", type=int, default=48)
    return p


def main() -> None:
    args = parser().parse_args()
    pairs = pd.read_csv(args.pairs, sep="\t", low_memory=False)
    embeddings = pd.read_csv(args.embeddings, sep="\t", low_memory=False)
    table = pairs.merge(embeddings, on="spot_uid", how="inner")
    train = table.loc[table["split"].eq("train") & table["supervised_eligible"].astype(bool)].copy()
    model = EMTVistaEnsemble(alpha=args.alpha, n_models=args.models, max_components=args.components).fit(
        train, feature_cols=embedding_columns(table)
    )
    predictions = model.predict(table)
    metrics = evaluate_predictions(table, predictions, PRIMARY_TARGETS)
    selective = selective_risk_summary(table, predictions)
    prevalence_predictions = table[["spot_uid", "split"]].copy()
    for target in PRIMARY_TARGETS:
        prevalence_predictions[f"pred_{target}"] = float(train[target].mean())
    prevalence_metrics = evaluate_predictions(table, prevalence_predictions, PRIMARY_TARGETS)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    model.save(out_dir / "emt_vista_baseline.joblib")
    predictions.to_csv(out_dir / "baseline_predictions.tsv", sep="\t", index=False)
    metrics.to_csv(out_dir / "baseline_metrics.tsv", sep="\t", index=False)
    prevalence_metrics.to_csv(out_dir / "prevalence_baseline_metrics.tsv", sep="\t", index=False)
    selective.to_csv(out_dir / "baseline_selective_risk.tsv", sep="\t", index=False)
    (out_dir / "baseline_model_metadata.json").write_text(json.dumps(model.metadata, indent=2), encoding="utf-8")
    print(metrics.loc[metrics["split"].eq("test")].to_string(index=False))


if __name__ == "__main__":
    main()
