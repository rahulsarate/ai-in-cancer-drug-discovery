# Remaining Blocker Solutions

## Full GSE274557 Non-PDX Scale-Up

Status: full non-PDX raw matrix/spatial downloads and standardized expression
metadata are complete locally.

- Samples: 55 non-PDX samples
- Patients: 13
- Spots after metadata matching: 142,641
- Sites: primary, liver metastasis, lung metastasis, peritoneal metastasis
- Current committed outputs: compact raw-download status, full site summary,
  full patient-site summary

The full graph workflow is intentionally not run in one monolithic command yet.
It should be run by patient batch to avoid very large edge tables and to keep
failure recovery simple.

## Real scRNA References

Status: marker-reference NNLS has run; true public/matched scRNA remains the
next upgrade.

Prioritized references:

- GSE154778: PDAC primary and metastatic lesions
- GSE155698: PDAC plus non-cancer pancreas
- GSE205013: chemotherapy-treated/untreated PDAC TME
- HTAN WUSTL sc/snRNA-seq through the HTAN portal/Synapse

Execution path:

1. Download processed cell x gene matrices and cell metadata.
2. Filter to major compartments: malignant epithelial, mesenchymal/plastic
   malignant, CAF, macrophage/TAM, T cell, endothelial, hypoxic/stress.
3. Average expression by cell type to produce `cell_type x gene` references.
4. Run NNLS first; then use the same reference for RCTD/cell2location/Tangram.

## HTAN Portal Download

Status: HTAN WUSTL PDAC manifest is ready; actual assay download requires
using the HTAN Data Portal file table and Synapse/Gen3 workflow.

Practical route:

1. Open `https://data.humantumoratlas.org/explore`.
2. Filter Atlas to HTAN WUSTL.
3. Filter assay/file types to 10x Visium spatial transcriptomics, Level 3.
4. Select one sample from the manifest, for example `HT264P1`.
5. Use Download selected files to obtain Synapse/Gen3 instructions.
6. Place the matrix, barcodes/features, spatial metadata, and image files under
   `data/raw/spatial/htan/wustl_pdac/<sample_id>/`.

## Pathologist Expert Review

Status: review template exists; expert review is external human work.

The template asks for tumor-rich, invasive-edge, stroma-rich/CAF-rich,
necrosis/hypoxia, immune/TAM-rich, vessel-rich, and artifact/acellular regions.
These labels can validate whether weak EMT labels are tumor-cell EMT, stromal
inflation, or mixed-spot ambiguity.

## Pathology Foundation Embeddings

Status: color/stain-proxy histology features and first histology-similarity
edges are implemented. Foundation embeddings require model weights/access.

Recommended staged solution:

1. Keep the current color/stain baseline as a reproducible comparator.
2. Add optional model adapters for UNI, CONCH, CTransPath/HIPT, or HEST/STORM
   models after weights/access are configured.
3. Compare foundation embeddings against the current histology-similarity edge
   baseline and pathologist regions.
