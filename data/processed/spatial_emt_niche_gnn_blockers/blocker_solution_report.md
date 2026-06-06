# Spatial EMT Blocker Solution Report

## Best Solutions

- HEST-1k: gated HuggingFace access check plus selected cancer subset ingestion before full-scale download.
- H&E/pathology: basic tile features are implemented now; foundation embeddings come later.
- Deconvolution: marker-proxy and PDAC marker-reference NNLS are implemented; cell2location/RCTD/Tangram need matched scRNA references.
- HTAN: WUSTL PDAC target manifest is selected; portal file download remains next.
- Metastasis/progression: GSE179572 brain metastasis and GSE274557 Pt-1 matched primary/liver/peritoneal PDAC now run end-to-end.

## Immediate Next Runs

1. Run H&E tile features across all local 10x cohorts.
2. Replace marker-reference NNLS with matched/public PDAC scRNA signatures.
3. Scale GSE274557 from Pt-1 to the full non-PDX sample set.
