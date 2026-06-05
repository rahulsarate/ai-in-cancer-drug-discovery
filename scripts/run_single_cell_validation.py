from __future__ import annotations

import argparse
from pathlib import Path

from emt_state_atlas.io import read_expression, read_metadata
from emt_state_atlas.single_cell import score_single_cell_expression, summarize_single_cell_states


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Score single-cell or cell-state expression for EMT validation.")
    p.add_argument("--expression", required=True, help="Cell x gene or gene x cell matrix.")
    p.add_argument("--metadata", help="Optional cell metadata with sample_id or cell_id.")
    p.add_argument("--out-dir", default="data/processed/single_cell_validation")
    return p


def main() -> None:
    args = parser().parse_args()
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    expression = read_expression(args.expression)
    metadata = read_metadata(args.metadata)
    scores = score_single_cell_expression(expression, metadata)
    summary = summarize_single_cell_states(scores)
    scores.to_csv(out / "single_cell_emt_scores.tsv", sep="\t", index=False)
    summary.to_csv(out / "single_cell_state_summary.tsv", sep="\t", index=False)


if __name__ == "__main__":
    main()
