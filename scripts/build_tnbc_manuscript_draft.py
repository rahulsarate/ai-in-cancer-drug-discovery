from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


def read_table(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    return pd.read_csv(path, sep="\t")


def best_metric(metrics: pd.DataFrame, dataset: str | None = None) -> str:
    if metrics.empty:
        return "No metrics available."
    df = metrics.copy()
    if dataset and "test_dataset" in df.columns:
        df = df[df["test_dataset"].astype(str).str.contains(dataset, na=False)]
    if df.empty:
        return "No matching metrics available."
    if "feature_set" in df.columns:
        combined = df[df["feature_set"] == "combined"]
        if not combined.empty:
            df = combined
    sort_col = "auroc" if "auroc" in df.columns else "accuracy"
    df[sort_col] = pd.to_numeric(df[sort_col], errors="coerce")
    row = df.sort_values(sort_col, ascending=False).iloc[0]
    parts = []
    for col in ["test_dataset", "calibration_method", "feature_set", "samples", "accuracy", "auroc", "auprc", "brier"]:
        if col in row.index:
            parts.append(f"{col}={row[col]}")
    return ", ".join(parts)


def section_table(df: pd.DataFrame, n: int = 12) -> str:
    if df.empty:
        return "No table available."
    return df.head(n).to_markdown(index=False)


def write_draft(processed: Path, docs: Path, out_path: Path) -> None:
    external = read_table(processed / "external_validation" / "gse163882" / "external_validation_metrics.tsv")
    curated = read_table(processed / "response_label_curation" / "curated_model" / "tnbc_nac_response_model_metrics.tsv")
    lodo = read_table(processed / "leave_dataset_out_validation" / "tnbc_leave_dataset_out_metrics.tsv")
    bootstrap = read_table(processed / "response_model_robustness" / "gse163882_external_metric_bootstrap_intervals.tsv")
    marker = read_table(processed / "gse164715_marker_validation" / "gse164715_marker_panel_direction_checks.tsv")
    ambiguity = read_table(processed / "gse164715_ambiguity_review" / "gse164715_sample_stage_ambiguity_review.tsv")
    recurrence = read_table(processed / "residual_persister_biology" / "gse43502_recurrence_feature_summary.tsv")
    transition = read_table(processed / "transition_calibration" / "gse43816_calibrated_transition_parameters.tsv")

    marker_pass = "NA"
    if not marker.empty and "passes_direction_check" in marker.columns:
        marker_pass = f"{marker['passes_direction_check'].astype(str).str.lower().eq('true').sum()}/{len(marker)}"

    lines = [
        "# Digital Twin of EMT Plasticity Under Neoadjuvant Chemotherapy in Triple-Negative Breast Cancer",
        "",
        "## Draft Status",
        "",
        "This is a manuscript/thesis chapter draft generated from the locked local analysis outputs. It supports a research-prototype claim only and should undergo author, pathology, oncology, and bioinformatics review before submission.",
        "",
        "## Abstract",
        "",
        "Triple-negative breast cancer (TNBC) has heterogeneous response to neoadjuvant chemotherapy (NAC), with residual disease after therapy associated with high recurrence risk. We developed a reproducible EMT plasticity digital-twin prototype that converts public TNBC NAC transcriptomic cohorts into interpretable epithelial-like, hybrid epithelial/mesenchymal, mesenchymal-like, and drug-tolerant persister state features. The workflow integrates baseline response modeling, longitudinal pre/post-NAC EMT-shift analysis, transition-prior calibration, residual recurrence-axis analysis, persister single-cell refinement, and external validation. The resulting system is not a clinical treatment-selection model, but it provides a transparent research framework for studying therapy-induced EMT plasticity and residual-disease biology.",
        "",
        "## Concept and Innovation",
        "",
        "The core concept is to represent TNBC under therapy as a changing mixture of four interpretable cell-state compartments: chemo-sensitive epithelial-like cells, hybrid plastic cells, mesenchymal-resistant cells, and drug-tolerant persister cells. Rather than using a black-box pCR predictor alone, the project links model outputs to biological axes that clinicians and researchers can inspect: EMT state, hypoxia, AXL/TAM signaling, TGF-beta, YAP/TAZ, immune/stromal context, and persister niche signals.",
        "",
        "Novel elements include longitudinal transition-prior calibration from paired pre/post-NAC TNBC samples, separation of tumor-cell persister and niche persister layers, platform-aware external validation, and explicit clinician-versus-research reporting boundaries.",
        "",
        "## Methods Summary",
        "",
        "Public GEO TNBC NAC cohorts were downloaded and parsed into standardized metadata, response labels, and gene-expression signature tables. EMT, TME, resistance, and digital-twin features were scored using curated gene signatures. Response models used logistic regression pipelines with median imputation, scaling, and class balancing. `GSE43816` paired pre/post-NAC samples were used for longitudinal EMT-shift analysis and transition-prior calibration. `GSE43502` residual chemoresistant samples were used for recurrence-axis analysis with bootstrap intervals. `GSE164715` persister single-cell data were species-filtered, scored, targeted-annotated, and reviewed for ambiguous compartments. `GSE163882` was used as a held-out RNA-seq TPM validation cohort with raw, percentile, z-score, and quantile calibration sensitivity analyses.",
        "",
        "## Response-Label Curation",
        "",
        "The original broad endpoint was `pcr_or_good_response` versus `residual_or_poor_response`. A curation pass identified rows in `GSE25055` and `GSE25065` where the pathology field indicated residual disease despite the broad good-response label. These rows were conservatively recoded to residual disease for the locked curated composite sensitivity analysis. Unknown response labels remain excluded.",
        "",
        "Curated model best combined metric:",
        "",
        best_metric(curated),
        "",
        "## Main External Validation",
        "",
        "`GSE163882_TNBC_TPM` provides the primary independent RNA-seq TPM validation layer. Because internal training cohorts are mostly array-derived, cross-platform performance is interpreted cautiously and calibration modes are reported separately.",
        "",
        "Best external combined metric:",
        "",
        best_metric(external, "GSE163882"),
        "",
        "Bootstrap robustness preview:",
        "",
        section_table(bootstrap[bootstrap.get("feature_set", pd.Series(dtype=str)).eq("combined")] if not bootstrap.empty and "feature_set" in bootstrap.columns else bootstrap, 6),
        "",
        "## Additional Independent Cohort Checks",
        "",
        "Leave-dataset-out validation was added for small TNBC NAC cohorts, especially `GSE18864` and `GSE45898`, by excluding the held-out cohort from training before testing on it. These checks are valuable as independent sensitivity analyses but are underpowered.",
        "",
        section_table(lodo, 12),
        "",
        "## Longitudinal Therapy-Induced EMT Plasticity",
        "",
        "`GSE43816` contains seven paired TNBC pre/post-NAC cases. It is used to study state shifts rather than pCR prediction because parsed response labels are unavailable. The analysis supports therapy-induced heterogeneity: some patients show decreased EMT after NAC, while others show increased hybrid/persister or therapy-selection-pressure features.",
        "",
        "Transition-prior calibration preview:",
        "",
        section_table(transition, 10),
        "",
        "## Residual Disease and Recurrence-Axis Biology",
        "",
        "`GSE43502` residual chemoresistant TNBC samples were used to rank recurrence-associated EMT/TME/persister axes. These results remain hypothesis-generating because sample size is limited.",
        "",
        section_table(recurrence, 8),
        "",
        "## Single-Cell Persister and Niche Layer",
        "",
        f"`GSE164715` marker-panel validation passed {marker_pass} targeted direction checks. The single-cell layer supports broad targeted compartments but not a full atlas-level cell-type claim.",
        "",
        "Ambiguity review preview:",
        "",
        section_table(ambiguity[ambiguity.get("review_status", pd.Series(dtype=str)).astype(str).str.contains("ambiguity", na=False)] if not ambiguity.empty and "review_status" in ambiguity.columns else ambiguity, 12),
        "",
        "## Clinical Usefulness",
        "",
        "For clinicians, the current prototype is useful as a research report generator that explains therapy-induced EMT/persister shifts and dominant resistance axes in cohort-relative terms. It may help frame molecular tumor board discussions, identify cases where residual-disease biology is enriched for hypoxia, stromal, immune, or persister features, and communicate uncertainty clearly. It must not be used to choose therapy for an individual patient.",
        "",
        "## Research Usefulness",
        "",
        "For researchers, the project provides a reproducible scaffold for testing EMT plasticity hypotheses, benchmarking response signatures, comparing platform-normalization strategies, integrating single-cell persister biology, and prioritizing future validation cohorts. The frozen release and pipeline runner make it easier to rerun or extend the analysis as new cohorts become available.",
        "",
        "## Limitations",
        "",
        "- Retrospective public cohorts have heterogeneous treatments, platforms, and metadata definitions.",
        "- The response endpoint mixes pCR and good-response concepts unless strict pCR fields are used explicitly.",
        "- Cross-platform validation is encouraging but not definitive.",
        "- Single-cell targeted annotation validates broad compartments, not full cell ontology.",
        "- The therapy simulator visualizes plausible state dynamics but is not a calibrated individual tumor-burden forecast.",
        "",
        "## Conclusion",
        "",
        "The TNBC EMT digital-twin prototype is computationally complete for a research manuscript package. It shows that EMT/TME/persister features can be scored reproducibly, linked to longitudinal therapy-induced state shifts, evaluated in residual-disease biology, and externally validated with platform-aware caution. The next step is expert sign-off and manuscript refinement, not clinical deployment.",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Build a manuscript/thesis draft for the TNBC EMT digital-twin project.")
    p.add_argument("--processed-dir", default="data/processed/tnbc_digital_twin")
    p.add_argument("--docs-dir", default="docs/tnbc_digital_twin_emt_plasticity")
    return p


def main() -> None:
    args = parser().parse_args()
    processed = ROOT / args.processed_dir
    docs = ROOT / args.docs_dir
    docs.mkdir(parents=True, exist_ok=True)
    out_path = docs / "manuscript_draft_tnbc_emt_digital_twin.md"
    write_draft(processed, docs, out_path)
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
