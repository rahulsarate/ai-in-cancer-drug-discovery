# Spatial EMT Niche GNN Project Report

## Executive Summary

The project is currently 87.2% complete by the weighted implementation tracker.
It has processed 61,764 spatial spots and 1,303,172 graph edges across demo, 10x public cancer, GEO pancreatic cancer, and GEO brain-metastasis cohorts.
The core value is an interpretable pipeline for weak-label discovery of EMT, partial EMT, stromal contamination, CAF/TAM/hypoxic niches, ECM remodeling, angiogenesis, and ferroptosis-window signals in spatial transcriptomics.

All current outputs are research hypotheses only. They are not diagnostic, prognostic, or treatment recommendations.

## Completion Chart

| Phase | Completion |
| --- | ---: |
| advanced | 81.6% |
| starter | 87.5% |
| validation | 72.9% |
| workflow_graph | 94.3% |
| workflow_ingestion | 100.0% |
| workflow_scoring | 83.3% |
| overall | 87.2% |

## Implemented System

- Standardized public Visium and GEO cohorts into expression and spatial metadata tables.
- Exported lightweight AnnData-style h5ad files for downstream spatial workflows.
- Implemented EMT, partial EMT, stromal, immune, CAF/TAM, hypoxia, ECM remodeling, angiogenesis, and ferroptosis scores.
- Implemented marker-proxy and NNLS-reference deconvolution paths.
- Built typed spatial graphs with kNN/radius, ligand-receptor, hypoxia-gradient, and ECM-gradient edges.
- Built heterogeneous compartment graphs for tumor, CAF, TAM, endothelial, T cell, hypoxic, ECM-rich, and ferroptosis-window nodes.
- Trained a dependency-light graph-aware logistic baseline for reproducible MVP benchmarking.
- Added H&E tile color/stain-proxy feature extraction for 10x tissue images.
- Added first real histology-similarity graph edges in the 10x breast cohort.
- Added GSE274557 matched Pt-1 primary/liver/peritoneal metastatic PDAC pilot.
- Downloaded, standardized, and scored the full 55-sample non-PDX GSE274557 cohort locally.
- Completed patient-batched graph/model summaries for all 13 GSE274557 non-PDX patients.
- Added PDAC marker-reference NNLS deconvolution summary for the matched metastatic pilot.
- Added real GSE154778 scRNA-derived marker-assigned reference and NNLS deconvolution summary.

## Cohort Results

| Cohort | Spots | EMT niche fraction | Tumor-cell EMT fraction | Stromal-inflated fraction | Mean ECM | Mean angiogenesis | Edges | LR edges | Hypoxia edges | ECM edges | Histology edges |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| synthetic_demo | 144 | 0.250 | 0.167 | 0.083 | 0.000 | -0.000 | 1,807 | 776 | 90 | 77 | 0 |
| 10x_breast_ffpe_idc | 2,518 | 0.250 | 0.101 | 0.149 | 0.000 | 0.000 | 32,575 | 8,046 | 2,596 | 3,528 | 3,681 |
| 10x_lung_lusc_cytassist | 3,858 | 0.250 | 0.116 | 0.134 | -0.000 | 0.000 | 49,593 | 21,018 | 3,089 | 2,594 | 0 |
| geo_pdac_gse274103 | 23,436 | 0.250 | 0.135 | 0.115 | 0.000 | 0.000 | 432,914 | 251,484 | 23,809 | 18,103 | 0 |
| geo_met_pdac_gse274557_pt1 | 8,756 | 0.250 | 0.106 | 0.144 | 0.000 | 0.000 | 277,446 | 210,579 | 7,185 | 8,085 | 0 |
| geo_brain_met_gse179572 | 12,566 | 0.250 | 0.135 | 0.115 | 0.000 | -0.000 | 370,126 | 269,785 | 14,904 | 11,853 | 0 |
| 10x_prostate_ffpe | 4,371 | 0.250 | 0.153 | 0.097 | 0.000 | 0.000 | 66,541 | 26,594 | 7,518 | 6,525 | 0 |
| 10x_ovarian_ffpe | 3,455 | 0.250 | 0.067 | 0.183 | 0.000 | 0.000 | 38,628 | 11,353 | 3,304 | 3,499 | 0 |
| 10x_colorectal_intestinal_ffpe | 2,660 | 0.250 | 0.094 | 0.156 | -0.000 | -0.000 | 33,542 | 12,212 | 3,532 | 2,134 | 0 |

## Metastasis And Progression Work

| Accession | Disease | Samples | Pipeline Status | Output |
| --- | --- | --- | --- | --- |
| GSE274557 | metastatic pancreatic cancer | 55 samples; primary, liver, lung, peritoneal metastases | all_55_non_pdx_downloaded_standardized_scored_patient_batched_graph_complete | data/processed/spatial_emt_niche_gnn_geo_met_pdac_gse274557_patient_batches |
| GSE179572 | brain metastasis | six brain metastasis samples | downloaded_standardized_scored_graph_trained | data/processed/spatial_emt_niche_gnn_geo_brain_met |

## Full GSE274557 Scoring Scale-Up

Full non-PDX status: 55/55 samples downloaded for 13 patients.

| Site | Spots | EMT niche fraction | Stromal-inflated fraction | Tumor-cell EMT fraction | Mean CAF/TAM | Mean hypoxia | Mean ECM |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| liver_metastasis | 44,415 | 0.172 | 0.032 | 0.089 | -0.152 | 0.103 | -0.206 |
| lung_metastasis | 15,981 | 0.266 | 0.126 | 0.107 | 0.121 | -0.045 | 0.010 |
| peritoneal_metastasis | 36,633 | 0.346 | 0.198 | 0.170 | 0.070 | 0.056 | 0.157 |
| primary | 45,612 | 0.244 | 0.164 | 0.123 | 0.050 | -0.129 | 0.071 |

## Full GSE274557 Patient-Batched Graphs

| Patient | Samples | Spots | Edges | Test accuracy |
| --- | ---: | ---: | ---: | ---: |
| Pt-1 | 3 | 8,756 | 278,269 | 0.894 |
| Pt-10 | 4 | 8,792 | 285,528 | 0.898 |
| Pt-11 | 4 | 11,784 | 238,481 | 0.850 |
| Pt-12 | 4 | 11,072 | 324,560 | 0.841 |
| Pt-13 | 7 | 15,673 | 279,547 | 0.782 |
| Pt-2 | 3 | 7,863 | 119,698 | 0.831 |
| Pt-3 | 4 | 8,676 | 200,115 | 0.812 |
| Pt-4 | 4 | 12,044 | 210,986 | 0.833 |
| Pt-5 | 3 | 8,100 | 172,447 | 0.897 |
| Pt-6 | 6 | 11,853 | 342,740 | 0.770 |
| Pt-7 | 4 | 13,346 | 363,637 | 0.951 |
| Pt-8 | 5 | 13,178 | 322,132 | 0.852 |
| Pt-9 | 4 | 11,504 | 346,909 | 0.951 |

## Real scRNA-Based Deconvolution

Reference: GSE154778 PDAC primary and metastatic scRNA-seq, marker-assigned into major compartments.

| Sample | Site | Spots | Epithelial tumor | Mesenchymal-plastic tumor | CAF | TAM | T cell |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| GSM8452847_Pt-1A | primary | 2,753 | 0.286 | 0.098 | 0.295 | 0.056 | 0.043 |
| GSM8452848_Pt-1B | liver_metastasis | 2,956 | 0.312 | 0.083 | 0.045 | 0.178 | 0.180 |
| GSM8452849_Pt-1C | peritoneal_metastasis | 3,047 | 0.380 | 0.227 | 0.142 | 0.042 | 0.100 |

## Blocker Solutions

| Blocker | Current Solution | Status | Next Action |
| --- | --- | --- | --- |
| HEST-1k scale ingestion | Use authenticated HuggingFace/Hest library manifest; select cancer subsets first. | access_required | Request/confirm HF access, then cache HEST_v1_1_0.csv and subset cancer samples. |
| H&E/pathology features | Use 10x H&E tile features plus morphology embedding baseline; later add configured foundation model weights. | morphology_embedding_baseline_implemented | Configure UNI/CONCH/HEST-compatible model weights and compare embeddings to the current baseline. |
| Real deconvolution | Use marker-proxy, marker-reference NNLS, and real GSE154778 scRNA-derived NNLS now. | real_scrna_reference_v1_nnls_run | Install Scanpy/AnnData/Tangram/cell2location or R/spacexr in a dedicated environment for advanced deconvolution. |
| HTAN validation | Use HTAN portal manifests and level-2 spatial transcriptomics auxiliary/RNA-seq files. | htan_wustl_pdac_target_manifest_ready | Install/configure Synapse or use the HTAN portal Download selected files workflow for HTAN WUSTL PDAC. |
| Metastasis/progression cohorts | Run brain-metastasis, GSE274557 Pt-1 pilot, and full GSE274557 patient-batched graph/model summaries. | full_patient_batched_graph_complete | Use patient-batched outputs for leave-patient/site validation and manuscript figures. |

## Remaining Work

| Task | Status | Why It Still Matters |
| --- | --- | --- |
| HEST-1k manifest/reproducibility plan | access_required | Needed for multimodal scale and H&E-linked validation. |
| cell2location/Tangram/RCTD/stereoscope deconvolution | environment_blocked_after_real_reference | Needed to separate malignant EMT from CAF/stromal mixtures. |
| Candidate niche labels | template_ready | Needed before claims move beyond weak-label biology. |
| Histology-similarity edges | implemented_first_cohort | Needed to fuse transcriptomic neighborhoods with tissue morphology. |
| HTAN spatial datasets | portal_download_pending | Needed for external validation beyond 10x/GEO examples. |
| Additional GEO Visium cancer cohorts | implemented_multiple_cohorts | Needed for broader generalization and disease diversity. |
| SpatialTME/SCAR public atlas feasibility | feasibility_manifest_ready | Needed to compare against public immune/stromal spatial atlases. |
| Matched scRNA-seq references | real_reference_v1 | Needed for real deconvolution and compartment-level claims. |
| Metastasis/progression cohorts | full_graph_complete | First cohort done; matched primary-metastatic PDAC remains the important scale-up. |
| Pathology foundation embeddings | embedding_baseline_ready | Needed for richer H&E features beyond color/stain proxies. |

## Next Execution Order

1. Install a dedicated Python/R deconvolution environment for Tangram, cell2location, and RCTD.
2. Expand the real scRNA reference with GSE155698 and GSE205013, then compare against the GSE154778 reference.
3. Download one HTAN WUSTL PDAC spatial sample from the portal and adapt it into the standard expression/metadata format.
4. Run histology-similarity edges across every cohort with local H&E tiles, then compare against pathologist regions.
5. Use the pathologist review template to annotate invasive edge, necrosis/hypoxia, stroma-rich, tumor-rich, immune-rich, and vessel-rich regions.
6. Evaluate pathology foundation embeddings after the color/stain-proxy baseline is stable.

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
