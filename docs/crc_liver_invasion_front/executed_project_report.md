# CRC Liver-Metastasis Invasion-Front Model: Executed Report

## Executive Summary

This project constructs biologically typed spatial graphs around the colorectal
cancer-liver interface. It uses 22,260
public Visium spots from 6 sections in GSE225857, including
2 liver-metastasis sections.
The interface labels are transparent marker-plus-spatial weak labels, not
pathologist ground truth.

The typed message-passing baseline achieved leave-one-liver-section-out ROC AUC
**0.908** and average precision **0.857**.
Its within-section permutation P value was **0.020**.
These values measure reproducibility across two public sections; they do not
establish clinical prediction or causal invasion biology.

## Executed Data

| dataset_id   | section_id    | sample_label   | site             |   spots_under_tissue | source_url                                                   | study_doi              | patient_pairing                             |
|:-------------|:--------------|:---------------|:-----------------|---------------------:|:-------------------------------------------------------------|:-----------------------|:--------------------------------------------|
| GSE225857    | GSM7058756_C1 | C1             | primary_crc      |                 2054 | https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE225857 | 10.1126/sciadv.adf5464 | not available for public Visium section IDs |
| GSE225857    | GSM7058757_C2 | C2             | primary_crc      |                 3305 | https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE225857 | 10.1126/sciadv.adf5464 | not available for public Visium section IDs |
| GSE225857    | GSM7058758_C3 | C3             | primary_crc      |                 3417 | https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE225857 | 10.1126/sciadv.adf5464 | not available for public Visium section IDs |
| GSE225857    | GSM7058759_C4 | C4             | primary_crc      |                 4016 | https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE225857 | 10.1126/sciadv.adf5464 | not available for public Visium section IDs |
| GSE225857    | GSM7058760_L1 | L1             | liver_metastasis |                 4672 | https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE225857 | 10.1126/sciadv.adf5464 | not available for public Visium section IDs |
| GSE225857    | GSM7058761_L2 | L2             | liver_metastasis |                 4796 | https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE225857 | 10.1126/sciadv.adf5464 | not available for public Visium section IDs |

An open 48-AOI GeoMx CTA table from four patients (Zenodo 7520789) was also
downloaded. It is retained as an orthogonal validation asset, but it was not
silently assigned tissue labels because the public count file lacks a
machine-readable AOI-to-primary/metastasis annotation.

## Study-Matched Single-Cell Reference

The GSE225857 processed single-cell tables yielded four author-annotated
pseudobulk references from 56,072 cells: 23,954 malignant, 15,093 fibroblast,
14,180 macrophage/myeloid and 2,845 endothelial cells. The metadata/count cell
identifier delimiter was harmonized before aggregation. Hepatocytes were absent
from the author-processed clusters and are reported as unavailable rather than
imputed into the matched reference.

## Interface Construction

The pipeline scores malignant CRC epithelium, partial EMT, hepatocytes,
MRC1/CCL18-like macrophages, activated fibroblasts, endothelial cells, damaged
hepatocytes, ECM remodelling, glycolysis and hypoxia. A spatial boundary is
defined only where high-confidence malignant and hepatocyte compartments touch.
Tumour and liver fronts extend three Visium hops, approximately 300 micrometres,
from that boundary.

| section_id    | site             |   spots |   boundary_pairs |   interface_spots |   tumour_front_spots |   mean_front_partial_emt |   mean_front_macrophage |   mean_front_fibroblast |   mean_front_ecm |   mean_front_glycolysis |   direct_contact_fraction | growth_pattern_proxy     | label_source                   |
|:--------------|:-----------------|--------:|-----------------:|------------------:|---------------------:|-------------------------:|------------------------:|------------------------:|-----------------:|------------------------:|--------------------------:|:-------------------------|:-------------------------------|
| GSM7058760_L1 | liver_metastasis |    4672 |              303 |              1562 |                  861 |                 0.309962 |                0.407215 |                0.390692 |         0.406078 |                0.494233 |                 0.0194368 | mixed_or_uncertain_proxy | marker_plus_spatial_weak_label |
| GSM7058761_L2 | liver_metastasis |    4796 |              452 |              2597 |                 1130 |                 0.310252 |                0.474627 |                0.427688 |         0.425554 |                0.462416 |                 0.02825   | mixed_or_uncertain_proxy | marker_plus_spatial_weak_label |

The growth-pattern field is explicitly a proxy. Desmoplastic-like means a
fibroblast/ECM-rich separated interface; replacement-like means stronger direct
tumour-hepatocyte contact with hepatocyte injury. A pathologist must score H&E
sections using consensus HGP criteria before this field can become a reference
label.

## Front-versus-Core Findings

| program               |   front_spots |   core_spots |   mean_front |   mean_core |   front_minus_core |   rank_biserial_effect |   mannwhitney_p |      fdr_bh |
|:----------------------|--------------:|-------------:|-------------:|------------:|-------------------:|-----------------------:|----------------:|------------:|
| damaged_hepatocyte    |          1290 |         2149 |     0.437088 |    0.376692 |          0.0603961 |              0.132795  |     5.90726e-11 | 7.87635e-11 |
| mrc1_ccl18_macrophage |          1290 |         2149 |     0.341484 |    0.36814  |         -0.026656  |             -0.0650903 |     0.00137147  | 0.00137147  |
| endothelial           |          1290 |         2149 |     0.374151 |    0.412974 |         -0.0388226 |             -0.0722012 |     0.000306686 | 0.000350498 |
| ecm_remodeling        |          1290 |         2149 |     0.376532 |    0.493712 |         -0.11718   |             -0.229451  |     1.61134e-29 | 2.57814e-29 |

The full statistics table includes rank-biserial effect size, Mann-Whitney P
value and Benjamini-Hochberg FDR. Spot-level significance is descriptive because
spots from one section are not independent patients.

## Model Drivers

| feature                               |   coefficient |   absolute_coefficient | direction             |
|:--------------------------------------|--------------:|-----------------------:|:----------------------|
| spatial_neighbor_hypoxia              |     -0.832088 |               0.832088 | tumour_core_enriched  |
| spatial_neighbor_damaged_hepatocyte   |      0.80864  |               0.80864  | tumour_front_enriched |
| spatial_neighbor_ecm_remodeling       |     -0.793812 |               0.793812 | tumour_core_enriched  |
| spatial_neighbor_partial_emt          |     -0.744988 |               0.744988 | tumour_core_enriched  |
| spatial_neighbor_glycolysis           |     -0.641496 |               0.641496 | tumour_core_enriched  |
| spatial_neighbor_activated_fibroblast |     -0.510973 |               0.510973 | tumour_core_enriched  |

Features include local programs and typed messages from spatial, compartment
contact, ligand-receptor and ECM/glycolysis-gradient edges. Coefficients indicate
predictive direction in this dataset, not drug targets or causal mechanisms.

## Novel Elements

1. A signed tumour-to-liver coordinate system rather than whole-slide averaging.
2. Separate malignant partial EMT and stromal-inflated EMT labels.
3. Heterogeneous nodes for malignant, hepatocyte, macrophage, fibroblast and
   endothelial compartments.
4. Directional ECM and glycolysis gradient edges.
5. Biologically named ligand-receptor edge families.
6. Leave-section-out validation, within-section permutation and feature-group
   ablation.
7. Pathology-inspired desmoplastic/replacement proxies with an explicit human
   review requirement.

## Supported Claims

- The public sections contain spatially coherent CRC, hepatocyte and niche
  programs that permit an automatically inferred interface.
- An interpretable multivariable graph-context signature can be tested for
  reproducibility between the two liver sections.
- The output produces experimentally testable hypotheses about partial EMT,
  macrophage, fibroblast, endothelial, ECM and metabolic gradients.

## Claims Not Supported

- The model does not predict survival, recurrence or treatment response.
- Weak interface labels are not equivalent to pathologist HGP annotations.
- Ligand-receptor co-expression does not prove signalling.
- Two liver sections are insufficient for a clinical or population-level claim.
- The project does not recommend treatment for any patient.

## Next Experimental Tests

1. Pathologist annotation of tumour boundary and HGP percentage on the H&E image.
2. Multiplex IF/IHC for EPCAM or KRT20, VIM/LAMC2, MRC1/CCL18, FAP/POSTN,
   CD31 and CA9/GLUT1 in the same 300 micrometre bands.
3. Spatial perturbation of CCL18-PITPNM3, SPP1-CD44/ITGAV, TGF-beta and
   CXCL12-CXCR4 axes in CRC liver organoid or precision-cut liver models.
4. Independent validation in PRJEB71493 or the 26-sample ISS CRLM cohort once
   processed matrices and region annotations can be redistributed.

## Reproducibility

Run `python scripts/run_crc_liver_invasion_front.py`. Large raw files remain in
`data/raw/`; derived tables, figures, metrics and this report are reproducible.
