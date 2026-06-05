# Blocker Solution Plan

## HEST-1k

HEST-1k is the right multimodal scale-up source because it links spatial
transcriptomics to aligned whole-slide histology. The practical blocker is
access: the HuggingFace dataset currently returns an authentication/gated-access
response in this environment. The implemented solution is:

- track HEST access status with `scripts/check_hest_access.py`;
- request/confirm HuggingFace access outside the pipeline;
- cache the HEST metadata CSV first;
- subset cancer samples before any full-scale image download.

This avoids a fragile giant download and makes the blocker explicit.

## H&E And Pathology Features

Basic H&E features are now implemented through `scripts/extract_he_tile_features.py`.
The script reads 10x `tissue_hires_image.png`, scale factors, and spot pixel
coordinates, then computes per-spot color, brightness, stain-proxy, and tissue
density features.

This is the bridge from no pathology signal to usable pathology covariates.
Foundation model embeddings remain a later upgrade.

## Deconvolution

Three deconvolution levels are now defined:

- marker-proxy proportions from EMT/TME scores;
- NNLS reference deconvolution from a `cell_type x gene` reference matrix;
- later publication-grade tools: cell2location, RCTD, Tangram, stereoscope.

The key remaining dependency is not code; it is high-quality matched or
disease-matched scRNA-seq reference profiles.

## HTAN Validation

HTAN validation should begin with portal manifests rather than ad hoc downloads.
The next executable step is to select one HTAN spatial transcriptomics cancer
atlas, export/download the matrix and auxiliary spatial metadata, and adapt it
to the same standardized table format used for 10x/GEO cohorts.

## Metastasis And Progression Cohorts

The first candidate manifest prioritizes:

- GSE274557: metastatic pancreatic cancer with primary and metastatic sites;
- GSE179572: human brain metastasis Visium samples.

GSE179572 is now downloaded, standardized, scored, graphed, trained, and
summarized under `data/processed/spatial_emt_niche_gnn_geo_brain_met`.
This provides the first real metastasis benchmark for the niche graph model.

Initial GSE179572 run signal:

- six brain-metastasis samples standardized from GEO H5/spatial archives;
- 12,566 in-tissue spots after metadata matching;
- 358,273 graph edges;
- sample EMT-niche fractions range from 0.052 to 0.569;
- strongest ligand-receptor edge families include CSF1-CSF1R, GAS6-AXL,
  TGFB1-TGFBR1/2, CXCL12-CXCR4, VEGFA-KDR, and SPP1-CD44/ITGAV.

The next implementation step is GSE274557. That cohort is larger and more
valuable for metastasis biology because it includes matched primary tumour,
liver, lung, and peritoneal metastatic samples from metastatic pancreatic
cancer. It should be ingested after sample-level site labels are parsed.
