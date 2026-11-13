from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from emt_state_atlas.therapy import write_therapy_evidence_cards, write_therapy_report


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Build EMT-context therapeutic target cards.")
    p.add_argument("--ranking", required=True, help="Target ranking TSV/CSV.")
    p.add_argument("--state-summary", help="Cancer-type EMT state summary TSV/CSV.")
    p.add_argument("--out-dir", default="data/processed/pan_cancer_emt_state_atlas/cards/target_md")
    p.add_argument("--report-out", default="docs/pan_cancer_emt_state_atlas/reports/pan_cancer_emt_therapeutic_evidence_report.md")
    p.add_argument("--top-n", type=int, default=20)
    return p


def read_table(path: str | Path) -> pd.DataFrame:
    return pd.read_csv(path, sep=None, engine="python")


def main() -> None:
    args = parser().parse_args()
    ranking = read_table(args.ranking)
    state_summary = read_table(args.state_summary) if args.state_summary else None
    write_therapy_evidence_cards(ranking, state_summary, args.out_dir, top_n=args.top_n)
    write_therapy_report(ranking, state_summary, args.report_out, top_n=args.top_n)


if __name__ == "__main__":
    main()
