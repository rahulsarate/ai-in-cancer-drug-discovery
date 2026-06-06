# Spatial EMT Blocker Solution Report

## Best Solutions

- HEST-1k: gated HuggingFace access check plus selected cancer subset ingestion before full-scale download.
- H&E/pathology: tile features, histology-similarity edges, and morphology embedding baseline are implemented; foundation model weights remain optional.
- Deconvolution: marker-proxy, PDAC marker-reference NNLS, and real GSE154778 scRNA-derived NNLS are implemented.
- HTAN: WUSTL PDAC target manifest is selected; Synapse/portal assay download remains next.
- Metastasis/progression: GSE179572 brain metastasis and full GSE274557 patient-batched graph/model summaries are complete.

## Immediate Next Runs

1. Run H&E tile features across all local 10x cohorts.
2. Install an advanced deconvolution environment for Tangram/cell2location/RCTD.
3. Expand real scRNA references with GSE155698/GSE205013.
