from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from emt_state_atlas.lineage_targets import merge_lineage_targets, summarize_depmap_by_cancer_group, write_lineage_target_report


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Build cancer-lineage-specific DepMap evidence for EMT targets.")
    p.add_argument("--gene-effect", default="data/raw/depmap/target_family_CRISPRGeneEffect.csv")
    p.add_argument("--models", default="data/raw/depmap/Model.csv")
    p.add_argument("--disease-targets", default="data/processed/pan_cancer_emt_state_atlas/cards/target_disease_group_recommendations.tsv")
    p.add_argument("--out-dir", default="data/processed/pan_cancer_emt_state_atlas/lineage_targets")
    p.add_argument("--report-out", default="docs/pan_cancer_emt_state_atlas/reports/pan_cancer_emt_lineage_target_report.md")
    return p


def main() -> None:
    args = parser().parse_args()
    gene_effect = pd.read_csv(args.gene_effect, low_memory=False)
    models = pd.read_csv(args.models, low_memory=False)
    disease_targets = pd.read_csv(args.disease_targets, sep="\t", low_memory=False)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    depmap_summary = summarize_depmap_by_cancer_group(gene_effect, models)
    merged_targets = merge_lineage_targets(disease_targets, depmap_summary)
    depmap_summary.to_csv(out_dir / "depmap_lineage_target_dependency.tsv", sep="\t", index=False)
    merged_targets.to_csv(out_dir / "disease_target_recommendations_with_lineage_evidence.tsv", sep="\t", index=False)
    write_lineage_target_report(depmap_summary, merged_targets, args.report_out)
    print(f"Wrote lineage target evidence to {out_dir}")


if __name__ == "__main__":
    main()
