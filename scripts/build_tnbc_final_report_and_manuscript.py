from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


REFERENCES = [
    {
        "id": "CTNeoBC",
        "title": "Pathological complete response and long-term clinical benefit in breast cancer: the CTNeoBC pooled analysis",
        "url": "https://pubmed.ncbi.nlm.nih.gov/24529560/",
        "use": "pCR is most prognostic in aggressive subtypes including TNBC, but trial-level pCR improvement is not a complete surrogate for survival.",
    },
    {
        "id": "RCB_Yau_2022",
        "title": "Residual cancer burden after neoadjuvant chemotherapy and long-term survival outcomes in breast cancer",
        "url": "https://pubmed.ncbi.nlm.nih.gov/34902335/",
        "use": "Residual cancer burden is a strong long-term prognostic framework after neoadjuvant therapy.",
    },
    {
        "id": "KEYNOTE522_OS",
        "title": "Overall survival with pembrolizumab in early-stage triple-negative breast cancer",
        "url": "https://pubmed.ncbi.nlm.nih.gov/39282906/",
        "use": "Modern TNBC NAC includes chemo-immunotherapy and shows survival gains, increasing the need for interpretable residual-risk biology.",
    },
    {
        "id": "EMP_Review",
        "title": "Update on epithelial-mesenchymal plasticity in cancer progression",
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC10872224/",
        "use": "EMP is a spectrum of reversible states tied to progression, metastasis, and therapy resistance.",
    },
    {
        "id": "GSE164715_GEO",
        "title": "GSE164715: single-cell persister/residual TNBC models",
        "url": "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE164715",
        "use": "Source dataset for single-cell persister and residual disease biology.",
    },
    {
        "id": "DTP_2025",
        "title": "Drug-tolerant persister cells in cancer: bridging the gaps between biology and clinical opportunity",
        "url": "https://www.nature.com/articles/s41467-025-66376-6",
        "use": "Drug-tolerant persisters are reversible, non-genetic survivor states that can seed relapse.",
    },
    {
        "id": "DT_Health_Review",
        "title": "Digital twins for health: a scoping review",
        "url": "https://www.nature.com/articles/s41746-024-01073-0",
        "use": "Digital twins connect patient-specific data with simulation and prediction to support decision processes.",
    },
    {
        "id": "DT_Oncology_Review",
        "title": "Exploring the potential of digital twins in cancer treatment",
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC12111985/",
        "use": "Oncology digital twins are promising but need validation, transparency, and careful governance.",
    },
    {
        "id": "Explainable_DT_MM",
        "title": "A digital twin model for evidence-based clinical decision support in multiple myeloma treatment",
        "url": "https://www.frontiersin.org/journals/digital-health/articles/10.3389/fdgth.2023.1324453/full",
        "use": "Example of explainable, evidence-linked oncology digital twin architecture.",
    },
    {
        "id": "Residual_TNBC_Relapse",
        "title": "Predictive factors for relapse in TNBC patients without pCR after neoadjuvant chemotherapy",
        "url": "https://www.frontiersin.org/journals/oncology/articles/10.3389/fonc.2022.1016295/full",
        "use": "Residual TNBC after NAC remains a clinically urgent relapse-risk setting.",
    },
]


def read_table(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    return pd.read_csv(path, sep="\t")


def md_table(df: pd.DataFrame, cols: list[str] | None = None, n: int | None = None) -> str:
    if df.empty:
        return "No table available."
    out = df.copy()
    if cols:
        out = out[[col for col in cols if col in out.columns]]
    if n:
        out = out.head(n)
    out = out.where(pd.notna(out), "NA")
    return out.to_markdown(index=False)


def best_row(metrics: pd.DataFrame, feature_set: str = "combined", dataset: str | None = None) -> pd.Series | None:
    if metrics.empty:
        return None
    df = metrics.copy()
    if feature_set and "feature_set" in df.columns:
        df = df[df["feature_set"] == feature_set]
    if dataset and "test_dataset" in df.columns:
        df = df[df["test_dataset"].astype(str).str.contains(dataset, na=False)]
    if df.empty:
        return None
    df["auroc"] = pd.to_numeric(df.get("auroc", pd.Series(dtype=float)), errors="coerce")
    return df.sort_values("auroc", ascending=False).iloc[0]


def metric_sentence(row: pd.Series | None) -> str:
    if row is None:
        return "No metric row available."
    bits = []
    for col, label in [
        ("test_dataset", "test dataset"),
        ("calibration_method", "calibration"),
        ("feature_set", "feature set"),
        ("samples", "n"),
        ("accuracy", "accuracy"),
        ("auroc", "AUROC"),
        ("auprc", "AUPRC"),
        ("brier", "Brier"),
    ]:
        if col in row.index and pd.notna(row[col]):
            value = row[col]
            if col == "samples":
                value = str(int(float(value)))
            elif isinstance(value, float):
                value = f"{value:.3f}"
            bits.append(f"{label}={value}")
    return ", ".join(bits) + "."


def reference_list() -> str:
    lines = []
    for ref in REFERENCES:
        lines.append(f"- [{ref['id']}] [{ref['title']}]({ref['url']}). Relevance: {ref['use']}")
    return "\n".join(lines)


def write_project_report(processed: Path, docs: Path) -> Path:
    external = read_table(processed / "external_validation" / "gse163882" / "external_validation_metrics.tsv")
    curated = read_table(processed / "response_label_curation" / "curated_model" / "tnbc_nac_response_model_metrics.tsv")
    lodo = read_table(processed / "leave_dataset_out_validation" / "tnbc_leave_dataset_out_metrics.tsv")
    bootstrap = read_table(processed / "response_model_robustness" / "gse163882_external_metric_bootstrap_intervals.tsv")
    label_curation = read_table(processed / "response_label_curation" / "tnbc_response_label_curation_table.tsv")
    ambiguity = read_table(processed / "gse164715_ambiguity_review" / "gse164715_sample_stage_ambiguity_review.tsv")
    marker = read_table(processed / "gse164715_marker_validation" / "gse164715_marker_panel_direction_checks.tsv")
    stage = read_table(processed / "gse164715_targeted_annotation" / "gse164715_targeted_annotation_stage_summary.tsv")

    curation_summary = pd.DataFrame()
    if not label_curation.empty:
        curation_summary = (
            label_curation.groupby(["dataset_id", "locked_composite_response", "curation_decision"], dropna=False)
            .size()
            .reset_index(name="samples")
            .sort_values(["dataset_id", "locked_composite_response", "curation_decision"])
        )
        curation_summary["locked_composite_response"] = curation_summary["locked_composite_response"].fillna("excluded_or_blank")
    marker_pass = "NA"
    if not marker.empty and "passes_direction_check" in marker.columns:
        marker_pass = f"{marker['passes_direction_check'].astype(str).str.lower().eq('true').sum()} of {len(marker)}"

    lines = [
        "# Detailed Project Report",
        "",
        "## Project Title",
        "",
        "Digital Twin of EMT Plasticity Under Therapy in Triple-Negative Breast Cancer During Neoadjuvant Chemotherapy",
        "",
        "## Executive Summary",
        "",
        "This project built a reproducible research prototype that translates public TNBC neoadjuvant chemotherapy transcriptomic data into an interpretable digital twin of epithelial-mesenchymal plasticity. The model does not attempt to replace clinical judgment. Its purpose is to expose the biological structure behind response and residual disease: epithelial sensitivity, hybrid plasticity, mesenchymal resistance, drug-tolerant persister programs, and stromal/endothelial/immune niche context.",
        "",
        "The project is now computationally finalized for a research manuscript or thesis chapter. Remaining work is expert review and writing polish, especially response-label curation sign-off and single-cell ambiguity wording.",
        "",
        "## Why This Project Matters",
        "",
        "TNBC is clinically urgent because patients who do not achieve pCR after NAC remain at high risk of relapse. Modern regimens such as chemo-immunotherapy have improved outcomes, but residual disease remains a difficult biological and clinical problem. A simple pCR classifier can say whether a tumor appears more or less likely to respond, but it does not explain the route by which a tumor survives. This project asks a different question: what therapy-tolerant state is the tumor moving toward?",
        "",
        "The clinical value is interpretability. The research value is a reproducible scaffold for testing EMT, persister, and niche hypotheses across bulk and single-cell cohorts.",
        "",
        "## Biological Concept",
        "",
        "The digital twin represents the tumor as a four-state system:",
        "",
        "- E: epithelial-like, relatively chemo-sensitive state.",
        "- H: hybrid epithelial/mesenchymal state, plastic and transitional.",
        "- M: mesenchymal-like resistant state.",
        "- P: drug-tolerant persister state.",
        "",
        "The creative leap is to treat NAC not just as a binary selection event but as a state-space pressure. A tumor can shrink while leaving behind a more dangerous state mixture. A patient can have reduced epithelial tumor burden but enriched persister or resistant fractions. This is the biological idea the digital twin makes visible.",
        "",
        "## Literature Grounding",
        "",
        reference_list(),
        "",
        "## Data Resources Integrated",
        "",
        "- Response-labeled TNBC NAC cohorts: GSE18864, GSE25055, GSE25065, GSE45898, and GSE163882.",
        "- Longitudinal pre/post-NAC EMT-shift cohort: GSE43816.",
        "- Residual chemoresistant recurrence-axis cohort: GSE43502.",
        "- Single-cell persister/residual biology layer: GSE164715.",
        "- Reproducible config: `configs/tnbc_digital_twin.yml`.",
        "",
        "## Work Completed",
        "",
        "1. Built metadata parsing and response-label standardization for public TNBC NAC cohorts.",
        "2. Built EMT, TME, resistance, and persister signature scoring.",
        "3. Built four-state E/H/M/P digital-twin feature extraction.",
        "4. Trained baseline response models and generated same-platform reports.",
        "5. Completed paired longitudinal EMT-shift analysis in GSE43816.",
        "6. Calibrated transition priors from GSE43816 state shifts.",
        "7. Built calibrated therapy simulations with uncertainty bands.",
        "8. Analyzed GSE43502 residual recurrence-axis biology with bootstrap intervals.",
        "9. Imported, species-filtered, scored, and annotated GSE164715 single-cell persister data.",
        "10. Validated GSE164715 broad targeted annotations with marker-panel direction checks.",
        "11. Added GSE163882 as an independent RNA-seq TPM external validation cohort.",
        "12. Added cross-platform calibration diagnostics and sensitivity modes.",
        "13. Curated response-label conflicts and created a locked curated sensitivity table.",
        "14. Added leave-dataset-out validation for GSE18864 and GSE45898.",
        "15. Built final validation memo, manuscript bundle, manuscript draft, and frozen release.",
        "",
        "## Main Quantitative Results",
        "",
        "### Primary External Validation",
        "",
        metric_sentence(best_row(external, "combined", "GSE163882")),
        "",
        "Bootstrap robustness for the best combined GSE163882 configuration:",
        "",
        md_table(bootstrap[bootstrap.get("feature_set", pd.Series(dtype=str)).eq("combined")] if not bootstrap.empty and "feature_set" in bootstrap.columns else bootstrap, n=6),
        "",
        "### Curated-Label Sensitivity",
        "",
        metric_sentence(best_row(curated, "combined", "GSE25065")),
        "",
        md_table(curated, n=10),
        "",
        "### Additional Leave-Dataset-Out Validation",
        "",
        "These cohorts are small, so they are interpreted as sensitivity checks rather than decisive external validation.",
        "",
        md_table(lodo[lodo.get("feature_set", pd.Series(dtype=str)).eq("combined")] if not lodo.empty and "feature_set" in lodo.columns else lodo, n=12),
        "",
        "### Response-Label Curation",
        "",
        "The most important curation decision was to separate broad good-response labels from strict residual disease evidence. Rows in GSE25055 and GSE25065 with pathology evidence of residual disease were conservatively recoded for the curated sensitivity analysis.",
        "",
        md_table(curation_summary, n=24),
        "",
        "### Single-Cell Persister and Niche Review",
        "",
        f"Marker-panel direction checks passed {marker_pass}.",
        "",
        "GSE164715 targeted annotation scale:",
        "",
        md_table(stage, n=20),
        "",
        "Ambiguous compartment review:",
        "",
        md_table(ambiguity[ambiguity.get("review_status", pd.Series(dtype=str)).astype(str).str.contains("ambiguity", na=False)] if not ambiguity.empty and "review_status" in ambiguity.columns else ambiguity, n=12),
        "",
        "## How This Helps Clinicians",
        "",
        "For clinicians, this project is not a treatment recommendation engine. Its value is in making residual-risk biology easier to inspect. A clinician-facing report can show whether a sample appears epithelial-sensitive, hybrid-plastic, mesenchymal-resistant, persister-enriched, hypoxic, stromal-supported, or immune-inflamed. That can support research tumor board discussion, trial hypothesis generation, and communication of uncertainty.",
        "",
        "Potential clinician-facing uses after prospective validation:",
        "",
        "- Explain why two TNBC tumors with similar clinical stage may have different residual-risk biology.",
        "- Identify post-NAC samples where residual disease appears driven by hypoxia, AXL/TAM, YAP/TAZ, stromal niche, or persister stress tolerance.",
        "- Provide cohort-relative percentiles instead of opaque scores.",
        "- Generate transparent caveated reports for molecular review.",
        "- Help prioritize biospecimens for deeper profiling, such as spatial transcriptomics or single-cell analysis.",
        "",
        "## How This Helps Researchers",
        "",
        "For researchers, the project is a reusable experimental scaffold. It links bulk response cohorts, paired longitudinal samples, residual recurrence biology, and single-cell persister biology in one reproducible workflow.",
        "",
        "Research uses:",
        "",
        "- Test EMT plasticity hypotheses across public TNBC NAC datasets.",
        "- Compare response predictors under original versus curated endpoint definitions.",
        "- Study platform sensitivity between array-derived cohorts and RNA-seq TPM cohorts.",
        "- Explore whether persister tumor-cell programs and niche programs should be modeled separately.",
        "- Prioritize future validation cohorts and prospective sample collection designs.",
        "",
        "## Creative Future Directions",
        "",
        "1. Time-lapse digital twin: add early on-treatment biopsies to model velocity, not only baseline state.",
        "2. Spatial digital twin: combine EMT state with tumor-stroma distance, vascular proximity, and immune exclusion.",
        "3. Perturbation twin: simulate how blocking AXL/TAM, TGF-beta, YAP/TAZ, hypoxia, or ferroptosis resistance changes P-state persistence.",
        "4. Trial-enrichment twin: identify molecularly coherent residual-disease groups for post-NAC trials.",
        "5. Patient explant twin: calibrate state transitions with organoid or PDX drug response assays.",
        "6. Uncertainty-first reporting: show confidence, platform shift, cohort percentile, and label ambiguity before any score interpretation.",
        "",
        "## Risks and Limitations",
        "",
        "- Retrospective metadata are imperfect and response definitions differ across cohorts.",
        "- Cross-platform validation is encouraging but modest.",
        "- GSE18864 and GSE45898 holdout cohorts are small.",
        "- GSE164715 supports broad targeted compartments, not definitive cell ontology.",
        "- The therapy simulator is mechanistic and illustrative, not a calibrated individual tumor-burden forecast.",
        "- Clinical use would require prospective validation, locked assays, calibrated thresholds, regulatory review, and clinician usability testing.",
        "",
        "## Final Status",
        "",
        "Computational work is complete for a research-prototype manuscript. The next step is expert review, citation formatting, figure/table numbering, and target-journal or thesis formatting.",
    ]
    out = docs / "final_project_report_tnbc_emt_digital_twin.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def write_manuscript(processed: Path, docs: Path) -> Path:
    external = read_table(processed / "external_validation" / "gse163882" / "external_validation_metrics.tsv")
    curated = read_table(processed / "response_label_curation" / "curated_model" / "tnbc_nac_response_model_metrics.tsv")
    lodo = read_table(processed / "leave_dataset_out_validation" / "tnbc_leave_dataset_out_metrics.tsv")
    recurrence = read_table(processed / "residual_persister_biology" / "gse43502_recurrence_feature_summary.tsv")
    ambiguity = read_table(processed / "gse164715_ambiguity_review" / "gse164715_sample_stage_ambiguity_review.tsv")
    marker = read_table(processed / "gse164715_marker_validation" / "gse164715_marker_panel_direction_checks.tsv")
    transition = read_table(processed / "transition_calibration" / "gse43816_calibrated_transition_parameters.tsv")
    marker_pass = "NA"
    if not marker.empty and "passes_direction_check" in marker.columns:
        marker_pass = f"{marker['passes_direction_check'].astype(str).str.lower().eq('true').sum()}/{len(marker)}"

    lines = [
        "# Manuscript Draft",
        "",
        "## Title",
        "",
        "A Research Digital Twin of EMT Plasticity and Drug-Tolerant Persister Biology in Triple-Negative Breast Cancer Under Neoadjuvant Chemotherapy",
        "",
        "## Short Title",
        "",
        "TNBC EMT Plasticity Digital Twin",
        "",
        "## Abstract",
        "",
        "Background: Triple-negative breast cancer (TNBC) treated with neoadjuvant chemotherapy (NAC) shows heterogeneous response. Pathologic complete response is associated with improved outcomes, but residual disease remains a major clinical problem. Biological interpretation is difficult because resistant disease is not a single state; it may involve epithelial-mesenchymal plasticity, stromal and immune context, hypoxia, and drug-tolerant persister programs.",
        "",
        "Objective: To build a reproducible research digital twin that models therapy-associated EMT plasticity in TNBC using public bulk and single-cell transcriptomic cohorts.",
        "",
        "Methods: Public TNBC NAC datasets were parsed into standardized metadata, response labels, gene-expression signatures, and digital-twin state features. The model represented tumor biology as epithelial-like, hybrid epithelial/mesenchymal, mesenchymal-like, and persister-like compartments. Analyses included baseline response modeling, response-label curation, GSE43816 paired pre/post-NAC EMT-shift analysis, transition-prior calibration, GSE43502 residual recurrence-axis analysis, GSE164715 single-cell persister/niche annotation, GSE163882 external RNA-seq TPM validation, platform-normalization diagnostics, bootstrap uncertainty, and leave-dataset-out sensitivity validation.",
        "",
        f"Results: In the primary external GSE163882 validation cohort, the best combined configuration achieved {metric_sentence(best_row(external, 'combined', 'GSE163882'))} Curated-label sensitivity improved the GSE25055-to-GSE25065 train-test result for TME/resistance and combined feature sets, with the combined model achieving {metric_sentence(best_row(curated, 'combined', 'GSE25065'))} GSE164715 marker-panel validation passed {marker_pass} targeted direction checks. Leave-dataset-out validation in GSE18864 and GSE45898 provided small-cohort sensitivity evidence but remained underpowered.",
        "",
        "Conclusion: The TNBC EMT digital twin supports a research-prototype claim: EMT/TME/persister features can be scored reproducibly, linked to therapy-induced state shifts, and externally evaluated with platform-aware caution. The prototype is not a clinical decision tool, but it provides a transparent framework for studying residual-disease biology and designing prospective validation.",
        "",
        "## Keywords",
        "",
        "Triple-negative breast cancer; neoadjuvant chemotherapy; epithelial-mesenchymal transition; epithelial-mesenchymal plasticity; digital twin; drug-tolerant persister; residual disease; transcriptomics; single-cell RNA-seq.",
        "",
        "## Introduction",
        "",
        "TNBC is a high-risk breast cancer subtype in which NAC is both therapeutic and informative. Patients who achieve pCR generally have better outcomes, while patients with residual disease remain vulnerable to relapse. However, pCR is a clinical endpoint, not a mechanistic explanation. It tells us whether visible invasive disease remains after treatment, but not which molecular survival strategy allowed tumor cells to persist.",
        "",
        "A central problem in TNBC is that residual disease is biologically plural. One residual tumor may be hypoxic and stromal-supported; another may show immune escape; another may contain hybrid epithelial/mesenchymal cells poised between proliferation and invasion; another may contain drug-tolerant persister states that survive by reversible non-genetic adaptation. EMT is therefore better treated as epithelial-mesenchymal plasticity, a spectrum of dynamic states rather than a binary switch.",
        "",
        "Digital twins offer a conceptual bridge between molecular measurement and dynamic clinical reasoning. In this project, the twin is deliberately modest: it is not a bedside prescriber. It is a transparent state model that turns transcriptomic measurements into interpretable compartments, transition priors, uncertainty bands, and research reports.",
        "",
        "## Hypothesis",
        "",
        "We hypothesized that a TNBC NAC digital twin based on EMT plasticity and persister biology could do three useful things: first, summarize baseline and residual response biology more transparently than a black-box classifier; second, model therapy-induced shifts in state composition; and third, expose which components of response prediction remain stable or fragile across platforms and cohorts.",
        "",
        "## Study Design",
        "",
        "The project used a multi-layer retrospective public-data design. Bulk response cohorts were used to train and test response-associated features. GSE43816 paired samples were used for longitudinal state-shift analysis and transition-prior calibration. GSE43502 residual chemoresistant TNBC samples were used to examine recurrence-associated resistance axes. GSE164715 single-cell data were used to refine persister and niche layers. GSE163882 was used as the primary held-out external RNA-seq TPM validation cohort.",
        "",
        "## Digital-Twin Architecture",
        "",
        "The model uses four state compartments: E, H, M, and P. E denotes epithelial-like chemo-sensitive biology. H denotes hybrid epithelial/mesenchymal plasticity. M denotes mesenchymal-like resistance. P denotes drug-tolerant persister biology. Each bulk sample is projected into these compartments using signature-derived scores, and each score is accompanied by resistance-axis features including AXL/TAM, TGF-beta, YAP/TAZ, hypoxia, immune/stromal context, and refined persister tumor/niche layers.",
        "",
        "The model is intentionally explainable. Every feature is tied to a gene signature, every response label is auditable, every validation result is separated by cohort and platform, and every clinician-style statement is constrained by caveats.",
        "",
        "## Methods",
        "",
        "### Data Acquisition and Harmonization",
        "",
        "GEO series matrices and supplementary files were collected for TNBC NAC and residual-disease cohorts. Sample metadata were standardized into dataset identifiers, sample identifiers, TNBC-likely labels, timepoints, and response labels. Where response labels were unavailable or ambiguous, samples were excluded from response modeling but could still contribute to biological interpretation if appropriate.",
        "",
        "### Signature Scoring",
        "",
        "Gene-expression matrices were mapped to compact signature gene tables. Signature blocks included epithelial markers, mesenchymal markers, EMT transcription factors, hybrid plasticity markers, AXL/TAM, TGF-beta, YAP/TAZ, hypoxia, stemness/persister, refined tumor-cell persister, stress-tolerance persister, and persister-niche genes.",
        "",
        "### Response Modeling",
        "",
        "Response models used logistic regression with median imputation, standard scaling, and class balancing. Feature sets included EMT core, EMT plus TME/resistance, digital-twin features, and combined features. The positive class was residual or poor response.",
        "",
        "### Response-Label Curation",
        "",
        "A dedicated curation layer separated the original broad pCR/good-response endpoint from stricter residual-disease evidence. Rows in GSE25055 and GSE25065 with pathology evidence of residual disease were conservatively recoded to residual/poor response in the curated sensitivity table. Unknown labels were excluded. This preserved the original endpoint for comparison while preventing a good-response bucket from being interpreted as strict pCR.",
        "",
        "### Longitudinal State-Shift and Transition Calibration",
        "",
        "GSE43816 paired pre/post-NAC TNBC samples were used to measure therapy-induced shifts and calibrate first transition priors between E/H/M/P states. These priors were then used in the therapy simulator to create uncertainty bands and final-state summaries.",
        "",
        "### Single-Cell Persister Layer",
        "",
        "GSE164715 single-cell matrices were imported, species-filtered, and scored. Human-dominant cells were assigned targeted broad annotations: malignant-like, endothelial-like, stromal-like, immune-like, or ambiguous human. Marker-panel validation assessed whether broad annotations had expected directional scores. An ambiguity review separated interpretable targeted compartments from unresolved human-dominant clusters.",
        "",
        "### External and Sensitivity Validation",
        "",
        "GSE163882 was prepared as a held-out TNBC RNA-seq TPM validation cohort. Because the internal cohorts were mostly array-derived, validation was reported under raw, internal-percentile, external-z-score, and external-quantile calibration modes. Leave-dataset-out validation was added for GSE18864 and GSE45898 by training on all other response-labeled cohorts and testing on the held-out dataset.",
        "",
        "## Results",
        "",
        "### External Validation on GSE163882",
        "",
        "The combined feature set performed best in the main external validation setting, but performance was moderate and platform-sensitive.",
        "",
        md_table(external[external.get("feature_set", pd.Series(dtype=str)).eq("combined")] if not external.empty and "feature_set" in external.columns else external, n=8),
        "",
        "The strongest result by AUROC was the combined external quantile-to-internal calibration configuration. The raw combined configuration had very similar AUROC and slightly higher AUPRC, supporting the decision to report calibration as sensitivity rather than as a definitive correction.",
        "",
        "### Curated-Label Sensitivity",
        "",
        "Curating pathology-conflict rows shifted the response balance toward residual disease and improved the discovery-to-validation result for TME/resistance features.",
        "",
        md_table(curated, n=10),
        "",
        "### Leave-Dataset-Out Validation",
        "",
        "GSE18864 and GSE45898 were held out as small independent same-project cohorts. Their results were variable, as expected from sample sizes of 24 and 10, respectively.",
        "",
        md_table(lodo[lodo.get("feature_set", pd.Series(dtype=str)).eq("combined")] if not lodo.empty and "feature_set" in lodo.columns else lodo, n=12),
        "",
        "### Longitudinal EMT Plasticity and Transition Priors",
        "",
        "GSE43816 showed that NAC-associated state shifts are heterogeneous. Mean EMT score decreased after therapy, but several paired samples showed increased hybrid/persister or therapy-selection-pressure features. This supports the central premise that residual biology is not captured by a single scalar response label.",
        "",
        md_table(transition, n=5),
        "",
        "### Residual Recurrence-Axis Biology",
        "",
        "In GSE43502 residual chemoresistant TNBC, AXL/TAM and hypoxia showed positive recurrence-associated shifts with wide intervals. These findings are hypothesis-generating and should guide future validation rather than direct clinical interpretation.",
        "",
        md_table(recurrence, n=8),
        "",
        "### Single-Cell Persister and Niche Biology",
        "",
        f"GSE164715 marker-panel validation passed {marker_pass} direction checks. However, ambiguity review identified unresolved human-dominant compartments, especially cluster_1 and high-ambiguity HBCx172 sample-stage rows. The single-cell analysis therefore supports broad targeted annotation, not definitive cell ontology.",
        "",
        md_table(ambiguity[ambiguity.get("review_status", pd.Series(dtype=str)).astype(str).str.contains("ambiguity", na=False)] if not ambiguity.empty and "review_status" in ambiguity.columns else ambiguity, n=10),
        "",
        "## Discussion",
        "",
        "This project shows that a digital twin does not need to begin as a clinically autonomous predictor. A useful first-generation oncology twin can be an interpretive state machine: a system that translates measurements into biologically meaningful compartments, identifies fragile assumptions, and makes uncertainty visible.",
        "",
        "The most important scientific observation is that the combined EMT/TME/persister feature space performed better than EMT core features alone in external validation. That does not prove clinical utility, but it supports the biological idea that residual TNBC risk is not only an EMT problem. It is an ecosystem problem involving tumor-cell state, stress adaptation, vascular/stromal niche, immune context, and platform-dependent measurement effects.",
        "",
        "The curated-label analysis also matters. When broad pCR/good-response labels were confronted with pathology evidence of residual disease, the endpoint changed. This is not a nuisance detail; it is part of the biology-to-clinic translation problem. A model trained on an endpoint that mixes RCB-0/I with strict pCR may be useful for good-response biology but should not be described as a strict pCR model.",
        "",
        "The single-cell analysis adds another important caution. Marker panels supported broad targeted compartments, but a large ambiguous human cluster remained unresolved. A mature digital twin should not force every cell into a confident label. Instead, ambiguity should become part of the report.",
        "",
        "## Importance for Clinicians",
        "",
        "Clinicians need models that explain, not only predict. This project could eventually help clinicians interpret why a residual TNBC sample appears dangerous: is the dominant signal hypoxia, AXL/TAM, YAP/TAZ, stromal support, immune context, or persister stress tolerance? That kind of report could support molecular tumor board discussion, trial matching research, and post-NAC residual-disease hypothesis generation. In its current form, however, it is not a treatment-selection tool.",
        "",
        "## Importance for Researchers",
        "",
        "Researchers gain a reproducible framework for joining several normally separate evidence layers: public response cohorts, longitudinal therapy-shift data, residual recurrence biology, and single-cell persister/niche evidence. The pipeline makes it possible to test new signatures, add new cohorts, compare calibration methods, and evaluate whether future interventions should target tumor-intrinsic persisters, niche-protected cells, or both.",
        "",
        "## Creative Translation Roadmap",
        "",
        "A future version could become a multi-modal residual-disease twin. It would ingest baseline biopsy, early on-treatment biopsy, surgery specimen, spatial transcriptomics, pathology RCB features, imaging response, ctDNA, and organoid perturbation data. It would output not one score but a patient-specific map: state fractions, transition velocity, uncertainty, resistant axes, suggested research assays, and trial hypotheses. The most creative and clinically useful version would treat uncertainty as a first-class result.",
        "",
        "## Limitations",
        "",
        "The study is retrospective and public-data based. Treatments, platforms, and response definitions differ across cohorts. External validation is moderate and platform-sensitive. Small holdout cohorts are underpowered. Single-cell targeted annotation does not equal a full atlas. The simulator is not a patient-specific tumor burden forecast. All clinical interpretations require prospective validation.",
        "",
        "## Conclusion",
        "",
        "The project provides a completed research-prototype digital twin for TNBC EMT plasticity under NAC. It is transparent, reproducible, biologically interpretable, and honest about uncertainty. Its strongest immediate role is not clinical decision-making but research translation: organizing residual-disease biology into a state-based framework that clinicians can understand and researchers can extend.",
        "",
        "## References and Resources",
        "",
        reference_list(),
    ]
    out = docs / "manuscript_full_draft_tnbc_emt_digital_twin.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Build detailed final report and manuscript for TNBC EMT digital-twin project.")
    p.add_argument("--processed-dir", default="data/processed/tnbc_digital_twin")
    p.add_argument("--docs-dir", default="docs/tnbc_digital_twin_emt_plasticity")
    return p


def main() -> None:
    args = parser().parse_args()
    processed = ROOT / args.processed_dir
    docs = ROOT / args.docs_dir
    docs.mkdir(parents=True, exist_ok=True)
    report = write_project_report(processed, docs)
    manuscript = write_manuscript(processed, docs)
    print(f"wrote {report}")
    print(f"wrote {manuscript}")


if __name__ == "__main__":
    main()
