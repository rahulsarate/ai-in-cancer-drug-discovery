# TNBC EMT Digital Twin Validation Memo

## Purpose

Separate what can be shown in clinician-style research reports from what must remain exploratory while the TNBC neoadjuvant chemotherapy EMT digital twin is still a research prototype.

## Current Validation Status

| Layer | Current evidence | Clinician-facing status | Research-only status |
| --- | --- | --- | --- |
| Baseline response model | Retrospective GEO TNBC-like NAC cohorts with deduplicated `GSE25055`/`GSE25065` split | Show only as model-performance context | Do not use for treatment selection or individual pCR prediction |
| `GSE43816` longitudinal shift | 7 paired pretreatment/post-NAC TNBC samples | Show paired state-shift plots, cohort percentiles, and bootstrap uncertainty with caution | Do not infer pCR or survival response because parsed response labels are unavailable |
| Therapy simulator | Synthetic archetypes plus `GSE43816` calibrated transition priors | Show as scenario simulation and uncertainty visualization | Do not interpret as calibrated tumor-burden forecast |
| `GSE43502` residual recurrence biology | 25 residual chemoresistant TNBC samples, 16 recurrence and 9 no recurrence | Show only hypothesis-generating recurrence-axis trends | Do not make biomarker claims without larger validation |
| `GSE164715` scRNA persister layer | Species-filtered PDX scRNA with targeted annotation of human-dominant cells plus marker-panel direction checks | Use to explain why persister risk is split into tumor/stress/niche layers | Do not present as full single-cell atlas or definitive malignant-cell classifier |

## Locked Response-Label Curation

| dataset_id   | locked_composite_response   | curation_decision                       |   samples |
|:-------------|:----------------------------|:----------------------------------------|----------:|
| GSE163882    | pcr_or_good_response        | lock_original_composite_label           |        38 |
| GSE163882    | residual_or_poor_response   | lock_original_composite_label           |        52 |
| GSE163882    | nan                         | exclude                                 |       132 |
| GSE18864     | pcr_or_good_response        | lock_original_composite_label           |         8 |
| GSE18864     | residual_or_poor_response   | lock_original_composite_label           |        16 |
| GSE18864     | nan                         | exclude                                 |        60 |
| GSE25055     | pcr_or_good_response        | lock_original_composite_label           |        40 |
| GSE25055     | residual_or_poor_response   | lock_original_composite_label           |        63 |
| GSE25055     | residual_or_poor_response   | recode_to_residual_for_locked_composite |        13 |
| GSE25055     | nan                         | exclude                                 |       194 |
| GSE25065     | pcr_or_good_response        | lock_original_composite_label           |        24 |
| GSE25065     | residual_or_poor_response   | lock_original_composite_label           |        19 |
| GSE25065     | residual_or_poor_response   | recode_to_residual_for_locked_composite |        22 |
| GSE25065     | nan                         | exclude                                 |       133 |
| GSE45898     | pcr_or_good_response        | lock_original_composite_label           |         2 |
| GSE45898     | residual_or_poor_response   | lock_original_composite_label           |         8 |

Interpretation: rows with available pathology fields indicating residual disease are conservatively recoded to `residual_or_poor_response` for the curated composite sensitivity analysis. Unknown response labels remain excluded.

## Response-Model Metrics

| evaluation    | feature_set        |   samples |    auroc |    auprc |   accuracy |
|:--------------|:-------------------|----------:|---------:|---------:|-----------:|
| stratified_cv | emt_core           |       215 | 0.430673 | 0.446188 |   0.47907  |
| train_test    | emt_core           |        65 | 0.392449 | 0.270282 |   0.430769 |
| stratified_cv | emt_tme_resistance |       215 | 0.530725 | 0.540373 |   0.493023 |
| train_test    | emt_tme_resistance |        65 | 0.514874 | 0.333694 |   0.492308 |
| stratified_cv | digital_twin       |       215 | 0.474987 | 0.482125 |   0.493023 |
| train_test    | digital_twin       |        65 | 0.529748 | 0.315979 |   0.507692 |
| stratified_cv | combined           |       215 | 0.473516 | 0.506838 |   0.446512 |
| train_test    | combined           |        65 | 0.459954 | 0.337478 |   0.476923 |

Interpretation: the response model remains a benchmark and feature-prior engine. The cross-dataset performance is modest, so individual patient prediction should stay out of clinician-facing claims.

## Curated-Label Sensitivity Metrics

| evaluation    | feature_set        |   samples |    auroc |    auprc |   accuracy |
|:--------------|:-------------------|----------:|---------:|---------:|-----------:|
| stratified_cv | emt_core           |       215 | 0.520893 | 0.661287 |   0.493023 |
| train_test    | emt_core           |        65 | 0.50813  | 0.642596 |   0.476923 |
| stratified_cv | emt_tme_resistance |       215 | 0.579164 | 0.719704 |   0.6      |
| train_test    | emt_tme_resistance |        65 | 0.618902 | 0.803878 |   0.6      |
| stratified_cv | digital_twin       |       215 | 0.499808 | 0.658888 |   0.47907  |
| train_test    | digital_twin       |        65 | 0.559959 | 0.703621 |   0.538462 |
| stratified_cv | combined           |       215 | 0.524248 | 0.678734 |   0.52093  |
| train_test    | combined           |        65 | 0.60874  | 0.783751 |   0.6      |

Interpretation: curated-label sensitivity changes the residual/poor-response prevalence and should be reported alongside the original broad endpoint.

## Additional Same-Project Holdout Validation

| test_dataset   | calibration_method            | feature_set        |   samples |   positive_rate |    auroc |    auprc |   accuracy |    brier |
|:---------------|:------------------------------|:-------------------|----------:|----------------:|---------:|---------:|-----------:|---------:|
| GSE18864       | raw                           | emt_core           |        24 |        0.666667 | 0.507812 | 0.677773 |   0.458333 | 0.25102  |
| GSE18864       | internal_percentile           | emt_core           |        24 |        0.666667 | 0.5      | 0.636202 |   0.583333 | 0.244633 |
| GSE18864       | external_zscore_to_internal   | emt_core           |        24 |        0.666667 | 0.507812 | 0.671821 |   0.5      | 0.250725 |
| GSE18864       | external_quantile_to_internal | emt_core           |        24 |        0.666667 | 0.492188 | 0.667087 |   0.458333 | 0.253274 |
| GSE18864       | raw                           | emt_tme_resistance |        24 |        0.666667 | 0.484375 | 0.68379  |   0.541667 | 0.319644 |
| GSE18864       | internal_percentile           | emt_tme_resistance |        24 |        0.666667 | 0.5625   | 0.746593 |   0.625    | 0.28109  |
| GSE18864       | external_zscore_to_internal   | emt_tme_resistance |        24 |        0.666667 | 0.492188 | 0.69004  |   0.541667 | 0.311018 |
| GSE18864       | external_quantile_to_internal | emt_tme_resistance |        24 |        0.666667 | 0.476562 | 0.668251 |   0.583333 | 0.312538 |
| GSE18864       | raw                           | digital_twin       |        24 |        0.666667 | 0.28125  | 0.560643 |   0.375    | 0.290287 |
| GSE18864       | internal_percentile           | digital_twin       |        24 |        0.666667 | 0.273438 | 0.558707 |   0.416667 | 0.300667 |
| GSE18864       | external_zscore_to_internal   | digital_twin       |        24 |        0.666667 | 0.289062 | 0.565108 |   0.333333 | 0.298141 |
| GSE18864       | external_quantile_to_internal | digital_twin       |        24 |        0.666667 | 0.296875 | 0.562624 |   0.333333 | 0.30103  |
| GSE18864       | raw                           | combined           |        24 |        0.666667 | 0.46875  | 0.675871 |   0.541667 | 0.328623 |
| GSE18864       | internal_percentile           | combined           |        24 |        0.666667 | 0.53125  | 0.751506 |   0.5      | 0.311176 |
| GSE18864       | external_zscore_to_internal   | combined           |        24 |        0.666667 | 0.453125 | 0.665409 |   0.583333 | 0.324632 |
| GSE18864       | external_quantile_to_internal | combined           |        24 |        0.666667 | 0.4375   | 0.67157  |   0.5      | 0.333075 |
| GSE45898       | raw                           | emt_core           |        10 |        0.8      | 0.1875   | 0.746925 |   0.4      | 0.281785 |
| GSE45898       | internal_percentile           | emt_core           |        10 |        0.8      | 0.25     | 0.765675 |   0.4      | 0.269346 |
| GSE45898       | external_zscore_to_internal   | emt_core           |        10 |        0.8      | 0.1875   | 0.746925 |   0.4      | 0.260123 |
| GSE45898       | external_quantile_to_internal | emt_core           |        10 |        0.8      | 0.125    | 0.684425 |   0.4      | 0.265103 |
| GSE45898       | raw                           | emt_tme_resistance |        10 |        0.8      | 0.5      | 0.870139 |   0.6      | 0.228309 |
| GSE45898       | internal_percentile           | emt_tme_resistance |        10 |        0.8      | 0.625    | 0.875546 |   0.9      | 0.177933 |
| GSE45898       | external_zscore_to_internal   | emt_tme_resistance |        10 |        0.8      | 0.5      | 0.870139 |   0.5      | 0.267805 |
| GSE45898       | external_quantile_to_internal | emt_tme_resistance |        10 |        0.8      | 0.5      | 0.880258 |   0.5      | 0.332278 |
| GSE45898       | raw                           | digital_twin       |        10 |        0.8      | 0.25     | 0.788591 |   0.3      | 0.268073 |
| GSE45898       | internal_percentile           | digital_twin       |        10 |        0.8      | 0.4375   | 0.810615 |   0.6      | 0.238997 |
| GSE45898       | external_zscore_to_internal   | digital_twin       |        10 |        0.8      | 0.25     | 0.788591 |   0.4      | 0.261096 |
| GSE45898       | external_quantile_to_internal | digital_twin       |        10 |        0.8      | 0.1875   | 0.746925 |   0.2      | 0.286725 |
| GSE45898       | raw                           | combined           |        10 |        0.8      | 0.5      | 0.880258 |   0.5      | 0.235963 |
| GSE45898       | internal_percentile           | combined           |        10 |        0.8      | 0.625    | 0.875546 |   0.8      | 0.176545 |
| GSE45898       | external_zscore_to_internal   | combined           |        10 |        0.8      | 0.5      | 0.880258 |   0.5      | 0.278765 |
| GSE45898       | external_quantile_to_internal | combined           |        10 |        0.8      | 0.4375   | 0.855258 |   0.5      | 0.387243 |

Interpretation: leave-dataset-out checks on small TNBC NAC cohorts add independent-label sensitivity but remain underpowered.

## GSE43502 Bootstrap Recurrence-Axis Summary

| feature                     |   delta_recurrence_minus_no_recurrence |   delta_mean_q025 |   delta_mean_q975 |   bootstrap_probability_delta_gt_0 |   mannwhitney_p |
|:----------------------------|---------------------------------------:|------------------:|------------------:|-----------------------------------:|----------------:|
| tnbc_axl_tam                |                              0.51858   |       0.000297097 |         1.05327   |                             0.975  |        0.119499 |
| tnbc_hypoxia                |                              0.421728  |       0.00243107  |         0.841233  |                             0.9758 |        0.183378 |
| tnbc_yap_taz                |                             -0.402033  |      -0.833437    |        -0.0134439 |                             0.019  |        0.20273  |
| partial_emt_score           |                              0.0930884 |      -0.231652    |         0.408075  |                             0.7308 |        0.294935 |
| therapy_selection_pressure  |                              0.0293338 |      -0.0914373   |         0.155114  |                             0.6714 |        0.630362 |
| emt_score                   |                             -0.0640939 |      -0.658831    |         0.545816  |                             0.4154 |        0.671125 |
| caf_tam_niche               |                              0.256839  |      -0.269822    |         0.809168  |                             0.819  |        0.755515 |
| resistant_fraction_estimate |                             -0.0323304 |      -0.186413    |         0.134917  |                             0.3388 |        0.755515 |

Interpretation: AXL/TAM and hypoxia remain the strongest recurrence-associated directions, but intervals are wide and should be treated as hypothesis-generating.

## Calibrated Therapy Simulation Summary

| archetype                  |   final_tumor_burden |   final_resistant_fraction |   persister_delta |   residual_disease_probability_proxy |
|:---------------------------|---------------------:|---------------------------:|------------------:|-------------------------------------:|
| chemo_sensitive_epithelial |             0.276271 |                   0.81067  |          0.203722 |                             0.54515  |
| mesenchymal_persister_high |             0.725501 |                   0.98477  |          0.173773 |                             0.844457 |
| plastic_residual_risk      |             0.599185 |                   0.966966 |          0.232703 |                             0.769641 |

Interpretation: calibrated-prior simulation is useful for comparing state dynamics across archetypes, especially resistant and persister enrichment, but it is not yet a patient-specific outcome model.

## Real External Validation: GSE163882

| test_dataset       | calibration_method            | feature_set        |   samples |   positive_rate |    auroc |    auprc |   accuracy |    brier |
|:-------------------|:------------------------------|:-------------------|----------:|----------------:|---------:|---------:|-----------:|---------:|
| GSE163882_TNBC_TPM | raw                           | emt_core           |        90 |        0.577778 | 0.434211 | 0.582964 |   0.511111 | 0.257857 |
| GSE163882_TNBC_TPM | internal_percentile           | emt_core           |        90 |        0.577778 | 0.444838 | 0.567499 |   0.477778 | 0.260752 |
| GSE163882_TNBC_TPM | external_zscore_to_internal   | emt_core           |        90 |        0.577778 | 0.435223 | 0.580112 |   0.455556 | 0.254566 |
| GSE163882_TNBC_TPM | external_quantile_to_internal | emt_core           |        90 |        0.577778 | 0.447874 | 0.597876 |   0.444444 | 0.253432 |
| GSE163882_TNBC_TPM | raw                           | emt_tme_resistance |        90 |        0.577778 | 0.642713 | 0.707881 |   0.633333 | 0.229278 |
| GSE163882_TNBC_TPM | internal_percentile           | emt_tme_resistance |        90 |        0.577778 | 0.610324 | 0.662025 |   0.633333 | 0.239377 |
| GSE163882_TNBC_TPM | external_zscore_to_internal   | emt_tme_resistance |        90 |        0.577778 | 0.611842 | 0.69175  |   0.6      | 0.237799 |
| GSE163882_TNBC_TPM | external_quantile_to_internal | emt_tme_resistance |        90 |        0.577778 | 0.646255 | 0.709051 |   0.666667 | 0.234539 |
| GSE163882_TNBC_TPM | raw                           | digital_twin       |        90 |        0.577778 | 0.584008 | 0.700093 |   0.577778 | 0.242047 |
| GSE163882_TNBC_TPM | internal_percentile           | digital_twin       |        90 |        0.577778 | 0.507085 | 0.626495 |   0.511111 | 0.254651 |
| GSE163882_TNBC_TPM | external_zscore_to_internal   | digital_twin       |        90 |        0.577778 | 0.522773 | 0.643652 |   0.466667 | 0.249878 |
| GSE163882_TNBC_TPM | external_quantile_to_internal | digital_twin       |        90 |        0.577778 | 0.527834 | 0.646858 |   0.488889 | 0.24948  |
| GSE163882_TNBC_TPM | raw                           | combined           |        90 |        0.577778 | 0.647773 | 0.721259 |   0.644444 | 0.228155 |
| GSE163882_TNBC_TPM | internal_percentile           | combined           |        90 |        0.577778 | 0.61083  | 0.674309 |   0.566667 | 0.242155 |
| GSE163882_TNBC_TPM | external_zscore_to_internal   | combined           |        90 |        0.577778 | 0.631579 | 0.707764 |   0.611111 | 0.234608 |
| GSE163882_TNBC_TPM | external_quantile_to_internal | combined           |        90 |        0.577778 | 0.648785 | 0.713864 |   0.655556 | 0.231701 |

Interpretation: `GSE163882_TNBC_TPM` is a held-out RNA-seq TPM cohort with 90 TNBC response-labeled samples. Performance is strongest for TME/resistance and combined feature sets, but it must be interpreted with platform diagnostics because the internal training cohorts are mostly array-derived.

## Platform-Normalization Diagnostics

| feature                         |   standardized_mean_shift |   ks_statistic |   ks_pvalue |
|:--------------------------------|--------------------------:|---------------:|------------:|
| tnbc_stemness_persister         |                -0.611685  |       0.3      | 2.46909e-06 |
| tnbc_hypoxia                    |                -0.624361  |       0.290909 | 5.60345e-06 |
| tnbc_yap_taz                    |                -0.586291  |       0.271212 | 3.01908e-05 |
| tnbc_tgfb                       |                 0.0687756 |       0.257071 | 9.37115e-05 |
| therapy_selection_pressure      |                -0.456593  |       0.252525 | 0.000133065 |
| hypoxia                         |                -0.524907  |       0.231818 | 0.00060543  |
| tnbc_persister_stress_tolerance |                -0.0956536 |       0.206566 | 0.00320666  |
| hybrid_fraction_estimate        |                 0.290705  |       0.19798  | 0.00540459  |

Interpretation: the largest platform/cohort shifts involve stemness/persister, TNBC hypoxia, YAP/TAZ, and therapy-selection-pressure features. Cross-platform performance should therefore be reported as external research validation, not as a locked clinical predictor.

Batch-correction decision: because the current external test is a single RNA-seq TPM cohort compared against mostly array-derived internal cohorts, explicit batch correction should remain a sensitivity analysis rather than the primary validation result until a bridge cohort or multiple independent external cohorts are available. The report therefore keeps raw, internal-percentile, external-z-score, and external-quantile calibration results separated.

## GSE164715 Targeted Annotation Summary

| targeted_annotation   |   cells |   fraction |
|:----------------------|--------:|-----------:|
| malignant_like        |    9983 |  0.373475  |
| ambiguous_human       |    9691 |  0.362551  |
| stromal_like          |    2619 |  0.0979798 |
| endothelial_like      |    2322 |  0.0868687 |
| immune_like           |    2115 |  0.0791246 |

Interpretation: human-dominant targeted annotations support separating malignant-like persister signal from endothelial/stromal/immune-like residual-niche signal.

## GSE164715 Ambiguity Review

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

Interpretation: ambiguous human-dominant compartments should be treated as unresolved cells, not as a named biological cell state.

## Clinician-Style Report Rules

Use these elements:

- Dataset, sample, and timepoint provenance.
- State fractions and direction of change.
- Cohort-relative percentiles when cohort size is named clearly.
- Bootstrap uncertainty intervals and explicit research-only caveats.
- Dominant resistance axis as a molecular-review prompt.

Avoid these elements:

- Treatment recommendations.
- Claims of validated pCR prediction from `GSE43816`.
- Survival or recurrence prediction for an individual patient.
- Single-cell cell-type claims beyond targeted annotation and marker-panel direction checks.

## Next Validation Actions

1. Obtain final expert/author sign-off on the computational response-label curation table.
2. Keep explicit batch correction as sensitivity-only unless a bridge cohort or additional external cohorts become available.
3. Obtain expert/author review of `GSE164715` ambiguity language before publication-level single-cell claims.
4. Polish the manuscript/thesis draft and format citations, figures, and tables for the target venue.