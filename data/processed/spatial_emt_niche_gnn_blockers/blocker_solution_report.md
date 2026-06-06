# Spatial EMT Blocker Solution Report

## Best Solutions

- HEST-1k: gated HuggingFace access check plus selected cancer subset ingestion before full-scale download.
- H&E/pathology: tile features, histology-similarity edges, and morphology embedding baseline are implemented; foundation model weights remain optional.
- Deconvolution: marker-proxy and PDAC marker-reference NNLS are implemented; public scRNA references are prioritized for upgrade.
- HTAN: WUSTL PDAC target manifest is selected; Synapse/portal assay download remains next.
- Metastasis/progression: GSE179572 brain metastasis and GSE274557 full non-PDX scoring are complete; Pt-1 graph pilot is complete.

## Immediate Next Runs

1. Run H&E tile features across all local 10x cohorts.
2. Build real scRNA-derived references from GSE154778/GSE155698/GSE205013.
3. Run full GSE274557 graph workflow in patient batches.
