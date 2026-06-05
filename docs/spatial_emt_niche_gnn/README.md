# Spatial EMT Niche GNN

## Aim

Build a spatial graph learning workflow that maps EMT and partial-EMT tumor
niches, separates tumor-cell EMT from stromal contamination, and ranks
microenvironment circuits that may support invasion and metastasis.

## First Deliverable

The MVP is intentionally executable before large public datasets are downloaded:

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

## Risk Controls

- Spatial preprocessing is hard: use a manifest and standard `spot_id`, `x`, `y`,
  `cohort`, `sample_id`, and `section_id` columns.
- EMT can be stromal contamination: preserve `stromal_inflated_emt_candidate`
  separately from `tumor_cell_emt_candidate`.
- Labels are weak: use `emt_niche_proxy_score`, `emt_niche_label`,
  `label_strength`, and `weak_label_source` columns explicitly.
- Cross-cohort batch effects: keep cohort metadata and use `--holdout-cohort`
  once multiple cohorts are present.
- Interpretability is essential: generate edge-type summaries, edge ablations,
  and feature-perturbation reports.

## Data Expansion Plan

Start with 10x Visium public cancer examples and selected HEST-1k cancer cohorts.
Then add HTAN and GEO exports through dataset-specific adapters. Raw datasets
remain local under `data/raw/spatial/`; only small derived tables should be
committed.
