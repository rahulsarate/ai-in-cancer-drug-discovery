# How Targets Are Ranked

The target ranker combines seven evidence categories:

1. `emt_state_specificity`
2. `metastatic_association`
3. `druggability`
4. `crispr_dependency`
5. `compound_availability`
6. `normal_tissue_safety`
7. `literature_support`

Each category is min-max normalized and combined with the weights in `configs/target_ranker.yml`.

## Missing evidence

Missing categories are filled with neutral values for scoring, but `evidence_completeness` and `missing_evidence_count` show how much evidence was actually present.

## First-pass interpretation

High-priority targets are not automatically good drug targets. They are candidates for deeper review, including cell-state specificity, assay relevance, normal tissue safety, target tractability, and experimental feasibility.

