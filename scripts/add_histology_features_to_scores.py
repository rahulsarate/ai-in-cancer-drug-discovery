from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Merge per-spot H&E tile features into spatial EMT niche scores.")
    p.add_argument("--scores", required=True)
    p.add_argument("--features", required=True)
    p.add_argument("--out", required=True)
    return p


def main() -> None:
    args = parser().parse_args()
    scores = pd.read_csv(args.scores, sep="\t")
    features = pd.read_csv(args.features, sep="\t")
    overlap = [col for col in features.columns if col != "spot_id" and col in scores.columns]
    if overlap:
        scores = scores.drop(columns=overlap)
    merged = scores.merge(features, on="spot_id", how="left")
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(out, sep="\t", index=False)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
