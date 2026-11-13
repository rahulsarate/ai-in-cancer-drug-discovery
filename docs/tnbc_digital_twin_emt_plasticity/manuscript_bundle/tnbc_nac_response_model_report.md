# TNBC NAC Response Model Report

## Cohort Summary

| dataset_id   | standard_response         |   samples |
|:-------------|:--------------------------|----------:|
| GSE18864     | pcr_or_good_response      |         8 |
| GSE18864     | residual_or_poor_response |        16 |
| GSE25055     | pcr_or_good_response      |        40 |
| GSE25055     | residual_or_poor_response |        76 |
| GSE25065     | pcr_or_good_response      |        24 |
| GSE25065     | residual_or_poor_response |        41 |
| GSE45898     | pcr_or_good_response      |         2 |
| GSE45898     | residual_or_poor_response |         8 |

## Model Metrics

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

## Top Discovery-to-Validation Coefficients

| feature_set        | feature                         |   coefficient |
|:-------------------|:--------------------------------|--------------:|
| emt_core           | partial_emt_balance             |    -0.231517  |
| emt_core           | mesenchymal                     |     0.112719  |
| emt_core           | partial_emt_score               |    -0.0596576 |
| emt_core           | epithelial                      |     0.0485857 |
| emt_core           | emt_score                       |     0.028181  |
| emt_tme_resistance | caf                             |     0.612554  |
| emt_tme_resistance | tnbc_yap_taz                    |    -0.522303  |
| emt_tme_resistance | tnbc_hypoxia                    |    -0.47052   |
| emt_tme_resistance | immune_total                    |    -0.428175  |
| emt_tme_resistance | caf_tam_niche                   |     0.386924  |
| emt_tme_resistance | hypoxia                         |     0.325855  |
| emt_tme_resistance | tnbc_persister_niche            |    -0.217075  |
| emt_tme_resistance | tnbc_persister_stress_tolerance |    -0.165759  |
| emt_tme_resistance | tnbc_stemness_persister         |    -0.155929  |
| emt_tme_resistance | mesenchymal                     |    -0.13801   |
| emt_tme_resistance | partial_emt_score               |    -0.130546  |
| emt_tme_resistance | stromal_fibroblast              |    -0.128471  |
| emt_tme_resistance | tnbc_tgfb                       |    -0.0831723 |
| emt_tme_resistance | tnbc_axl_tam                    |     0.075075  |
| emt_tme_resistance | partial_emt_balance             |    -0.0698226 |
| emt_tme_resistance | emt_score                       |    -0.0631372 |
| emt_tme_resistance | t_cell_cytotoxic                |     0.0563234 |
| emt_tme_resistance | tnbc_persister_tumor_refined    |     0.0474342 |
| emt_tme_resistance | tam_spp1                        |    -0.0423918 |
| emt_tme_resistance | epithelial                      |    -0.0153576 |

## Interpretation Rules

- Positive label is residual disease or poor response.
- These are first-pass research models, not clinical decision tools.
- `GSE25066` is a superseries overlapping `GSE25055` and `GSE25065`; deduplicated modeling keeps subseries rows first.
- The strongest immediate validation comparison is train on `GSE25055` and test on `GSE25065`.