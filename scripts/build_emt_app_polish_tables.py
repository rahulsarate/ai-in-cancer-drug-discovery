from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from emt_state_atlas.app_tables import group_small_cohort_warnings, state_comparison_table


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Build app helper tables for warnings and EMT-state comparisons.")
    p.add_argument("--scores", default="data/processed/pan_cancer_emt_state_atlas/cards/emt_scores_with_consensus.tsv")
    p.add_argument("--group-summary", default="data/processed/pan_cancer_emt_state_atlas/cards/cancer_group_state_summary.tsv")
    p.add_argument("--out-dir", default="data/processed/pan_cancer_emt_state_atlas/app")
    return p


def main() -> None:
    args = parser().parse_args()
    scores = pd.read_csv(args.scores, sep="\t", low_memory=False)
    group_summary = pd.read_csv(args.group_summary, sep="\t", low_memory=False)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    group_small_cohort_warnings(group_summary).to_csv(out_dir / "app_group_warnings.tsv", sep="\t", index=False)
    state_comparison_table(scores).to_csv(out_dir / "app_state_comparison.tsv", sep="\t", index=False)
    print(f"Wrote app polish tables to {out_dir}")


if __name__ == "__main__":
    main()
