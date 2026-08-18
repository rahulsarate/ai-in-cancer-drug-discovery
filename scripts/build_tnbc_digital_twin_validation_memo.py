from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


def read_table(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path, sep="\t")


def format_metric(value: object, digits: int = 3) -> str:
    try:
        if pd.isna(value):
            return "NA"
        return f"{float(value):.{digits}f}"
    except (TypeError, ValueError):
        return str(value)


def response_model_summary(metrics: pd.DataFrame) -> str:
    if metrics.empty:
        return "No response-model metrics available."
    keep = metrics[["evaluation", "feature_set", "samples", "auroc", "auprc", "accuracy"]].copy()
    return keep.to_markdown(index=False)


def gse43502_summary(feature_summary: pd.DataFrame) -> str:
    if feature_summary.empty:
        return "No `GSE43502` bootstrap summary available."
    cols = [
        "feature",
        "delta_recurrence_minus_no_recurrence",
        "delta_mean_q025",
        "delta_mean_q975",
        "bootstrap_probability_delta_gt_0",
        "mannwhitney_p",
    ]
    cols = [col for col in cols if col in feature_summary.columns]
    return feature_summary[cols].head(8).to_markdown(index=False)


def gse164715_summary(annotation_summary: pd.DataFrame) -> str:
    if annotation_summary.empty:
        return "No `GSE164715` targeted annotation summary available."
    totals = (
        annotation_summary.groupby("targeted_annotation")["cells"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )
    totals["fraction"] = totals["cells"] / totals["cells"].sum()
    return totals.to_markdown(index=False)


def simulation_summary(sim_summary: pd.DataFrame) -> str:
    if sim_summary.empty:
        return "No calibrated simulation summary available."
    cols = [
        "archetype",
        "final_tumor_burden",
        "final_resistant_fraction",
        "persister_delta",
        "residual_disease_probability_proxy",
    ]
    cols = [col for col in cols if col in sim_summary.columns]
    return sim_summary[cols].to_markdown(index=False)


def external_validation_summary(metrics: pd.DataFrame) -> str:
    if metrics.empty:
        return "No real external validation metrics available yet."
    cols = ["test_dataset", "calibration_method", "feature_set", "samples", "positive_rate", "auroc", "auprc", "accuracy", "brier"]
    cols = [col for col in cols if col in metrics.columns]
    return metrics[cols].to_markdown(index=False)


def label_curation_summary(curated: pd.DataFrame) -> str:
    if curated.empty:
        return "No response-label curation table available."
    summary = (
        curated.groupby(["dataset_id", "locked_composite_response", "curation_decision"], dropna=False)
        .size()
        .reset_index(name="samples")
        .sort_values(["dataset_id", "locked_composite_response", "curation_decision"])
    )
    return summary.to_markdown(index=False)


def ambiguity_summary(review: pd.DataFrame) -> str:
    if review.empty:
        return "No GSE164715 ambiguity-review table available."
    ambiguous = review[review["review_status"].astype(str).str.contains("ambiguity", na=False)].copy()
    cols = ["model", "sample_name", "stage", "targeted_annotation", "cells", "fraction", "review_status"]
    cols = [col for col in cols if col in ambiguous.columns]
    return ambiguous[cols].to_markdown(index=False) if not ambiguous.empty else "No high/moderate ambiguous sample-stage rows detected."


def platform_shift_summary(platform_shift: pd.DataFrame) -> str:
    if platform_shift.empty:
        return "No platform-normalization diagnostics available yet."
    cols = ["feature", "standardized_mean_shift", "ks_statistic", "ks_pvalue"]
    cols = [col for col in cols if col in platform_shift.columns]
    return platform_shift[cols].head(8).to_markdown(index=False)


def write_memo(
    response_metrics: pd.DataFrame,
    gse43502_features: pd.DataFrame,
    annotation_summary: pd.DataFrame,
    sim_summary: pd.DataFrame,
    external_metrics: pd.DataFrame,
    label_curation: pd.DataFrame,
    curated_metrics: pd.DataFrame,
    lodo_metrics: pd.DataFrame,
    platform_shift: pd.DataFrame,
    ambiguity_review: pd.DataFrame,
    out_path: Path,
) -> None:
    lines = [
        "# TNBC EMT Digital Twin Validation Memo",
        "",
        "## Purpose",
        "",
        "Separate what can be shown in clinician-style research reports from what must remain exploratory while the TNBC neoadjuvant chemotherapy EMT digital twin is still a research prototype.",
        "",
        "## Current Validation Status",
        "",
        "| Layer | Current evidence | Clinician-facing status | Research-only status |",
        "| --- | --- | --- | --- |",
        "| Baseline response model | Retrospective GEO TNBC-like NAC cohorts with deduplicated `GSE25055`/`GSE25065` split | Show only as model-performance context | Do not use for treatment selection or individual pCR prediction |",
        "| `GSE43816` longitudinal shift | 7 paired pretreatment/post-NAC TNBC samples | Show paired state-shift plots, cohort percentiles, and bootstrap uncertainty with caution | Do not infer pCR or survival response because parsed response labels are unavailable |",
        "| Therapy simulator | Synthetic archetypes plus `GSE43816` calibrated transition priors | Show as scenario simulation and uncertainty visualization | Do not interpret as calibrated tumor-burden forecast |",
        "| `GSE43502` residual recurrence biology | 25 residual chemoresistant TNBC samples, 16 recurrence and 9 no recurrence | Show only hypothesis-generating recurrence-axis trends | Do not make biomarker claims without larger validation |",
        "| `GSE164715` scRNA persister layer | Species-filtered PDX scRNA with targeted annotation of human-dominant cells plus marker-panel direction checks | Use to explain why persister risk is split into tumor/stress/niche layers | Do not present as full single-cell atlas or definitive malignant-cell classifier |",
        "",
        "## Locked Response-Label Curation",
        "",
        label_curation_summary(label_curation),
        "",
        "Interpretation: rows with available pathology fields indicating residual disease are conservatively recoded to `residual_or_poor_response` for the curated composite sensitivity analysis. Unknown response labels remain excluded.",
        "",
        "## Response-Model Metrics",
        "",
        response_model_summary(response_metrics),
        "",
        "Interpretation: the response model remains a benchmark and feature-prior engine. The cross-dataset performance is modest, so individual patient prediction should stay out of clinician-facing claims.",
        "",
        "## Curated-Label Sensitivity Metrics",
        "",
        response_model_summary(curated_metrics),
        "",
        "Interpretation: curated-label sensitivity changes the residual/poor-response prevalence and should be reported alongside the original broad endpoint.",
        "",
        "## Additional Same-Project Holdout Validation",
        "",
        external_validation_summary(lodo_metrics),
        "",
        "Interpretation: leave-dataset-out checks on small TNBC NAC cohorts add independent-label sensitivity but remain underpowered.",
        "",
        "## GSE43502 Bootstrap Recurrence-Axis Summary",
        "",
        gse43502_summary(gse43502_features),
        "",
        "Interpretation: AXL/TAM and hypoxia remain the strongest recurrence-associated directions, but intervals are wide and should be treated as hypothesis-generating.",
        "",
        "## Calibrated Therapy Simulation Summary",
        "",
        simulation_summary(sim_summary),
        "",
        "Interpretation: calibrated-prior simulation is useful for comparing state dynamics across archetypes, especially resistant and persister enrichment, but it is not yet a patient-specific outcome model.",
        "",
        "## Real External Validation: GSE163882",
        "",
        external_validation_summary(external_metrics),
        "",
        "Interpretation: `GSE163882_TNBC_TPM` is a held-out RNA-seq TPM cohort with 90 TNBC response-labeled samples. Performance is strongest for TME/resistance and combined feature sets, but it must be interpreted with platform diagnostics because the internal training cohorts are mostly array-derived.",
        "",
        "## Platform-Normalization Diagnostics",
        "",
        platform_shift_summary(platform_shift),
        "",
        "Interpretation: the largest platform/cohort shifts involve stemness/persister, TNBC hypoxia, YAP/TAZ, and therapy-selection-pressure features. Cross-platform performance should therefore be reported as external research validation, not as a locked clinical predictor.",
        "",
        "Batch-correction decision: because the current external test is a single RNA-seq TPM cohort compared against mostly array-derived internal cohorts, explicit batch correction should remain a sensitivity analysis rather than the primary validation result until a bridge cohort or multiple independent external cohorts are available. The report therefore keeps raw, internal-percentile, external-z-score, and external-quantile calibration results separated.",
        "",
        "## GSE164715 Targeted Annotation Summary",
        "",
        gse164715_summary(annotation_summary),
        "",
        "Interpretation: human-dominant targeted annotations support separating malignant-like persister signal from endothelial/stromal/immune-like residual-niche signal.",
        "",
        "## GSE164715 Ambiguity Review",
        "",
        ambiguity_summary(ambiguity_review),
        "",
        "Interpretation: ambiguous human-dominant compartments should be treated as unresolved cells, not as a named biological cell state.",
        "",
        "## Clinician-Style Report Rules",
        "",
        "Use these elements:",
        "",
        "- Dataset, sample, and timepoint provenance.",
        "- State fractions and direction of change.",
        "- Cohort-relative percentiles when cohort size is named clearly.",
        "- Bootstrap uncertainty intervals and explicit research-only caveats.",
        "- Dominant resistance axis as a molecular-review prompt.",
        "",
        "Avoid these elements:",
        "",
        "- Treatment recommendations.",
        "- Claims of validated pCR prediction from `GSE43816`.",
        "- Survival or recurrence prediction for an individual patient.",
        "- Single-cell cell-type claims beyond targeted annotation and marker-panel direction checks.",
        "",
        "## Next Validation Actions",
        "",
        "1. Obtain final expert/author sign-off on the computational response-label curation table.",
        "2. Keep explicit batch correction as sensitivity-only unless a bridge cohort or additional external cohorts become available.",
        "3. Obtain expert/author review of `GSE164715` ambiguity language before publication-level single-cell claims.",
        "4. Polish the manuscript/thesis draft and format citations, figures, and tables for the target venue.",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Build a validation memo for the TNBC EMT digital-twin prototype.")
    p.add_argument("--processed-dir", default="data/processed/tnbc_digital_twin")
    p.add_argument("--docs-dir", default="docs/tnbc_digital_twin_emt_plasticity")
    return p


def main() -> None:
    args = parser().parse_args()
    processed = ROOT / args.processed_dir
    docs = ROOT / args.docs_dir
    response_metrics = read_table(processed / "tnbc_nac_response_model_metrics.tsv")
    gse43502_features = read_table(processed / "residual_persister_biology" / "gse43502_recurrence_feature_summary.tsv")
    annotation_summary = read_table(processed / "gse164715_targeted_annotation" / "gse164715_targeted_annotation_stage_summary.tsv")
    sim_summary = read_table(processed / "tnbc_digital_twin_calibrated_prior_summary.tsv")
    external_metrics = read_table(processed / "external_validation" / "gse163882" / "external_validation_metrics.tsv")
    label_curation = read_table(processed / "response_label_curation" / "tnbc_response_label_curation_table.tsv")
    curated_metrics = read_table(processed / "response_label_curation" / "curated_model" / "tnbc_nac_response_model_metrics.tsv")
    lodo_metrics = read_table(processed / "leave_dataset_out_validation" / "tnbc_leave_dataset_out_metrics.tsv")
    platform_shift = read_table(processed / "platform_normalization" / "tnbc_platform_feature_shift_diagnostics.tsv")
    ambiguity_review = read_table(processed / "gse164715_ambiguity_review" / "gse164715_sample_stage_ambiguity_review.tsv")
    out_processed = processed / "tnbc_digital_twin_validation_memo.md"
    out_docs = docs / "validation_memo.md"
    write_memo(response_metrics, gse43502_features, annotation_summary, sim_summary, external_metrics, label_curation, curated_metrics, lodo_metrics, platform_shift, ambiguity_review, out_processed)
    docs.mkdir(parents=True, exist_ok=True)
    write_memo(response_metrics, gse43502_features, annotation_summary, sim_summary, external_metrics, label_curation, curated_metrics, lodo_metrics, platform_shift, ambiguity_review, out_docs)
    print(f"wrote {out_processed}")
    print(f"wrote {out_docs}")


if __name__ == "__main__":
    main()
