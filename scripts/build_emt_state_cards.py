from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from emt_state_atlas.cards import write_card_report, write_state_cards
from emt_state_atlas.consensus import add_consensus_states


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Build consensus EMT state labels and user-facing state cards.")
    p.add_argument("--scores", required=True, help="Input EMT score table.")
    p.add_argument("--out-dir", default="data/processed/pan_cancer_emt_state_atlas/cards")
    p.add_argument("--report-out", default="docs/pan_cancer_emt_state_atlas/reports/pan_cancer_emt_state_atlas_card_report.md")
    p.add_argument("--cancer-type-col", default="cancer_type")
    p.add_argument("--max-sample-cards", type=int, default=50)
    return p


def main() -> None:
    args = parser().parse_args()
    scores = pd.read_csv(args.scores, sep=None, engine="python")
    scored = add_consensus_states(scores, cancer_type_col=args.cancer_type_col)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    write_state_cards(
        scored,
        out_dir=out_dir,
        max_sample_cards=args.max_sample_cards,
        cancer_type_col=args.cancer_type_col,
    )
    write_card_report(scored, args.report_out, cancer_type_col=args.cancer_type_col)


if __name__ == "__main__":
    main()
