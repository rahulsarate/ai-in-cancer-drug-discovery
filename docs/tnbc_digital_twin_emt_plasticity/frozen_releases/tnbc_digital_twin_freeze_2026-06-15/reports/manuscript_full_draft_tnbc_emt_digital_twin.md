# Manuscript Draft

## Title

A Research Digital Twin of EMT Plasticity and Drug-Tolerant Persister Biology in Triple-Negative Breast Cancer Under Neoadjuvant Chemotherapy

## Short Title

TNBC EMT Plasticity Digital Twin

## Abstract

Background: Triple-negative breast cancer (TNBC) treated with neoadjuvant chemotherapy (NAC) shows heterogeneous response. Pathologic complete response is associated with improved outcomes, but residual disease remains a major clinical problem. Biological interpretation is difficult because resistant disease is not a single state; it may involve epithelial-mesenchymal plasticity, stromal and immune context, hypoxia, and drug-tolerant persister programs.

Objective: To build a reproducible research digital twin that models therapy-associated EMT plasticity in TNBC using public bulk and single-cell transcriptomic cohorts.

Methods: Public TNBC NAC datasets were parsed into standardized metadata, response labels, gene-expression signatures, and digital-twin state features. The model represented tumor biology as epithelial-like, hybrid epithelial/mesenchymal, mesenchymal-like, and persister-like compartments. Analyses included baseline response modeling, response-label curation, GSE43816 paired pre/post-NAC EMT-shift analysis, transition-prior calibration, GSE43502 residual recurrence-axis analysis, GSE164715 single-cell persister/niche annotation, GSE163882 external RNA-seq TPM validation, platform-normalization diagnostics, bootstrap uncertainty, and leave-dataset-out sensitivity validation.

Results: In the primary external GSE163882 validation cohort, the best combined configuration achieved test dataset=GSE163882_TNBC_TPM, calibration=external_quantile_to_internal, feature set=combined, n=90, accuracy=0.656, AUROC=0.649, AUPRC=0.714, Brier=0.232. Curated-label sensitivity improved the GSE25055-to-GSE25065 train-test result for TME/resistance and combined feature sets, with the combined model achieving test dataset=GSE25065, feature set=combined, n=65, accuracy=0.600, AUROC=0.609, AUPRC=0.784, Brier=0.254. GSE164715 marker-panel validation passed 11/11 targeted direction checks. Leave-dataset-out validation in GSE18864 and GSE45898 provided small-cohort sensitivity evidence but remained underpowered.

Conclusion: The TNBC EMT digital twin supports a research-prototype claim: EMT/TME/persister features can be scored reproducibly, linked to therapy-induced state shifts, and externally evaluated with platform-aware caution. The prototype is not a clinical decision tool, but it provides a transparent framework for studying residual-disease biology and designing prospective validation.

## Keywords

Triple-negative breast cancer; neoadjuvant chemotherapy; epithelial-mesenchymal transition; epithelial-mesenchymal plasticity; digital twin; drug-tolerant persister; residual disease; transcriptomics; single-cell RNA-seq.

## Introduction

TNBC is a high-risk breast cancer subtype in which NAC is both therapeutic and informative. Patients who achieve pCR generally have better outcomes, while patients with residual disease remain vulnerable to relapse. However, pCR is a clinical endpoint, not a mechanistic explanation. It tells us whether visible invasive disease remains after treatment, but not which molecular survival strategy allowed tumor cells to persist.

A central problem in TNBC is that residual disease is biologically plural. One residual tumor may be hypoxic and stromal-supported; another may show immune escape; another may contain hybrid epithelial/mesenchymal cells poised between proliferation and invasion; another may contain drug-tolerant persister states that survive by reversible non-genetic adaptation. EMT is therefore better treated as epithelial-mesenchymal plasticity, a spectrum of dynamic states rather than a binary switch.

Digital twins offer a conceptual bridge between molecular measurement and dynamic clinical reasoning. In this project, the twin is deliberately modest: it is not a bedside prescriber. It is a transparent state model that turns transcriptomic measurements into interpretable compartments, transition priors, uncertainty bands, and research reports.

## Hypothesis

We hypothesized that a TNBC NAC digital twin based on EMT plasticity and persister biology could do three useful things: first, summarize baseline and residual response biology more transparently than a black-box classifier; second, model therapy-induced shifts in state composition; and third, expose which components of response prediction remain stable or fragile across platforms and cohorts.

## Study Design

The project used a multi-layer retrospective public-data design. Bulk response cohorts were used to train and test response-associated features. GSE43816 paired samples were used for longitudinal state-shift analysis and transition-prior calibration. GSE43502 residual chemoresistant TNBC samples were used to examine recurrence-associated resistance axes. GSE164715 single-cell data were used to refine persister and niche layers. GSE163882 was used as the primary held-out external RNA-seq TPM validation cohort.

## Digital-Twin Architecture

The model uses four state compartments: E, H, M, and P. E denotes epithelial-like chemo-sensitive biology. H denotes hybrid epithelial/mesenchymal plasticity. M denotes mesenchymal-like resistance. P denotes drug-tolerant persister biology. Each bulk sample is projected into these compartments using signature-derived scores, and each score is accompanied by resistance-axis features including AXL/TAM, TGF-beta, YAP/TAZ, hypoxia, immune/stromal context, and refined persister tumor/niche layers.

The model is intentionally explainable. Every feature is tied to a gene signature, every response label is auditable, every validation result is separated by cohort and platform, and every clinician-style statement is constrained by caveats.

## Methods

### Data Acquisition and Harmonization

GEO series matrices and supplementary files were collected for TNBC NAC and residual-disease cohorts. Sample metadata were standardized into dataset identifiers, sample identifiers, TNBC-likely labels, timepoints, and response labels. Where response labels were unavailable or ambiguous, samples were excluded from response modeling but could still contribute to biological interpretation if appropriate.

### Signature Scoring

Gene-expression matrices were mapped to compact signature gene tables. Signature blocks included epithelial markers, mesenchymal markers, EMT transcription factors, hybrid plasticity markers, AXL/TAM, TGF-beta, YAP/TAZ, hypoxia, stemness/persister, refined tumor-cell persister, stress-tolerance persister, and persister-niche genes.

### Response Modeling

Response models used logistic regression with median imputation, standard scaling, and class balancing. Feature sets included EMT core, EMT plus TME/resistance, digital-twin features, and combined features. The positive class was residual or poor response.

### Response-Label Curation

A dedicated curation layer separated the original broad pCR/good-response endpoint from stricter residual-disease evidence. Rows in GSE25055 and GSE25065 with pathology evidence of residual disease were conservatively recoded to residual/poor response in the curated sensitivity table. Unknown labels were excluded. This preserved the original endpoint for comparison while preventing a good-response bucket from being interpreted as strict pCR.

### Longitudinal State-Shift and Transition Calibration

GSE43816 paired pre/post-NAC TNBC samples were used to measure therapy-induced shifts and calibrate first transition priors between E/H/M/P states. These priors were then used in the therapy simulator to create uncertainty bands and final-state summaries.

### Single-Cell Persister Layer

GSE164715 single-cell matrices were imported, species-filtered, and scored. Human-dominant cells were assigned targeted broad annotations: malignant-like, endothelial-like, stromal-like, immune-like, or ambiguous human. Marker-panel validation assessed whether broad annotations had expected directional scores. An ambiguity review separated interpretable targeted compartments from unresolved human-dominant clusters.

### External and Sensitivity Validation

GSE163882 was prepared as a held-out TNBC RNA-seq TPM validation cohort. Because the internal cohorts were mostly array-derived, validation was reported under raw, internal-percentile, external-z-score, and external-quantile calibration modes. Leave-dataset-out validation was added for GSE18864 and GSE45898 by training on all other response-labeled cohorts and testing on the held-out dataset.

## Results

### External Validation on GSE163882

The combined feature set performed best in the main external validation setting, but performance was moderate and platform-sensitive.

|   samples |   positive_rate |   accuracy |    brier |    auroc |    auprc | evaluation          | calibration_method            | feature_set   |   feature_count | train_dataset             | test_dataset       |
|----------:|----------------:|-----------:|---------:|---------:|---------:|:--------------------|:------------------------------|:--------------|----------------:|:--------------------------|:-------------------|
|        90 |        0.577778 |   0.644444 | 0.228155 | 0.647773 | 0.721259 | external_validation | raw                           | combined      |              30 | internal_geo_deduplicated | GSE163882_TNBC_TPM |
|        90 |        0.577778 |   0.566667 | 0.242155 | 0.61083  | 0.674309 | external_validation | internal_percentile           | combined      |              30 | internal_geo_deduplicated | GSE163882_TNBC_TPM |
|        90 |        0.577778 |   0.611111 | 0.234608 | 0.631579 | 0.707764 | external_validation | external_zscore_to_internal   | combined      |              30 | internal_geo_deduplicated | GSE163882_TNBC_TPM |
|        90 |        0.577778 |   0.655556 | 0.231701 | 0.648785 | 0.713864 | external_validation | external_quantile_to_internal | combined      |              30 | internal_geo_deduplicated | GSE163882_TNBC_TPM |

The strongest result by AUROC was the combined external quantile-to-internal calibration configuration. The raw combined configuration had very similar AUROC and slightly higher AUPRC, supporting the decision to report calibration as sensitivity rather than as a definitive correction.

### Curated-Label Sensitivity

Curating pathology-conflict rows shifted the response balance toward residual disease and improved the discovery-to-validation result for TME/resistance features.

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

### Leave-Dataset-Out Validation

GSE18864 and GSE45898 were held out as small independent same-project cohorts. Their results were variable, as expected from sample sizes of 24 and 10, respectively.

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

### Longitudinal EMT Plasticity and Transition Priors

GSE43816 showed that NAC-associated state shifts are heterogeneous. Mean EMT score decreased after therapy, but several paired samples showed increased hybrid/persister or therapy-selection-pressure features. This supports the central premise that residual biology is not captured by a single scalar response label.

|        aEH |      aHE |      aHM |   aEP |   aHP |      aPH |    kE |    kH |       kM |       kP |
|-----------:|---------:|---------:|------:|------:|---------:|------:|------:|---------:|---------:|
| 0.00320824 | 0.785461 | 0.254747 | 0.001 | 0.001 | 0.444672 | 1.267 | 0.001 | 0.899473 | 0.026296 |

### Residual Recurrence-Axis Biology

In GSE43502 residual chemoresistant TNBC, AXL/TAM and hypoxia showed positive recurrence-associated shifts with wide intervals. These findings are hypothesis-generating and should guide future validation rather than direct clinical interpretation.

| feature                     |   recurrence_n |   no_recurrence_n |   recurrence_mean |   no_recurrence_mean |   delta_recurrence_minus_no_recurrence |   recurrence_median |   no_recurrence_median |   delta_mean_q025 |   delta_mean_q975 |   bootstrap_probability_delta_gt_0 |   bootstrap_probability_delta_lt_0 |   mannwhitney_p |
|:----------------------------|---------------:|------------------:|------------------:|---------------------:|---------------------------------------:|--------------------:|-----------------------:|------------------:|------------------:|-----------------------------------:|-----------------------------------:|----------------:|
| tnbc_axl_tam                |             16 |                 9 |         0.186689  |           -0.331891  |                              0.51858   |           0.291894  |              0.0782869 |       0.000297097 |         1.05327   |                             0.975  |                             0.025  |        0.119499 |
| tnbc_hypoxia                |             16 |                 9 |         0.151822  |           -0.269906  |                              0.421728  |           0.0777229 |             -0.217242  |       0.00243107  |         0.841233  |                             0.9758 |                             0.0242 |        0.183378 |
| tnbc_yap_taz                |             16 |                 9 |        -0.144732  |            0.257301  |                             -0.402033  |           0.0972364 |              0.163542  |      -0.833437    |        -0.0134439 |                             0.019  |                             0.981  |        0.20273  |
| partial_emt_score           |             16 |                 9 |        -0.267185  |           -0.360274  |                              0.0930884 |          -0.26529   |             -0.391077  |      -0.231652    |         0.408075  |                             0.7308 |                             0.2692 |        0.294935 |
| therapy_selection_pressure  |             16 |                 9 |         0.561919  |            0.532585  |                              0.0293338 |           0.56278   |              0.566271  |      -0.0914373   |         0.155114  |                             0.6714 |                             0.3286 |        0.630362 |
| emt_score                   |             16 |                 9 |        -0.0230738 |            0.0410201 |                             -0.0640939 |          -0.156542  |              0.0395534 |      -0.658831    |         0.545816  |                             0.4154 |                             0.5846 |        0.671125 |
| caf_tam_niche               |             16 |                 9 |         0.0924622 |           -0.164377  |                              0.256839  |          -0.0103778 |              0.165758  |      -0.269822    |         0.809168  |                             0.819  |                             0.181  |        0.755515 |
| resistant_fraction_estimate |             16 |                 9 |         0.696513  |            0.728843  |                             -0.0323304 |           0.789064  |              0.810088  |      -0.186413    |         0.134917  |                             0.3388 |                             0.6612 |        0.755515 |

### Single-Cell Persister and Niche Biology

GSE164715 marker-panel validation passed 11/11 direction checks. However, ambiguity review identified unresolved human-dominant compartments, especially cluster_1 and high-ambiguity HBCx172 sample-stage rows. The single-cell analysis therefore supports broad targeted annotation, not definitive cell ontology.

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

## Discussion

This project shows that a digital twin does not need to begin as a clinically autonomous predictor. A useful first-generation oncology twin can be an interpretive state machine: a system that translates measurements into biologically meaningful compartments, identifies fragile assumptions, and makes uncertainty visible.

The most important scientific observation is that the combined EMT/TME/persister feature space performed better than EMT core features alone in external validation. That does not prove clinical utility, but it supports the biological idea that residual TNBC risk is not only an EMT problem. It is an ecosystem problem involving tumor-cell state, stress adaptation, vascular/stromal niche, immune context, and platform-dependent measurement effects.

The curated-label analysis also matters. When broad pCR/good-response labels were confronted with pathology evidence of residual disease, the endpoint changed. This is not a nuisance detail; it is part of the biology-to-clinic translation problem. A model trained on an endpoint that mixes RCB-0/I with strict pCR may be useful for good-response biology but should not be described as a strict pCR model.

The single-cell analysis adds another important caution. Marker panels supported broad targeted compartments, but a large ambiguous human cluster remained unresolved. A mature digital twin should not force every cell into a confident label. Instead, ambiguity should become part of the report.

## Importance for Clinicians

Clinicians need models that explain, not only predict. This project could eventually help clinicians interpret why a residual TNBC sample appears dangerous: is the dominant signal hypoxia, AXL/TAM, YAP/TAZ, stromal support, immune context, or persister stress tolerance? That kind of report could support molecular tumor board discussion, trial matching research, and post-NAC residual-disease hypothesis generation. In its current form, however, it is not a treatment-selection tool.

## Importance for Researchers

Researchers gain a reproducible framework for joining several normally separate evidence layers: public response cohorts, longitudinal therapy-shift data, residual recurrence biology, and single-cell persister/niche evidence. The pipeline makes it possible to test new signatures, add new cohorts, compare calibration methods, and evaluate whether future interventions should target tumor-intrinsic persisters, niche-protected cells, or both.

## Creative Translation Roadmap

A future version could become a multi-modal residual-disease twin. It would ingest baseline biopsy, early on-treatment biopsy, surgery specimen, spatial transcriptomics, pathology RCB features, imaging response, ctDNA, and organoid perturbation data. It would output not one score but a patient-specific map: state fractions, transition velocity, uncertainty, resistant axes, suggested research assays, and trial hypotheses. The most creative and clinically useful version would treat uncertainty as a first-class result.

## Limitations

The study is retrospective and public-data based. Treatments, platforms, and response definitions differ across cohorts. External validation is moderate and platform-sensitive. Small holdout cohorts are underpowered. Single-cell targeted annotation does not equal a full atlas. The simulator is not a patient-specific tumor burden forecast. All clinical interpretations require prospective validation.

## Conclusion

The project provides a completed research-prototype digital twin for TNBC EMT plasticity under NAC. It is transparent, reproducible, biologically interpretable, and honest about uncertainty. Its strongest immediate role is not clinical decision-making but research translation: organizing residual-disease biology into a state-based framework that clinicians can understand and researchers can extend.

## References and Resources

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