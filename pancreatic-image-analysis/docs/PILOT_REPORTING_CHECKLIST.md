# Pilot reporting crosswalk

Practical reporting aid informed by TRIPOD+AI (2024), not the official checklist or a compliance certificate. This pilot is feasibility research, not clinical model validation.

| Reporting domain | Implemented evidence | Outstanding limitation |
|---|---|---|
| Title and purpose | Technical feasibility explicitly named | No clinical intended-use claim |
| Data source and dates | GDC inventory, planned-at date, UUIDs and receipts | Historical donor specimens, not a prospective cohort |
| Eligibility and flow | Prespecified morphology/diagnostic-slide/primary-RNA rules and flow | Expert pathology confirmation pending |
| Predictors and outcome | Fixed 18 features and documented RNA composite | Tissue-level, stromally confounded exploratory endpoint |
| Sample size | 24 patients with 4-GB acquisition ceiling | Resource-based, no clinical precision/power justification |
| Missingness | Gene/MPP checks and processing exclusion log | Complete-case selection can bias results |
| Model and evaluation | Fixed Ridge pipeline, site-grouped folds, mean baseline | Internal evaluation; tiny site groups |
| Performance and uncertainty | OOF predictions and conditional bootstrap intervals | No full model-refit or site-cluster uncertainty |
| Clinical context | Stage distribution and edition preserved | Four-stage gate can fail; treatment response not studied |
| Open science | Code, configuration, manifest, hashes and reproducible downloads | Actual data use remains subject to repository policies |
| Human and ethics review | Public deidentified data scope documented | No claimed ethics approval, clinical sign-off or patient involvement |
| Applicability | Limitations and next-study gates documented | No external, prospective or clinical utility validation |

For formal reporting, complete the original 27-item TRIPOD+AI checklist against the final study report: https://www.bmj.com/content/385/bmj-2023-078378
