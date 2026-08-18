# External TNBC NAC Response Validation Report

## Feature Availability

| feature_set        |   requested_features |   available_internal_features |   available_external_features | features                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
|:-------------------|---------------------:|------------------------------:|------------------------------:|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| emt_core           |                    5 |                             5 |                             5 | epithelial,mesenchymal,emt_score,partial_emt_score,partial_emt_balance                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| emt_tme_resistance |                   21 |                            21 |                            21 | epithelial,mesenchymal,emt_score,partial_emt_score,partial_emt_balance,stromal_fibroblast,caf,immune_total,t_cell_cytotoxic,tam_spp1,hypoxia,caf_tam_niche,tnbc_axl_tam,tnbc_tgfb,tnbc_yap_taz,tnbc_hypoxia,tnbc_stemness_persister,tnbc_persister_tumor_refined,tnbc_persister_stress_tolerance,tnbc_persister_niche,tnbc_immune_checkpoint                                                                                                                                                                                                                                                        |
| digital_twin       |                    9 |                             9 |                             9 | epithelial_fraction_estimate,hybrid_fraction_estimate,mesenchymal_fraction_estimate,persister_fraction_estimate,plasticity_index,resistant_fraction_estimate,therapy_selection_pressure,residual_disease_probability_proxy,prediction_confidence_proxy                                                                                                                                                                                                                                                                                                                                              |
| combined           |                   30 |                            30 |                            30 | epithelial,mesenchymal,emt_score,partial_emt_score,partial_emt_balance,stromal_fibroblast,caf,immune_total,t_cell_cytotoxic,tam_spp1,hypoxia,caf_tam_niche,tnbc_axl_tam,tnbc_tgfb,tnbc_yap_taz,tnbc_hypoxia,tnbc_stemness_persister,tnbc_persister_tumor_refined,tnbc_persister_stress_tolerance,tnbc_persister_niche,tnbc_immune_checkpoint,epithelial_fraction_estimate,hybrid_fraction_estimate,mesenchymal_fraction_estimate,persister_fraction_estimate,plasticity_index,resistant_fraction_estimate,therapy_selection_pressure,residual_disease_probability_proxy,prediction_confidence_proxy |

## External Metrics

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

## Prediction Preview

| dataset_id         | sample_id   | standard_response         | feature_set   | calibration_method   |   residual_or_poor_response_probability | predicted_response        |
|:-------------------|:------------|:--------------------------|:--------------|:---------------------|----------------------------------------:|:--------------------------|
| GSE163882_TNBC_TPM | GSM4989073  | pcr_or_good_response      | emt_core      | raw                  |                                0.51443  | residual_or_poor_response |
| GSE163882_TNBC_TPM | GSM4989078  | pcr_or_good_response      | emt_core      | raw                  |                                0.488905 | pcr_or_good_response      |
| GSE163882_TNBC_TPM | GSM4989084  | pcr_or_good_response      | emt_core      | raw                  |                                0.450373 | pcr_or_good_response      |
| GSE163882_TNBC_TPM | GSM4989090  | residual_or_poor_response | emt_core      | raw                  |                                0.51896  | residual_or_poor_response |
| GSE163882_TNBC_TPM | GSM4989091  | residual_or_poor_response | emt_core      | raw                  |                                0.514803 | residual_or_poor_response |
| GSE163882_TNBC_TPM | GSM4989092  | residual_or_poor_response | emt_core      | raw                  |                                0.55078  | residual_or_poor_response |
| GSE163882_TNBC_TPM | GSM4989093  | residual_or_poor_response | emt_core      | raw                  |                                0.547468 | residual_or_poor_response |
| GSE163882_TNBC_TPM | GSM4989094  | residual_or_poor_response | emt_core      | raw                  |                                0.508949 | residual_or_poor_response |
| GSE163882_TNBC_TPM | GSM4989095  | residual_or_poor_response | emt_core      | raw                  |                                0.498674 | pcr_or_good_response      |
| GSE163882_TNBC_TPM | GSM4989097  | pcr_or_good_response      | emt_core      | raw                  |                                0.497866 | pcr_or_good_response      |
| GSE163882_TNBC_TPM | GSM4989098  | pcr_or_good_response      | emt_core      | raw                  |                                0.528293 | residual_or_poor_response |
| GSE163882_TNBC_TPM | GSM4989099  | residual_or_poor_response | emt_core      | raw                  |                                0.497656 | pcr_or_good_response      |
| GSE163882_TNBC_TPM | GSM4989100  | pcr_or_good_response      | emt_core      | raw                  |                                0.495241 | pcr_or_good_response      |
| GSE163882_TNBC_TPM | GSM4989101  | residual_or_poor_response | emt_core      | raw                  |                                0.427307 | pcr_or_good_response      |
| GSE163882_TNBC_TPM | GSM4989110  | pcr_or_good_response      | emt_core      | raw                  |                                0.443692 | pcr_or_good_response      |
| GSE163882_TNBC_TPM | GSM4989111  | pcr_or_good_response      | emt_core      | raw                  |                                0.412128 | pcr_or_good_response      |
| GSE163882_TNBC_TPM | GSM4989122  | residual_or_poor_response | emt_core      | raw                  |                                0.405649 | pcr_or_good_response      |
| GSE163882_TNBC_TPM | GSM4989125  | pcr_or_good_response      | emt_core      | raw                  |                                0.514627 | residual_or_poor_response |
| GSE163882_TNBC_TPM | GSM4989126  | residual_or_poor_response | emt_core      | raw                  |                                0.452128 | pcr_or_good_response      |
| GSE163882_TNBC_TPM | GSM4989127  | residual_or_poor_response | emt_core      | raw                  |                                0.456238 | pcr_or_good_response      |

## Interpretation Rules

- External validation must use locked response labels and a held-out dataset not used in model fitting.
- Positive label is `residual_or_poor_response`.
- `raw` uses feature values directly; `internal_percentile` maps train and external features to empirical percentiles relative to the internal training distribution.
- If the external cohort has only one response class, AUROC/AUPRC are not interpretable.
- Results are research validation metrics, not clinical decision support.