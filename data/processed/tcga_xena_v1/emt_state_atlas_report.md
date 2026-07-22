# EMT State Atlas Report

This report summarizes EMT, stromal, immune, CAF/TAM, hypoxia, and ferroptosis-window signals.

Interpret all results as research hypotheses. Bulk EMT scores can be inflated by stromal/fibroblast signal.

## Dataset Overview

- Samples scored: 11069
- Cancer types: 33
- EMT-high samples: 2768
- Stromal-inflated EMT candidates: 833

## Top Cancer Types by Mean EMT Score

| cancer_type | emt_score_mean | partial_emt_score_mean | stromal_fibroblast_mean | caf_tam_niche_mean |
| --- | --- | --- | --- | --- |
| SARC | 2.31 | -1.35 | 0.945 | 0.657 |
| GBM | 1.77 | -1.49 | -0.19 | 0.185 |
| SKCM | 1.67 | -1.37 | -0.182 | 0.112 |
| DLBC | 1.38 | -1.59 | -0.0916 | 0.192 |
| ACC | 1.34 | -1.45 | -0.608 | -0.484 |
| PCPG | 1.34 | -1.54 | -0.35 | -0.384 |
| MESO | 1.08 | -0.379 | 0.756 | 0.753 |
| UVM | 0.903 | -1.37 | -1.27 | -0.61 |
| LGG | 0.886 | -1.55 | -0.988 | -0.597 |
| UCS | 0.614 | -0.181 | 0.377 | 0.0905 |

## Survival Associations

| score | method | n | events | high_group_median_time | low_group_median_time | logrank_chi2 | p |
| --- | --- | --- | --- | --- | --- | --- | --- |
| emt_score | median_split_logrank_fallback | 1.1e+04 | 3.28e+03 | 722 | 763 | 145 | 2.07e-33 |
| partial_emt_score | median_split_logrank_fallback | 1.1e+04 | 3.28e+03 | 719 | 767 | 3.99 | 0.0458 |
| stromal_fibroblast | median_split_logrank_fallback | 1.1e+04 | 3.28e+03 | 718 | 764 | 45.1 | 1.84e-11 |
| immune_total | median_split_logrank_fallback | 1.1e+04 | 3.28e+03 | 753 | 734 | 2.16 | 0.141 |
| caf_tam_niche | median_split_logrank_fallback | 1.1e+04 | 3.28e+03 | 714 | 771 | 84 | 4.88e-20 |

## Plots

- emt_vs_stromal.png
- partial_emt_distribution.png
- niche_heatmap.png
- ferroptosis_window_top.png
