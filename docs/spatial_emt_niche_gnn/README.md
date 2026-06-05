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

## Real 10x Breast Cancer Comparison

The first public-data run uses the 10x Genomics **Visium FFPE Human Breast
Cancer** dataset, a breast invasive ductal carcinoma sample analyzed with Space
Ranger 1.3.0. The raw matrix and spatial archives stay under ignored
`data/raw/spatial/10x/`; the workflow writes a signature-gene expression matrix,
metadata, graph outputs, interpretation tables, and comparison report under
`data/processed/`.

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
python scripts/05_interpret_niche_drivers.py `
  --scores data/processed/spatial_emt_niche_gnn_10x_breast/spatial_emt_niche_scores.tsv `
  --edges data/processed/spatial_emt_niche_gnn_10x_breast/spatial_graph_edges.tsv `
  --predictions data/processed/spatial_emt_niche_gnn_10x_breast/emt_niche_predictions.tsv `
  --out-dir data/processed/spatial_emt_niche_gnn_10x_breast
python scripts/06_generate_paper_figures.py `
  --scores data/processed/spatial_emt_niche_gnn_10x_breast/spatial_emt_niche_scores.tsv `
  --edges data/processed/spatial_emt_niche_gnn_10x_breast/spatial_graph_edges.tsv `
  --predictions data/processed/spatial_emt_niche_gnn_10x_breast/emt_niche_predictions.tsv `
  --interpret-dir data/processed/spatial_emt_niche_gnn_10x_breast `
  --out-dir data/processed/spatial_emt_niche_gnn_10x_breast/paper
python scripts/compare_spatial_demo_vs_real.py
```

Current real-run headline:

- 2,518 real tissue spots.
- EMT-niche weak-label fraction: about 25%.
- Tumor-cell EMT candidate fraction: about 10%.
- Stromal-inflated EMT warning fraction: about 15%.
- Real-data graph: 26,811 typed edges, including spatial, hypoxia-gradient, and ligand-receptor-like circuit edges.
- Baseline graph-aware test accuracy: about 0.85 against weak proxy labels.

Interpretation boundary: this is not a validated biological discovery yet. It is
a first real-data comparison showing that the pipeline runs on public Visium
cancer data and produces auditable EMT/stromal/niche outputs.

## Lung, Pancreatic, Prostate, Ovarian, and Colorectal Extensions

The workflow now also supports:

- 10x CytAssist FFPE Human Lung Squamous Cell Carcinoma.
- GEO GSE274103 treatment-naive PDAC Visium FFPE cohort with five samples.
- 10x Visium FFPE Human Prostate Cancer.
- 10x Visium FFPE Human Ovarian Cancer.
- 10x Visium FFPE Human Intestinal/Colorectal Cancer.

```powershell
$env:PYTHONPATH="src"
python scripts/fetch_10x_visium_lung_lusc.py
python scripts/fetch_geo_pdac_gse274103.py
python scripts/fetch_10x_visium_prostate.py
python scripts/fetch_10x_visium_ovarian.py
python scripts/fetch_10x_visium_colorectal.py
```

Then run the same score/graph/train/interpret/figure scripts with the cohort
output folders:

- `data/processed/spatial_emt_niche_gnn_10x_lung_lusc`
- `data/processed/spatial_emt_niche_gnn_geo_pdac`
- `data/processed/spatial_emt_niche_gnn_10x_prostate`
- `data/processed/spatial_emt_niche_gnn_10x_ovarian`
- `data/processed/spatial_emt_niche_gnn_10x_colorectal`

Generate the multi-cancer comparison:

```powershell
$env:PYTHONPATH="src"
python scripts/compare_spatial_cancer_cohorts.py
```

Current multi-cancer summary:

- Breast IDC: 2,518 spots; EMT-niche proxy fraction about 25%; stromal-inflated
  warning about 15%.
- Lung LUSC: 3,858 spots; EMT-niche proxy fraction about 25%; leading prediction
  correlates are partial EMT, hypoxia, stromal risk, and CAF/TAM niche.
- PDAC GSE274103: 23,436 spots across five samples; EMT-niche proxy fraction
  about 25%; leading prediction correlates are CAF/TAM niche, partial EMT,
  stromal risk, immune context, and hypoxia.
- Prostate: 4,371 spots; leading prediction correlates are EMT score,
  CAF/TAM niche, stromal risk, immune context, and partial EMT.
- Ovarian: 3,455 spots; leading prediction correlates are partial EMT,
  immune context, CAF/TAM niche, hypoxia, and ferroptosis-window signal.
- Colorectal: 2,660 spots; leading prediction correlates are partial EMT,
  CAF/TAM niche, stromal risk, hypoxia, and immune context.

Colorectal blocker note: the public 10x Visium HD colorectal binned output is
very large, so this first reproducible pass uses the standard 10x Human
Intestinal/Colorectal Cancer Visium FFPE dataset. The Visium HD data and its
pathologist annotation remain an excellent later validation upgrade.

Pathology/literature interpretation notes live in
`docs/spatial_emt_niche_gnn/pathology_literature_grounding.md`.
