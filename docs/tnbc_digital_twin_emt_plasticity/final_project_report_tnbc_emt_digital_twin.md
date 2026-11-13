# Detailed Project Report

## Project Title

Digital Twin of EMT Plasticity Under Therapy in Triple-Negative Breast Cancer During Neoadjuvant Chemotherapy

## Executive Summary

This project built a reproducible research prototype that translates public TNBC neoadjuvant chemotherapy transcriptomic data into an interpretable digital twin of epithelial-mesenchymal plasticity. The model does not attempt to replace clinical judgment. Its purpose is to expose the biological structure behind response and residual disease: epithelial sensitivity, hybrid plasticity, mesenchymal resistance, drug-tolerant persister programs, and stromal/endothelial/immune niche context.

The project is now computationally finalized for a research manuscript or thesis chapter. Remaining work is expert review and writing polish, especially response-label curation sign-off and single-cell ambiguity wording.

## Why This Project Matters

TNBC is clinically urgent because patients who do not achieve pCR after NAC remain at high risk of relapse. Modern regimens such as chemo-immunotherapy have improved outcomes, but residual disease remains a difficult biological and clinical problem. A simple pCR classifier can say whether a tumor appears more or less likely to respond, but it does not explain the route by which a tumor survives. This project asks a different question: what therapy-tolerant state is the tumor moving toward?

The clinical value is interpretability. The research value is a reproducible scaffold for testing EMT, persister, and niche hypotheses across bulk and single-cell cohorts.

## Biological Concept

The digital twin represents the tumor as a four-state system:

- E: epithelial-like, relatively chemo-sensitive state.
- H: hybrid epithelial/mesenchymal state, plastic and transitional.
- M: mesenchymal-like resistant state.
- P: drug-tolerant persister state.

The creative leap is to treat NAC not just as a binary selection event but as a state-space pressure. A tumor can shrink while leaving behind a more dangerous state mixture. A patient can have reduced epithelial tumor burden but enriched persister or resistant fractions. This is the biological idea the digital twin makes visible.

## Literature Grounding

- [CTNeoBC] [Pathological complete response and long-term clinical benefit in breast cancer: the CTNeoBC pooled analysis](https://pubmed.ncbi.nlm.nih.gov/24529560/). Relevance: pCR is most prognostic in aggressive subtypes including TNBC, but trial-level pCR improvement is not a complete surrogate for survival.
- [RCB_Yau_2022] [Residual cancer burden after neoadjuvant chemotherapy and long-term survival outcomes in breast cancer](https://pubmed.ncbi.nlm.nih.gov/34902335/). Relevance: Residual cancer burden is a strong long-term prognostic framework after neoadjuvant therapy.
- [KEYNOTE522_OS] [Overall survival with pembrolizumab in early-stage triple-negative breast cancer](https://pubmed.ncbi.nlm.nih.gov/39282906/). Relevance: Modern TNBC NAC includes chemo-immunotherapy and shows survival gains, increasing the need for interpretable residual-risk biology.
- [EMP_Review] [Update on epithelial-mesenchymal plasticity in cancer progression](https://pmc.ncbi.nlm.nih.gov/articles/PMC10872224/). Relevance: EMP is a spectrum of reversible states tied to progression, metastasis, and therapy resistance.
- [GSE164715_GEO] [GSE164715: single-cell persister/residual TNBC models](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE164715). Relevance: Source dataset for single-cell persister and residual disease biology.
- [DTP_2025] [Drug-tolerant persister cells in cancer: bridging the gaps between biology and clinical opportunity](https://www.nature.com/articles/s41467-025-66376-6). Relevance: Drug-tolerant persisters are reversible, non-genetic survivor states that can seed relapse.
- [DT_Health_Review] [Digital twins for health: a scoping review](https://www.nature.com/articles/s41746-024-01073-0). Relevance: Digital twins connect patient-specific data with simulation and prediction to support decision processes.
- [DT_Oncology_Review] [Exploring the potential of digital twins in cancer treatment](https://pmc.ncbi.nlm.nih.gov/articles/PMC12111985/). Relevance: Oncology digital twins are promising but need validation, transparency, and careful governance.
- [Explainable_DT_MM] [A digital twin model for evidence-based clinical decision support in multiple myeloma treatment](https://www.frontiersin.org/journals/digital-health/articles/10.3389/fdgth.2023.1324453/full). Relevance: Example of explainable, evidence-linked oncology digital twin architecture.
- [Residual_TNBC_Relapse] [Predictive factors for relapse in TNBC patients without pCR after neoadjuvant chemotherapy](https://www.frontiersin.org/journals/oncology/articles/10.3389/fonc.2022.1016295/full). Relevance: Residual TNBC after NAC remains a clinically urgent relapse-risk setting.

## Data Resources Integrated

- Response-labeled TNBC NAC cohorts: GSE18864, GSE25055, GSE25065, GSE45898, and GSE163882.
- Longitudinal pre/post-NAC EMT-shift cohort: GSE43816.
- Residual chemoresistant recurrence-axis cohort: GSE43502.
- Single-cell persister/residual biology layer: GSE164715.
- Reproducible config: `configs/tnbc_digital_twin.yml`.

## Work Completed

1. Built metadata parsing and response-label standardization for public TNBC NAC cohorts.
2. Built EMT, TME, resistance, and persister signature scoring.
3. Built four-state E/H/M/P digital-twin feature extraction.
4. Trained baseline response models and generated same-platform reports.
5. Completed paired longitudinal EMT-shift analysis in GSE43816.
6. Calibrated transition priors from GSE43816 state shifts.
7. Built calibrated therapy simulations with uncertainty bands.
8. Analyzed GSE43502 residual recurrence-axis biology with bootstrap intervals.
9. Imported, species-filtered, scored, and annotated GSE164715 single-cell persister data.
10. Validated GSE164715 broad targeted annotations with marker-panel direction checks.
11. Added GSE163882 as an independent RNA-seq TPM external validation cohort.
12. Added cross-platform calibration diagnostics and sensitivity modes.
13. Curated response-label conflicts and created a locked curated sensitivity table.
14. Added leave-dataset-out validation for GSE18864 and GSE45898.
15. Built final validation memo, manuscript bundle, manuscript draft, and frozen release.

## Main Quantitative Results

### Primary External Validation

test dataset=GSE163882_TNBC_TPM, calibration=external_quantile_to_internal, feature set=combined, n=90, accuracy=0.656, AUROC=0.649, AUPRC=0.714, Brier=0.232.

Bootstrap robustness for the best combined GSE163882 configuration:

| dataset_id         | feature_set   | calibration_method            |   samples |   accuracy_point |   accuracy_q025 |   accuracy_q975 |   brier_point |   brier_q025 |   brier_q975 |   auroc_point |   auroc_q025 |   auroc_q975 |   auprc_point | auprc_q025   | auprc_q975   |
|:-------------------|:--------------|:------------------------------|----------:|-----------------:|----------------:|----------------:|--------------:|-------------:|-------------:|--------------:|-------------:|-------------:|--------------:|:-------------|:-------------|
| GSE163882_TNBC_TPM | combined      | external_quantile_to_internal |        90 |         0.655556 |        0.555556 |        0.722222 |      0.231701 |     0.211334 |     0.259672 |      0.648785 |     0.520594 |     0.728303 |      0.713864 | NA           | NA           |
| GSE163882_TNBC_TPM | combined      | external_zscore_to_internal   |        90 |         0.611111 |        0.510833 |        0.688889 |      0.234608 |     0.210477 |     0.260372 |      0.631579 |     0.513488 |     0.74148  |      0.707764 | NA           | NA           |
| GSE163882_TNBC_TPM | combined      | internal_percentile           |        90 |         0.566667 |        0.4775   |        0.655833 |      0.242155 |     0.207698 |     0.276015 |      0.61083  |     0.515263 |     0.717709 |      0.674309 | NA           | NA           |
| GSE163882_TNBC_TPM | combined      | raw                           |        90 |         0.644444 |        0.533333 |        0.733611 |      0.228155 |     0.193809 |     0.265245 |      0.647773 |     0.516644 |     0.764937 |      0.721259 | NA           | NA           |

### Curated-Label Sensitivity

test dataset=GSE25065, feature set=combined, n=65, accuracy=0.600, AUROC=0.609, AUPRC=0.784, Brier=0.254.

|   samples |   positive_rate |   accuracy |    brier |    auroc |    auprc | evaluation    | feature_set        |   feature_count | train_dataset    | test_dataset     |
|----------:|----------------:|-----------:|---------:|---------:|---------:|:--------------|:-------------------|----------------:|:-----------------|:-----------------|
|       215 |        0.655814 |   0.493023 | 0.253763 | 0.520893 | 0.661287 | stratified_cv | emt_core           |               5 | all_deduplicated | all_deduplicated |
|        65 |        0.630769 |   0.476923 | 0.254095 | 0.50813  | 0.642596 | train_test    | emt_core           |               5 | GSE25055         | GSE25065         |
|       215 |        0.655814 |   0.6      | 0.254164 | 0.579164 | 0.719704 | stratified_cv | emt_tme_resistance |              21 | all_deduplicated | all_deduplicated |
|        65 |        0.630769 |   0.6      | 0.246661 | 0.618902 | 0.803878 | train_test    | emt_tme_resistance |              21 | GSE25055         | GSE25065         |
|       215 |        0.655814 |   0.47907  | 0.25712  | 0.499808 | 0.658888 | stratified_cv | digital_twin       |               9 | all_deduplicated | all_deduplicated |
|        65 |        0.630769 |   0.538462 | 0.248793 | 0.559959 | 0.703621 | train_test    | digital_twin       |               9 | GSE25055         | GSE25065         |
|       215 |        0.655814 |   0.52093  | 0.268817 | 0.524248 | 0.678734 | stratified_cv | combined           |              30 | all_deduplicated | all_deduplicated |
|        65 |        0.630769 |   0.6      | 0.253885 | 0.60874  | 0.783751 | train_test    | combined           |              30 | GSE25055         | GSE25065         |

### Additional Leave-Dataset-Out Validation

These cohorts are small, so they are interpreted as sensitivity checks rather than decisive external validation.

|   samples |   positive_rate |   accuracy |    brier |    auroc |    auprc | evaluation        | calibration_method            | feature_set   |   feature_count | train_dataset       | test_dataset   |
|----------:|----------------:|-----------:|---------:|---------:|---------:|:------------------|:------------------------------|:--------------|----------------:|:--------------------|:---------------|
|        24 |        0.666667 |   0.541667 | 0.328623 | 0.46875  | 0.675871 | leave_dataset_out | raw                           | combined      |              30 | all_except_GSE18864 | GSE18864       |
|        24 |        0.666667 |   0.5      | 0.311176 | 0.53125  | 0.751506 | leave_dataset_out | internal_percentile           | combined      |              30 | all_except_GSE18864 | GSE18864       |
|        24 |        0.666667 |   0.583333 | 0.324632 | 0.453125 | 0.665409 | leave_dataset_out | external_zscore_to_internal   | combined      |              30 | all_except_GSE18864 | GSE18864       |
|        24 |        0.666667 |   0.5      | 0.333075 | 0.4375   | 0.67157  | leave_dataset_out | external_quantile_to_internal | combined      |              30 | all_except_GSE18864 | GSE18864       |
|        10 |        0.8      |   0.5      | 0.235963 | 0.5      | 0.880258 | leave_dataset_out | raw                           | combined      |              30 | all_except_GSE45898 | GSE45898       |
|        10 |        0.8      |   0.8      | 0.176545 | 0.625    | 0.875546 | leave_dataset_out | internal_percentile           | combined      |              30 | all_except_GSE45898 | GSE45898       |
|        10 |        0.8      |   0.5      | 0.278765 | 0.5      | 0.880258 | leave_dataset_out | external_zscore_to_internal   | combined      |              30 | all_except_GSE45898 | GSE45898       |
|        10 |        0.8      |   0.5      | 0.387243 | 0.4375   | 0.855258 | leave_dataset_out | external_quantile_to_internal | combined      |              30 | all_except_GSE45898 | GSE45898       |

### Response-Label Curation

The most important curation decision was to separate broad good-response labels from strict residual disease evidence. Rows in GSE25055 and GSE25065 with pathology evidence of residual disease were conservatively recoded for the curated sensitivity analysis.

| dataset_id   | locked_composite_response   | curation_decision                       |   samples |
|:-------------|:----------------------------|:----------------------------------------|----------:|
| GSE163882    | pcr_or_good_response        | lock_original_composite_label           |        38 |
| GSE163882    | residual_or_poor_response   | lock_original_composite_label           |        52 |
| GSE163882    | excluded_or_blank           | exclude                                 |       132 |
| GSE18864     | pcr_or_good_response        | lock_original_composite_label           |         8 |
| GSE18864     | residual_or_poor_response   | lock_original_composite_label           |        16 |
| GSE18864     | excluded_or_blank           | exclude                                 |        60 |
| GSE25055     | pcr_or_good_response        | lock_original_composite_label           |        40 |
| GSE25055     | residual_or_poor_response   | lock_original_composite_label           |        63 |
| GSE25055     | residual_or_poor_response   | recode_to_residual_for_locked_composite |        13 |
| GSE25055     | excluded_or_blank           | exclude                                 |       194 |
| GSE25065     | pcr_or_good_response        | lock_original_composite_label           |        24 |
| GSE25065     | residual_or_poor_response   | lock_original_composite_label           |        19 |
| GSE25065     | residual_or_poor_response   | recode_to_residual_for_locked_composite |        22 |
| GSE25065     | excluded_or_blank           | exclude                                 |       133 |
| GSE45898     | pcr_or_good_response        | lock_original_composite_label           |         2 |
| GSE45898     | residual_or_poor_response   | lock_original_composite_label           |         8 |

### Single-Cell Persister and Niche Review

Marker-panel direction checks passed 11 of 11.

GSE164715 targeted annotation scale:

| model   | sample_name        | stage      | targeted_annotation   |   cells |   fraction |
|:--------|:-------------------|:-----------|:----------------------|--------:|-----------:|
| HBCx172 | HBCx172_chemonaive | chemonaive | ambiguous_human       |     922 | 0.657163   |
| HBCx172 | HBCx172_chemonaive | chemonaive | endothelial_like      |     116 | 0.08268    |
| HBCx172 | HBCx172_chemonaive | chemonaive | immune_like           |      79 | 0.0563079  |
| HBCx172 | HBCx172_chemonaive | chemonaive | malignant_like        |     217 | 0.154669   |
| HBCx172 | HBCx172_chemonaive | chemonaive | stromal_like          |      69 | 0.0491803  |
| HBCx172 | HBCx172_persister  | persister  | ambiguous_human       |     321 | 0.696312   |
| HBCx172 | HBCx172_persister  | persister  | endothelial_like      |      48 | 0.104121   |
| HBCx172 | HBCx172_persister  | persister  | immune_like           |       4 | 0.00867679 |
| HBCx172 | HBCx172_persister  | persister  | malignant_like        |      63 | 0.136659   |
| HBCx172 | HBCx172_persister  | persister  | stromal_like          |      25 | 0.0542299  |
| HBCx39  | HBCx39_chemonaive  | chemonaive | ambiguous_human       |    1331 | 0.362473   |
| HBCx39  | HBCx39_chemonaive  | chemonaive | endothelial_like      |     188 | 0.0511983  |
| HBCx39  | HBCx39_chemonaive  | chemonaive | immune_like           |     230 | 0.0626362  |
| HBCx39  | HBCx39_chemonaive  | chemonaive | malignant_like        |    1331 | 0.362473   |
| HBCx39  | HBCx39_chemonaive  | chemonaive | stromal_like          |     592 | 0.16122    |
| HBCx39  | HBCx39_persister   | persister  | ambiguous_human       |     869 | 0.358943   |
| HBCx39  | HBCx39_persister   | persister  | endothelial_like      |     144 | 0.0594796  |
| HBCx39  | HBCx39_persister   | persister  | immune_like           |     215 | 0.0888063  |
| HBCx39  | HBCx39_persister   | persister  | malignant_like        |    1009 | 0.41677    |
| HBCx39  | HBCx39_persister   | persister  | stromal_like          |     184 | 0.0760017  |

Ambiguous compartment review:

| model   | sample_name        | stage      | targeted_annotation   |   cells |   fraction | review_status                          |
|:--------|:-------------------|:-----------|:----------------------|--------:|-----------:|:---------------------------------------|
| HBCx172 | HBCx172_chemonaive | chemonaive | ambiguous_human       |     922 |   0.657163 | high_ambiguity_review_required         |
| HBCx172 | HBCx172_persister  | persister  | ambiguous_human       |     321 |   0.696312 | high_ambiguity_review_required         |
| HBCx39  | HBCx39_chemonaive  | chemonaive | ambiguous_human       |    1331 |   0.362473 | moderate_ambiguity_report_with_caution |
| HBCx39  | HBCx39_persister   | persister  | ambiguous_human       |     869 |   0.358943 | moderate_ambiguity_report_with_caution |
| HBCx95  | HBCx95_chemonaive  | chemonaive | ambiguous_human       |    1093 |   0.31381  | moderate_ambiguity_report_with_caution |
| HBCx95  | HBCx95_persister   | persister  | ambiguous_human       |     250 |   0.462107 | moderate_ambiguity_report_with_caution |
| HBCx95  | HBCx95_recurrent   | recurrent  | ambiguous_human       |    1616 |   0.328122 | moderate_ambiguity_report_with_caution |
| HBCx95  | HBCx95_residual    | residual   | ambiguous_human       |    1771 |   0.365985 | moderate_ambiguity_report_with_caution |
| HBCx95  | HBCx95_resistant   | resistant  | ambiguous_human       |    1518 |   0.304514 | moderate_ambiguity_report_with_caution |

## How This Helps Clinicians

For clinicians, this project is not a treatment recommendation engine. Its value is in making residual-risk biology easier to inspect. A clinician-facing report can show whether a sample appears epithelial-sensitive, hybrid-plastic, mesenchymal-resistant, persister-enriched, hypoxic, stromal-supported, or immune-inflamed. That can support research tumor board discussion, trial hypothesis generation, and communication of uncertainty.

Potential clinician-facing uses after prospective validation:

- Explain why two TNBC tumors with similar clinical stage may have different residual-risk biology.
- Identify post-NAC samples where residual disease appears driven by hypoxia, AXL/TAM, YAP/TAZ, stromal niche, or persister stress tolerance.
- Provide cohort-relative percentiles instead of opaque scores.
- Generate transparent caveated reports for molecular review.
- Help prioritize biospecimens for deeper profiling, such as spatial transcriptomics or single-cell analysis.

## How This Helps Researchers

For researchers, the project is a reusable experimental scaffold. It links bulk response cohorts, paired longitudinal samples, residual recurrence biology, and single-cell persister biology in one reproducible workflow.

Research uses:

- Test EMT plasticity hypotheses across public TNBC NAC datasets.
- Compare response predictors under original versus curated endpoint definitions.
- Study platform sensitivity between array-derived cohorts and RNA-seq TPM cohorts.
- Explore whether persister tumor-cell programs and niche programs should be modeled separately.
- Prioritize future validation cohorts and prospective sample collection designs.

## Creative Future Directions

1. Time-lapse digital twin: add early on-treatment biopsies to model velocity, not only baseline state.
2. Spatial digital twin: combine EMT state with tumor-stroma distance, vascular proximity, and immune exclusion.
3. Perturbation twin: simulate how blocking AXL/TAM, TGF-beta, YAP/TAZ, hypoxia, or ferroptosis resistance changes P-state persistence.
4. Trial-enrichment twin: identify molecularly coherent residual-disease groups for post-NAC trials.
5. Patient explant twin: calibrate state transitions with organoid or PDX drug response assays.
6. Uncertainty-first reporting: show confidence, platform shift, cohort percentile, and label ambiguity before any score interpretation.

## Risks and Limitations

- Retrospective metadata are imperfect and response definitions differ across cohorts.
- Cross-platform validation is encouraging but modest.
- GSE18864 and GSE45898 holdout cohorts are small.
- GSE164715 supports broad targeted compartments, not definitive cell ontology.
- The therapy simulator is mechanistic and illustrative, not a calibrated individual tumor-burden forecast.
- Clinical use would require prospective validation, locked assays, calibrated thresholds, regulatory review, and clinician usability testing.

## Final Status

Computational work is complete for a research-prototype manuscript. The next step is expert review, citation formatting, figure/table numbering, and target-journal or thesis formatting.