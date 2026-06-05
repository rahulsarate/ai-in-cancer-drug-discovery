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

Still requires prepared public extracts:

- DepMap gene-effect matrices are large and release-specific.
- PRISM drug-response data require compound-to-target mapping.
- LINCS requires constructing EMT reversal signatures and mapping perturbagens to targets.

Use templates under `templates/target_evidence/` to create target-level extracts before feeding them into the ranker.

## CancerSEA/TISCH2/HTAN

Resolved at workflow level:

- `scripts/run_single_cell_validation.py` can score cell x gene or gene x cell matrices.

Still requires downloaded datasets:

- CancerSEA/TISCH2/HTAN expression matrices and metadata must be downloaded or exported locally.
