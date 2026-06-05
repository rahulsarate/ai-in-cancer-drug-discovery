from __future__ import annotations

import argparse
from pathlib import Path

from .io import orient_expression, read_expression, read_metadata
from .metadata import attach_patient_metadata
from .plots import write_atlas_plots
from .reports import write_atlas_report
from .scoring import score_expression
from .signatures import SIGNATURES
from .summaries import add_state_flags, cancer_type_summary, validate_outputs
from .survival import run_univariate_survival


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Score EMT and TME states from expression data.")
    parser.add_argument("--expression", required=True, help="Expression matrix, TSV or CSV.")
    parser.add_argument("--metadata", help="Optional metadata with sample_id column.")
    parser.add_argument("--out", required=True, help="Output TSV for scores.")
    parser.add_argument("--summary-out", help="Optional cancer-type summary TSV.")
    parser.add_argument("--survival-out", help="Optional survival result TSV.")
    parser.add_argument("--validation-out", help="Optional output-column validation TSV.")
    parser.add_argument("--plots-dir", help="Optional directory for atlas plots.")
    parser.add_argument("--report-out", help="Optional Markdown report path.")
    parser.add_argument("--time-col", default="time")
    parser.add_argument("--event-col", default="event")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    known_genes = {gene.upper() for genes in SIGNATURES.values() for gene in genes}
    expr = orient_expression(read_expression(args.expression), known_genes)
    metadata = read_metadata(args.metadata)
    scores = add_state_flags(attach_patient_metadata(score_expression(expr), metadata))

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    scores.to_csv(out, sep="\t", index=False)

    summary = None
    if args.summary_out:
        summary = cancer_type_summary(scores)
        summary_out = Path(args.summary_out)
        summary_out.parent.mkdir(parents=True, exist_ok=True)
        summary.to_csv(summary_out, sep="\t", index=False)

    survival = None
    if args.survival_out:
        try:
            survival = run_univariate_survival(
                scores,
                ["emt_score", "partial_emt_score", "stromal_fibroblast", "immune_total", "caf_tam_niche"],
                time_col=args.time_col,
                event_col=args.event_col,
            )
        except RuntimeError as exc:
            import pandas as pd

            survival = pd.DataFrame([{"status": "not_run", "reason": str(exc)}])
        survival_out = Path(args.survival_out)
        survival_out.parent.mkdir(parents=True, exist_ok=True)
        survival.to_csv(survival_out, sep="\t", index=False)

    if args.validation_out:
        validation = validate_outputs(
            scores,
            [
                "sample_id",
                "emt_score",
                "partial_emt_score",
                "stromal_contamination_risk",
                "cancer_type",
                args.time_col,
                args.event_col,
            ],
        )
        validation_out = Path(args.validation_out)
        validation_out.parent.mkdir(parents=True, exist_ok=True)
        validation.to_csv(validation_out, sep="\t", index=False)

    plots = write_atlas_plots(scores, args.plots_dir) if args.plots_dir else []
    if args.report_out:
        if summary is None:
            summary = cancer_type_summary(scores)
        write_atlas_report(scores, summary, survival, plots, args.report_out)


if __name__ == "__main__":
    main()
