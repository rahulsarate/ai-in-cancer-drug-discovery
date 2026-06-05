from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from spatial_emt_niche_gnn.graph import build_spatial_graph, edge_type_summary


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Build typed spatial EMT niche graphs.")
    p.add_argument("--scores", required=True)
    p.add_argument("--out-dir", default="data/processed/spatial_emt_niche_gnn_demo")
    p.add_argument("--k", type=int, default=6)
    p.add_argument("--radius", type=float, default=2.5)
    return p


def main() -> None:
    args = parser().parse_args()
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    scored = pd.read_csv(args.scores, sep="\t")
    edges = build_spatial_graph(scored, k=args.k, radius=args.radius)
    edges.to_csv(out / "spatial_graph_edges.tsv", sep="\t", index=False)
    edge_type_summary(edges).to_csv(out / "spatial_graph_summary.tsv", sep="\t", index=False)
    print(f"Wrote {out / 'spatial_graph_edges.tsv'} ({len(edges)} edges)")


if __name__ == "__main__":
    main()
