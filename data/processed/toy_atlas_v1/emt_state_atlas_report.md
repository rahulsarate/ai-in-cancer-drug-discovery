# EMT State Atlas Report

This report summarizes EMT, stromal, immune, CAF/TAM, hypoxia, and ferroptosis-window signals.

Interpret all results as research hypotheses. Bulk EMT scores can be inflated by stromal/fibroblast signal.

## Dataset Overview

- Samples scored: 30
- Cancer types: 1
- EMT-high samples: 8
- Stromal-inflated EMT candidates: 0

## Top Cancer Types by Mean EMT Score

| cancer_type | emt_score_mean | partial_emt_score_mean | stromal_fibroblast_mean | caf_tam_niche_mean |
| --- | --- | --- | --- | --- |
| toy | -1.37e-16 | -0.393 | 1.22e-16 | 0 |

## Survival Associations

| score | method | n | events | high_group_median_time | low_group_median_time | logrank_chi2 | p |
| --- | --- | --- | --- | --- | --- | --- | --- |
| emt_score | median_split_logrank_fallback | 30 | 15 | 1.2e+03 | 972 | 0.897 | 0.343 |
| partial_emt_score | median_split_logrank_fallback | 30 | 15 | 1.2e+03 | 972 | 0.84 | 0.359 |
| stromal_fibroblast | median_split_logrank_fallback | 30 | 15 | 1.13e+03 | 1.14e+03 | 0.0525 | 0.819 |
| immune_total | median_split_logrank_fallback | 30 | 15 | 935 | 1.21e+03 | 0.44 | 0.507 |
| caf_tam_niche | median_split_logrank_fallback | 30 | 15 | 876 | 1.2e+03 | 1.62 | 0.204 |

## Plots

No plots were written because plotting dependencies were unavailable or required columns were missing.
