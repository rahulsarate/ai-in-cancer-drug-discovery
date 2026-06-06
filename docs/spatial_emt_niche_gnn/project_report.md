# Spatial EMT Niche GNN Project Report

## Executive Summary

The project is currently 71.4% complete by the weighted implementation tracker.
It has processed 53,008 spatial spots and 975,267 graph edges across demo, 10x public cancer, GEO pancreatic cancer, and GEO brain-metastasis cohorts.
The core value is an interpretable pipeline for weak-label discovery of EMT, partial EMT, stromal contamination, CAF/TAM/hypoxic niches, ECM remodeling, angiogenesis, and ferroptosis-window signals in spatial transcriptomics.

All current outputs are research hypotheses only. They are not diagnostic, prognostic, or treatment recommendations.

## Completion Chart

| Phase | Completion |
| --- | ---: |
| advanced | 21.9% |
| starter | 87.5% |
| validation | 50.0% |
| workflow_graph | 90.5% |
| workflow_ingestion | 100.0% |
| workflow_scoring | 69.0% |
| overall | 71.4% |

## Implemented System

- Standardized public Visium and GEO cohorts into expression and spatial metadata tables.
- Exported lightweight AnnData-style h5ad files for downstream spatial workflows.
- Implemented EMT, partial EMT, stromal, immune, CAF/TAM, hypoxia, ECM remodeling, angiogenesis, and ferroptosis scores.
- Implemented marker-proxy and NNLS-reference deconvolution paths.
- Built typed spatial graphs with kNN/radius, ligand-receptor, hypoxia-gradient, and ECM-gradient edges.
- Built heterogeneous compartment graphs for tumor, CAF, TAM, endothelial, T cell, hypoxic, ECM-rich, and ferroptosis-window nodes.
- Trained a dependency-light graph-aware logistic baseline for reproducible MVP benchmarking.
- Added H&E tile color/stain-proxy feature extraction for 10x tissue images.

## Cohort Results

| Cohort | Spots | EMT niche fraction | Tumor-cell EMT fraction | Stromal-inflated fraction | Edges | LR edges | Hypoxia edges |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| synthetic_demo | 144 | 0.250 | 0.167 | 0.083 | 3,265 | 2,168 | 233 |
| 10x_breast_ffpe_idc | 2,518 | 0.250 | 0.101 | 0.149 | 25,366 | 8,046 | 2,596 |
| 10x_lung_lusc_cytassist | 3,858 | 0.250 | 0.116 | 0.134 | 46,999 | 21,018 | 3,089 |
| geo_pdac_gse274103 | 23,436 | 0.250 | 0.135 | 0.115 | 414,811 | 251,484 | 23,809 |
| geo_brain_met_gse179572 | 12,566 | 0.250 | 0.135 | 0.115 | 358,273 | 269,785 | 14,904 |
| 10x_prostate_ffpe | 4,371 | 0.250 | 0.153 | 0.097 | 60,016 | 26,594 | 7,518 |
| 10x_ovarian_ffpe | 3,455 | 0.250 | 0.067 | 0.183 | 35,129 | 11,353 | 3,304 |
| 10x_colorectal_intestinal_ffpe | 2,660 | 0.250 | 0.094 | 0.156 | 31,408 | 12,212 | 3,532 |

## Metastasis And Progression Work

| Accession | Disease | Samples | Pipeline Status | Output |
| --- | --- | --- | --- | --- |
| GSE274557 | metastatic pancreatic cancer | 55 samples; primary, liver, lung, peritoneal metastases | candidate_scale_up_not_downloaded |  |
| GSE179572 | brain metastasis | six brain metastasis samples | downloaded_standardized_scored_graph_trained | data/processed/spatial_emt_niche_gnn_geo_brain_met |

## Blocker Solutions

| Blocker | Current Solution | Status | Next Action |
| --- | --- | --- | --- |
| HEST-1k scale ingestion | Use authenticated HuggingFace/Hest library manifest; select cancer subsets first. | access_required | Request/confirm HF access, then cache HEST_v1_1_0.csv and subset cancer samples. |
| H&E/pathology features | Use 10x tissue_hires_image + spot coordinates for basic tile features; later add foundation embeddings. | basic_solution_implemented | Run extract_he_tile_features.py for each cohort; add QuPath/pathologist regions when available. |
| Real deconvolution | Use marker-proxy now; add NNLS reference deconvolution; later run cell2location/Tangram/RCTD. | fallback_implemented | Build matched scRNA reference matrices per cancer type. |
| HTAN validation | Use HTAN portal manifests and level-2 spatial transcriptomics auxiliary/RNA-seq files. | manifest_ready | Select one HTAN cancer atlas and download exported matrix + metadata. |
| Metastasis/progression cohorts | Run a smaller public GEO brain-metastasis cohort first; keep matched metastatic PDAC as scale-up. | first_real_cohort_implemented | Use GSE179572 as the real metastasis benchmark; next add GSE274557 primary/metastasis site labels. |

## Remaining Work

| Task | Status | Why It Still Matters |
| --- | --- | --- |
| HEST-1k manifest/reproducibility plan | partial | Needed for multimodal scale and H&E-linked validation. |
| cell2location/Tangram/RCTD/stereoscope deconvolution | blocked_external_reference | Needed to separate malignant EMT from CAF/stromal mixtures. |
| Candidate niche labels | partial | Needed before claims move beyond weak-label biology. |
| Histology-similarity edges | partial | Needed to fuse transcriptomic neighborhoods with tissue morphology. |
| HTAN spatial datasets | partial | Needed for external validation beyond 10x/GEO examples. |
| Additional GEO Visium cancer cohorts | partial | Needed for broader generalization and disease diversity. |
| SpatialTME/SCAR public atlas feasibility | partial | Needed to compare against public immune/stromal spatial atlases. |
| Matched scRNA-seq references | pending | Needed for real deconvolution and compartment-level claims. |
| Metastasis/progression cohorts | implemented_first_cohort | First cohort done; matched primary-metastatic PDAC remains the important scale-up. |
| Pathology foundation embeddings | pending | Needed for richer H&E features beyond color/stain proxies. |

## Next Execution Order

1. Rerun all spatial cohorts with the new ECM remodeling and angiogenesis features.
2. Add GSE274557 primary/liver/lung/peritoneal metastatic pancreatic cancer labels and run the full workflow.
3. Build one disease-matched scRNA reference matrix, then run NNLS deconvolution as the first real reference-based deconvolution output.
4. Select one HTAN spatial atlas and standardize it into the same expression/metadata format.
5. Add histology-similarity edges from H&E tile features; later replace proxies with foundation embeddings.
6. Draft pathologist-review templates for invasive edge, necrosis/hypoxia, stroma-rich, tumor-rich, and immune-rich regions.

## Publication Direction

The strongest first manuscript angle is not claiming a final GNN biomarker. It is a reproducible open pipeline showing how EMT-like tumor-cell plasticity, stromal inflation, CAF/TAM crosstalk, hypoxia, ECM remodeling, and metastasis-associated niches can be separated and stress-tested across public spatial cohorts.

## Key Public Resources

- 10x public Visium cancer examples.
- GEO GSE274103 treatment-naive pancreatic cancer Visium.
- GEO GSE179572 human brain metastasis Visium.
- GEO GSE274557 metastatic pancreatic cancer, prioritized for next matched-site validation.
- HEST-1k, pending authenticated metadata/image access.
- HTAN spatial transcriptomics portal, pending selected atlas ingestion.

## Clinical Caveats

- A high EMT score in a Visium spot can reflect malignant EMT, CAF/stromal admixture, or both.
- Partial EMT is a plasticity proxy, not a tumor-cell identity label.
- Current labels are weak labels generated from transcriptomic proxies.
- Survival or treatment implications require independent clinical annotation and expert review.
