# EMT Spatial Pathology Review Queue

This queue turns spatial EMT niche outputs into reviewable pathology tasks for invasive edge, CAF/TAM, hypoxia, and tumor-intrinsic EMT validation.

## Review Queue

| run | cancer_group | spots | pathology_priority_score | review_focus | review_status | minimum_review_regions | emt_niche_fraction | tumor_cell_emt_fraction | stromal_inflated_fraction | mean_caf_tam | mean_hypoxia | mean_predicted_emt_niche_probability | source_page |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 10x_prostate_ffpe | Prostate Cancer | 4371 | 0.17 | tumor_intrinsic_emt;tam_neighborhood;hypoxia_necrosis;invasive_edge | pending_pathologist_review | 10 | 0.25 | 0.153 | 0.0975 | 1.63e-18 | 1.14e-17 | 0.252 | https://www.10xgenomics.com/datasets/human-prostate-cancer-1-standard |
| geo_pdac_gse274103 | Pancreatic Cancer | 23436 | 0.169 | tumor_intrinsic_emt;hypoxia_necrosis;invasive_edge | pending_pathologist_review | 10 | 0.25 | 0.135 | 0.115 | -4.85e-18 | 1.94e-17 | 0.251 | https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE274103 |
| geo_brain_met_gse179572 | Brain Tumors | 12566 | 0.169 | tumor_intrinsic_emt;tam_neighborhood;invasive_edge | pending_pathologist_review | 10 | 0.25 | 0.135 | 0.115 | 1.81e-17 | -9.05e-18 | 0.248 | https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE179572 |
| 10x_lung_lusc_cytassist | Lung Cancer | 3858 | 0.169 | tumor_intrinsic_emt;caf_stromal_interface;tam_neighborhood;hypoxia_necrosis;invasive_edge | pending_pathologist_review | 10 | 0.25 | 0.116 | 0.134 | 7.37e-18 | 1.84e-18 | 0.251 | https://cf.10xgenomics.com/samples/spatial-exp/2.0.0/CytAssist_FFPE_Human_Lung_Squamous_Cell_Carcinoma/CytAssist_FFPE_Human_Lung_Squamous_Cell_Carcinoma_web_summary.html |
| geo_met_pdac_gse274557_pt1 | Pancreatic Cancer | 8756 | 0.168 | tumor_intrinsic_emt;caf_stromal_interface;tam_neighborhood;invasive_edge | pending_pathologist_review | 10 | 0.25 | 0.106 | 0.144 | 1.3e-17 | 0 | 0.251 | https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE274557 |
| 10x_colorectal_intestinal_ffpe | Colon / Intestine Cancer | 2660 | 0.168 | caf_stromal_interface;hypoxia_necrosis;invasive_edge | pending_pathologist_review | 10 | 0.25 | 0.0936 | 0.156 | -1.14e-17 | 6.68e-18 | 0.253 | https://www.10xgenomics.com/datasets/human-intestine-cancer-1-standard |
| 10x_breast_ffpe_idc | Breast Cancer | 2518 | 0.167 | tumor_intrinsic_emt;caf_stromal_interface;hypoxia_necrosis;invasive_edge | pending_pathologist_review | 10 | 0.25 | 0.101 | 0.149 | -1.69e-17 | 6.7e-18 | 0.247 | https://www.10xgenomics.com/datasets/human-breast-cancer-ductal-carcinoma-in-situ-invasive-carcinoma-ffpe-1-standard-1-3-0 |
| 10x_ovarian_ffpe | Ovarian Cancer | 3455 | 0.166 | caf_stromal_interface;invasive_edge | pending_pathologist_review | 10 | 0.25 | 0.0669 | 0.183 | -2.57e-19 | -3.08e-18 | 0.252 | https://www.10xgenomics.com/datasets/human-ovarian-cancer-1-standard |

## Review Checklist

| review_feature | pathology_question | required_marker_or_context |
| --- | --- | --- |
| invasive_edge | Is the EMT-high region at an invasive front or tumor-stroma boundary? | H&E region annotation; epithelial/tumor boundary; VIM/CDH1/KRT panel if available |
| caf_stromal_interface | Is EMT signal dominated by CAF/desmoplastic stroma rather than malignant tumor cells? | COL1A1/COL1A2/DCN/LUM/ACTA2/FAP markers and H&E stroma score |
| tam_neighborhood | Are EMT-high regions adjacent to macrophage/TAM-rich neighborhoods? | CD68/CD163/SPP1/TREM2 or equivalent macrophage markers |
| hypoxia_necrosis | Does EMT signal co-localize with hypoxia, necrosis, or poor perfusion? | CA9/SLC2A1/LDHA signatures; necrosis/hypoxia region annotation |
| tumor_intrinsic_emt | Do malignant epithelial cells themselves express EMT markers? | EPCAM/KRT lineage markers plus VIM/ZEB1/SNAI2/AXL/ITGA5 |

## Review Boundary

This is a research review queue, not diagnostic sign-out. Final region labels require expert pathology review and documented criteria.
