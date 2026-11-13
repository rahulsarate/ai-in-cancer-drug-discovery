# Build Status: TNBC NAC EMT Digital Twin

## Completed in first implementation pass

- Locked the project to triple-negative breast cancer under neoadjuvant chemotherapy.
- Created project planning, variable, dataset, and sprint documents.
- Added a TNBC digital-twin config with EMT, hybrid plasticity, and resistance-axis marker blocks.
- Verified core Python tooling and installed `tabulate` for Markdown audit reports.
- Added a public-resource downloader for GEO and PubMed seed resources.
- Downloaded GEO series matrix files for 9 of 10 seeded datasets.
- Downloaded PubMed metadata and XML abstracts for the first literature seed.
- Added a GEO metadata parser and standardized first-pass TNBC, timepoint, and response labels.
- Added a four-compartment synthetic EMT digital-twin simulator.
- Downloaded and parsed GEO platform annotation files for expression-ready array datasets.
- Converted 7 GEO probe-level matrices to compact signature gene-level expression tables.
- Scored real TNBC NAC cohorts for EMT, TME, resistance axes, and first digital-twin state features.
- Built a first TNBC-likely response-labeled model table and baseline response predictors.
- Completed longitudinal EMT-shift analysis for `GSE43816` paired before/after NAC TNBC samples.
- Generated paired shift plots, delta heatmap, dominant resistance-axis plot, and a clinician-style digital-twin report for a representative patient.
- Calibrated first cohort-level E/H/M/P transition-rate priors from `GSE43816` paired state fractions.
- Analyzed `GSE43502` residual chemoresistant TNBC recurrence biology.
- Audited `GSE164715` persister scRNA metadata and supplementary-file availability.
- Downloaded `GSE164715_RAW.tar` and imported selected PDX scRNA matrix triplets for chemonaive, persister, residual, resistant, and recurrent states.
- Scored 66,515 single cells against EMT, resistance, and refined persister signatures.
- Added refined persister sub-signatures to `configs/tnbc_digital_twin.yml`: tumor-cell persister, stress-tolerance, and persister-niche layers.
- Performed human/mouse feature separation and human-dominant cell filtering on selected `GSE164715` PDX scRNA matrices.
- Rebuilt persister contrasts using 26,730 human-dominant cells to reduce host/niche contamination in the tumor `P` state.
- Used `GSE43816` calibrated transition priors and refined persister layers inside the therapy simulator.
- Added calibrated-prior uncertainty bands to the synthetic therapy simulation.
- Updated the `GSE43816` clinician-style report with cohort-relative percentiles and bootstrap uncertainty intervals.
- Added targeted malignant/endothelial/stromal/immune annotation for 26,730 human-dominant `GSE164715` cells.
- Added bootstrap confidence intervals for `GSE43502` recurrence-axis differences.
- Built a validation memo separating clinician-style research reporting from exploratory-only outputs.
- Added a reproducible end-to-end TNBC digital-twin pipeline runner with dry-run and skip-existing modes.
- Added external validation hooks and input templates for independent TNBC NAC response datasets.
- Added `GSE163882` as a real held-out external-style TNBC NAC RNA-seq TPM validation cohort.
- Added platform-normalization diagnostics comparing internal array-derived features with external RNA-seq TPM-derived features.
- Added internal-empirical-percentile calibration for cross-platform external validation.
- Split response-model reporting into same-platform and cross-platform validation reports.
- Added external z-score alignment and external quantile-to-internal calibration for cross-platform validation.
- Added response-label audit tables for the main response-model cohorts.
- Added bootstrap robustness intervals for `GSE163882` external response metrics.
- Added directional marker-panel validation for `GSE164715` targeted annotations.
- Added locked response-label curation for flagged `GSE25055` and `GSE25065` rows, with a curated-label sensitivity model.
- Added leave-dataset-out validation for small independent TNBC NAC cohorts `GSE18864` and `GSE45898`.
- Added explicit `GSE164715` ambiguous-compartment review for publication claim control.
- Built a manuscript-ready results bundle.
- Drafted a manuscript/thesis chapter from the locked analysis outputs.
- Froze final reports, tables, and figures into a checksum-tracked release folder.

## Local data now present

Raw GEO series matrices:

- `GSE163882`
- `GSE164715`
- `GSE18864`
- `GSE25055`
- `GSE25065`
- `GSE25066`
- `GSE43502`
- `GSE43816`
- `GSE45898`

Manual-review item:

- `GSE194040`: standard GEO series-matrix URL returned 404. This likely requires supplemental-file-specific handling rather than the generic matrix path.

## Current parsed cohort size

The current GEO metadata parser found:

- 1,390 total parsed samples.
- 604 TNBC-confirmed or TNBC-likely samples.
- 9 datasets with local matrix metadata.

Response label availability:

| Dataset | Response labels parsed | Notes |
| --- | ---: | --- |
| GSE163882 | 222 | RNA classifier cohort; 90 TNBC-likely samples. |
| GSE18864 | 24 | Miller-Payne response converted conservatively; 60 samples still unknown. |
| GSE25055 | 310 | Discovery NAC cohort; 116 TNBC-likely samples. |
| GSE25065 | 198 | Validation NAC cohort; 65 TNBC-likely samples. |
| GSE25066 | 508 | Combined SuperSeries; 181 TNBC-likely samples. |
| GSE45898 | 10 | Small TNBC response cohort. |
| GSE43816 | 0 | Useful longitudinal before/after cohort, but response labels need manual curation. |
| GSE43502 | 0 | Residual chemoresistant TNBC biology cohort. |
| GSE164715 | 0 | Single-cell/persister biology metadata; expression assets need separate handling. |

## Generated outputs

- `data/processed/tnbc_digital_twin/tnbc_nac_dataset_inventory_seed.tsv`
- `data/processed/tnbc_digital_twin/tnbc_nac_literature_seed.tsv`
- `data/processed/tnbc_digital_twin/tnbc_nac_geo_download_audit.tsv`
- `data/processed/tnbc_digital_twin/tnbc_nac_geo_sample_metadata.tsv`
- `data/processed/tnbc_digital_twin/tnbc_nac_geo_tnbc_likely_samples.tsv`
- `data/processed/tnbc_digital_twin/tnbc_nac_geo_matrix_dimensions.tsv`
- `data/processed/tnbc_digital_twin/tnbc_nac_geo_metadata_summary.md`
- `data/processed/tnbc_digital_twin/tnbc_digital_twin_synthetic_trajectories.tsv`
- `data/processed/tnbc_digital_twin/tnbc_digital_twin_synthetic_summary.tsv`
- `data/processed/tnbc_digital_twin/tnbc_digital_twin_calibrated_prior_trajectories.tsv`
- `data/processed/tnbc_digital_twin/tnbc_digital_twin_calibrated_prior_summary.tsv`
- `data/processed/tnbc_digital_twin/tnbc_digital_twin_calibrated_uncertainty_bands.tsv`
- `data/processed/tnbc_digital_twin/tnbc_digital_twin_calibrated_uncertainty_final_states.tsv`
- `data/processed/tnbc_digital_twin/tnbc_digital_twin_therapy_simulation_report.md`
- `data/processed/tnbc_digital_twin/tnbc_digital_twin_archetype_parameters.json`
- `data/processed/tnbc_digital_twin/tnbc_nac_platform_annotation_audit.tsv`
- `data/processed/tnbc_digital_twin/tnbc_nac_gene_expression_audit.tsv`
- `data/processed/tnbc_digital_twin/tnbc_nac_gene_expression_build_report.md`
- `data/processed/tnbc_digital_twin/gene_expression/*_signature_gene_expression.tsv`
- `data/processed/tnbc_digital_twin/tnbc_nac_emt_digital_twin_scores.tsv`
- `data/processed/tnbc_digital_twin/tnbc_nac_emt_digital_twin_model_table.tsv`
- `data/processed/tnbc_digital_twin/tnbc_nac_emt_digital_twin_tnbc_response_model_table.tsv`
- `data/processed/tnbc_digital_twin/tnbc_nac_response_model_table_deduplicated.tsv`
- `data/processed/tnbc_digital_twin/tnbc_nac_response_model_metrics.tsv`
- `data/processed/tnbc_digital_twin/tnbc_nac_response_model_feature_importance.tsv`
- `data/processed/tnbc_digital_twin/tnbc_nac_response_model_report.md`
- `data/processed/tnbc_digital_twin/gse43816_longitudinal/gse43816_paired_shift_wide.tsv`
- `data/processed/tnbc_digital_twin/gse43816_longitudinal/gse43816_paired_shift_long.tsv`
- `data/processed/tnbc_digital_twin/gse43816_longitudinal/gse43816_shift_summary.tsv`
- `data/processed/tnbc_digital_twin/gse43816_longitudinal/gse43816_shift_bootstrap_uncertainty.tsv`
- `data/processed/tnbc_digital_twin/gse43816_longitudinal/gse43816_longitudinal_emt_shift_report.md`
- `data/processed/tnbc_digital_twin/gse43816_longitudinal/gse43816_clinician_style_digital_twin_report.md`
- `docs/tnbc_digital_twin_emt_plasticity/assets/gse43816_longitudinal/*.png`
- `docs/tnbc_digital_twin_emt_plasticity/assets/therapy_simulation/*.png`
- `data/processed/tnbc_digital_twin/transition_calibration/gse43816_calibrated_transition_parameters.tsv`
- `data/processed/tnbc_digital_twin/transition_calibration/gse43816_transition_fit_predictions.tsv`
- `data/processed/tnbc_digital_twin/transition_calibration/gse43816_transition_allocation_matrix.tsv`
- `data/processed/tnbc_digital_twin/transition_calibration/gse43816_transition_calibration_report.md`
- `data/processed/tnbc_digital_twin/residual_persister_biology/gse43502_recurrence_feature_summary.tsv`
- `data/processed/tnbc_digital_twin/residual_persister_biology/gse43502_resistance_axis_counts.tsv`
- `data/processed/tnbc_digital_twin/residual_persister_biology/gse164715_persister_metadata_summary.tsv`
- `data/processed/tnbc_digital_twin/residual_persister_biology/gse164715_supplement_listing.tsv`
- `data/processed/tnbc_digital_twin/residual_persister_biology/residual_persister_biology_report.md`
- `data/processed/tnbc_digital_twin/tnbc_digital_twin_validation_memo.md`
- `docs/tnbc_digital_twin_emt_plasticity/validation_memo.md`
- `data/processed/tnbc_digital_twin/pipeline_runs/tnbc_digital_twin_pipeline_run_manifest.json`
- `data/processed/tnbc_digital_twin/pipeline_runs/tnbc_digital_twin_pipeline_run_report.md`
- `data/processed/tnbc_digital_twin/external_validation/external_validation_input_templates.md`
- `data/processed/tnbc_digital_twin/external_validation/external_scored_feature_template.tsv`
- `data/processed/tnbc_digital_twin/external_validation/external_expression_template.tsv`
- `data/processed/tnbc_digital_twin/external_validation/external_metadata_template.tsv`
- `data/processed/tnbc_digital_twin/external_validation/external_validation_report.md`
- `data/processed/tnbc_digital_twin/external_validation_smoke_test/external_validation_report.md`
- `data/processed/tnbc_digital_twin/external_validation/gse163882/gse163882_external_preparation_report.md`
- `data/processed/tnbc_digital_twin/external_validation/gse163882/gse163882_tnbc_external_expression_log2tpm.tsv`
- `data/processed/tnbc_digital_twin/external_validation/gse163882/gse163882_tnbc_external_metadata.tsv`
- `data/processed/tnbc_digital_twin/external_validation/gse163882/external_validation_report.md`
- `data/processed/tnbc_digital_twin/external_validation/gse163882/external_validation_metrics.tsv`
- `data/processed/tnbc_digital_twin/platform_normalization/tnbc_platform_normalization_diagnostics_report.md`
- `data/processed/tnbc_digital_twin/platform_normalization/tnbc_platform_feature_shift_diagnostics.tsv`
- `data/processed/tnbc_digital_twin/tnbc_same_platform_response_model_report.md`
- `data/processed/tnbc_digital_twin/tnbc_cross_platform_external_validation_report.md`
- `data/processed/tnbc_digital_twin/response_label_audit/tnbc_response_label_audit_report.md`
- `data/processed/tnbc_digital_twin/response_label_curation/tnbc_response_label_curation_signoff_report.md`
- `data/processed/tnbc_digital_twin/response_label_curation/curated_model/tnbc_nac_response_model_report.md`
- `data/processed/tnbc_digital_twin/leave_dataset_out_validation/tnbc_leave_dataset_out_validation_report.md`
- `data/processed/tnbc_digital_twin/response_model_robustness/gse163882_external_metric_bootstrap_report.md`
- `data/processed/tnbc_digital_twin/gse164715_marker_validation/gse164715_marker_panel_validation_report.md`
- `data/processed/tnbc_digital_twin/gse164715_ambiguity_review/gse164715_ambiguity_review_report.md`
- `docs/tnbc_digital_twin_emt_plasticity/assets/gse164715_marker_validation/*.png`
- `docs/tnbc_digital_twin_emt_plasticity/manuscript_bundle/tnbc_manuscript_results_bundle_summary.md`
- `docs/tnbc_digital_twin_emt_plasticity/manuscript_bundle/bundle_file_index.tsv`
- `docs/tnbc_digital_twin_emt_plasticity/manuscript_draft_tnbc_emt_digital_twin.md`
- `docs/tnbc_digital_twin_emt_plasticity/final_project_report_tnbc_emt_digital_twin.md`
- `docs/tnbc_digital_twin_emt_plasticity/manuscript_full_draft_tnbc_emt_digital_twin.md`
- `docs/tnbc_digital_twin_emt_plasticity/novelty_positioning/novelty_and_positioning_report.md`
- `docs/tnbc_digital_twin_emt_plasticity/novelty_positioning/tnbc_emt_digital_twin_novelty_deck.pptx`
- `docs/tnbc_digital_twin_emt_plasticity/novelty_positioning/assets/*.png`
- `docs/tnbc_digital_twin_emt_plasticity/frozen_releases/tnbc_digital_twin_freeze_2026-06-15/README.md`
- `docs/tnbc_digital_twin_emt_plasticity/assets/platform_normalization/*.png`
- `docs/tnbc_digital_twin_emt_plasticity/assets/transition_calibration/*.png`
- `docs/tnbc_digital_twin_emt_plasticity/assets/residual_persister_biology/*.png`
- `data/processed/tnbc_digital_twin/gse164715_persister_scrna/gse164715_scrna_import_audit.tsv`
- `data/processed/tnbc_digital_twin/gse164715_persister_scrna/gse164715_persister_scrna_cell_scores.tsv.gz`
- `data/processed/tnbc_digital_twin/gse164715_persister_scrna/gse164715_persister_scrna_stage_summary.tsv`
- `data/processed/tnbc_digital_twin/gse164715_persister_scrna/gse164715_persister_scrna_chemonaive_contrasts.tsv`
- `data/processed/tnbc_digital_twin/gse164715_persister_scrna/gse164715_persister_signature_gene_contrasts.tsv`
- `data/processed/tnbc_digital_twin/gse164715_persister_scrna/gse164715_persister_scrna_import_report.md`
- `docs/tnbc_digital_twin_emt_plasticity/persister_state_refinement.md`
- `docs/tnbc_digital_twin_emt_plasticity/assets/gse164715_persister_scrna/*.png`
- `data/processed/tnbc_digital_twin/gse164715_human_filter/gse164715_species_filter_import_audit.tsv`
- `data/processed/tnbc_digital_twin/gse164715_human_filter/gse164715_species_call_summary.tsv`
- `data/processed/tnbc_digital_twin/gse164715_human_filter/gse164715_species_qc_by_cell.tsv.gz`
- `data/processed/tnbc_digital_twin/gse164715_human_filter/gse164715_human_dominant_cell_scores.tsv.gz`
- `data/processed/tnbc_digital_twin/gse164715_human_filter/gse164715_human_dominant_chemonaive_contrasts.tsv`
- `data/processed/tnbc_digital_twin/gse164715_human_filter/gse164715_human_dominant_gene_contrasts.tsv`
- `data/processed/tnbc_digital_twin/gse164715_human_filter/gse164715_human_dominant_filter_report.md`
- `docs/tnbc_digital_twin_emt_plasticity/assets/gse164715_human_filter/*.png`
- `data/processed/tnbc_digital_twin/gse164715_targeted_annotation/gse164715_targeted_cell_annotations.tsv.gz`
- `data/processed/tnbc_digital_twin/gse164715_targeted_annotation/gse164715_targeted_cluster_summary.tsv`
- `data/processed/tnbc_digital_twin/gse164715_targeted_annotation/gse164715_targeted_annotation_stage_summary.tsv`
- `data/processed/tnbc_digital_twin/gse164715_targeted_annotation/gse164715_persister_annotation_enrichment.tsv`
- `data/processed/tnbc_digital_twin/gse164715_targeted_annotation/gse164715_targeted_annotation_report.md`
- `docs/tnbc_digital_twin_emt_plasticity/assets/gse164715_targeted_annotation/*.png`

## First digital-twin model implemented

The current prototype uses four states:

- `E`: epithelial-like chemo-sensitive cells.
- `H`: hybrid epithelial/mesenchymal plastic cells.
- `M`: mesenchymal-like resistant cells.
- `P`: drug-tolerant persister cells.

Synthetic archetypes:

- `chemo_sensitive_epithelial`
- `plastic_residual_risk`
- `mesenchymal_persister_high`

## First response-model result

The first deduplicated TNBC-likely response table contains 215 response-labeled samples after removing `GSE25066` superseries duplicates in favor of `GSE25055` and `GSE25065` subseries rows.

First-pass results:

- EMT-only features perform weakly, which means baseline EMT score alone is not sufficient.
- EMT plus TME/resistance-axis features improve stratified cross-validation AUROC relative to EMT-only.
- Train-on-`GSE25055`, test-on-`GSE25065` performance remains modest, so this should be treated as a starting benchmark rather than a clinically useful predictor.
- Digital-twin state features provide a transparent state summary but need stronger calibration with longitudinal and/or response-specific datasets.

## GSE43816 longitudinal EMT-shift result

`GSE43816` contains 7 paired TNBC patients with pretreatment and post-NAC/tumorectomy samples. This cohort does not include response labels in the parsed GEO metadata, so it is used to study therapy-induced plasticity rather than pCR prediction.

Main paired-shift findings:

- Mean EMT score decreased after NAC, but 4 of 7 patients increased.
- Hybrid E/M fraction increased in 4 of 7 patients.
- Therapy-selection pressure increased in 4 of 7 patients.
- Median residual-disease-risk proxy decreased slightly, but 3 of 7 patients increased.
- The selected clinician-report case, patient 6, remained persister-dominant and showed increased modeled therapy-selection pressure after NAC.

## E/H/M/P transition calibration result

The first transition calibration fits normalized pretreatment E/H/M/P fractions to post-NAC fractions in the 7 `GSE43816` paired patients.

Fit summary:

- Paired patients: 7.
- State-fraction RMSE: approximately 0.10.
- Optimizer converged successfully.
- The fitted rates should be treated as regularized simulation priors because tumor burden and response labels are unavailable in this cohort.

The calibrated transition allocation suggests the model needs reversible plasticity between epithelial/hybrid and persister/hybrid states to explain the observed post-treatment fractions.

## Calibrated therapy-simulation result

The therapy simulator now has two modes:

- Baseline synthetic archetypes.
- `GSE43816` calibrated-prior archetypes with refined persister-layer effects.

The calibrated-prior simulation adds uncertainty bands by perturbing the 7-patient transition calibration. Final-state uncertainty summaries are available for tumor burden, persister fraction, plasticity index, and resistant fraction.

In the calibrated-prior simulation:

- `chemo_sensitive_epithelial` ends with lower tumor burden but still gains resistant/persister fraction.
- `plastic_residual_risk` and `mesenchymal_persister_high` retain higher final burden and high resistant fraction.
- This supports using the simulator as a transparent scenario engine rather than a final patient-level predictor.

## Residual and persister biology result

`GSE43502` contributes 25 residual chemoresistant TNBC samples with recurrence/no-recurrence labels. In this first-pass analysis:

- Recurrent residual samples trend higher for AXL/TAM and hypoxia-axis scores.
- Bootstrap mean-difference intervals now support AXL/TAM and hypoxia as the strongest positive recurrence-associated directions in this small cohort.
- YAP/TAZ trends lower in recurrence samples in the current resampling analysis.
- The cohort is too small for strong statistical claims; these trends are hypothesis-generating.
- The result supports keeping AXL/TAM, hypoxia, CAF/TAM niche, and persister/stemness axes in the digital-twin residual-risk model.

`GSE164715` now contributes metadata, supplement availability, and a selected raw scRNA import:

- 19 persister-related scRNA sample records.
- Supplementary files are available, including `GSE164715_RAW.tar` and scRNA metadata files.
- Selected PDX scRNA matrices have been imported and scored for targeted EMT/resistance/persister features.

## GSE164715 scRNA persister import result

The raw scRNA archive was downloaded and selected PDX matrices were imported for:

- `HBCx95`: chemonaive, persister, residual, resistant, recurrent.
- `HBCx39`: chemonaive, persister.
- `HBCx172`: chemonaive, persister.

Import scale:

- 66,515 cells scored.
- 9 samples imported.
- 154 target genes detected.

Main interpretation:

- The original `tnbc_stemness_persister` signature alone is not sufficient to represent persister biology.
- HBCx95 persister cells show strong targeted increases in niche/vascular genes such as `FLT1`, `CDH5`, `PECAM1`, `KDR`, and `CXCL12`, which should be tracked separately from tumor-cell persister identity.
- Candidate tumor/stress persister genes from the targeted import include `NOTCH1`, `WWTR1`, `YAP1`, `TGFB1`, `HMOX1`, `GAS6`, `ZEB1`, `CD274`, `FTH1`, `FTL`, and `KRT14`.
- The digital twin now separates persister evidence into tumor-cell persister, stress-tolerance, and persister-niche layers.

## GSE164715 human-dominant filtering result

The selected PDX matrices contain both human (`hg19`) and mouse (`mm10`) features. A species-aware filter classified cells by human and mouse count fractions.

Filtering result:

- Total cells inspected: 66,515.
- Human-dominant cells retained for malignant-cell scoring: 26,730.
- `HBCx95_persister` is mostly mouse-dominant: 541 human-dominant cells versus 14,722 mouse-dominant cells.
- `HBCx39_persister` is mostly human-dominant: 2,421 human-dominant cells.
- `HBCx172_persister` has a smaller human-dominant persister compartment: 461 cells.

Digital-twin implication:

- Use human-dominant cells to refine the tumor-cell `P` state.
- Treat mouse-dominant cells as host/niche context.
- Keep vascular/niche genes separate as a `persister_niche` modifier.
- Human-dominant persister contrasts highlight stress/plasticity candidates such as `FTL`, `FTH1`, `GPX4`, `KRT14`, `KRT19`, `YAP1`, `SMAD2`, `HIF1A`, `BNIP3`, `LAMC2`, and `S100A4`.

## GSE164715 targeted annotation result

Human-dominant cells were annotated using targeted EMT, persister, endothelial, stromal, and immune score layers.

Annotation scale:

- Human-dominant cells annotated: 26,730.
- Malignant-like: 9,983.
- Ambiguous human: 9,691.
- Stromal-like: 2,619.
- Endothelial-like: 2,322.
- Immune-like: 2,115.

Main interpretation:

- `HBCx39_persister` shows a modest malignant-like fraction increase versus chemonaive.
- `HBCx95_persister` human-dominant cells show lower malignant-like fraction and higher ambiguous/stromal-like fractions versus chemonaive, consistent with the earlier warning that this sample is dominated by host/niche signal.
- These are targeted annotations, not a full single-cell atlas; marker-panel direction checks now support the broad annotation layers, but publication-level single-cell claims still need expert review of ambiguous compartments.

## Validation memo result

The validation memo explicitly separates:

- Clinician-style research report elements that can be shown with strong caveats.
- Exploratory-only outputs that should not be used for treatment selection.
- Current model-performance limitations.
- Required next validation actions before broader clinical interpretation.

## Reproducibility and external validation result

The project now has a one-command runner:

- `python scripts/run_tnbc_digital_twin_pipeline.py`

Default behavior uses local data, skips fresh GEO/PubMed downloads, and skips the long raw scRNA import/filter steps. Optional flags:

- `--dry-run`: list the exact execution order without running scripts.
- `--skip-existing`: verify required outputs and avoid rerunning completed steps.
- `--include-downloads`: include the public-resource download step.
- `--include-scrna`: include long raw `GSE164715` scRNA import/filter steps.
- `--start-at` / `--stop-after`: resume or bound the pipeline.

The external validation hook supports:

- Already-scored external EMT/digital-twin feature tables.
- External sample-by-gene expression matrices plus response metadata.
- Template generation when no external dataset is supplied.

`GSE163882` has now been added as the first real external-style validation cohort:

- Source expression: `GSE163882_all.data.tpms_222Samples.csv.gz`.
- Prepared scale: `log2(TPM + 1)`.
- TNBC response-labeled samples with expression: 90.
- Response balance: 38 pCR/good response and 52 residual/poor response.
- Mapped target genes: 154.

External validation results on `GSE163882_TNBC_TPM`:

- EMT-core: AUROC 0.434, AUPRC 0.583.
- EMT plus TME/resistance: AUROC 0.643, AUPRC 0.708.
- Digital-twin features: AUROC 0.584, AUPRC 0.700.
- Combined features: AUROC 0.648, AUPRC 0.721.

Internal-percentile calibrated external validation results:

- EMT-core: AUROC 0.445, AUPRC 0.567.
- EMT plus TME/resistance: AUROC 0.610, AUPRC 0.662.
- Digital-twin features: AUROC 0.507, AUPRC 0.626.
- Combined features: AUROC 0.611, AUPRC 0.674.

Percentile calibration did not improve `GSE163882` performance. This suggests that some of the useful external signal is carried by raw signature-space structure, while the validation remains sensitive to cohort/platform feature shifts.

Additional cross-platform calibration results:

- External z-score alignment, combined: AUROC 0.632, AUPRC 0.708.
- External quantile-to-internal mapping, combined: AUROC 0.649, AUPRC 0.714.
- External quantile-to-internal mapping slightly improves combined AUROC over raw and improves accuracy, but the gain is small and should be treated as calibration sensitivity rather than definitive correction.

Bootstrap robustness intervals were added for external metrics. For the external quantile-to-internal combined model, AUROC is approximately 0.649 with a bootstrap 95% interval of about 0.521 to 0.728.

Platform-normalization diagnostics show the largest internal-versus-external shifts in `tnbc_stemness_persister`, `tnbc_hypoxia`, `tnbc_yap_taz`, and `therapy_selection_pressure`. These shifts mean the external results are encouraging but should be treated as platform-sensitive research validation, not final clinical performance.

## Finalization work completed

Response-label curation has been completed computationally:

- `GSE25055`: 13 TNBC rows with pathology evidence of residual disease were recoded from the broad good-response bucket to `residual_or_poor_response` in the curated sensitivity table.
- `GSE25065`: 22 TNBC rows with pathology evidence of residual disease were recoded from the broad good-response bucket to `residual_or_poor_response` in the curated sensitivity table.
- `GSE18864`: 60 unknown response labels remain excluded.
- The original broad endpoint is preserved for historical comparison, while the curated table is used for sensitivity modeling.

Curated-label sensitivity result:

- Combined features, train `GSE25055` and test `GSE25065`: AUROC 0.609, AUPRC 0.784, accuracy 0.600.
- EMT plus TME/resistance, train `GSE25055` and test `GSE25065`: AUROC 0.619, AUPRC 0.804, accuracy 0.600.

Additional same-project independent holdout validation has been added:

- `GSE18864` leave-dataset-out validation: small 24-sample TNBC NAC cohort, best combined calibration AUROC 0.531 and AUPRC 0.752.
- `GSE45898` leave-dataset-out validation: very small 10-sample TNBC NAC cohort, best combined calibration AUROC 0.625 and AUPRC 0.876.
- These checks are sensitivity/robustness evidence only because cohort sizes are small.

`GSE164715` ambiguity review has been completed:

- Marker-panel direction checks passed 11 of 11 checks.
- `cluster_1` is the dominant ambiguous human cluster and should not be assigned a definitive cell type.
- High-ambiguity HBCx172 sample-stage rows and moderate-ambiguity HBCx39/HBCx95 rows must be described cautiously.

Final manuscript artifacts have been created:

- Manuscript/thesis draft: `docs/tnbc_digital_twin_emt_plasticity/manuscript_draft_tnbc_emt_digital_twin.md`.
- Detailed final project report: `docs/tnbc_digital_twin_emt_plasticity/final_project_report_tnbc_emt_digital_twin.md`.
- Full manuscript draft with literature grounding and clinical/research importance: `docs/tnbc_digital_twin_emt_plasticity/manuscript_full_draft_tnbc_emt_digital_twin.md`.
- Novelty/positioning report, charts, and PowerPoint deck: `docs/tnbc_digital_twin_emt_plasticity/novelty_positioning/`.
- Frozen release: `docs/tnbc_digital_twin_emt_plasticity/frozen_releases/tnbc_digital_twin_freeze_2026-06-15/`.

## Current remaining step

The next step is **expert review and writing polish**, not additional core computation:

1. Final author/expert sign-off on response-label curation decisions.
2. Final expert review of `GSE164715` ambiguity language.
3. Citation formatting, figure/table numbering, and journal/thesis style formatting.
4. Optional future strengthening: add another large independent external cohort or bridge cohort if one becomes available.
