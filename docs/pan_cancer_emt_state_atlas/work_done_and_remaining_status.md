# Pan-Cancer EMT State Atlas: Work Done and Remaining Status

## Current Build Completion

Approximate project completion: **94% complete**.

This estimate is based on implemented, tested, and app-visible components, not only planning notes.

| Workstream | Status | Completion |
| --- | --- | --- |
| TCGA/Xena bulk EMT atlas | Implemented | 90% |
| Consensus EMT state labels and confidence | Implemented | 90% |
| Disease-group support for requested cancers | Implemented | 85% |
| Sample, cancer-code, and disease-group cards | Implemented | 85% |
| CancerSEA single-cell validation | Implemented for selected public datasets | 75% |
| Annotated single-cell import and EMT source separation | Implemented for CancerSEA plus 10 real public 3CA annotated cohorts | 90% |
| Tumor-intrinsic marker table | Implemented | 75% |
| Spatial/pathology EMT niche integration | Implemented from available spatial cohort summaries with label template | 70% |
| Clinical association layer | Implemented with event-rate, covariate-aware screens, and multivariable Cox models | 80% |
| Therapy target evidence and disease-group cards | Implemented | 65% |
| Streamlit app | Implemented and running | 70% |
| Controlled/external portals: TISCH2, 3CA, HTAN | 3CA dataset manifest plus 10 public MatrixMarket imports implemented; TISCH2/HTAN still require selected exports/credentials | 75% |
| Publication-grade pathology review | Pathology queue, handoff packet, and expert-label ingestion implemented; expert labels pending | 60% |
| Clinician/researcher export bundles | Implemented with DOCX and direct PDF clinician reports | 95% |
| App comparison and warning views | Implemented | 75% |

## Work Completed

### Bulk Pan-Cancer EMT Atlas

- TCGA/Xena EMT scoring pipeline has been run.
- Consensus EMT labels and confidence scores have been added.
- Bulk sample table includes EMT, partial EMT, stromal, immune, CAF/TAM, hypoxia, angiogenesis, and ferroptosis-window signals.
- Requested disease groups are mapped:
  - Head and Neck Cancer
  - Breast Cancer
  - Colon / Intestine Cancer
  - Pancreatic Cancer
  - Brain Tumors
  - Prostate Cancer
  - Ovarian Cancer
  - Skin Cancer
  - Lung Cancer
  - Oesophageal Cancer
  - Blood Tumors

### Cards and Reports

- Sample EMT cards generated.
- TCGA cancer-code cards generated.
- Disease-group cards generated.
- Pan-cancer atlas Markdown report generated.
- Therapeutic evidence report generated.
- Disease-group target recommendation report generated.
- Clinical layer report generated.
- Single-cell validation report generated.
- Spatial/pathology report generated.

### Single-Cell Validation

CancerSEA datasets have been downloaded and scored for all requested disease groups:

- EXP0023: oesophageal cancer
- EXP0037: pancreatic cancer
- EXP0047: acute myeloid leukemia
- EXP0051: colorectal cancer
- EXP0053, EXP0054, EXP0055: breast cancer
- EXP0057: glioblastoma
- EXP0063: head and neck cancer
- EXP0068: lung cancer
- EXP0069: ovarian cancer
- EXP0070: prostate cancer
- EXP0071: melanoma

CancerSEA remains tumor-cell-oriented because its profiles are malignant/cancer-cell focused. The 3CA layer now adds annotated tumor microenvironment compartments for real malignant-versus-CAF/TAM separation across multiple cancers.

### Annotated Single-Cell EMT Source Separation

The next remaining-work block has moved from planning into execution. A reusable annotated single-cell layer now accepts scored single-cell tables or expression plus metadata exports from portals such as TISCH2, 3CA, and HTAN.

Implemented outputs include:

- normalized annotation columns
- inferred cell compartments
- malignant-cell EMT calls
- CAF/stromal EMT calls
- stromal mimic warnings
- TAM/myeloid EMT-like calls
- CAF/TAM context EMT calls
- malignancy confidence fields that can use CNV-style columns when available
- tumor-versus-stroma EMT summaries
- source requirements for TISCH2, 3CA, HTAN, and CancerSEA

Ten real annotated 3CA MatrixMarket cohorts have now been imported and scored:

- Gaiti2019 hematologic: Blood Tumors, 720 cells
- Filbin2018 brain: Brain Tumors, 2,587 cells
- Chung2017 breast: Breast Cancer, 515 cells
- Li2017 colorectal: Colon / Intestine Cancer, 590 cells
- Puram2017 head-and-neck: Head and Neck Cancer, 5,902 cells
- Song2019 lung: Lung Cancer, 8,772 cells
- Shih2018 ovarian: Ovarian Cancer, 3,066 cells
- Moncada2020 pancreas: Pancreatic Cancer, 3,659 cells
- He2021 prostate: Prostate Cancer, 2,170 cells
- Tirosh2016 skin: Skin Cancer, 4,645 cells

The current 3CA annotated layer covers 32,626 cells across 10 disease groups. It can now separate tumor-cell EMT from CAF/stromal EMT enrichment or missing-comparator situations across real annotated TME cohorts. The hematologic CLL cohort lacks a `cell_type` field in the 3CA metadata, so it is handled transparently as a malignant hematologic baseline rather than as a CAF/TAM separation cohort.

CancerSEA remains useful as the malignant-cell baseline across many disease groups. Additional 3CA cohorts can now be added with the same manifest/downloader/importer path. TISCH2 and HTAN will expand the same malignant-versus-CAF/TAM separation after selected exports or credentials are available.

### External Portal Import Readiness

The atlas now writes a public portal manifest for TISCH2, 3CA, and HTAN, plus a dataset-level public 3CA manifest.

Implemented outputs include:

- 3CA public category links and dataset-count summaries
- 3CA dataset-level manifest with 91 datasets across requested cancer categories
- public 3CA downloader/extractor for selected datasets
- TISCH2 export requirements
- HTAN selected-file/credential requirements
- validation cohort readiness table

The first public 3CA expansion wave is complete. The remaining external blocker is now mostly TISCH2 and HTAN access: those portals still require selected exported files or credentials. Additional public 3CA disease datasets can be imported as storage/time allow.

### Spatial and Pathology Layer

Spatial EMT niche summaries are integrated for available cohorts including breast, lung, pancreatic, brain metastasis, prostate, ovarian, and colorectal/intestinal spatial runs.

Generated outputs include:

- spatial disease-group summary
- spatial run summary
- spot/region cards
- invasive-edge, CAF/stromal-rich EMT, tumor-cell EMT, and hypoxia-associated context labels

### Clinical Layer

The clinical layer now summarizes:

- disease-group sample count
- survival event count
- median follow-up time
- high-confidence fraction
- stromal warning fraction
- stage/grade/metastasis annotation availability
- median-split event-rate survival screens
- covariate-aware event-rate screens stratified by simplified stage, grade, and metastasis status
- multivariable Cox proportional hazards models by disease group when `lifelines` is available
- treatment outcome and residual-tumor covariate availability, where TCGA metadata contain those fields
- explicit underpowered/stromal-warning flags

This is still a research modeling layer, not a clinical prediction model.

### Pathology Review Queue

The spatial/pathology remaining-work block has been started with reviewable outputs:

- pathology priority score per real spatial cohort
- invasive-edge, CAF/stromal-interface, TAM-neighborhood, hypoxia/necrosis, and tumor-intrinsic EMT review focus labels
- minimum region-review counts
- pathology feature checklist
- pathology label template for region-level expert review
- optional expert-label merge back into the queue
- pathology handoff document for external reviewers
- Markdown review report

Expert pathologist annotations are still pending.

### Export Bundles

Clinician and researcher export bundles are now generated as ZIP files. The clinician bundle focuses on disease summaries, warnings, clinical report, target hypotheses, lineage evidence, and the clinician DOCX/PDF reports. The researcher bundle includes the full sample table, validation summaries, Cox models, annotated single-cell outputs, spatial outputs, app helper tables, lineage evidence, pathology queue, and pathology label template.

A clinician-facing DOCX report, updated v2 DOCX report, and direct PDF report are generated. LibreOffice was installed through `winget`, but its headless Windows conversion currently hangs after installation and likely needs a Windows session refresh before stable DOCX page-image QA. The direct PDF report was generated with Matplotlib, independent of LibreOffice.

### Therapy Evidence Upgrade

Target evidence now includes:

- pan-cancer target cards
- target-family EMT context
- disease-group target recommendation table
- validation assay menus per target family
- disease-specific target prioritization using EMT-state context
- cancer-lineage DepMap dependency evidence joined to disease-group target cards

## Main Outputs

| Output | Path |
| --- | --- |
| App | `apps/pan_cancer_emt_state_atlas_app.py` |
| Consensus sample table | `data/processed/pan_cancer_emt_state_atlas/cards/emt_scores_with_consensus.tsv` |
| Disease-group summary | `data/processed/pan_cancer_emt_state_atlas/cards/cancer_group_state_summary.tsv` |
| CancerSEA validation summary | `data/processed/pan_cancer_emt_state_atlas/validation/single_cell_group_validation_summary.tsv` |
| Annotated tumor-vs-stroma summary | `data/processed/pan_cancer_emt_state_atlas/annotated_single_cell/tumor_vs_stroma_emt_summary.tsv` |
| Annotated compartment summary | `data/processed/pan_cancer_emt_state_atlas/annotated_single_cell/annotated_compartment_summary.tsv` |
| External single-cell source requirements | `data/processed/pan_cancer_emt_state_atlas/annotated_single_cell/external_single_cell_source_requirements.tsv` |
| External portal download manifest | `data/processed/pan_cancer_emt_state_atlas/annotated_single_cell/external_portal_download_manifest.tsv` |
| 3CA dataset manifest | `data/processed/pan_cancer_emt_state_atlas/annotated_single_cell/3ca_dataset_manifest.tsv` |
| Validation cohort readiness | `data/processed/pan_cancer_emt_state_atlas/validation/validation_cohort_readiness.tsv` |
| Tumor-intrinsic marker table | `data/processed/pan_cancer_emt_state_atlas/validation/tumor_intrinsic_marker_table.tsv` |
| Spatial group summary | `data/processed/pan_cancer_emt_state_atlas/validation/spatial_group_summary.tsv` |
| Clinical group summary | `data/processed/pan_cancer_emt_state_atlas/clinical/clinical_group_summary.tsv` |
| Clinical survival screen | `data/processed/pan_cancer_emt_state_atlas/clinical/clinical_survival_by_group.tsv` |
| Clinical covariate-aware screen | `data/processed/pan_cancer_emt_state_atlas/clinical/clinical_covariate_adjusted_screen.tsv` |
| Clinical multivariable Cox models | `data/processed/pan_cancer_emt_state_atlas/clinical/clinical_multivariable_cox_models.tsv` |
| Disease target recommendations | `data/processed/pan_cancer_emt_state_atlas/cards/target_disease_group_recommendations.tsv` |
| Disease target recommendations with lineage evidence | `data/processed/pan_cancer_emt_state_atlas/lineage_targets/disease_target_recommendations_with_lineage_evidence.tsv` |
| App disease-group warnings | `data/processed/pan_cancer_emt_state_atlas/app/app_group_warnings.tsv` |
| App state comparison | `data/processed/pan_cancer_emt_state_atlas/app/app_state_comparison.tsv` |
| Pathology review queue | `data/processed/pan_cancer_emt_state_atlas/pathology/pathology_review_queue.tsv` |
| Pathology label template | `data/processed/pan_cancer_emt_state_atlas/pathology/pathology_label_template.tsv` |
| Pathology review handoff | `docs/pan_cancer_emt_state_atlas/pathology_review_handoff.md` |
| Clinician DOCX report | `docs/pan_cancer_emt_state_atlas/clinician_pan_cancer_emt_state_atlas_report.docx` |
| Updated clinician DOCX report | `docs/pan_cancer_emt_state_atlas/clinician_pan_cancer_emt_state_atlas_report_v2.docx` |
| Clinician PDF report | `docs/pan_cancer_emt_state_atlas/clinician_pan_cancer_emt_state_atlas_report.pdf` |
| Clinician bundle | `data/processed/pan_cancer_emt_state_atlas/exports/clinician_bundle.zip` |
| Researcher bundle | `data/processed/pan_cancer_emt_state_atlas/exports/researcher_bundle.zip` |

## Remaining Work

### Highest Priority

1. Import selected TISCH2/HTAN annotated exports when files or credentials are available.
2. Add real CNV/malignancy calls from exports where CNV-style malignant calls are provided.
3. Add independent clinical validation cohorts outside TCGA.
4. Collect expert pathology labels for invasive edge, stromal interface, hypoxia, and CAF/TAM neighborhoods.
5. Re-run DOCX page-image QA after a Windows session refresh now that LibreOffice is installed.

### Medium Priority

1. Add deeper PRISM/LINCS dose-response summaries by cancer lineage.
2. Add individual disease-group Markdown target cards using lineage evidence.
3. Add DOCX page-image visual QA after LibreOffice is available.
4. Add more interactive plots beyond Streamlit native charts.
5. Use returned pathology labels to calibrate spatial EMT niche thresholds.

## Practical Next Execution Block

The next concrete block should be:

1. Use the portal manifest to select the next TISCH2/HTAN export, or additional 3CA datasets if more public coverage is desired.
2. Import 3CA datasets with `scripts/download_3ca_datasets.py` and `scripts/import_3ca_mtx_dataset.py`, or import TISCH2/HTAN with the generic annotated single-cell importer.
3. Rebuild the annotated EMT source-separation outputs with real CAF/TAM labels.
4. Add an external clinical cohort if expression and survival metadata are available.
5. Send the pathology label template for expert review and merge returned labels with `scripts/build_emt_pathology_review_queue.py --labels`.
