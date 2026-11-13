# Research protocol: pancreatic image phenotype, stage association and EMT

## 1. Research questions and scope

Primary feasibility question: do patient-level image summaries contain reproducible information associated with an independently measured tumor EMT phenotype? Secondary question: are morphology features associated with clinical stage after accounting for center, sampling procedure and disease burden? Stage classification is hypothesis generation, not anatomical staging. Therapeutic context is an educational component independent of either model.

Target population: adults with pathologist-confirmed PDAC, a defined pretreatment index biopsy/resection, contemporaneous clinical staging and matched molecular tissue. Exclude pancreatic neuroendocrine tumors, benign lesions and other histologies from this implementation. Include these only after a separately designed detection/differential-diagnosis study. Do not equate grade, stage, resectability and EMT.

## 2. Cohort and reference labels

Secure ethics approval/data-use permissions, deidentify images and maintain linkage keys outside this project. Store scanner, institution, staining batch, magnification, microns per pixel, specimen procedure, tumor content, treatment history and collection date in a governed cohort database. Do not place identifiers in filenames, logs or exported patient split IDs.

An expert team assigns stage with a specified AJCC edition and documented cTNM/pTNM basis. Keep clinical versus pathological stages distinct and avoid mixing pretreatment and post-neoadjuvant stages. This baseline accepts broad I-IV labels only; the manifest does not encode the full staging provenance, so preserve that in the cohort database. Biopsy-only and surgical cohorts have different selection mechanisms; surgical sampling can make stage prediction spuriously easy.

EMT reference: predefine an assay-derived signature or blinded multiplex epithelial/mesenchymal marker assessment with malignant-cell localization. CDH1/EPCAM/keratins and VIM/ZEB/SNAI-family markers may inform a panel but no single marker establishes EMT. Fibroblasts can dominate a bulk mesenchymal signal. Use tumor-aware segmentation, spatial localization or single-cell evidence to distinguish malignant EMT from stroma. Document panel, normalization, aggregation, quality control, reference population and score mapping to [0,1]. Derive normalization parameters on training data only. Quantify interobserver agreement or assay reproducibility.

This project requires the same assay string across patients but cannot verify biological equivalence. The operator is responsible for assay provenance. Do not use model predictions as training ground truth.

## 3. Images and preprocessing

The supplied code accepts single-frame PNG/JPEG/TIFF tiles, not native whole-slide files, CT volumes or MRI. A pathologist should mark tumor regions and exclude folds, pen marks, blur, necrosis and non-tumor fields before tiling. Choose a fixed physical resolution and tile size, recording both externally. For a whole-slide extension use an audited slide reader and coordinate manifest, retain slide-level provenance and control sampling density; this is planned work, not implemented functionality.

Implemented QC rejects images below 32 pixels and tiles with under 5% colored tissue. Feature extraction resizes to 128 pixels and computes per-channel tissue color mean, standard deviation, quantiles, tissue fraction and image-gradient magnitude. These crude summaries are sensitive to stain/scanner variation and do not quantify cellular EMT. Patient features are arithmetic means across reviewed tiles. There is no stain normalization, tumor segmentation or learned feature encoder in this baseline. Unequal tissue area, specimen type and region sampling remain potential confounders.

## 4. Modeling and leakage control

Baseline: two independent random forests on the same 18 patient image features, one classifier for stage and one regressor for EMT. Fixed parameters and seed avoid a tuning loop in the demo. Every patient's tiles are combined before stratified 60/20/20 splitting; patient IDs and exact cross-patient duplicates are checked. Features do not include stage or EMT labels. Validation and test patients never fit the forests. No ensemble confidence interval or biological EMT threshold is claimed.

For a publishable extension, compare color-only baseline, clinical-only model, frozen pathology encoder with patient-level attention pooling, and multimodal image-plus-clinical models. Separate CT models can assess lesion/vascular anatomy but need volumetric annotations and their own validation. Choose hyperparameters on nested training/validation folds; lock the model before final evaluation. Audit stage associations by site, specimen type and treatment exposure. Entire institutions and temporally later patients must be held out in additional studies; the supplied random patient split is internal validation only.

## 5. Evaluation and statistical analysis

Implemented: stage accuracy, balanced accuracy, fixed-label confusion matrix, EMT mean absolute error, split IDs and model/manifest provenance. The generated synthetic metrics are integration-test artifacts only.

Before clinical claims add patient-bootstrap 95% intervals, per-class sensitivity/specificity, macro-F1, ordinal error analysis, classwise AUROC where defined, calibration curves/Brier score and a validation-fitted calibration method. For EMT add RMSE, rank correlation and assay repeatability comparisons. Analyze site/scanner/sex/age/specimen subgroups with uncertainty and small-cell suppression. Establish sample size from endpoint precision, class prevalence and expected effect rather than the code's minimum row count. Pre-register primary endpoint, success margins, exclusions and missing-data handling.

Use an independent multi-institutional external cohort, blinded pathology review and prospective silent deployment before considering clinical use. Do not reuse external test data to normalize stains, choose thresholds or select architectures. Evaluate failure cases, rejected images and missing assays, not only successful predictions. No implemented metric establishes treatment benefit.

## 6. EMT progression and therapy research

One image provides a state-associated observation, not a temporal trajectory. To investigate progression, collect matched pretreatment/on-treatment/progression samples, aligned assays, specimen metadata and response assessments. Analyze repeated measures with patient-level longitudinal models, batch adjustment and uncertainty. A difference between predictions from two samples is not validated progression and may reflect sampling or technical variation. This repository intentionally reports progression as undetermined.

Treatment-response modeling requires actual treatment/exposure and outcome data, predefined response criteria, follow-up and causal-confounding controls. No such model is included. The context panel lists discussion domains from clinician-confirmed resectability. It does not infer resectability from stage, suggest EMT-directed therapy, or make patient-specific recommendations. A multidisciplinary team determines eligibility and care.

## 7. Work packages and deliverables

1. Weeks 1-2: protocol, governance, cohort dictionary, staging/assay definitions, pilot image QC.
2. Weeks 3-5: expert tumor annotations, standardized tile export, assay alignment and patient/site leakage audit.
3. Weeks 6-7: run this baseline, inspect artifacts and compare confounder-only baselines.
4. Weeks 8-11: encoder/MIL extension and training-only model selection if cohort size supports it.
5. Weeks 12-14: locked external evaluation, confidence intervals, subgroup analysis and blinded failure review.
6. Weeks 15-16: reproducible report, data/model cards and prospective validation plan.

These are planning estimates, not work already completed. Clinical cohort access and paired molecular labels are the main dependencies. No accuracy or biological discovery is promised.

## Sources

- NCI staging: https://www.cancer.gov/types/pancreatic/stages
- NCI professional treatment summary: https://www.cancer.gov/types/pancreatic/hp/pancreatic-treatment-pdq
- Yang et al., EMT consensus, 2020: https://www.nature.com/articles/s41580-020-0237-9

Reviewed 2026-11-13. Recheck clinical sources before future use.
