# Digital Twin of EMT Plasticity Under Neoadjuvant Chemotherapy in Triple-Negative Breast Cancer

## Draft Status

This is a manuscript/thesis chapter draft generated from the locked local analysis outputs. It supports a research-prototype claim only and should undergo author, pathology, oncology, and bioinformatics review before submission.

## Abstract

Triple-negative breast cancer (TNBC) has heterogeneous response to neoadjuvant chemotherapy (NAC), with residual disease after therapy associated with high recurrence risk. We developed a reproducible EMT plasticity digital-twin prototype that converts public TNBC NAC transcriptomic cohorts into interpretable epithelial-like, hybrid epithelial/mesenchymal, mesenchymal-like, and drug-tolerant persister state features. The workflow integrates baseline response modeling, longitudinal pre/post-NAC EMT-shift analysis, transition-prior calibration, residual recurrence-axis analysis, persister single-cell refinement, and external validation. The resulting system is not a clinical treatment-selection model, but it provides a transparent research framework for studying therapy-induced EMT plasticity and residual-disease biology.

## Concept and Innovation

The core concept is to represent TNBC under therapy as a changing mixture of four interpretable cell-state compartments: chemo-sensitive epithelial-like cells, hybrid plastic cells, mesenchymal-resistant cells, and drug-tolerant persister cells. Rather than using a black-box pCR predictor alone, the project links model outputs to biological axes that clinicians and researchers can inspect: EMT state, hypoxia, AXL/TAM signaling, TGF-beta, YAP/TAZ, immune/stromal context, and persister niche signals.

Novel elements include longitudinal transition-prior calibration from paired pre/post-NAC TNBC samples, separation of tumor-cell persister and niche persister layers, platform-aware external validation, and explicit clinician-versus-research reporting boundaries.

## Methods Summary

Public GEO TNBC NAC cohorts were downloaded and parsed into standardized metadata, response labels, and gene-expression signature tables. EMT, TME, resistance, and digital-twin features were scored using curated gene signatures. Response models used logistic regression pipelines with median imputation, scaling, and class balancing. `GSE43816` paired pre/post-NAC samples were used for longitudinal EMT-shift analysis and transition-prior calibration. `GSE43502` residual chemoresistant samples were used for recurrence-axis analysis with bootstrap intervals. `GSE164715` persister single-cell data were species-filtered, scored, targeted-annotated, and reviewed for ambiguous compartments. `GSE163882` was used as a held-out RNA-seq TPM validation cohort with raw, percentile, z-score, and quantile calibration sensitivity analyses.

## Response-Label Curation

The original broad endpoint was `pcr_or_good_response` versus `residual_or_poor_response`. A curation pass identified rows in `GSE25055` and `GSE25065` where the pathology field indicated residual disease despite the broad good-response label. These rows were conservatively recoded to residual disease for the locked curated composite sensitivity analysis. Unknown response labels remain excluded.

Curated model best combined metric:

test_dataset=GSE25065, feature_set=combined, samples=65.0, accuracy=0.6, auroc=0.6087398373983739, auprc=0.7837506396089681, brier=0.2538854207249759

## Main External Validation

`GSE163882_TNBC_TPM` provides the primary independent RNA-seq TPM validation layer. Because internal training cohorts are mostly array-derived, cross-platform performance is interpreted cautiously and calibration modes are reported separately.

Best external combined metric:

test_dataset=GSE163882_TNBC_TPM, calibration_method=external_quantile_to_internal, feature_set=combined, samples=90.0, accuracy=0.6555555555555556, auroc=0.6487854251012146, auprc=0.7138642350852893, brier=0.231700775014528

Bootstrap robustness preview:

| dataset_id         | feature_set   | calibration_method            |   samples |   accuracy_point |   accuracy_q025 |   accuracy_q975 |   brier_point |   brier_q025 |   brier_q975 |   auroc_point |   auroc_q025 |   auroc_q975 |   auprc_point |   auprc_q025 |   auprc_q975 |
|:-------------------|:--------------|:------------------------------|----------:|-----------------:|----------------:|----------------:|--------------:|-------------:|-------------:|--------------:|-------------:|-------------:|--------------:|-------------:|-------------:|
| GSE163882_TNBC_TPM | combined      | external_quantile_to_internal |        90 |         0.655556 |        0.555556 |        0.722222 |      0.231701 |     0.211334 |     0.259672 |      0.648785 |     0.520594 |     0.728303 |      0.713864 |          nan |          nan |
| GSE163882_TNBC_TPM | combined      | external_zscore_to_internal   |        90 |         0.611111 |        0.510833 |        0.688889 |      0.234608 |     0.210477 |     0.260372 |      0.631579 |     0.513488 |     0.74148  |      0.707764 |          nan |          nan |
| GSE163882_TNBC_TPM | combined      | internal_percentile           |        90 |         0.566667 |        0.4775   |        0.655833 |      0.242155 |     0.207698 |     0.276015 |      0.61083  |     0.515263 |     0.717709 |      0.674309 |          nan |          nan |
| GSE163882_TNBC_TPM | combined      | raw                           |        90 |         0.644444 |        0.533333 |        0.733611 |      0.228155 |     0.193809 |     0.265245 |      0.647773 |     0.516644 |     0.764937 |      0.721259 |          nan |          nan |

## Additional Independent Cohort Checks

Leave-dataset-out validation was added for small TNBC NAC cohorts, especially `GSE18864` and `GSE45898`, by excluding the held-out cohort from training before testing on it. These checks are valuable as independent sensitivity analyses but are underpowered.

|   samples |   positive_rate |   accuracy |    brier |    auroc |    auprc | evaluation        | calibration_method            | feature_set        |   feature_count | train_dataset       | test_dataset   |
|----------:|----------------:|-----------:|---------:|---------:|---------:|:------------------|:------------------------------|:-------------------|----------------:|:--------------------|:---------------|
|        24 |        0.666667 |   0.458333 | 0.25102  | 0.507812 | 0.677773 | leave_dataset_out | raw                           | emt_core           |               5 | all_except_GSE18864 | GSE18864       |
|        24 |        0.666667 |   0.583333 | 0.244633 | 0.5      | 0.636202 | leave_dataset_out | internal_percentile           | emt_core           |               5 | all_except_GSE18864 | GSE18864       |
|        24 |        0.666667 |   0.5      | 0.250725 | 0.507812 | 0.671821 | leave_dataset_out | external_zscore_to_internal   | emt_core           |               5 | all_except_GSE18864 | GSE18864       |
|        24 |        0.666667 |   0.458333 | 0.253274 | 0.492188 | 0.667087 | leave_dataset_out | external_quantile_to_internal | emt_core           |               5 | all_except_GSE18864 | GSE18864       |
|        24 |        0.666667 |   0.541667 | 0.319644 | 0.484375 | 0.68379  | leave_dataset_out | raw                           | emt_tme_resistance |              21 | all_except_GSE18864 | GSE18864       |
|        24 |        0.666667 |   0.625    | 0.28109  | 0.5625   | 0.746593 | leave_dataset_out | internal_percentile           | emt_tme_resistance |              21 | all_except_GSE18864 | GSE18864       |
|        24 |        0.666667 |   0.541667 | 0.311018 | 0.492188 | 0.69004  | leave_dataset_out | external_zscore_to_internal   | emt_tme_resistance |              21 | all_except_GSE18864 | GSE18864       |
|        24 |        0.666667 |   0.583333 | 0.312538 | 0.476562 | 0.668251 | leave_dataset_out | external_quantile_to_internal | emt_tme_resistance |              21 | all_except_GSE18864 | GSE18864       |
|        24 |        0.666667 |   0.375    | 0.290287 | 0.28125  | 0.560643 | leave_dataset_out | raw                           | digital_twin       |               9 | all_except_GSE18864 | GSE18864       |
|        24 |        0.666667 |   0.416667 | 0.300667 | 0.273438 | 0.558707 | leave_dataset_out | internal_percentile           | digital_twin       |               9 | all_except_GSE18864 | GSE18864       |
|        24 |        0.666667 |   0.333333 | 0.298141 | 0.289062 | 0.565108 | leave_dataset_out | external_zscore_to_internal   | digital_twin       |               9 | all_except_GSE18864 | GSE18864       |
|        24 |        0.666667 |   0.333333 | 0.30103  | 0.296875 | 0.562624 | leave_dataset_out | external_quantile_to_internal | digital_twin       |               9 | all_except_GSE18864 | GSE18864       |

## Longitudinal Therapy-Induced EMT Plasticity

`GSE43816` contains seven paired TNBC pre/post-NAC cases. It is used to study state shifts rather than pCR prediction because parsed response labels are unavailable. The analysis supports therapy-induced heterogeneity: some patients show decreased EMT after NAC, while others show increased hybrid/persister or therapy-selection-pressure features.

Transition-prior calibration preview:

|        aEH |      aHE |      aHM |   aEP |   aHP |      aPH |    kE |    kH |       kM |       kP |
|-----------:|---------:|---------:|------:|------:|---------:|------:|------:|---------:|---------:|
| 0.00320824 | 0.785461 | 0.254747 | 0.001 | 0.001 | 0.444672 | 1.267 | 0.001 | 0.899473 | 0.026296 |

## Residual Disease and Recurrence-Axis Biology

`GSE43502` residual chemoresistant TNBC samples were used to rank recurrence-associated EMT/TME/persister axes. These results remain hypothesis-generating because sample size is limited.

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

## Single-Cell Persister and Niche Layer

`GSE164715` marker-panel validation passed 11/11 targeted direction checks. The single-cell layer supports broad targeted compartments but not a full atlas-level cell-type claim.

Ambiguity review preview:

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

## Clinical Usefulness

For clinicians, the current prototype is useful as a research report generator that explains therapy-induced EMT/persister shifts and dominant resistance axes in cohort-relative terms. It may help frame molecular tumor board discussions, identify cases where residual-disease biology is enriched for hypoxia, stromal, immune, or persister features, and communicate uncertainty clearly. It must not be used to choose therapy for an individual patient.

## Research Usefulness

For researchers, the project provides a reproducible scaffold for testing EMT plasticity hypotheses, benchmarking response signatures, comparing platform-normalization strategies, integrating single-cell persister biology, and prioritizing future validation cohorts. The frozen release and pipeline runner make it easier to rerun or extend the analysis as new cohorts become available.

## Limitations

- Retrospective public cohorts have heterogeneous treatments, platforms, and metadata definitions.
- The response endpoint mixes pCR and good-response concepts unless strict pCR fields are used explicitly.
- Cross-platform validation is encouraging but not definitive.
- Single-cell targeted annotation validates broad compartments, not full cell ontology.
- The therapy simulator visualizes plausible state dynamics but is not a calibrated individual tumor-burden forecast.

## Conclusion

The TNBC EMT digital-twin prototype is computationally complete for a research manuscript package. It shows that EMT/TME/persister features can be scored reproducibly, linked to longitudinal therapy-induced state shifts, evaluated in residual-disease biology, and externally validated with platform-aware caution. The next step is expert sign-off and manuscript refinement, not clinical deployment.