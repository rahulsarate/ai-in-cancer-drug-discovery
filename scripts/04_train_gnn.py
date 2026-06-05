from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from spatial_emt_niche_gnn.model import train_graph_logistic, write_model_outputs


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Train a graph-aware EMT niche prediction baseline.")
    p.add_argument("--scores", required=True)
    p.add_argument("--edges", required=True)
    p.add_argument("--out-dir", default="data/processed/spatial_emt_niche_gnn_demo")
    p.add_argument("--label-column", default="emt_niche_label")
    p.add_argument("--holdout-cohort", default="")
    p.add_argument("--epochs", type=int, default=1200)
    p.add_argument("--learning-rate", type=float, default=0.08)
    p.add_argument("--l2", type=float, default=0.01)
    return p


def main() -> None:
    args = parser().parse_args()
    scored = pd.read_csv(args.scores, sep="\t")
    edges = pd.read_csv(args.edges, sep="\t")
    predictions, metrics = train_graph_logistic(
        scored,
        edges,
        label_col=args.label_column,
        holdout_cohort=args.holdout_cohort or None,
        epochs=args.epochs,
        lr=args.learning_rate,
        l2=args.l2,
    )
    write_model_outputs(predictions, metrics, Path(args.out_dir))
    print(f"Wrote {Path(args.out_dir) / 'emt_niche_predictions.tsv'}")


if __name__ == "__main__":
    main()
