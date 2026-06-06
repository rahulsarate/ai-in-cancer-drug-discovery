# Deconvolution Tool Setup

## Current State

The project now has a real PDAC scRNA-derived marker-assigned reference from
GSE154778 and an NNLS deconvolution run against the GSE274557 matched Pt-1
spatial pilot.

The following advanced tools are not installed in the current Windows Python
3.14 environment:

- cell2location
- Tangram
- Scanpy/AnnData
- PyTorch
- R/RCTD

## Recommended Environment

Use a separate conda or micromamba environment instead of the current Python
3.14 runtime:

```text
python=3.10 or python=3.11
scanpy
anndata
pytorch
tangram-sc
cell2location
```

For RCTD/spacexr:

```text
R >= 4.2
Bioconductor dependencies
spacexr
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
2. Install Scanpy/AnnData and export the reference/spatial tables to h5ad.
3. Run Tangram first because it is usually lighter than cell2location.
4. Run cell2location after validating the reference and GPU/CPU runtime.
5. Run RCTD in an R environment to cross-check spot mixture estimates.
