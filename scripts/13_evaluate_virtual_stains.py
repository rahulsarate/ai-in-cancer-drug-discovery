from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from emt_virtual_spatial_staining.evaluation import (
    evaluate_predictions,
    go_no_go,
    partial_emt_safety_metrics,
    selective_risk_summary,
)
from emt_virtual_spatial_staining.labels import PRIMARY_TARGETS


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Evaluate EMT-ViSTA predictions with explicit go/no-go gates.")
    p.add_argument("--pairs", required=True)
    p.add_argument("--predictions", required=True)
    p.add_argument("--out-dir", required=True)
    return p


def main() -> None:
    args = parser().parse_args()
    pairs = pd.read_csv(args.pairs, sep="\t", low_memory=False)
    predictions = pd.read_csv(args.predictions, sep="\t", low_memory=False)
    metrics = evaluate_predictions(pairs, predictions, PRIMARY_TARGETS)
    selective = selective_risk_summary(pairs, predictions)
    safety = partial_emt_safety_metrics(pairs, predictions)
    gates = go_no_go(metrics, safety=safety, selective=selective)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(out_dir / "evaluation_metrics.tsv", sep="\t", index=False)
    selective.to_csv(out_dir / "selective_risk.tsv", sep="\t", index=False)
    safety.to_csv(out_dir / "partial_emt_safety.tsv", sep="\t", index=False)
    gates.to_csv(out_dir / "go_no_go.tsv", sep="\t", index=False)
    print(gates.to_string(index=False))


if __name__ == "__main__":
    main()
