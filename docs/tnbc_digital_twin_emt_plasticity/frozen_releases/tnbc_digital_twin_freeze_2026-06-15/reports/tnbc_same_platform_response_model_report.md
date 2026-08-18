# Same-Platform TNBC NAC Response Model Report

## Scope

This report separates internal same-platform response modeling from cross-platform external validation. The strongest same-platform comparison remains training on `GSE25055` and testing on `GSE25065`.

## Metrics

| validation_scope                           | feature_set        |   samples |   positive_rate |    auroc |    auprc |   accuracy |    brier | train_dataset    | test_dataset     |
|:-------------------------------------------|:-------------------|----------:|----------------:|---------:|---------:|-----------:|---------:|:-----------------|:-----------------|
| internal_deduplicated_cv                   | emt_core           |       215 |        0.493023 | 0.430673 | 0.446188 |   0.47907  | 0.261982 | all_deduplicated | all_deduplicated |
| same_platform_train_gse25055_test_gse25065 | emt_core           |        65 |        0.292308 | 0.392449 | 0.270282 |   0.430769 | 0.263566 | GSE25055         | GSE25065         |
| internal_deduplicated_cv                   | emt_tme_resistance |       215 |        0.493023 | 0.530725 | 0.540373 |   0.493023 | 0.271116 | all_deduplicated | all_deduplicated |
| same_platform_train_gse25055_test_gse25065 | emt_tme_resistance |        65 |        0.292308 | 0.514874 | 0.333694 |   0.492308 | 0.27514  | GSE25055         | GSE25065         |
| internal_deduplicated_cv                   | digital_twin       |       215 |        0.493023 | 0.474987 | 0.482125 |   0.493023 | 0.264231 | all_deduplicated | all_deduplicated |
| same_platform_train_gse25055_test_gse25065 | digital_twin       |        65 |        0.292308 | 0.529748 | 0.315979 |   0.507692 | 0.261067 | GSE25055         | GSE25065         |
| internal_deduplicated_cv                   | combined           |       215 |        0.493023 | 0.473516 | 0.506838 |   0.446512 | 0.292785 | all_deduplicated | all_deduplicated |
| same_platform_train_gse25055_test_gse25065 | combined           |        65 |        0.292308 | 0.459954 | 0.337478 |   0.476923 | 0.286862 | GSE25055         | GSE25065         |

## Interpretation

- These metrics estimate internal retrospective performance across GEO cohorts already used in model development.
- Same-platform results should not be mixed with RNA-seq external validation metrics.
- Positive label is `residual_or_poor_response`.