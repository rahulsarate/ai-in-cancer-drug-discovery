from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from emt_state_atlas.clinical import (
    association_summary,
    clinical_group_summary,
    clinical_warnings,
    covariate_adjusted_event_screen,
    run_multivariable_cox_models,
    survival_by_stratum,
    write_clinical_report,
)


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Build clinical association layer for the Pan-Cancer EMT State Atlas.")
    p.add_argument("--scores", default="data/processed/pan_cancer_emt_state_atlas/cards/emt_scores_with_consensus.tsv")
    p.add_argument("--out-dir", default="data/processed/pan_cancer_emt_state_atlas/clinical")
    p.add_argument("--report-out", default="docs/pan_cancer_emt_state_atlas/reports/pan_cancer_emt_clinical_report.md")
    return p


def main() -> None:
    args = parser().parse_args()
    scores = pd.read_csv(args.scores, sep="\t", low_memory=False)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    group_summary = clinical_group_summary(scores)
    survival = survival_by_stratum(scores)
    covariate_screen = covariate_adjusted_event_screen(scores)
    cox_models = run_multivariable_cox_models(scores)
    associations = association_summary(scores)
    warnings = clinical_warnings(group_summary)

    group_summary.to_csv(out_dir / "clinical_group_summary.tsv", sep="\t", index=False)
    survival.to_csv(out_dir / "clinical_survival_by_group.tsv", sep="\t", index=False)
    covariate_screen.to_csv(out_dir / "clinical_covariate_adjusted_screen.tsv", sep="\t", index=False)
    cox_models.to_csv(out_dir / "clinical_multivariable_cox_models.tsv", sep="\t", index=False)
    associations.to_csv(out_dir / "clinical_stage_grade_metastasis_summary.tsv", sep="\t", index=False)
    warnings.to_csv(out_dir / "clinical_warnings.tsv", sep="\t", index=False)
    write_clinical_report(group_summary, survival, covariate_screen, cox_models, associations, warnings, args.report_out)
    print(f"Wrote clinical layer to {out_dir}")


if __name__ == "__main__":
    main()
