from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from spatial_emt_niche_gnn.histology import extract_tile_features, summarize_histology_features


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Extract basic H&E tile features around Visium spot coordinates.")
    p.add_argument("--metadata", required=True)
    p.add_argument("--spatial-dir", required=True, help="10x spatial directory containing tissue_hires_image.png.")
    p.add_argument("--out-dir", required=True)
    p.add_argument("--tile-px", type=int, default=48)
    return p


def main() -> None:
    args = parser().parse_args()
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    metadata = pd.read_csv(args.metadata, sep="\t")
    features = extract_tile_features(metadata, args.spatial_dir, tile_px=args.tile_px)
    features.to_csv(out / "he_tile_features.tsv", sep="\t", index=False)
    summarize_histology_features(features).to_csv(out / "he_tile_feature_summary.tsv", sep="\t", index=False)
    print(f"Wrote {out / 'he_tile_features.tsv'}")


if __name__ == "__main__":
    main()
