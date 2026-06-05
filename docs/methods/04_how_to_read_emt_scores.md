# How to Read EMT Scores

## Main scores

- `epithelial`: high values suggest epithelial adhesion and keratin programs.
- `mesenchymal`: high values suggest motility, matrix remodeling, and invasion programs.
- `emt_score`: mesenchymal minus epithelial. High values suggest a mesenchymal-shifted sample.
- `partial_emt_score`: the lower of epithelial and mesenchymal scores. High values suggest coexistence of epithelial and mesenchymal programs.
- `partial_emt_balance`: highest when epithelial and mesenchymal scores are balanced.

## Microenvironment scores

- `stromal_fibroblast`: fibroblast/stromal matrix signal.
- `stromal_contamination_risk`: percentile version of the stromal score.
- `immune_total`: immune-cell signal.
- `caf_tam_niche`: combined CAF and macrophage niche signal.
- `hypoxia`: low-oxygen stress program.

## Vulnerability score

- `ferroptosis_window`: ferroptosis-sensitivity program minus ferroptosis-resistance program.

## Important interpretation rule

Bulk RNA-seq EMT is not automatically tumor-cell EMT. If `emt_score` and `stromal_contamination_risk` are both high, the signal may reflect CAF/fibroblast content. Prioritize samples with high `emt_score` but lower stromal risk for tumor-cell-intrinsic EMT hypotheses.

