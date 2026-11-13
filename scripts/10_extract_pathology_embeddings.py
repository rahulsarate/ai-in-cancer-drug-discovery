from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from emt_virtual_spatial_staining.tiles import extract_embeddings


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Extract aligned multi-scale H&E embeddings for EMT-ViSTA.")
    p.add_argument("--pairs", required=True)
    p.add_argument("--out-dir", required=True)
    p.add_argument(
        "--backend",
        choices=["handcrafted", "resnet50", "phikon_v2", "h_optimus_0"],
        default="handcrafted",
    )
    p.add_argument("--tile-px", type=int, default=224)
    p.add_argument("--context-px", type=int, default=448)
    p.add_argument("--batch-size", type=int, default=8)
    p.add_argument("--max-spots-per-dataset", type=int)
    return p


def main() -> None:
    args = parser().parse_args()
    pairs = pd.read_csv(args.pairs, sep="\t", low_memory=False)
    if args.max_spots_per_dataset:
        selected = []
        for _, group in pairs.groupby("dataset_id", sort=False):
            if len(group) <= args.max_spots_per_dataset:
                selected.append(group)
            else:
                order = group.sort_values(["x", "y"], kind="stable")
                positions = pd.Series(range(args.max_spots_per_dataset)).map(
                    lambda index: round(index * (len(order) - 1) / max(args.max_spots_per_dataset - 1, 1))
                )
                selected.append(order.iloc[positions.to_numpy(dtype=int)])
        pairs = pd.concat(selected, ignore_index=True)
    embeddings, metadata = extract_embeddings(
        pairs,
        backend=args.backend,
        tile_px=args.tile_px,
        context_px=args.context_px,
        batch_size=args.batch_size,
    )
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    embeddings.to_csv(out_dir / f"pathology_embeddings_{args.backend}.tsv", sep="\t", index=False)
    (out_dir / f"pathology_embeddings_{args.backend}.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(json.dumps({key: value for key, value in metadata.items() if key != "qc"}, indent=2))


if __name__ == "__main__":
    main()
