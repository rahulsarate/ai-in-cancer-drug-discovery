# Annotated Single-Cell EMT Separation Layer

This layer starts the explicit separation of malignant-cell EMT from CAF/stromal EMT and immune-context EMT-like signal.

## Tumor versus Stroma Summary

| source | datasets | cancer_group | cells | malignant_cells | caf_stromal_cells | tam_myeloid_cells | tumor_intrinsic_emt_cells | caf_stromal_emt_cells | tam_myeloid_emt_like_cells | malignant_emt_score_mean | caf_stromal_emt_score_mean | tam_myeloid_emt_score_mean | malignant_vs_stromal_emt_delta | interpretation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3CA | Gaiti2019_hematologic | Blood Tumors | 720 | 720 | 0 | 0 | 180 | 0 | 0 | -1.26e-08 |  |  |  | malignant_available_no_caf_stromal_comparator |
| 3CA | Filbin2018_brain | Brain Tumors | 2587 | 2259 | 0 | 96 | 588 | 0 | 54 | 0.019 |  | 0.3217321005625 |  | malignant_available_no_caf_stromal_comparator |
| 3CA | Chung2017_breast | Breast Cancer | 515 | 317 | 23 | 38 | 10 | 11 | 30 | -0.595 | 1.1622121597826087 | 1.2590852586842105 | -1.7570443859277192 | caf_stromal_emt_enriched |
| 3CA | Li2017_colorectal | Colon / Intestine Cancer | 590 | 254 | 9 | 10 | 15 | 9 | 10 | -0.312 | 1.5222626644444444 | 0.956244156 | -1.833854588077909 | caf_stromal_emt_enriched |
| 3CA | Puram2017_Head-and-Neck | Head and Neck Cancer | 5902 | 2539 | 1440 | 149 | 153 | 1009 | 75 | -0.584 | 0.760870749856111 | 0.48159303588255037 | -1.3449728362628695 | caf_stromal_emt_enriched |
| 3CA | Song2019_lung | Lung Cancer | 8772 | 1147 | 32 | 2958 | 0 | 28 | 1608 | -1.58 | 1.136789193125 | 0.4287239469129716 | -2.7159561119046858 | caf_stromal_emt_enriched |
| 3CA | Shih2018_ovarian | Ovarian Cancer | 3066 | 793 | 633 | 190 | 1 | 451 | 125 | -0.983 | 0.8127856862192732 | 0.5327195628105263 | -1.7953896375738758 | caf_stromal_emt_enriched |
| 3CA | Moncada2020_pancreas | Pancreatic Cancer | 3659 | 635 | 5 | 180 | 188 | 5 | 180 | 0.00502 | 5.698907180000001 | 1.2817182423333333 | -5.693889504573072 | caf_stromal_emt_enriched |
| 3CA | He2021_prostate | Prostate Cancer | 2170 | 836 | 0 | 185 | 17 | 0 | 109 | -0.616 |  | 0.5751425754237838 |  | malignant_available_no_caf_stromal_comparator |
| 3CA | Tirosh2016_skin | Skin Cancer | 4645 | 1257 | 56 | 119 | 671 | 48 | 73 | 0.23 | 1.3328769557142857 | 0.28594050752941164 | -1.1032233487621235 | caf_stromal_emt_enriched |
| CancerSEA | EXP0047 | Blood Tumors | 1339 | 1339 | 0 | 0 | 335 | 0 | 0 | 0 |  |  |  | malignant_available_no_caf_stromal_comparator |
| CancerSEA | EXP0057 | Brain Tumors | 991 | 991 | 0 | 0 | 248 | 0 | 0 | 0 |  |  |  | malignant_available_no_caf_stromal_comparator |
| CancerSEA | EXP0053;EXP0054;EXP0055 | Breast Cancer | 440 | 440 | 0 | 0 | 112 | 0 | 0 | 1.33e-16 |  |  |  | malignant_available_no_caf_stromal_comparator |
| CancerSEA | EXP0051 | Colon / Intestine Cancer | 293 | 293 | 0 | 0 | 74 | 0 | 0 | 1.52e-18 |  |  |  | malignant_available_no_caf_stromal_comparator |
| CancerSEA | EXP0063 | Head and Neck Cancer | 2215 | 2215 | 0 | 0 | 554 | 0 | 0 | 3.21e-17 |  |  |  | malignant_available_no_caf_stromal_comparator |
| CancerSEA | EXP0068 | Lung Cancer | 3524 | 3524 | 0 | 0 | 881 | 0 | 0 | 8.07e-18 |  |  |  | malignant_available_no_caf_stromal_comparator |
| CancerSEA | EXP0023 | Oesophageal Cancer | 314 | 314 | 0 | 0 | 79 | 0 | 0 | -1.06e-16 |  |  |  | malignant_available_no_caf_stromal_comparator |
| CancerSEA | EXP0069 | Ovarian Cancer | 244 | 244 | 0 | 0 | 61 | 0 | 0 | 1.46e-17 |  |  |  | malignant_available_no_caf_stromal_comparator |
| CancerSEA | EXP0037 | Pancreatic Cancer | 96 | 96 | 0 | 0 | 24 | 0 | 0 | 4.63e-17 |  |  |  | malignant_available_no_caf_stromal_comparator |
| CancerSEA | EXP0070 | Prostate Cancer | 122 | 122 | 0 | 0 | 31 | 0 | 0 | -2.73e-18 |  |  |  | malignant_available_no_caf_stromal_comparator |
| CancerSEA | EXP0071 | Skin Cancer | 1257 | 1257 | 0 | 0 | 315 | 0 | 0 | -5.65e-17 |  |  |  | malignant_available_no_caf_stromal_comparator |

## Compartment-Level EMT Summary

| source | dataset | cancer_group | cell_compartment | malignant_status | cells | emt_high_fraction | tumor_intrinsic_emt_fraction | caf_stromal_emt_fraction | tam_myeloid_emt_like_fraction | caf_tam_context_emt_fraction | stromal_mimic_warning_fraction | emt_score_mean | partial_emt_score_mean | stromal_fibroblast_mean | caf_tam_niche_mean | hypoxia_mean |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CancerSEA | EXP0047 | Blood Tumors | malignant | malignant | 1339 | 0.25 | 0.25 | 0 | 0 | 0 | 0 | -1.39e-18 | -0.126 | 1.73e-17 | 1.26e-17 | 3.07e-17 |
| 3CA | Gaiti2019_hematologic | Blood Tumors | malignant | malignant | 720 | 0.25 | 0.25 | 0 | 0 | 0 | 0 | -1.26e-08 | -0.132 | -9.9e-09 | 4.9e-09 | 7.67e-10 |
| 3CA | Filbin2018_brain | Brain Tumors | malignant | malignant | 2259 | 0.26 | 0.26 | 0 | 0 | 0 | 0 | 0.019 | -0.131 | 0.0236 | -0.0555 | -0.00332 |
| CancerSEA | EXP0057 | Brain Tumors | malignant | malignant | 991 | 0.25 | 0.25 | 0 | 0 | 0 | 0 | -3.14e-18 | -0.222 | -2.41e-17 | 2.98e-17 | -8.07e-18 |
| 3CA | Filbin2018_brain | Brain Tumors | unknown | non-malignant | 232 | 0.0216 | 0 | 0 | 0 | 0 | 0.0776 | -0.318 | -0.187 | -0.22 | -0.093 | 0.0988 |
| 3CA | Filbin2018_brain | Brain Tumors | myeloid_tam | non-malignant | 96 | 0.562 | 0 | 0 | 0.562 | 0.927 | 0.177 | 0.322 | -0.114 | -0.0236 | 1.53 | -0.161 |
| 3CA | Chung2017_breast | Breast Cancer | malignant | malignant | 317 | 0.0315 | 0.0315 | 0 | 0 | 0 | 0 | -0.595 | -0.144 | -0.12 | -0.135 | 0.175 |
| CancerSEA | EXP0053 | Breast Cancer | malignant | malignant | 317 | 0.252 | 0.252 | 0 | 0 | 0 | 0 | 1.88e-16 | -0.214 | -1.05e-17 | 3.06e-18 | -1.18e-16 |
| 3CA | Chung2017_breast | Breast Cancer | unknown | non-malignant | 137 | 0.569 | 0 | 0 | 0 | 0 | 0.212 | 0.832 | -0.887 | -0.137 | -0.136 | -0.313 |
| CancerSEA | EXP0054 | Breast Cancer | malignant | malignant | 74 | 0.257 | 0.257 | 0 | 0 | 0 | 0 | -2.25e-17 | -0.321 | 8.81e-18 | 1.88e-17 | 3.15e-17 |
| CancerSEA | EXP0055 | Breast Cancer | malignant | malignant | 49 | 0.265 | 0.265 | 0 | 0 | 0 | 0 | 3.4e-18 | -0.225 | 2.83e-17 | 1.7e-17 | 2.27e-17 |
| 3CA | Chung2017_breast | Breast Cancer | myeloid_tam | non-malignant | 38 | 0.789 | 0 | 0 | 0.789 | 0.921 | 0.316 | 1.26 | -0.834 | 0.0818 | 1.03 | -0.167 |
| 3CA | Chung2017_breast | Breast Cancer | caf_stromal | non-malignant | 23 | 0.478 | 0 | 0.478 | 0 | 0.565 | 1 | 1.16 | -0.49 | 2.33 | 0.957 | -0.268 |
| CancerSEA | EXP0051 | Colon / Intestine Cancer | malignant | malignant | 293 | 0.253 | 0.253 | 0 | 0 | 0 | 0 | -1.89e-18 | -0.156 | 6.06e-17 | 3.64e-17 | 9.38e-18 |
| 3CA | Li2017_colorectal | Colon / Intestine Cancer | malignant | malignant | 254 | 0.0591 | 0.0591 | 0 | 0 | 0 | 0 | -0.312 | -0.165 | -0.159 | -0.068 | 0.136 |
| 3CA | Li2017_colorectal | Colon / Intestine Cancer | normal_epithelial | non-malignant | 160 | 0.025 | 0 | 0 | 0 | 0 | 0.263 | -0.408 | -0.132 | -0.136 | -0.155 | -0.0975 |
| 3CA | Li2017_colorectal | Colon / Intestine Cancer | unknown | non-malignant | 155 | 0.703 | 0 | 0 | 0 | 0 | 0.342 | 0.778 | -0.611 | 0.256 | 0.215 | -0.0926 |
| 3CA | Li2017_colorectal | Colon / Intestine Cancer | myeloid_tam | non-malignant | 10 | 1 | 0 | 0 | 1 | 1 | 0 | 0.956 | -0.884 | -0.207 | 0.307 | -0.323 |
| 3CA | Li2017_colorectal | Colon / Intestine Cancer | caf_stromal | non-malignant | 9 | 1 | 0 | 1 | 0 | 1 | 1 | 1.52 | -0.546 | 2.71 | 0.616 | -0.111 |
| 3CA | Li2017_colorectal | Colon / Intestine Cancer | endothelial | non-malignant | 2 | 0.5 | 0 | 0 | 0 | 0 | 1 | 0.295 | -0.143 | 0.127 | 0.0981 | -0.17 |
| 3CA | Puram2017_Head-and-Neck | Head and Neck Cancer | malignant | malignant | 2539 | 0.0603 | 0.0603 | 0 | 0 | 0 | 0 | -0.584 | -0.119 | -0.262 | -0.0647 | 0.421 |
| CancerSEA | EXP0063 | Head and Neck Cancer | malignant | malignant | 2215 | 0.25 | 0.25 | 0 | 0 | 0 | 0 | 2.44e-17 | -0.327 | 8.37e-18 | 7.47e-18 | 7.63e-17 |
| 3CA | Puram2017_Head-and-Neck | Head and Neck Cancer | unknown | non-malignant | 1514 | 0.0462 | 0 | 0 | 0 | 0 | 0.00132 | 0.116 | -0.463 | -0.434 | -0.307 | -0.476 |
| 3CA | Puram2017_Head-and-Neck | Head and Neck Cancer | caf_stromal | non-malignant | 1440 | 0.701 | 0 | 0.701 | 0 | 0.852 | 1 | 0.761 | -0.397 | 1.01 | 0.334 | -0.203 |
| 3CA | Puram2017_Head-and-Neck | Head and Neck Cancer | endothelial | non-malignant | 260 | 0.65 | 0 | 0 | 0 | 0 | 0.0423 | 0.54 | -0.308 | -0.294 | -0.0833 | -0.14 |
| 3CA | Puram2017_Head-and-Neck | Head and Neck Cancer | myeloid_tam | non-malignant | 149 | 0.503 | 0 | 0 | 0.503 | 0.718 | 0.0134 | 0.482 | -0.435 | -0.386 | 1.14 | -0.138 |
| CancerSEA | EXP0068 | Lung Cancer | malignant | malignant | 3524 | 0.25 | 0.25 | 0 | 0 | 0 | 0 | -8.55e-18 | -0.247 | 2.95e-17 | 2.68e-17 | -2.45e-17 |
| 3CA | Song2019_lung | Lung Cancer | unknown | non-malignant | 3510 | 0.115 | 0 | 0 | 0 | 0 | 1 | 0.12 | -0.306 | -0.173 | -0.273 | -0.274 |
| 3CA | Song2019_lung | Lung Cancer | myeloid_tam | non-malignant | 2958 | 0.544 | 0 | 0 | 0.544 | 0.76 | 1 | 0.429 | -0.276 | -0.0958 | 0.431 | 0.164 |
| 3CA | Song2019_lung | Lung Cancer | malignant | malignant | 1147 | 0 | 0 | 0 | 0 | 0 | 0 | -1.58 | 0.0294 | 0.692 | -0.0191 | 0.591 |
| 3CA | Song2019_lung | Lung Cancer | t_cell | non-malignant | 947 | 0.159 | 0 | 0 | 0 | 0 | 1 | 0.244 | -0.314 | 0.105 | -0.258 | -0.266 |
| 3CA | Song2019_lung | Lung Cancer | normal_epithelial | non-malignant | 178 | 0.0225 | 0 | 0 | 0 | 0 | 1 | -0.811 | -0.169 | -0.0447 | -0.23 | 0.208 |
| 3CA | Song2019_lung | Lung Cancer | caf_stromal | non-malignant | 32 | 0.875 | 0 | 0.875 | 0 | 0.875 | 1 | 1.14 | -0.271 | 0.122 | -0.251 | 0.423 |
| CancerSEA | EXP0023 | Oesophageal Cancer | malignant | malignant | 314 | 0.252 | 0.252 | 0 | 0 | 0 | 0 | -1.06e-16 | -0.194 | 1.65e-17 | 2.7e-17 | -4.38e-17 |
| 3CA | Shih2018_ovarian | Ovarian Cancer | unknown | non-malignant | 1371 | 0.105 | 0 | 0 | 0 | 0 | 0.097 | 0.0946 | -0.339 | -0.281 | -0.203 | -0.283 |
| 3CA | Shih2018_ovarian | Ovarian Cancer | malignant | malignant | 793 | 0.00126 | 0.00126 | 0 | 0 | 0 | 0 | -0.983 | -0.185 | -0.298 | -0.18 | 0.331 |
| 3CA | Shih2018_ovarian | Ovarian Cancer | caf_stromal | non-malignant | 633 | 0.712 | 0 | 0.712 | 0 | 0.788 | 1 | 0.813 | -0.252 | 1.12 | 0.388 | 0.102 |
| CancerSEA | EXP0069 | Ovarian Cancer | malignant | malignant | 244 | 0.25 | 0.25 | 0 | 0 | 0 | 0 | 1.55e-17 | -0.186 | 4.82e-17 | 7.28e-18 | -3.46e-17 |
| 3CA | Shih2018_ovarian | Ovarian Cancer | myeloid_tam | non-malignant | 190 | 0.658 | 0 | 0 | 0.658 | 0.979 | 0.0105 | 0.533 | -0.341 | -0.342 | 0.994 | 0.333 |
| 3CA | Shih2018_ovarian | Ovarian Cancer | endothelial | non-malignant | 79 | 0.582 | 0 | 0 | 0 | 0 | 0.101 | 0.428 | -0.306 | -0.27 | -0.171 | -0.0189 |
| 3CA | Moncada2020_pancreas | Pancreatic Cancer | normal_epithelial | non-malignant | 2499 | 0.104 | 0 | 0 | 0 | 0 | 1 | -0.247 | -0.172 | -0.0492 | -0.0834 | 0.0602 |
| 3CA | Moncada2020_pancreas | Pancreatic Cancer | malignant | malignant | 635 | 0.296 | 0.296 | 0 | 0 | 0 | 0 | 0.00502 | -0.105 | -0.00877 | -0.0806 | -0.00418 |
| 3CA | Moncada2020_pancreas | Pancreatic Cancer | myeloid_tam | non-malignant | 180 | 1 | 0 | 0 | 1 | 1 | 1 | 1.28 | -0.94 | -0.0328 | 1.17 | -0.245 |
| 3CA | Moncada2020_pancreas | Pancreatic Cancer | endothelial | non-malignant | 170 | 1 | 0 | 0 | 0 | 0 | 1 | 1.57 | -0.874 | 0.521 | 0.255 | -0.225 |
| 3CA | Moncada2020_pancreas | Pancreatic Cancer | unknown | non-malignant | 170 | 0.665 | 0 | 0 | 0 | 0 | 1 | 0.519 | -0.636 | -0.0749 | -0.0844 | -0.392 |
| CancerSEA | EXP0037 | Pancreatic Cancer | malignant | malignant | 96 | 0.25 | 0.25 | 0 | 0 | 0 | 0 | 4.63e-17 | -0.169 | 1.94e-17 | 7.52e-18 | -1.24e-17 |
| 3CA | Moncada2020_pancreas | Pancreatic Cancer | caf_stromal | non-malignant | 5 | 1 | 0 | 1 | 0 | 1 | 1 | 5.7 | -0.911 | 11.7 | 4.06 | 0.264 |
| 3CA | He2021_prostate | Prostate Cancer | unknown | non-malignant | 1119 | 0.355 | 0 | 0 | 0 | 0 | 1 | 0.353 | -0.339 | 0.014 | -0.0518 | -0.161 |
| 3CA | He2021_prostate | Prostate Cancer | malignant | malignant | 836 | 0.0203 | 0.0203 | 0 | 0 | 0 | 0 | -0.616 | -0.103 | -0.0203 | -0.0712 | 0.213 |
| 3CA | He2021_prostate | Prostate Cancer | myeloid_tam | non-malignant | 185 | 0.589 | 0 | 0 | 0.589 | 0.946 | 1 | 0.575 | -0.352 | -0.00727 | 0.624 | 0.0421 |
| CancerSEA | EXP0070 | Prostate Cancer | malignant | malignant | 122 | 0.254 | 0.254 | 0 | 0 | 0 | 0 | -3.54e-17 | -0.149 | 1.39e-17 | 2.26e-17 | 3.32e-17 |
| 3CA | He2021_prostate | Prostate Cancer | t_cell | non-malignant | 30 | 0.667 | 0 | 0 | 0 | 0 | 1 | 0.454 | -0.372 | 0.0874 | 0.0702 | -0.16 |
| 3CA | Tirosh2016_skin | Skin Cancer | unknown | non-malignant | 3100 | 0.1 | 0 | 0 | 0 | 0 | 0.17 | -0.137 | -0.256 | -0.0997 | -0.143 | -0.183 |
| 3CA | Tirosh2016_skin | Skin Cancer | malignant | malignant | 1257 | 0.534 | 0.534 | 0 | 0 | 0 | 0 | 0.23 | 0.0854 | 0.0175 | 0.129 | 0.397 |
| CancerSEA | EXP0071 | Skin Cancer | malignant | malignant | 1257 | 0.251 | 0.251 | 0 | 0 | 0 | 0 | -6.9e-17 | -0.238 | -2.54e-17 | 9.36e-18 | -3.18e-18 |
| 3CA | Tirosh2016_skin | Skin Cancer | myeloid_tam | non-malignant | 119 | 0.613 | 0 | 0 | 0.613 | 1 | 0.193 | 0.286 | -0.169 | -0.0817 | 1.53 | 0.329 |
| 3CA | Tirosh2016_skin | Skin Cancer | endothelial | non-malignant | 62 | 0.774 | 0 | 0 | 0 | 0 | 0.629 | 0.472 | 0.112 | 0.219 | 0.206 | 0.335 |
| 3CA | Tirosh2016_skin | Skin Cancer | caf_stromal | non-malignant | 56 | 0.857 | 0 | 0.857 | 0 | 1 | 1 | 1.33 | 0.28 | 5.16 | 1.62 | 0.339 |
| 3CA | Tirosh2016_skin | Skin Cancer | t_cell | non-malignant | 51 | 0.235 | 0 | 0 | 0 | 0 | 0.196 | -0.00827 | -0.198 | -0.116 | -0.0802 | -0.225 |

## External Export Requirements

| source | required_files | best_use | access_note |
| --- | --- | --- | --- |
| TISCH2 | cell metadata with cell type; expression matrix or gene-by-cell table | tumor microenvironment cell-type annotation, CAF/TAM separation, gene expression by cell type | Use TISCH2 dataset download page; import exported cell metadata and expression table. |
| 3CA | curated cell annotations; malignant-cell labels; expression matrix or summarized gene table | curated malignant-cell and cancer-type single-cell validation | Use 3CA public download links and keep original dataset/cancer metadata. |
| HTAN | Level 3/4 single-cell or spatial-derived cell tables; Synapse/Gen3 selected files | matched human tumor atlas validation with clinical/spatial context | Export selected files from HTAN portal, then use Synapse or Gen3 credentials for download. |
| CancerSEA | CancerSEA PCG expression matrix | malignant/cancer-cell EMT functional validation | Already downloaded for the selected disease groups in this project. |

## Interpretation Boundary

The compartment calls are only as reliable as the source cell-type and malignancy annotations. CNV-based malignant-cell calls are preferred when available.
