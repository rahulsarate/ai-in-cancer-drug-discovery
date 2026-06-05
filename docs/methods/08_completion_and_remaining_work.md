# Completion and Remaining Work

The repository now includes a measurable completion dashboard:

```powershell
$env:PYTHONPATH="src"
python scripts/project_completion.py
python scripts/audit_data_readiness.py
```

## Current interpretation

`emt-state-atlas` is v1 complete for TCGA/Xena public-data execution and includes a real CancerSEA CTC single-cell validation run. TISCH2 and HTAN remain useful external validation extensions once exported matrices are available.

`metastasis-target-ranker` is v1 complete for real DepMap, PRISM, L1000FWD/LINCS-style reversal, Open Targets, ChEMBL, and DGIdb evidence integration. The ranking remains hypothesis-generating and requires expert biological review before wet-lab prioritization.

## What 100% means here

The completion dashboard measures reproducible repository implementation, not clinical validation. Large raw datasets stay local, while small derived summaries, reports, and review packs can be committed.

Completed v1 outputs now include:

- TCGA/Xena pan-cancer EMT atlas summaries and survival associations.
- Real CancerSEA CTC single-cell EMT/TME validation summaries.
- Real DepMap target-family CRISPR dependency extract.
- Real PRISM compound-target extract.
- Real L1000FWD EMT-reversal perturbagen extract.
- Target cards and a structured top-20 review handoff table.

Still external to repository automation:

- TISCH2/HTAN exports, because portal-specific download/export steps vary by dataset.
- Human expert sign-off, because computational review cannot substitute for clinician, cancer biologist, or pharmacology review.
