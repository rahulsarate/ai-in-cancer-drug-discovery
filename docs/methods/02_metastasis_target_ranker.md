# Metastasis Target Ranker

## Goal

Prioritize susceptible EMT/metastasis targets using interpretable evidence categories:

- EMT-state specificity
- metastatic association
- druggability
- CRISPR dependency
- public compound availability
- normal tissue safety risk
- literature support

## Evidence table format

Each evidence table should contain:

```text
target<TAB>evidence_column
AXL<TAB>0.92
TGFBR1<TAB>0.80
```

The current implementation expects normalized or raw numeric values. It min-max normalizes each category internally.

## Evidence construction ideas

### EMT-state specificity

Score a target by differential expression or dependency in EMT-high/partial-EMT samples versus EMT-low samples.

Public sources:

- TCGA/Xena expression
- CancerSEA functional states
- TISCH2 malignant-cell subsets
- DepMap/CCLE expression

### Metastatic association

Score by association with metastatic samples, stage, invasion signatures, recurrence, or poor survival.

Public sources:

- TCGA clinical endpoints
- cBioPortal metastatic cohorts
- GEO primary/metastasis comparisons
- CancerSEA metastasis/invasion states

### Druggability

Score by known tractability, small-molecule or antibody feasibility, and target class.

Public sources:

- Open Targets
- ChEMBL
- DGIdb

### CRISPR dependency

Score by selective dependency in EMT-high cancer cell lines while penalizing pan-essential genes.

Public sources:

- DepMap Achilles
- Sanger Project Score
- BioGRID ORCS

### Public compound availability

Score by number and quality of compounds with usable public bioactivity or perturbation data.

Public sources:

- ChEMBL
- PRISM
- LINCS/CLUE
- DGIdb

### Normal tissue safety risk

Prefer targets with lower normal-tissue essentiality or more selective tumor-state dependence. High expression in critical normal tissues should reduce priority.

Public sources:

- Open Targets safety
- Human Protein Atlas
- GTEx
- DepMap pan-essentiality

### Literature support

Score by curated evidence for EMT, invasion, metastasis, therapy resistance, immune evasion, or clinical trials.

Public sources:

- PubMed
- Open Targets literature evidence
- ClinicalTrials.gov

## Pros

- Produces transparent ranked hypotheses rather than black-box answers.
- Easy to update as new datasets arrive.
- Can be published as a community resource.
- Can support wet-lab prioritization.

## Cons

- Evidence categories are heterogeneous.
- Public data are biased toward proliferation and primary tumors.
- Literature support can overvalue popular targets.
- Normal tissue safety is difficult to infer from public tumor datasets alone.

