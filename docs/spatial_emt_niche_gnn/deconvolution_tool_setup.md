# Deconvolution Tool Setup

## Current State

The project now has a real PDAC scRNA-derived marker-assigned reference from
GSE154778 and an NNLS deconvolution run against the GSE274557 matched Pt-1
spatial pilot.

The current Windows Python 3.14 runtime is no longer the recommended runtime
for advanced spatial deconvolution. A dedicated Python 3.10 environment now
exists at `.venv-deconv`, and a project-local R library exists at `.r-lib`.

Installed and import-verified in `.venv-deconv`:

- anndata
- scanpy
- PyTorch CPU
- Tangram
- cell2location
- HuggingFace Hub
- Synapse client

Note: cell2location imports successfully, but full model training should still
be treated as a heavier run. Prefer WSL/Linux or GPU-backed execution for
publication-scale training.

Installed and import-verified in local R:

- R 4.6.0
- Bioconductor `spacexr 1.4.0`

## Recommended Environment

Use the existing project environment or rebuild it with:

```text
py -3.10 -m venv .venv-deconv
.venv-deconv\Scripts\python.exe -m pip install scanpy anndata torch tangram-sc cell2location huggingface_hub synapseclient
```

For RCTD/spacexr:

```text
winget install --id RProject.R --exact
$env:R_LIBS_USER=(Resolve-Path .r-lib).Path
& "C:\Program Files\R\R-4.6.0\bin\Rscript.exe" -e "install.packages('BiocManager'); BiocManager::install('spacexr')"
```

## Inputs Already Available

- Spatial expression:
  `data/processed/spatial_emt_niche_gnn_geo_met_pdac_gse274557/geo_met_pdac_gse274557_signature_expression.tsv`
- Spatial metadata:
  `data/processed/spatial_emt_niche_gnn_geo_met_pdac_gse274557/geo_met_pdac_gse274557_spatial_metadata.tsv`
- Real scRNA-derived reference:
  `data/processed/spatial_emt_niche_gnn_references/gse154778/gse154778_scrna_marker_reference.tsv`
- NNLS deconvolution summary:
  `data/processed/spatial_emt_niche_gnn_geo_met_pdac_gse274557/gse154778_scrna_deconv/reference_deconvolution_nnls_summary.tsv`

## Next Run Order

1. Use NNLS as the sanity check baseline.
2. Export the reference/spatial tables to h5ad.
3. Run Tangram first because it is installed and import-verified.
4. Run RCTD/spacexr to cross-check spot mixture estimates.
5. Run cell2location after validating the same input, preferably in WSL/Linux or a GPU-backed environment for full-scale training.
