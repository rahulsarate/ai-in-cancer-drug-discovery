# Manuscript-Ready Results Bundle: TNBC EMT Digital Twin

## Current Manuscript Claim Level

The project supports a research-prototype claim: EMT/TME/persister digital-twin features can be scored reproducibly in TNBC NAC cohorts, show interpretable therapy-induced state shifts, and have encouraging but platform-sensitive external validation on `GSE163882`.

It does not yet support clinical decision-making claims.

## External Validation Metrics

|   samples |   positive_rate |   accuracy |    brier |    auroc |    auprc | evaluation          | calibration_method            | feature_set        |   feature_count | train_dataset             | test_dataset       |
|----------:|----------------:|-----------:|---------:|---------:|---------:|:--------------------|:------------------------------|:-------------------|----------------:|:--------------------------|:-------------------|
|        90 |        0.577778 |   0.511111 | 0.257857 | 0.434211 | 0.582964 | external_validation | raw                           | emt_core           |               5 | internal_geo_deduplicated | GSE163882_TNBC_TPM |
|        90 |        0.577778 |   0.477778 | 0.260752 | 0.444838 | 0.567499 | external_validation | internal_percentile           | emt_core           |               5 | internal_geo_deduplicated | GSE163882_TNBC_TPM |
|        90 |        0.577778 |   0.455556 | 0.254566 | 0.435223 | 0.580112 | external_validation | external_zscore_to_internal   | emt_core           |               5 | internal_geo_deduplicated | GSE163882_TNBC_TPM |
|        90 |        0.577778 |   0.444444 | 0.253432 | 0.447874 | 0.597876 | external_validation | external_quantile_to_internal | emt_core           |               5 | internal_geo_deduplicated | GSE163882_TNBC_TPM |
|        90 |        0.577778 |   0.633333 | 0.229278 | 0.642713 | 0.707881 | external_validation | raw                           | emt_tme_resistance |              21 | internal_geo_deduplicated | GSE163882_TNBC_TPM |
|        90 |        0.577778 |   0.633333 | 0.239377 | 0.610324 | 0.662025 | external_validation | internal_percentile           | emt_tme_resistance |              21 | internal_geo_deduplicated | GSE163882_TNBC_TPM |
|        90 |        0.577778 |   0.6      | 0.237799 | 0.611842 | 0.69175  | external_validation | external_zscore_to_internal   | emt_tme_resistance |              21 | internal_geo_deduplicated | GSE163882_TNBC_TPM |
|        90 |        0.577778 |   0.666667 | 0.234539 | 0.646255 | 0.709051 | external_validation | external_quantile_to_internal | emt_tme_resistance |              21 | internal_geo_deduplicated | GSE163882_TNBC_TPM |
|        90 |        0.577778 |   0.577778 | 0.242047 | 0.584008 | 0.700093 | external_validation | raw                           | digital_twin       |               9 | internal_geo_deduplicated | GSE163882_TNBC_TPM |
|        90 |        0.577778 |   0.511111 | 0.254651 | 0.507085 | 0.626495 | external_validation | internal_percentile           | digital_twin       |               9 | internal_geo_deduplicated | GSE163882_TNBC_TPM |
|        90 |        0.577778 |   0.466667 | 0.249878 | 0.522773 | 0.643652 | external_validation | external_zscore_to_internal   | digital_twin       |               9 | internal_geo_deduplicated | GSE163882_TNBC_TPM |
|        90 |        0.577778 |   0.488889 | 0.24948  | 0.527834 | 0.646858 | external_validation | external_quantile_to_internal | digital_twin       |               9 | internal_geo_deduplicated | GSE163882_TNBC_TPM |
|        90 |        0.577778 |   0.644444 | 0.228155 | 0.647773 | 0.721259 | external_validation | raw                           | combined           |              30 | internal_geo_deduplicated | GSE163882_TNBC_TPM |
|        90 |        0.577778 |   0.566667 | 0.242155 | 0.61083  | 0.674309 | external_validation | internal_percentile           | combined           |              30 | internal_geo_deduplicated | GSE163882_TNBC_TPM |
|        90 |        0.577778 |   0.611111 | 0.234608 | 0.631579 | 0.707764 | external_validation | external_zscore_to_internal   | combined           |              30 | internal_geo_deduplicated | GSE163882_TNBC_TPM |
|        90 |        0.577778 |   0.655556 | 0.231701 | 0.648785 | 0.713864 | external_validation | external_quantile_to_internal | combined           |              30 | internal_geo_deduplicated | GSE163882_TNBC_TPM |

## External Metric Bootstrap Intervals

| dataset_id         | feature_set        | calibration_method            |   samples |   accuracy_point |   accuracy_q025 |   accuracy_q975 |   brier_point |   brier_q025 |   brier_q975 |   auroc_point |   auroc_q025 |   auroc_q975 |   auprc_point |   auprc_q025 |   auprc_q975 |
|:-------------------|:-------------------|:------------------------------|----------:|-----------------:|----------------:|----------------:|--------------:|-------------:|-------------:|--------------:|-------------:|-------------:|--------------:|-------------:|-------------:|
| GSE163882_TNBC_TPM | combined           | external_quantile_to_internal |        90 |         0.655556 |        0.555556 |        0.722222 |      0.231701 |     0.211334 |     0.259672 |      0.648785 |     0.520594 |     0.728303 |      0.713864 |          nan |          nan |
| GSE163882_TNBC_TPM | combined           | external_zscore_to_internal   |        90 |         0.611111 |        0.510833 |        0.688889 |      0.234608 |     0.210477 |     0.260372 |      0.631579 |     0.513488 |     0.74148  |      0.707764 |          nan |          nan |
| GSE163882_TNBC_TPM | combined           | internal_percentile           |        90 |         0.566667 |        0.4775   |        0.655833 |      0.242155 |     0.207698 |     0.276015 |      0.61083  |     0.515263 |     0.717709 |      0.674309 |          nan |          nan |
| GSE163882_TNBC_TPM | combined           | raw                           |        90 |         0.644444 |        0.533333 |        0.733611 |      0.228155 |     0.193809 |     0.265245 |      0.647773 |     0.516644 |     0.764937 |      0.721259 |          nan |          nan |
| GSE163882_TNBC_TPM | digital_twin       | external_quantile_to_internal |        90 |         0.488889 |        0.388611 |        0.600278 |      0.24948  |     0.235146 |     0.264367 |      0.527834 |     0.409224 |     0.651089 |      0.646858 |          nan |          nan |
| GSE163882_TNBC_TPM | digital_twin       | external_zscore_to_internal   |        90 |         0.466667 |        0.3775   |        0.577778 |      0.249878 |     0.233702 |     0.262126 |      0.522773 |     0.436716 |     0.65234  |      0.643652 |          nan |          nan |
| GSE163882_TNBC_TPM | digital_twin       | internal_percentile           |        90 |         0.511111 |        0.410833 |        0.633333 |      0.254651 |     0.232199 |     0.278723 |      0.507085 |     0.381846 |     0.621581 |      0.626495 |          nan |          nan |
| GSE163882_TNBC_TPM | digital_twin       | raw                           |        90 |         0.577778 |        0.5      |        0.666667 |      0.242047 |     0.226316 |     0.25538  |      0.584008 |     0.489435 |     0.704298 |      0.700093 |          nan |          nan |
| GSE163882_TNBC_TPM | emt_core           | external_quantile_to_internal |        90 |         0.444444 |        0.355556 |        0.544444 |      0.253432 |     0.24469  |     0.260159 |      0.447874 |     0.320178 |     0.579815 |      0.597876 |          nan |          nan |
| GSE163882_TNBC_TPM | emt_core           | external_zscore_to_internal   |        90 |         0.455556 |        0.344444 |        0.555556 |      0.254566 |     0.24788  |     0.262126 |      0.435223 |     0.31408  |     0.55623  |      0.580112 |          nan |          nan |
| GSE163882_TNBC_TPM | emt_core           | internal_percentile           |        90 |         0.477778 |        0.377778 |        0.588889 |      0.260752 |     0.248118 |     0.273167 |      0.444838 |     0.33961  |     0.560192 |      0.567499 |          nan |          nan |
| GSE163882_TNBC_TPM | emt_core           | raw                           |        90 |         0.511111 |        0.422222 |        0.622222 |      0.257857 |     0.249182 |     0.265555 |      0.434211 |     0.331802 |     0.560464 |      0.582964 |          nan |          nan |
| GSE163882_TNBC_TPM | emt_tme_resistance | external_quantile_to_internal |        90 |         0.666667 |        0.588611 |        0.766667 |      0.234539 |     0.206307 |     0.261069 |      0.646255 |     0.536547 |     0.767116 |      0.709051 |          nan |          nan |
| GSE163882_TNBC_TPM | emt_tme_resistance | external_zscore_to_internal   |        90 |         0.6      |        0.511111 |        0.688889 |      0.237799 |     0.215677 |     0.262432 |      0.611842 |     0.505926 |     0.73592  |      0.69175  |          nan |          nan |
| GSE163882_TNBC_TPM | emt_tme_resistance | internal_percentile           |        90 |         0.633333 |        0.544167 |        0.744444 |      0.239377 |     0.206764 |     0.274177 |      0.610324 |     0.500038 |     0.737621 |      0.662025 |          nan |          nan |
| GSE163882_TNBC_TPM | emt_tme_resistance | raw                           |        90 |         0.633333 |        0.544444 |        0.722222 |      0.229278 |     0.198205 |     0.256355 |      0.642713 |     0.53029  |     0.750787 |      0.707881 |          nan |          nan |

## Response Label Audit Summary

| dataset_id   | standard_response         | tnbc_confirmed_or_likely   | response_label_confidence   | audit_flag                                  |   samples |
|:-------------|:--------------------------|:---------------------------|:----------------------------|:--------------------------------------------|----------:|
| GSE163882    | pcr_or_good_response      | False                      | high                        | not_tnbc_likely                             |        42 |
| GSE163882    | pcr_or_good_response      | True                       | high                        | ok                                          |        38 |
| GSE163882    | residual_or_poor_response | False                      | high                        | not_tnbc_likely                             |        90 |
| GSE163882    | residual_or_poor_response | True                       | high                        | ok                                          |        52 |
| GSE18864     | pcr_or_good_response      | True                       | high                        | ok                                          |         8 |
| GSE18864     | residual_or_poor_response | True                       | high                        | ok                                          |        16 |
| GSE18864     | unknown                   | True                       | unlabeled                   | missing_standard_response                   |        60 |
| GSE25055     | pcr_or_good_response      | False                      | high                        | not_tnbc_likely                             |        19 |
| GSE25055     | pcr_or_good_response      | False                      | high                        | not_tnbc_likely;residual_text_but_pcr_label |        55 |
| GSE25055     | pcr_or_good_response      | True                       | high                        | ok                                          |        40 |
| GSE25055     | pcr_or_good_response      | True                       | high                        | residual_text_but_pcr_label                 |        13 |
| GSE25055     | residual_or_poor_response | False                      | high                        | not_tnbc_likely                             |       120 |
| GSE25055     | residual_or_poor_response | True                       | high                        | ok                                          |        63 |
| GSE25065     | pcr_or_good_response      | False                      | high                        | not_tnbc_likely                             |        26 |
| GSE25065     | pcr_or_good_response      | False                      | high                        | not_tnbc_likely;residual_text_but_pcr_label |        48 |
| GSE25065     | pcr_or_good_response      | True                       | high                        | ok                                          |        24 |
| GSE25065     | pcr_or_good_response      | True                       | high                        | residual_text_but_pcr_label                 |        22 |
| GSE25065     | residual_or_poor_response | False                      | high                        | not_tnbc_likely                             |        59 |
| GSE25065     | residual_or_poor_response | True                       | high                        | ok                                          |        19 |
| GSE45898     | pcr_or_good_response      | True                       | high                        | ok                                          |         2 |
| GSE45898     | residual_or_poor_response | True                       | high                        | ok                                          |         8 |

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

## Curated-Label Sensitivity Metrics

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

## Additional Leave-Dataset-Out Validation

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
|        24 |        0.666667 |   0.541667 | 0.328623 | 0.46875  | 0.675871 | leave_dataset_out | raw                           | combined           |              30 | all_except_GSE18864 | GSE18864       |
|        24 |        0.666667 |   0.5      | 0.311176 | 0.53125  | 0.751506 | leave_dataset_out | internal_percentile           | combined           |              30 | all_except_GSE18864 | GSE18864       |
|        24 |        0.666667 |   0.583333 | 0.324632 | 0.453125 | 0.665409 | leave_dataset_out | external_zscore_to_internal   | combined           |              30 | all_except_GSE18864 | GSE18864       |
|        24 |        0.666667 |   0.5      | 0.333075 | 0.4375   | 0.67157  | leave_dataset_out | external_quantile_to_internal | combined           |              30 | all_except_GSE18864 | GSE18864       |
|        10 |        0.8      |   0.4      | 0.281785 | 0.1875   | 0.746925 | leave_dataset_out | raw                           | emt_core           |               5 | all_except_GSE45898 | GSE45898       |
|        10 |        0.8      |   0.4      | 0.269346 | 0.25     | 0.765675 | leave_dataset_out | internal_percentile           | emt_core           |               5 | all_except_GSE45898 | GSE45898       |
|        10 |        0.8      |   0.4      | 0.260123 | 0.1875   | 0.746925 | leave_dataset_out | external_zscore_to_internal   | emt_core           |               5 | all_except_GSE45898 | GSE45898       |
|        10 |        0.8      |   0.4      | 0.265103 | 0.125    | 0.684425 | leave_dataset_out | external_quantile_to_internal | emt_core           |               5 | all_except_GSE45898 | GSE45898       |
|        10 |        0.8      |   0.6      | 0.228309 | 0.5      | 0.870139 | leave_dataset_out | raw                           | emt_tme_resistance |              21 | all_except_GSE45898 | GSE45898       |
|        10 |        0.8      |   0.9      | 0.177933 | 0.625    | 0.875546 | leave_dataset_out | internal_percentile           | emt_tme_resistance |              21 | all_except_GSE45898 | GSE45898       |
|        10 |        0.8      |   0.5      | 0.267805 | 0.5      | 0.870139 | leave_dataset_out | external_zscore_to_internal   | emt_tme_resistance |              21 | all_except_GSE45898 | GSE45898       |
|        10 |        0.8      |   0.5      | 0.332278 | 0.5      | 0.880258 | leave_dataset_out | external_quantile_to_internal | emt_tme_resistance |              21 | all_except_GSE45898 | GSE45898       |
|        10 |        0.8      |   0.3      | 0.268073 | 0.25     | 0.788591 | leave_dataset_out | raw                           | digital_twin       |               9 | all_except_GSE45898 | GSE45898       |
|        10 |        0.8      |   0.6      | 0.238997 | 0.4375   | 0.810615 | leave_dataset_out | internal_percentile           | digital_twin       |               9 | all_except_GSE45898 | GSE45898       |
|        10 |        0.8      |   0.4      | 0.261096 | 0.25     | 0.788591 | leave_dataset_out | external_zscore_to_internal   | digital_twin       |               9 | all_except_GSE45898 | GSE45898       |
|        10 |        0.8      |   0.2      | 0.286725 | 0.1875   | 0.746925 | leave_dataset_out | external_quantile_to_internal | digital_twin       |               9 | all_except_GSE45898 | GSE45898       |
|        10 |        0.8      |   0.5      | 0.235963 | 0.5      | 0.880258 | leave_dataset_out | raw                           | combined           |              30 | all_except_GSE45898 | GSE45898       |
|        10 |        0.8      |   0.8      | 0.176545 | 0.625    | 0.875546 | leave_dataset_out | internal_percentile           | combined           |              30 | all_except_GSE45898 | GSE45898       |
|        10 |        0.8      |   0.5      | 0.278765 | 0.5      | 0.880258 | leave_dataset_out | external_zscore_to_internal   | combined           |              30 | all_except_GSE45898 | GSE45898       |
|        10 |        0.8      |   0.5      | 0.387243 | 0.4375   | 0.855258 | leave_dataset_out | external_quantile_to_internal | combined           |              30 | all_except_GSE45898 | GSE45898       |

## GSE164715 Marker-Panel Validation

| targeted_annotation   | expected_marker_score        |   annotation_mean |   other_annotations_mean |   marker_margin | passes_direction_check   |
|:----------------------|:-----------------------------|------------------:|-------------------------:|----------------:|:-------------------------|
| malignant_like        | epithelial                   |         0.31546   |              -0.190903   |       0.506364  | True                     |
| malignant_like        | mesenchymal                  |         0.0547747 |              -0.00347497 |       0.0582496 | True                     |
| malignant_like        | tnbc_persister_tumor_refined |         0.173028  |              -0.0739859  |       0.247014  | True                     |
| endothelial_like      | angiogenesis                 |         0.496414  |              -0.0540032  |       0.550417  | True                     |
| endothelial_like      | tnbc_persister_niche         |         0.530986  |              -0.0582813  |       0.589268  | True                     |
| stromal_like          | stromal_fibroblast           |         0.385331  |              -0.0479572  |       0.433288  | True                     |
| stromal_like          | caf                          |         0.412136  |              -0.0426362  |       0.454772  | True                     |
| stromal_like          | ecm_remodeling               |         0.234543  |              -0.0237791  |       0.258322  | True                     |
| immune_like           | immune_total                 |         0.560762  |              -0.0478486  |       0.608611  | True                     |
| immune_like           | t_cell_cytotoxic             |         0.398417  |              -0.0344463  |       0.432864  | True                     |
| immune_like           | tam_spp1                     |         0.721425  |              -0.0597413  |       0.781166  | True                     |

## Reproducibility

Run the complete local pipeline with:

```powershell
python scripts\run_tnbc_digital_twin_pipeline.py --skip-existing
```

For fresh data downloads and long scRNA import steps, add `--include-downloads --include-scrna`.

## Remaining Before Submission

1. Final expert/author review of locked response-label curation decisions.
2. Final expert/author review of GSE164715 ambiguity language.
3. Manuscript polishing, citation formatting, and journal/thesis formatting.
4. Additional external cohorts remain valuable but are no longer required for a research-prototype manuscript claim.