# Spatial EMT Blocker Solution Report

## Best Solutions

- HEST-1k: HuggingFace access check is implemented; full ingestion waits for accepted access terms and HF_TOKEN.
- H&E/pathology: tile features, histology-similarity edges, morphology embedding baseline, and foundation access checks are implemented.
- Deconvolution: marker-proxy, PDAC marker-reference NNLS, real GSE154778 NNLS, Tangram environment, and RCTD/spacexr environment are implemented.
- HTAN: WUSTL PDAC target manifest and Synapse/Gen3 access checks are implemented; assay download waits for logged-in file selection.
- Pathologist review: expert scoring queue is generated; interpretation still requires human annotation.
- Metastasis/progression: GSE179572 brain metastasis and full GSE274557 patient-batched graph/model summaries are complete.

## Immediate Next Runs

1. Run H&E tile features across all local 10x cohorts.
2. Build Tangram and RCTD adapters around the existing GSE154778 reference.
3. Expand real scRNA references with GSE155698/GSE205013.
