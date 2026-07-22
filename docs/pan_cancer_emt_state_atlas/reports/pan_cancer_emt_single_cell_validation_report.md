# Pan-Cancer EMT Single-Cell Validation Layer

CancerSEA datasets were scored as tumor-cell-oriented EMT validation resources for the requested cancer groups.

## Disease-Group Validation Coverage

| cancer_group | cancersea_datasets | single_cells_or_profiles | tumor_intrinsic_validation | validation_context | single_cell_emt_score_mean | single_cell_partial_emt_score_mean | single_cell_stromal_fibroblast_mean | single_cell_immune_total_mean | single_cell_caf_tam_niche_mean | single_cell_hypoxia_mean | single_cell_ferroptosis_window_mean | sample_count | emt_score_mean | mesenchymal_like_fraction | stromal_dominant_fraction | high_confidence_fraction |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Lung Cancer | 1 | 3524 | available | CancerSEA malignant/cancer-cell expression profiles | -9.69e-18 | -0.247 | -1.54e-17 | 2.09e-17 | 2.35e-17 | -2.87e-17 | -3.38e-17 | 1129 | -0.255 | 0.156 | 0.129 | 0.328 |
| Head and Neck Cancer | 1 | 2215 | available | CancerSEA malignant/cancer-cell expression profiles | 2.4e-17 | -0.327 | -1.4e-17 | 9.02e-18 | 2.53e-18 | 7.32e-17 | -2.6e-17 | 566 | 0.311 | 0.498 | 0.26 | 0.3 |
| Blood Tumors | 1 | 1339 | available | CancerSEA malignant/cancer-cell expression profiles | 3.24e-18 | -0.126 | -2.71e-18 | 1.67e-17 | -4.64e-18 | 1.97e-17 | 4.97e-17 | 221 | 0.487 | 0.416 | 0.0226 | 0.394 |
| Skin Cancer | 1 | 1257 | available | CancerSEA malignant/cancer-cell expression profiles | -6.68e-17 | -0.238 | -5.09e-17 | 7.54e-18 | 7.24e-18 | -6.36e-18 | -9.78e-17 | 553 | 1.56 | 0.591 | 0.0723 | 0.519 |
| Brain Tumors | 1 | 991 | available | CancerSEA malignant/cancer-cell expression profiles | -2.24e-19 | -0.222 | -2.5e-17 | -3.4e-17 | 2.25e-17 | -1.29e-17 | 7.73e-18 | 701 | 1.1 | 0.193 | 0.0171 | 0.175 |
| Breast Cancer | 3 | 440 | available | CancerSEA malignant/cancer-cell expression profiles | 1.28e-16 | -0.233 | -1.61e-17 | 4.42e-18 | -3.03e-18 | -8.16e-17 | 6.94e-18 | 1215 | -0.181 | 0.129 | 0.12 | 0.198 |
| Oesophageal Cancer | 1 | 314 | available | CancerSEA malignant/cancer-cell expression profiles | -1.12e-16 | -0.194 | 5.92e-18 | 7.51e-19 | 1.68e-17 | -4.53e-17 | -8.13e-18 | 196 | -0.286 | 0.25 | 0.163 | 0.48 |
| Colon / Intestine Cancer | 1 | 293 | available | CancerSEA malignant/cancer-cell expression profiles | -3.03e-18 | -0.156 | 0 | 3.79e-18 | 3.03e-18 | -3.32e-18 | -2.88e-17 | 662 | -0.863 | 0.0287 | 0.0272 | 0.606 |
| Ovarian Cancer | 1 | 244 | available | CancerSEA malignant/cancer-cell expression profiles | 1.27e-17 | -0.186 | 4.55e-18 | 0 | 0 | -3.55e-17 | -3.26e-16 | 309 | -0.783 | 0.0324 | 0.0259 | 0.57 |
| Prostate Cancer | 1 | 122 | available | CancerSEA malignant/cancer-cell expression profiles | -1.14e-18 | -0.149 | 3.64e-18 | -1.18e-17 | -6.71e-18 | 8.42e-18 | -2.35e-17 | 550 | -0.724 | 0.0127 | 0.0127 | 0.245 |
| Pancreatic Cancer | 1 | 96 | available | CancerSEA malignant/cancer-cell expression profiles | 5.32e-17 | -0.169 | 3.47e-18 | 3.32e-18 | -3.18e-18 | -3.15e-17 | -6.94e-18 | 183 | 0.0645 | 0.328 | 0.322 | 0.0929 |

## Tumor-Intrinsic Marker Table

| marker | role | interpretation |
| --- | --- | --- |
| VIM | mesenchymal tumor-cell EMT | Prioritize when expressed in malignant cells, not only fibroblasts. |
| CDH2 | cadherin switch | Supports EMT-like adhesion remodeling. |
| ZEB1 | EMT transcription factor | Useful tumor-intrinsic EMT regulator candidate. |
| ZEB2 | EMT transcription factor | Useful tumor-intrinsic EMT regulator candidate. |
| SNAI1 | EMT transcription factor | Often transient; validate with matched epithelial loss. |
| SNAI2 | EMT transcription factor | Often linked to partial/plastic EMT states. |
| TWIST1 | invasion and plasticity | Candidate for invasive-edge EMT validation. |
| AXL | therapy-tolerant EMT axis | Connects EMT, TAM crosstalk, and drug-response hypotheses. |
| ITGA5 | ECM adhesion | Supports invasive matrix-interaction programs. |
| FN1 | matrix and EMT | Strong EMT marker but stromal contamination must be checked. |
| CDH1 | epithelial control | Loss or low signal supports EMT transition context. |
| EPCAM | epithelial/malignant control | Helps distinguish malignant epithelial cells from stromal cells. |
| KRT8 | epithelial lineage control | Useful for tumor-lineage anchoring in carcinoma datasets. |
| KRT18 | epithelial lineage control | Useful for tumor-lineage anchoring in carcinoma datasets. |
| COL1A1 | stromal caution marker | High signal may indicate CAF/fibroblast EMT mimicry. |
| COL1A2 | stromal caution marker | High signal may indicate CAF/fibroblast EMT mimicry. |
| DCN | stromal caution marker | Use to flag fibroblast-driven bulk EMT. |
| LUM | stromal caution marker | Use to flag fibroblast-driven bulk EMT. |
| ACTA2 | myofibroblast caution marker | Supports CAF/myofibroblast context rather than tumor-cell EMT alone. |
| PTPRC | immune exclusion marker | Use to rule out immune-cell expression effects. |

## Download Manifest

| dataset | label | cancer_group | url | table_path |
| --- | --- | --- | --- | --- |
| EXP0071 | Melanoma skin Tirosh 2016 | Skin Cancer | https://biocc.hrbmu.edu.cn/CancerSEA/download/Expression/EXP0071_PCG.zip | C:\Users\HP\OneDrive\Documents\AI in Cancer Drug Discovery\data\raw\cancersea\EXP0071\EXP0071_PCG_log2_afterQC.txt |

## Boundary

CancerSEA helps test malignant-cell EMT programs. Full malignant-versus-CAF/TAM separation still needs dedicated TISCH2, 3CA, HTAN, or matched single-cell annotations.
