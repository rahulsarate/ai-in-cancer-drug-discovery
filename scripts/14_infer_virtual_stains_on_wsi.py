from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from emt_virtual_spatial_staining.modeling import EMTVistaEnsemble, add_neighbor_features


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Run a trained EMT-ViSTA model on aligned H&E embeddings.")
    p.add_argument("--model", required=True)
    p.add_argument("--pairs", required=True)
    p.add_argument("--embeddings", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--k-neighbors", type=int, default=6)
    return p


def main() -> None:
    args = parser().parse_args()
    model = EMTVistaEnsemble.load(args.model)
    pairs = pd.read_csv(args.pairs, sep="\t", low_memory=False)
    embeddings = pd.read_csv(args.embeddings, sep="\t", low_memory=False)
    table = pairs.merge(embeddings, on="spot_uid", how="inner")
    missing = [column for column in model.feature_columns if column not in table.columns]
    if missing and all(column.startswith("neighbor_") for column in missing):
        base = [column for column in model.feature_columns if not column.startswith("neighbor_")]
        table = add_neighbor_features(table, base, k_neighbors=args.k_neighbors, group_col="dataset_id")
    remaining = [column for column in model.feature_columns if column not in table.columns]
    if remaining:
        raise ValueError(f"Inference embeddings are missing {len(remaining)} model features")
    predictions = model.predict(table)
    destination = Path(args.out)
    destination.parent.mkdir(parents=True, exist_ok=True)
    predictions.to_csv(destination, sep="\t", index=False)
    print(f"Wrote {len(predictions)} virtual-stain predictions to {destination}")


if __name__ == "__main__":
    main()
