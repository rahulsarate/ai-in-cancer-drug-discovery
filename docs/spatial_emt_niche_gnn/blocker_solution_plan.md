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

The next implementation step is to download one candidate, add primary vs
metastasis/progression labels, and rerun the spatial EMT niche workflow.
