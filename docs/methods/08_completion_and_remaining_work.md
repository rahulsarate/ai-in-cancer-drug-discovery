# Completion and Remaining Work

The repository now includes a measurable completion dashboard:

```powershell
$env:PYTHONPATH="src"
python scripts/project_completion.py
python scripts/audit_data_readiness.py
```

## Current interpretation

`emt-state-atlas` is code-complete for v1 public-data execution, but not scientifically complete until the full TCGA/Xena run and single-cell validation are performed.

`metastasis-target-ranker` is code-complete for v1 evidence integration and reporting, but not scientifically complete until real DepMap, Open Targets, ChEMBL, DGIdb, PRISM, and LINCS extracts are integrated.

## Why percentages are not 100%

The missing pieces require large external datasets or manual expert review:

- TCGA/Xena pan-cancer expression and survival files.
- CancerSEA/TISCH2/HTAN single-cell validation data.
- DepMap CRISPR dependency matrix.
- PRISM/LINCS drug response and perturbation extracts.
- Open Targets/ChEMBL/DGIdb target evidence extracts.
- Manual review of top target cards.

These should remain local or be summarized into small derived outputs before GitHub release.

