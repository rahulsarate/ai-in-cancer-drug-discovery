# EMT Metastasis AI

This repository is a public-data research starter kit for two linked projects:

1. **emt-state-atlas**: score EMT, partial EMT, stromal contamination, immune context, hypoxia, CAF/TAM niches, and survival associations across TCGA-style bulk RNA-seq and single-cell summaries.
2. **metastasis-target-ranker**: prioritize susceptible metastasis/EMT targets by integrating EMT-state specificity, metastatic association, druggability, CRISPR dependency, public compound availability, normal-tissue safety risk, and literature support.
3. **spatial-emt-niche-gnn**: map EMT-permissive spatial niches with Visium/HEST/HTAN-style spot graphs, stromal-contamination controls, weak-label-aware graph learning, and edge-ablation interpretability.

The project is designed for reproducible GitHub work. Large datasets are not committed. Place public data under `data/raw/`, run pipelines, and write outputs to `data/processed/`.

## Quick Start

```powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
pip install -e ".[dev,survival]"
pytest
```

Score an expression matrix:

```powershell
emt-score --expression data/raw/example_expression.tsv --metadata data/raw/example_metadata.tsv --out data/processed/emt_scores.tsv
```

Rank targets:

```powershell
rank-metastasis-targets --config configs/target_ranker.yml --out data/processed/target_ranking.tsv
```

## Input Format

Expression matrices can be either genes x samples or samples x genes. The scorer detects orientation by matching known signature genes. Metadata should contain `sample_id`; survival analysis additionally expects `time` and `event` columns.

## Recommended First Build

1. Download TCGA pan-cancer expression and phenotype data from UCSC Xena or GDC.
2. Score epithelial, mesenchymal, partial EMT, stromal, immune, CAF, TAM, and hypoxia programs.
3. Benchmark EMT scores against survival and metastatic labels where available.
4. Add single-cell/scRNA references from CancerSEA, TISCH2, HTAN, and GEO.
5. Feed EMT-high and partial-EMT target evidence into the target ranker.

See `docs/literature/` and `docs/methods/` for the scientific rationale and implementation notes.

## Spatial EMT Niche GNN

The spatial project starts with a runnable synthetic demo and expands to 10x Visium, HEST-1k, HTAN, and GEO cohorts:

```powershell
$env:PYTHONPATH="src"
python scripts/01_download_public_spatial_data.py --make-demo
python scripts/02_score_spatial_emt_niches.py `
  --expression data/processed/spatial_emt_niche_gnn_demo/demo_spatial_expression.tsv `
  --metadata data/processed/spatial_emt_niche_gnn_demo/demo_spatial_metadata.tsv
python scripts/03_build_spatial_graphs.py `
  --scores data/processed/spatial_emt_niche_gnn_demo/spatial_emt_niche_scores.tsv
python scripts/04_train_gnn.py `
  --scores data/processed/spatial_emt_niche_gnn_demo/spatial_emt_niche_scores.tsv `
  --edges data/processed/spatial_emt_niche_gnn_demo/spatial_graph_edges.tsv
python scripts/05_interpret_niche_drivers.py `
  --scores data/processed/spatial_emt_niche_gnn_demo/spatial_emt_niche_scores.tsv `
  --edges data/processed/spatial_emt_niche_gnn_demo/spatial_graph_edges.tsv `
  --predictions data/processed/spatial_emt_niche_gnn_demo/emt_niche_predictions.tsv
python scripts/06_generate_paper_figures.py `
  --scores data/processed/spatial_emt_niche_gnn_demo/spatial_emt_niche_scores.tsv `
  --edges data/processed/spatial_emt_niche_gnn_demo/spatial_graph_edges.tsv `
  --predictions data/processed/spatial_emt_niche_gnn_demo/emt_niche_predictions.tsv `
  --interpret-dir data/processed/spatial_emt_niche_gnn_demo
```

See `docs/spatial_emt_niche_gnn/README.md`.

Real 10x breast cancer comparison:

```powershell
$env:PYTHONPATH="src"
python scripts/fetch_10x_visium_breast_cancer.py
python scripts/02_score_spatial_emt_niches.py `
  --expression data/processed/spatial_emt_niche_gnn_10x_breast/10x_breast_cancer_signature_expression.tsv `
  --metadata data/processed/spatial_emt_niche_gnn_10x_breast/10x_breast_cancer_spatial_metadata.tsv `
  --out-dir data/processed/spatial_emt_niche_gnn_10x_breast
python scripts/03_build_spatial_graphs.py `
  --scores data/processed/spatial_emt_niche_gnn_10x_breast/spatial_emt_niche_scores.tsv `
  --out-dir data/processed/spatial_emt_niche_gnn_10x_breast
python scripts/04_train_gnn.py `
  --scores data/processed/spatial_emt_niche_gnn_10x_breast/spatial_emt_niche_scores.tsv `
  --edges data/processed/spatial_emt_niche_gnn_10x_breast/spatial_graph_edges.tsv `
  --out-dir data/processed/spatial_emt_niche_gnn_10x_breast
python scripts/compare_spatial_demo_vs_real.py
```

Additional lung and pancreatic spatial cohorts:

```powershell
$env:PYTHONPATH="src"
python scripts/fetch_10x_visium_lung_lusc.py
python scripts/fetch_geo_pdac_gse274103.py
python scripts/fetch_10x_visium_prostate.py
python scripts/fetch_10x_visium_ovarian.py
python scripts/fetch_10x_visium_colorectal.py
python scripts/compare_spatial_cancer_cohorts.py
```

See `docs/spatial_emt_niche_gnn/pathology_literature_grounding.md` for pathology and literature interpretation rules before treating EMT-niche outputs as biological hypotheses.

## Real-Data v1 Workflow

List public data sources and exact expected local paths:

```powershell
python scripts/download_manifest.py
```

Run the TCGA/Xena atlas after placing expression and phenotype files locally:

```powershell
$env:PYTHONPATH="src"
python scripts/fetch_signature_gene_aliases.py
python scripts/extract_xena_signature_matrix.py `
  --expression data/raw/xena/EB++AdjustPANCAN_IlluminaHiSeq_RNASeqV2.geneExp.xena.gz `
  --out data/processed/tcga_xena_v1/signature_expression.tsv
python scripts/run_tcga_xena_atlas.py `
  --expression data/processed/tcga_xena_v1/signature_expression.tsv `
  --metadata data/raw/xena/Survival_SupplementalTable_S1_20171025_xena_sp `
  --out-dir data/processed/tcga_xena_v1
```

Build target-ranker evidence and reports:

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

The same command accepts optional DepMap, PRISM, LINCS, Open Targets, ChEMBL, and DGIdb target-level extracts. See `configs/public_data_manifest.json`.

## Completion and Readiness

Calculate project completion and local public-data readiness:

```powershell
$env:PYTHONPATH="src"
python scripts/project_completion.py
python scripts/audit_data_readiness.py
```

Target evidence extract templates live in `templates/target_evidence/`.

Fetch small API-based evidence extracts for Open Targets, ChEMBL, and DGIdb:

```powershell
$env:PYTHONPATH="src"
python scripts/fetch_public_target_evidence.py --out-dir data/raw/api_evidence
```

Then pass those extracts into the target evidence builder:

```powershell
$env:PYTHONPATH="src"
python scripts/build_target_evidence.py `
  --expression data/raw/toy_expression.tsv `
  --emt-scores data/processed/toy_atlas_v1/emt_scores.tsv `
  --metadata data/raw/toy_metadata.tsv `
  --open-targets data/raw/api_evidence/open_targets_emt_metastasis.tsv `
  --chembl data/raw/api_evidence/chembl_target_compounds.tsv `
  --dgidb data/raw/api_evidence/dgidb_interactions.tsv `
  --out-dir data/processed/target_ranker_api_evidence_v1
```

Run single-cell validation once a CancerSEA/TISCH2/HTAN-style cell matrix is available:

```powershell
$env:PYTHONPATH="src"
python scripts/run_single_cell_validation.py `
  --expression data/raw/single_cell/example_expression.tsv `
  --metadata data/raw/single_cell/example_metadata.tsv `
  --out-dir data/processed/single_cell_validation
```

Fetch and score real CancerSEA CTC datasets:

```powershell
$env:PYTHONPATH="src"
python scripts/fetch_cancersea_validation.py --out-dir data/processed/cancersea_validation
```

Manual target-review templates live in `templates/target_review/`.

Generate a computational review pack from a target ranking:

```powershell
$env:PYTHONPATH="src"
python scripts/generate_target_review_pack.py `
  --ranking data/processed/target_ranker_real_evidence_v1/target_ranking.tsv `
  --out data/processed/target_review/top_target_review_real_evidence.tsv
```

The review pack is a structured human-review handoff, not a replacement for clinician or disease-area expert sign-off.

## Environment Notes

If your system Python is too new for scientific wheels, use a Python 3.10-3.12 environment or the bundled Codex runtime. Minimum required runtime packages are `numpy` and `pandas`; plots need `matplotlib` and `seaborn`; Cox survival analysis needs `lifelines`.
