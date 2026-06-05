# Spatial EMT Blocker Solution Report

## Best Solutions

- HEST-1k: gated HuggingFace access check plus selected cancer subset ingestion before full-scale download.
- H&E/pathology: basic tile features are implemented now; foundation embeddings come later.
- Deconvolution: marker-proxy and NNLS reference fallback are implemented; cell2location/RCTD/Tangram need matched scRNA references.
- HTAN: use portal manifests first, then select a single cancer atlas for validation.
- Metastasis/progression: GSE179572 brain metastasis now runs end-to-end; GSE274557 metastatic PDAC is the next larger matched-site cohort.

## Immediate Next Runs

1. Run H&E tile features across all local 10x cohorts.
2. Build a cancer-specific scRNA reference matrix for one cohort and run NNLS.
3. Add GSE274557 primary/liver/lung/peritoneal labels and run the same workflow.
