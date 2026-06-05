from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from spatial_emt_niche_gnn.figures import write_paper_figure_tables, write_research_article_stub


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Generate paper-ready figure source tables and article scaffold.")
    p.add_argument("--scores", required=True)
    p.add_argument("--edges", required=True)
    p.add_argument("--predictions", required=True)
    p.add_argument("--interpret-dir", required=True)
    p.add_argument("--out-dir", default="data/processed/spatial_emt_niche_gnn_demo/paper")
    return p


def main() -> None:
    args = parser().parse_args()
    out = Path(args.out_dir)
    scored = pd.read_csv(args.scores, sep="\t")
    edges = pd.read_csv(args.edges, sep="\t")
    predictions = pd.read_csv(args.predictions, sep="\t")
    interpretation = {}
    for name in ["edge_type_summary", "edge_ablation", "feature_perturbation"]:
        path = Path(args.interpret_dir) / f"{name}.tsv"
        if path.exists():
            interpretation[name] = pd.read_csv(path, sep="\t")
    write_paper_figure_tables(scored, edges, predictions, interpretation, out)
    write_research_article_stub(out / "spatial_emt_niche_gnn_article_draft.md")
    print(f"Wrote paper tables and article draft to {out}")


if __name__ == "__main__":
    main()
