# Literature and Data Grounding

## Executed Public Datasets

### GSE225857

The Science Advances study generated single-cell profiles from 27 samples of six
patients and six public Visium FFPE sections: four primary CRC and two liver
metastases. The public files include matrices, spot coordinates and tissue
images. The study reported distinct fibroblast programmes between primary and
liver-metastatic tumours and liver-metastasis-enriched MCAM-positive fibroblasts.

- GEO: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE225857
- Paper: https://doi.org/10.1126/sciadv.adf5464
- Role: discovery, graph construction and cross-section validation.
- Caveat: the public Visium section identifiers do not disclose patient pairing.

### Zenodo 7520789 / GSE224235

This open GeoMx CTA count table contains 48 AOIs from matched primary colorectal
and liver-metastatic tissue from four patients.

- Data: https://doi.org/10.5281/zenodo.7520789
- GEO context: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE224235
- Role: orthogonal evidence asset.
- Caveat: the count file does not contain a machine-readable AOI-to-site table,
  so v1 does not invent those labels.

## Interface Biology

The international HGP consensus defines desmoplastic, replacement and pushing
growth patterns at the tumour-liver interface. Replacement growth places cancer
cells in direct contact with liver plates and co-opts existing vessels;
desmoplastic growth separates tumour from hepatocytes with a fibrotic rim.

- Consensus: https://pmc.ncbi.nlm.nih.gov/articles/PMC5680474/
- Diagnostic reproducibility: https://pmc.ncbi.nlm.nih.gov/articles/PMC6611753/
- Immune/vascular context: https://pmc.ncbi.nlm.nih.gov/articles/PMC7217855/

A 2026 British Journal of Cancer study mapped 26 CRLM samples from 19 patients,
defined tumour and liver fronts as the first 300 micrometres from a manually
selected boundary, and validated all regions with a pathologist. It localized
ALB/CPS1/C3 to liver, COL1A1/COL4A1 to stroma and EPCAM/CDX2/KRT19 to tumour.
It also described SAA1/CRP/PLA2G2A-positive damaged hepatocytes in replacement
interfaces. These observations directly motivate the v1 distance bands and
damaged-hepatocyte programme.

- Paper: https://www.nature.com/articles/s41416-026-03567-y
- Interactive data viewer: https://crclm2.serve.scilifelab.se/iss_panel_2.tmap

## Why MRC1/CCL18, Fibroblasts, Endothelium, ECM and Glycolysis

- MRC1/CCL18-like macrophages capture an immunoregulatory myeloid state reported
  in liver-metastatic CRC single-cell studies; the score also includes APOE,
  MARCO, C1Q, TREM2 and GAS6 to avoid relying on two genes.
- Activated fibroblasts and ECM are separated analytically so a mesenchymal spot
  is not automatically called malignant EMT.
- Endothelial features distinguish angiogenic desmoplastic niches from possible
  vessel co-option at replacement interfaces.
- Glycolysis and hypoxia are modeled separately: glycolytic flux can be high
  without a canonical hypoxia programme, and the two imply different
  perturbation strategies.

## Planned External Data

PRJEB71493 contains three human CRLM Visium sequencing experiments but is about
63 GB at raw-read level. It is listed for a later processed-matrix adapter rather
than downloaded indiscriminately.

- https://www.ncbi.nlm.nih.gov/bioproject/PRJEB71493/

## Evidence Discipline

Signature scores are spatial relative abundances. Compartments are weak labels.
LR edges are co-expression opportunities. HGP proxies need pathologist review.
No part of this project provides a clinical biomarker or treatment recommendation.
