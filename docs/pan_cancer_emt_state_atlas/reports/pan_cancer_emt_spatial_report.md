# Pan-Cancer EMT Spatial and Pathology Layer

Spatial cohorts are summarized as EMT niche, invasive-edge, CAF/TAM neighborhood, and hypoxia-context evidence.

## Disease-Group Spatial Coverage

| cancer_group | spatial_cohorts | total_spots | mean_emt_niche_fraction | mean_tumor_cell_emt_fraction | mean_stromal_inflated_fraction | mean_caf_tam | mean_hypoxia | mean_predicted_emt_niche_probability | total_edges |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Pancreatic Cancer | 2 | 32192 | 0.25 | 0.12 | 0.13 | 4.07e-18 | 9.7e-18 | 0.251 | 710360 |
| Brain Tumors | 1 | 12566 | 0.25 | 0.135 | 0.115 | 1.81e-17 | -9.05e-18 | 0.248 | 370126 |
| Prostate Cancer | 1 | 4371 | 0.25 | 0.153 | 0.0975 | 1.63e-18 | 1.14e-17 | 0.252 | 66541 |
| Lung Cancer | 1 | 3858 | 0.25 | 0.116 | 0.134 | 7.37e-18 | 1.84e-18 | 0.251 | 49593 |
| Ovarian Cancer | 1 | 3455 | 0.25 | 0.0669 | 0.183 | -2.57e-19 | -3.08e-18 | 0.252 | 38628 |
| Colon / Intestine Cancer | 1 | 2660 | 0.25 | 0.0936 | 0.156 | -1.14e-17 | 6.68e-18 | 0.253 | 33542 |
| Breast Cancer | 1 | 2518 | 0.25 | 0.101 | 0.149 | -1.69e-17 | 6.7e-18 | 0.247 | 32575 |

## Spot/Region Cohort Cards

| run | cancer_group | spots | emt_niche_fraction | tumor_cell_emt_fraction | stromal_inflated_fraction | mean_caf_tam | mean_hypoxia | mean_predicted_emt_niche_probability | spatial_context | source_page |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| synthetic_demo | Demo / Synthetic | 144 | 0.25 | 0.167 | 0.0833 | 0 | -1.05e-16 | 0.256 | invasive-edge EMT niche; tumor-cell EMT region |  |
| 10x_breast_ffpe_idc | Breast Cancer | 2518 | 0.25 | 0.101 | 0.149 | -1.69e-17 | 6.7e-18 | 0.247 | invasive-edge EMT niche; CAF/stromal-rich EMT; tumor-cell EMT region; hypoxia-associated region | https://www.10xgenomics.com/datasets/human-breast-cancer-ductal-carcinoma-in-situ-invasive-carcinoma-ffpe-1-standard-1-3-0 |
| 10x_lung_lusc_cytassist | Lung Cancer | 3858 | 0.25 | 0.116 | 0.134 | 7.37e-18 | 1.84e-18 | 0.251 | invasive-edge EMT niche; CAF/stromal-rich EMT; tumor-cell EMT region; hypoxia-associated region | https://cf.10xgenomics.com/samples/spatial-exp/2.0.0/CytAssist_FFPE_Human_Lung_Squamous_Cell_Carcinoma/CytAssist_FFPE_Human_Lung_Squamous_Cell_Carcinoma_web_summary.html |
| geo_pdac_gse274103 | Pancreatic Cancer | 23436 | 0.25 | 0.135 | 0.115 | -4.85e-18 | 1.94e-17 | 0.251 | invasive-edge EMT niche; tumor-cell EMT region; hypoxia-associated region | https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE274103 |
| geo_met_pdac_gse274557_pt1 | Pancreatic Cancer | 8756 | 0.25 | 0.106 | 0.144 | 1.3e-17 | 0 | 0.251 | invasive-edge EMT niche; CAF/stromal-rich EMT; tumor-cell EMT region | https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE274557 |
| geo_brain_met_gse179572 | Brain Tumors | 12566 | 0.25 | 0.135 | 0.115 | 1.81e-17 | -9.05e-18 | 0.248 | invasive-edge EMT niche; tumor-cell EMT region | https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE179572 |
| 10x_prostate_ffpe | Prostate Cancer | 4371 | 0.25 | 0.153 | 0.0975 | 1.63e-18 | 1.14e-17 | 0.252 | invasive-edge EMT niche; tumor-cell EMT region; hypoxia-associated region | https://www.10xgenomics.com/datasets/human-prostate-cancer-1-standard |
| 10x_ovarian_ffpe | Ovarian Cancer | 3455 | 0.25 | 0.0669 | 0.183 | -2.57e-19 | -3.08e-18 | 0.252 | invasive-edge EMT niche; CAF/stromal-rich EMT | https://www.10xgenomics.com/datasets/human-ovarian-cancer-1-standard |
| 10x_colorectal_intestinal_ffpe | Colon / Intestine Cancer | 2660 | 0.25 | 0.0936 | 0.156 | -1.14e-17 | 6.68e-18 | 0.253 | invasive-edge EMT niche; CAF/stromal-rich EMT; hypoxia-associated region | https://www.10xgenomics.com/datasets/human-intestine-cancer-1-standard |

## Interpretation Boundary

Spatial EMT niche outputs support regional hypotheses. They still need pathologist review before clinical-grade statements about invasive edge or histologic patterning.
