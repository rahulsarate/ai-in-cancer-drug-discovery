# Next Experiments

## Experiment 1: TCGA EMT state scoring

Question: Which cancer types show strong EMT, partial EMT, stromal contamination, CAF/TAM niche, hypoxia, and ferroptosis-window scores?

Plan:

1. Download TCGA pan-cancer expression and phenotype data.
2. Run `emt-score`.
3. Stratify by cancer type.
4. Run Cox survival models per score.
5. Flag cancer types where EMT score and stromal score diverge.

Deliverable:

- Pan-cancer EMT score heatmap.
- Cancer-type survival table.
- List of cancer types suitable for single-cell follow-up.

## Experiment 2: Single-cell EMT validation

Question: Do the bulk signatures map to malignant-cell EMT states rather than CAF contamination?

Plan:

1. Select CancerSEA/TISCH2 datasets with malignant-cell annotations.
2. Score cells with the same signatures.
3. Compare epithelial, partial EMT, and mesenchymal groups.
4. Summarize target expression by state.

Deliverable:

- Single-cell state confusion matrix.
- Gene-state specificity table for target ranker.

## Experiment 3: Target evidence integration

Question: Which targets score highly across EMT-state specificity, metastasis association, druggability, dependency, compound availability, safety, and literature?

Plan:

1. Build evidence tables for the seven target-ranker categories.
2. Run `rank-metastasis-targets`.
3. Review top 20 targets manually.
4. Split targets into immediate, exploratory, and risky categories.

Deliverable:

- Ranked target table.
- Evidence cards for top targets.

