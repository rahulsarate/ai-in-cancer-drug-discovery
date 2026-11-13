from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from emt_state_atlas.therapy import disease_group_target_recommendations, write_disease_group_target_report


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Build EMT target recommendations by disease group.")
    p.add_argument("--ranking", default="data/processed/target_ranker_real_evidence_v1/target_ranking.tsv")
    p.add_argument("--group-summary", default="data/processed/pan_cancer_emt_state_atlas/cards/cancer_group_state_summary.tsv")
    p.add_argument("--out", default="data/processed/pan_cancer_emt_state_atlas/cards/target_disease_group_recommendations.tsv")
    p.add_argument("--report-out", default="docs/pan_cancer_emt_state_atlas/reports/pan_cancer_emt_disease_group_target_report.md")
    p.add_argument("--top-n-per-group", type=int, default=12)
    return p


def main() -> None:
    args = parser().parse_args()
    ranking = pd.read_csv(args.ranking, sep="\t", low_memory=False)
    group_summary = pd.read_csv(args.group_summary, sep="\t", low_memory=False)
    recommendations = disease_group_target_recommendations(ranking, group_summary, top_n_per_group=args.top_n_per_group)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    recommendations.to_csv(out, sep="\t", index=False)
    write_disease_group_target_report(recommendations, args.report_out)
    print(f"Wrote disease-group target recommendations to {out}")


if __name__ == "__main__":
    main()
