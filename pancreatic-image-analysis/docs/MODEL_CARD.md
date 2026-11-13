# Model and dataset card

This card describes the original synthetic demonstration baseline. The subsequent real TCGA-PAAD technical pilot is documented in `PILOT_PROTOCOL.md`, `PILOT_REPORTING_CHECKLIST.md` and `outputs/real_pilot/PILOT_REPORT.md`; it does not use the synthetic model. The real-data delivery includes public derived tissue tiles, audit data and results, with raw SVS/RNA files retained separately in the workspace.

Version: 0.1, original research baseline. Architecture: 120-tree random forests on 18 fixed RGB-summary features averaged per patient. Seed: 42 by default. The original baseline uses artificial data; no clinically validated weights or proprietary data are distributed. Dependency bounds are compatibility ranges, not a reproducible lockfile; preserve the environment used for a study.

## Intended use

Local software demonstrations and retrospective feasibility studies in reviewed, confirmed PDAC H&E tiles. Predicted targets are broad stage association and an independently defined EMT assay association. Model input assumes all uploaded tiles belong to one patient and one specimen/timepoint; the upload UI cannot verify this. Treatment context is a source-linked lookup keyed only to clinician-entered resectability.

## Exclusions

Not for diagnosing cancer, assigning TNM stage, assessing operability, measuring EMT progression, prescribing medication, screening populations or making patient-management decisions. Not validated for CT, MRI, radiographs, immunohistochemistry, cytology, live microscopy, native whole slides, pediatric samples or non-PDAC tumors. Not an EMT molecular assay.

## Data and performance

The bundled generator creates 160 random artificial textures in 80 fictional patients. Stages and scores are intentionally encoded in texture color. High demonstration accuracy has no clinical interpretation. Real-data performance is unknown until an independently collected, appropriately labeled cohort is trained and evaluated. See `outputs/metrics.json` for the particular local run, not a benchmark claim.

## Known limitations and safeguards

- Scanner/stain/site shortcuts, stromal signal and procedure selection may dominate morphology.
- A primary-tumor tile lacks whole-body extent, metastatic status and vascular imaging.
- EMT is heterogeneous and context dependent; an averaged scalar discards spatial variation.
- Random-forest votes are not calibrated probabilities or confidence intervals.
- Feature-range warnings miss many distribution shifts and cannot authorize interpretation.
- Patient splitting prevents direct tile overlap, but unknown identity errors and near duplicates remain possible.
- No automatic benign/cancer discrimination, segmentation, cell-level localization or explainability overlay is implemented.
- Manifests and split IDs can contain sensitive information: use deidentified research identifiers.
- Uploads use temporary local files. Configure and audit local deployment before handling restricted data.
- A trained artifact can be malicious if replaced: never load untrusted joblib files.

## Gates for further development

Before any clinical use: formal intended-use specification, cohort/sample-size plan, independent external and prospective validation, calibrated uncertainty, clinically acceptable prespecified endpoints, workflow/human-factors testing, security/privacy review, institutional oversight and applicable regulatory evaluation. These gates are not fulfilled by this project.
