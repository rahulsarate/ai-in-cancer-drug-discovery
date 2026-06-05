from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from spatial_emt_niche_gnn.interpret import niche_driver_summary


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Explain EMT niche predictions with edge ablations and feature perturbation.")
    p.add_argument("--scores", required=True)
    p.add_argument("--edges", required=True)
    p.add_argument("--predictions", required=True)
    p.add_argument("--out-dir", default="data/processed/spatial_emt_niche_gnn_demo")
    p.add_argument("--ablation-epochs", type=int, default=250)
    p.add_argument("--skip-edge-ablation", action="store_true")
    return p


def main() -> None:
    args = parser().parse_args()
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    scored = pd.read_csv(args.scores, sep="\t")
    edges = pd.read_csv(args.edges, sep="\t")
    predictions = pd.read_csv(args.predictions, sep="\t")
    reports = niche_driver_summary(
        scored,
        edges,
        predictions,
        ablation_epochs=args.ablation_epochs,
        skip_edge_ablation=args.skip_edge_ablation,
    )
    for name, table in reports.items():
        table.to_csv(out / f"{name}.tsv", sep="\t", index=False)
    print(f"Wrote interpretation tables to {out}")


if __name__ == "__main__":
    main()
