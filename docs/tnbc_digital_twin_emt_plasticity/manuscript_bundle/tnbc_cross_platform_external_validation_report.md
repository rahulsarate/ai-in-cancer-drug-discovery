# Cross-Platform External TNBC NAC Validation Report

## Scope

This report is restricted to held-out external validation where the training data and test data come from different cohorts/platform contexts. Current external cohort: `GSE163882_TNBC_TPM` RNA-seq TPM data.

## Raw Versus Percentile-Calibrated Metrics

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

## Largest Platform/Feature Shifts

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
| persister_fraction_estimate     |                -0.243165  |       0.195455 | 0.00627443  |
| partial_emt_score               |                 0.136032  |       0.193434 | 0.00706016  |
| emt_score                       |                -0.351538  |       0.191414 | 0.00793438  |
| epithelial_fraction_estimate    |                 0.270323  |       0.181818 | 0.0135816   |

## Interpretation

- `raw` validation uses feature values directly.
- `internal_percentile` maps features to empirical percentiles relative to the internal training distribution.
- Performance that changes substantially after percentile calibration is likely sensitive to platform/cohort distribution shift.
- These are external research-validation metrics, not clinical decision-support performance claims.