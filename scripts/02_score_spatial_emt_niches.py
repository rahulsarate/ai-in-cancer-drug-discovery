from __future__ import annotations

import argparse
from pathlib import Path

from spatial_emt_niche_gnn.data import qc_spots, read_spatial_expression, read_spatial_metadata
from spatial_emt_niche_gnn.scoring import score_spatial_niches, summarize_niches


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Score EMT and microenvironment programs in spatial transcriptomics spots.")
    p.add_argument("--expression", required=True)
    p.add_argument("--metadata", required=True)
    p.add_argument("--out-dir", default="data/processed/spatial_emt_niche_gnn_demo")
    return p


def main() -> None:
    args = parser().parse_args()
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    expression = read_spatial_expression(args.expression)
    metadata = read_spatial_metadata(args.metadata)
    qc = qc_spots(expression, metadata)
    scored = score_spatial_niches(expression, qc)
    scored.to_csv(out / "spatial_emt_niche_scores.tsv", sep="\t", index=False)
    summarize_niches(scored).to_csv(out / "spatial_niche_summary.tsv", sep="\t", index=False)
    print(f"Wrote {out / 'spatial_emt_niche_scores.tsv'}")


if __name__ == "__main__":
    main()
