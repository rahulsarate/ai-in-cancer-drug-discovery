# Unblocking External Data

## TCGA/Xena

Resolved:

- `Survival_SupplementalTable_S1_20171025_xena_sp` can be downloaded through `scripts/download_manifest.py`.

Still heavy:

- `EB++AdjustPANCAN_IlluminaHiSeq_RNASeqV2.geneExp.xena.gz` is the full PanCanAtlas expression matrix. It is large and should remain local under `data/raw/xena/`.

Recommended commands:

```powershell
$env:PYTHONPATH="src"
python scripts/download_manifest.py --group tcga_xena --id tcga_pancan_clinical_cdr --download
python scripts/download_manifest.py --group tcga_xena --id tcga_pancan_rnaseq_pancanatlas --download
python scripts/fetch_signature_gene_aliases.py
python scripts/extract_xena_signature_matrix.py `
  --expression data/raw/xena/EB++AdjustPANCAN_IlluminaHiSeq_RNASeqV2.geneExp.xena.gz `
  --out data/processed/tcga_xena_v1/signature_expression.tsv
python scripts/run_tcga_xena_atlas.py `
  --expression data/processed/tcga_xena_v1/signature_expression.tsv `
  --metadata data/raw/xena/Survival_SupplementalTable_S1_20171025_xena_sp `
  --out-dir data/processed/tcga_xena_v1
```

## Open Targets, ChEMBL, and DGIdb

Resolved:

- `scripts/fetch_public_target_evidence.py` can create small target-level API extracts for Open Targets symbol resolution, ChEMBL compound/activity records, and DGIdb drug-gene interactions.

Recommended commands:

```powershell
$env:PYTHONPATH="src"
python scripts/fetch_public_target_evidence.py --out-dir data/raw/api_evidence
python scripts/build_target_evidence.py `
  --expression data/raw/toy_expression.tsv `
  --emt-scores data/processed/toy_atlas_v1/emt_scores.tsv `
  --metadata data/raw/toy_metadata.tsv `
  --open-targets data/raw/api_evidence/open_targets_emt_metastasis.tsv `
  --chembl data/raw/api_evidence/chembl_target_compounds.tsv `
  --dgidb data/raw/api_evidence/dgidb_interactions.tsv `
  --out-dir data/processed/target_ranker_api_evidence_v1
```

## DepMap, PRISM, and LINCS

Resolved:

- `scripts/fetch_depmap_dependency.py` queries the DepMap download API, downloads the current public CRISPR gene-effect matrix plus model metadata, and writes a target-family-only extract.
- `scripts/fetch_prism_targets.py` downloads the DepMap/PRISM compound table and creates target-family compound evidence.
- `scripts/fetch_lincs_emt_reversal.py` submits an EMT reversal query to L1000FWD and maps perturbagens back to target families when public compound evidence supports the mapping.

Recommended commands:

```powershell
$env:PYTHONPATH="src"
python scripts/fetch_depmap_dependency.py
python scripts/fetch_prism_targets.py
python scripts/fetch_lincs_emt_reversal.py
python scripts/build_target_evidence.py `
  --expression data/processed/tcga_xena_v1/signature_expression.tsv `
  --emt-scores data/processed/tcga_xena_v1/emt_scores.tsv `
  --metadata data/raw/xena/Survival_SupplementalTable_S1_20171025_xena_sp `
  --depmap-gene-effect data/raw/depmap/target_family_CRISPRGeneEffect.csv `
  --open-targets data/raw/api_evidence/open_targets_emt_metastasis.tsv `
  --chembl data/raw/api_evidence/chembl_target_compounds.tsv `
  --dgidb data/raw/api_evidence/dgidb_interactions.tsv `
  --prism data/raw/prism/prism_target_hits.tsv `
  --lincs data/raw/lincs/lincs_target_hits.tsv `
  --out-dir data/processed/target_ranker_real_evidence_v1
```

## CancerSEA/TISCH2/HTAN

Resolved:

- `scripts/run_single_cell_validation.py` can score cell x gene or gene x cell matrices.
- `scripts/fetch_cancersea_validation.py` downloads selected real CancerSEA CTC expression datasets, applies alias mapping for Ensembl-style gene identifiers, scores EMT/TME programs, and writes validation summaries.

Recommended commands:

```powershell
$env:PYTHONPATH="src"
python scripts/fetch_cancersea_validation.py --out-dir data/processed/cancersea_validation
```

Still external:

- TISCH2 and HTAN are supported through the same single-cell scoring interface after export/download, but their portals do not expose one universal no-login bulk matrix endpoint. Add exported matrices under `data/raw/single_cell/` and run `scripts/run_single_cell_validation.py`.

## Human Expert Review

Resolved as a handoff package:

- `scripts/generate_target_review_pack.py` creates a top-target review table from any ranking output.
- The repository now includes `data/processed/target_review/top_target_review_real_evidence.tsv` for the real-evidence run.

Important boundary:

- This is computational triage. A clinician, cancer biologist, or pharmacology expert still needs to review disease context, assay feasibility, safety liabilities, and therapeutic strategy before any wet-lab or translational decision.
