# EMT Atlas Validation Cohort Readiness

This table tracks the remaining external validation inputs needed to move from internal research screens to stronger independent evidence.

| validation_layer | candidate_source | status | needed_fields | purpose |
| --- | --- | --- | --- | --- |
| annotated_single_cell | TISCH2 selected dataset export | ready_for_import_after_portal_export | expression matrix; cell_id; cell_type; malignant_status or CNV call; cancer type | separate malignant EMT from CAF/TAM EMT mimicry |
| annotated_single_cell | 3CA cancer category dataset | ready_for_import_after_dataset_download | AnnData or expression matrix; obs metadata; malignant/cell-type labels | curated malignant-cell validation across cancer categories |
| spatial_pathology | HTAN selected Level 3/4 spatial or single-cell files | requires_selected_files_and_credentials | spatial expression; spot/cell metadata; sample/cancer annotation; optional pathology regions | matched human tumor atlas validation |
| clinical | external survival cohort with treatment annotation | not_yet_imported | sample expression/signature scores; OS/PFS time/event; stage; grade; treatment; cancer group | independent validation of Cox and event-rate screens |
| pathology | expert region review form | queue_ready_labels_pending | cohort/run; region_id; invasive_edge; CAF score; TAM score; hypoxia/necrosis; tumor-intrinsic EMT label | convert spatial hypotheses into reviewed region labels |
