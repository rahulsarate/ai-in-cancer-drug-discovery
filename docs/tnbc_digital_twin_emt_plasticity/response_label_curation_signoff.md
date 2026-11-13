# TNBC Response-Label Curation Sign-Off

## Curation Decision

The original response model used a broad `pcr_or_good_response` versus `residual_or_poor_response` endpoint. During audit, several `GSE25055` and `GSE25065` rows had `pathologic_response_pcr_rd = RD` while the model label was `pcr_or_good_response`. For a locked modeling table, those rows are conservatively recoded to `residual_or_poor_response` because the available pathology field states residual disease.

Rows with unknown labels remain excluded. Non-TNBC-likely rows remain excluded from TNBC modeling. The curation table preserves a strict pCR/RD field separately from the curated composite model field so downstream reports do not overstate pCR specificity.

## Locked Composite Label Summary

| dataset_id   | locked_composite_response   | curation_decision                       |   samples |
|:-------------|:----------------------------|:----------------------------------------|----------:|
| GSE163882    |                             | exclude                                 |       132 |
| GSE163882    | pcr_or_good_response        | lock_original_composite_label           |        38 |
| GSE163882    | residual_or_poor_response   | lock_original_composite_label           |        52 |
| GSE18864     |                             | exclude                                 |        60 |
| GSE18864     | pcr_or_good_response        | lock_original_composite_label           |         8 |
| GSE18864     | residual_or_poor_response   | lock_original_composite_label           |        16 |
| GSE25055     |                             | exclude                                 |       194 |
| GSE25055     | pcr_or_good_response        | lock_original_composite_label           |        40 |
| GSE25055     | residual_or_poor_response   | lock_original_composite_label           |        63 |
| GSE25055     | residual_or_poor_response   | recode_to_residual_for_locked_composite |        13 |
| GSE25065     |                             | exclude                                 |       133 |
| GSE25065     | pcr_or_good_response        | lock_original_composite_label           |        24 |
| GSE25065     | residual_or_poor_response   | lock_original_composite_label           |        19 |
| GSE25065     | residual_or_poor_response   | recode_to_residual_for_locked_composite |        22 |
| GSE45898     | pcr_or_good_response        | lock_original_composite_label           |         2 |
| GSE45898     | residual_or_poor_response   | lock_original_composite_label           |         8 |

## Strict pCR/RD Availability

| dataset_id   | locked_strict_pcr_response   |   samples |
|:-------------|:-----------------------------|----------:|
| GSE163882    |                              |       170 |
| GSE163882    | residual_or_poor_response    |        52 |
| GSE18864     |                              |        68 |
| GSE18864     | residual_or_poor_response    |        16 |
| GSE25055     |                              |       195 |
| GSE25055     | pcr_or_good_response         |        39 |
| GSE25055     | residual_or_poor_response    |        76 |
| GSE25065     |                              |       137 |
| GSE25065     | pcr_or_good_response         |        20 |
| GSE25065     | residual_or_poor_response    |        41 |
| GSE45898     |                              |         2 |
| GSE45898     | residual_or_poor_response    |         8 |

## Manual-Review Rows Resolved or Excluded

| dataset_id   | curation_decision                       | curation_reason                                                                                                                                                                                                     |   samples |
|:-------------|:----------------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------:|
| GSE18864     | exclude                                 | missing_or_unknown_response_label                                                                                                                                                                                   |        60 |
| GSE25055     | exclude                                 | not_tnbc_confirmed_or_likely;audit_conflict_was_resolved_by_pathologic_rd_field                                                                                                                                     |        55 |
| GSE25055     | recode_to_residual_for_locked_composite | tnbc_likely_with_valid_original_label;pathologic_response_field_reports_residual_disease;original_good_response_bucket_probably_reflected_rcb_0_i_not_strict_pcr;audit_conflict_was_resolved_by_pathologic_rd_field |        10 |
| GSE25055     | recode_to_residual_for_locked_composite | tnbc_likely_with_valid_original_label;pathologic_response_field_reports_residual_disease;rcb_class_rcb-ii_supports_residual_or_poor_response;audit_conflict_was_resolved_by_pathologic_rd_field                     |         2 |
| GSE25055     | recode_to_residual_for_locked_composite | tnbc_likely_with_valid_original_label;pathologic_response_field_reports_residual_disease;rcb_class_rcb-iii_supports_residual_or_poor_response;audit_conflict_was_resolved_by_pathologic_rd_field                    |         1 |
| GSE25065     | exclude                                 | not_tnbc_confirmed_or_likely;audit_conflict_was_resolved_by_pathologic_rd_field                                                                                                                                     |        48 |
| GSE25065     | recode_to_residual_for_locked_composite | tnbc_likely_with_valid_original_label;pathologic_response_field_reports_residual_disease;original_good_response_bucket_probably_reflected_rcb_0_i_not_strict_pcr;audit_conflict_was_resolved_by_pathologic_rd_field |         3 |
| GSE25065     | recode_to_residual_for_locked_composite | tnbc_likely_with_valid_original_label;pathologic_response_field_reports_residual_disease;rcb_class_missing_but_rd_field_supports_residual;audit_conflict_was_resolved_by_pathologic_rd_field                        |         9 |
| GSE25065     | recode_to_residual_for_locked_composite | tnbc_likely_with_valid_original_label;pathologic_response_field_reports_residual_disease;rcb_class_rcb-ii_supports_residual_or_poor_response;audit_conflict_was_resolved_by_pathologic_rd_field                     |         6 |
| GSE25065     | recode_to_residual_for_locked_composite | tnbc_likely_with_valid_original_label;pathologic_response_field_reports_residual_disease;rcb_class_rcb-iii_supports_residual_or_poor_response;audit_conflict_was_resolved_by_pathologic_rd_field                    |         4 |

## Sign-Off Rules

- Use `locked_composite_response` for the curated response-model sensitivity analysis.
- Use `locked_strict_pcr_response` only when explicitly discussing strict pCR/RD evidence.
- Do not call RCB-0/I rows strict pCR unless an explicit pCR field is present.
- Unknown `GSE18864` labels remain excluded from response modeling.
- This is a computational curation sign-off; final publication should still cite the source cohort metadata definitions.