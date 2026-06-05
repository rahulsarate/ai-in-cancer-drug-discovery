from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from spatial_emt_niche_gnn.heterograph import build_heterogeneous_graph_nodes


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Build heterogeneous spot-compartment graph tables.")
    p.add_argument("--scores", required=True)
    p.add_argument("--proxy", required=True)
    p.add_argument("--out-dir", required=True)
    return p


def main() -> None:
    args = parser().parse_args()
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    scored = pd.read_csv(args.scores, sep="\t")
    proxy = pd.read_csv(args.proxy, sep="\t")
    nodes, edges = build_heterogeneous_graph_nodes(scored, proxy)
    nodes.to_csv(out / "heterogeneous_nodes.tsv", sep="\t", index=False)
    edges.to_csv(out / "heterogeneous_edges.tsv", sep="\t", index=False)
    print(f"Wrote {out / 'heterogeneous_nodes.tsv'} and {out / 'heterogeneous_edges.tsv'}")


if __name__ == "__main__":
    main()
