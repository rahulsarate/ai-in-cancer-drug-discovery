# Pan-Cancer EMT State Atlas Card Report

This report adds consensus EMT state labels, confidence fields, and user-facing card summaries to the scored atlas.

Interpret all results as research hypotheses. Bulk EMT calls require stromal, single-cell, spatial, or pathology validation before clinical use.

## Overview

- Samples: 11069
- Cancer types: 33
- High-confidence samples: 4014
- Stromal-warning samples: 2768

## State Distribution

| state | count |
| --- | --- |
| uncertain | 4136 |
| hybrid_e_m | 2383 |
| epithelial | 2012 |
| stromal_dominant | 1183 |
| immune_inflamed_emt | 791 |
| hypoxic_emt | 361 |
| mesenchymal | 203 |

## Confidence Distribution

| confidence | count |
| --- | --- |
| low | 4136 |
| high | 4014 |
| medium | 2919 |

## Top Cancer Types

| cancer_type | sample_count | emt_score_mean | mesenchymal_like_fraction | hybrid_fraction | stromal_dominant_fraction | high_confidence_fraction |
| --- | --- | --- | --- | --- | --- | --- |
| DLBC | 48 | 1.38 | 0.979 | 0 | 0.104 | 0.875 |
| SARC | 265 | 2.31 | 0.951 | 0.00377 | 0.74 | 0.215 |
| MESO | 87 | 1.08 | 0.862 | 0.0115 | 0.655 | 0.207 |
| KIRC | 606 | 0.556 | 0.744 | 0.0297 | 0.153 | 0.614 |
| SKCM | 473 | 1.67 | 0.681 | 0 | 0.0846 | 0.596 |
| GBM | 168 | 1.77 | 0.649 | 0 | 0.0536 | 0.595 |
| UCS | 57 | 0.614 | 0.632 | 0.105 | 0.368 | 0.316 |
| TGCT | 139 | 0.395 | 0.547 | 0.0216 | 0.158 | 0.396 |
| HNSC | 566 | 0.311 | 0.498 | 0.0459 | 0.26 | 0.3 |
| unknown | 46 | 0.351 | 0.478 | 0.13 | 0.413 | 0.109 |
| ACC | 79 | 1.34 | 0.342 | 0 | 0.0253 | 0.316 |
| PAAD | 183 | 0.0645 | 0.328 | 0.541 | 0.322 | 0.0929 |
| LUSC | 553 | 0.00353 | 0.277 | 0.215 | 0.228 | 0.183 |
| LAML | 173 | 0.239 | 0.26 | 0 | 0 | 0.26 |
| ESCA | 196 | -0.286 | 0.25 | 0.158 | 0.163 | 0.48 |

## Requested Cancer Groups

| cancer_group | tcga_codes | note |
| --- | --- | --- |
| Head and Neck Cancer | HNSC | TCGA HNSC; includes head and neck squamous cell carcinoma. |
| Breast Cancer | BRCA | TCGA BRCA. |
| Colon / Intestine Cancer | COAD, READ | TCGA COAD and READ; small-intestine tumors need external cohorts beyond TCGA PanCan. |
| Pancreatic Cancer | PAAD | TCGA PAAD. |
| Brain Tumors | GBM, LGG | TCGA GBM and LGG. |
| Prostate Cancer | PRAD | TCGA PRAD. |
| Ovarian Cancer | OV | TCGA OV. |
| Skin Cancer | SKCM, UVM | TCGA SKCM and UVM. |
| Lung Cancer | LUAD, LUSC | TCGA LUAD and LUSC. |
| Oesophageal Cancer | ESCA | TCGA ESCA. |
| Blood Tumors | LAML, DLBC | TCGA LAML and DLBC; additional hematologic cohorts can be added later. |

## Requested Group EMT Summary

| cancer_group | sample_count | emt_score_mean | mesenchymal_like_fraction | hybrid_fraction | stromal_dominant_fraction | high_confidence_fraction |
| --- | --- | --- | --- | --- | --- | --- |
| Skin Cancer | 553 | 1.56 | 0.591 | 0 | 0.0723 | 0.519 |
| Head and Neck Cancer | 566 | 0.311 | 0.498 | 0.0459 | 0.26 | 0.3 |
| Blood Tumors | 221 | 0.487 | 0.416 | 0 | 0.0226 | 0.394 |
| Pancreatic Cancer | 183 | 0.0645 | 0.328 | 0.541 | 0.322 | 0.0929 |
| Other / Not Requested | 4784 | -0.032 | 0.256 | 0.156 | 0.118 | 0.4 |
| Oesophageal Cancer | 196 | -0.286 | 0.25 | 0.158 | 0.163 | 0.48 |
| Brain Tumors | 701 | 1.1 | 0.193 | 0 | 0.0171 | 0.175 |
| Lung Cancer | 1129 | -0.255 | 0.156 | 0.387 | 0.129 | 0.328 |
| Breast Cancer | 1215 | -0.181 | 0.129 | 0.579 | 0.12 | 0.198 |
| Ovarian Cancer | 309 | -0.783 | 0.0324 | 0.34 | 0.0259 | 0.57 |
| Colon / Intestine Cancer | 662 | -0.863 | 0.0287 | 0.252 | 0.0272 | 0.606 |
| Prostate Cancer | 550 | -0.724 | 0.0127 | 0.122 | 0.0127 | 0.245 |

## Next Validation Steps

- Validate high EMT states in malignant single cells.
- Review stromal-dominant calls with CAF/fibroblast and pathology markers.
- Prioritize high-confidence hybrid or mesenchymal-like groups for target and drug evidence cards.
