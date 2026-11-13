# Real-data technical pilot: TCGA-PAAD

Protocol: TCGA_PAAD_TECHNICAL_PILOT_v1. Analysis configuration is in `pilot_config.json`. The acquisition plan is written before image inspection, feature extraction and model evaluation. This is a local, prospectively specified analysis plan for public retrospective data, not a registered trial or a completed clinical validation study. Do not describe it as certified against a clinical standard.

## Purpose and sample size

Use actual NCI GDC pancreatic diagnostic pathology and primary-tumor RNA files to test acquisition, linkage, physical-resolution-aware tiling and reproducible exploratory analysis. A fixed 24-patient convenience sample bounds acquisition at 4 GB. It is a technical resource choice, not an outcome-based power calculation. It cannot support a four-stage clinical model, therapeutic-response model, clinical EMT measurement or population performance claim.

## Selection and population

Query open GDC files for TCGA-PAAD slide images and gene-expression quantification. Retain a unique primary-disease diagnosis with pancreatic tissue of origin, morphology 8500/3 (infiltrating duct carcinoma), and prior treatment recorded as No. Retain primary diagnostic sample 01Z with a DX slide and one unambiguous file-linked primary-tumor STAR-Counts RNA sample. For multiple RNA files choose the lexicographically first stable UUID. For multiple eligible slides choose the smallest by byte size, with stable UUID tie-break. Select the 24 smallest resulting slides. Selection uses metadata, not observed model performance or the RNA score.

This favors smaller scanned tissue areas and particular contributing centers. The cohort is not consecutive, random, stage-balanced or representative. A TCGA project label alone does not guarantee PDAC: non-ductal histologies, unrelated metastases and prior-treatment ambiguity are excluded by the explicit rule. Expert pathology adjudication is still outstanding. Site ID denotes the TCGA tissue-source-site code, not necessarily the scanning laboratory or a single hospital.

## Endpoints and acceptance gates specified before analysis

Primary technical endpoints:

1. All planned raw files must match GDC file size and MD5. No unchecked download is processed.
2. At least 22/24 patients must yield a usable paired image/RNA record and at least eight tissue tiles. Counts and reasons for every exclusion are reported. This 90%-approximately completion goal is an engineering target, not a medical threshold.
3. Every retained tile must have a patient/file link, level-0 coordinate, physical-resolution record, quality fraction and SHA256. At most 32 tiles per patient; minimum eight.
4. No exact derived image hash may occur in different patients. Every patient belongs to exactly one held-out contributing-site fold.

If acquisition or linkage fails the gate, report failure, retain audit artifacts and revise a new protocol version rather than silently replace cases.

Secondary exploratory endpoint: predict the prespecified bulk RNA composite from 18 averaged image features using StandardScaler and Ridge(alpha=10). Fit scaling and regression on each training fold only. Hold out one contributing site at a time, using all eligible sites if at least three are present. Compare with a mean predictor fitted on the identical training fold. Do not select hyperparameters, genes, folds, images or thresholds using results. There is no independent external cohort or reserved final test set: this is internal site-grouped exploratory evaluation.

Report MAE, RMSE, R-squared, Spearman correlation, fold sizes and training-mean baseline error. Report model MAE and paired MAE-improvement percentile intervals from 2,000 patient resamples of fixed out-of-fold predictions. These are descriptive, conditional intervals; they do not include model-refit or site-cluster uncertainty. With only three source-site codes, robust site-level generalization cannot be established. A negative result must be reported unchanged.

Four-stage model gate: at least ten patients in each broad class I, II, III and IV before considering this existing baseline; otherwise do not train it. This minimum is an internal feasibility rule, not a sufficient clinical sample size. Preserve exact stage and staging edition. Do not convert stages into inferred treatment choices or relabel rare stages to manufacture model balance.

## Images, quality and physical resolution

Whole-slide images remain SVS on disk. OpenSlide reads source MPP metadata and extracts 256 x 256 pixel tiles at a nominal 1 micrometer per pixel (minor rounding in level-0 footprint is recorded). Uniform grid candidates require at least 40% colored tissue in a thumbnail; deterministic per-patient random sampling then validates 40% tissue on the full tile. Up to 500 candidates are attempted. Native MPP must be finite, between 0.1 and 2 micrometers and approximately isotropic. Unknown MPP is an exclusion, not an assumed magnification.

The 18 baseline features are RGB tissue mean, standard deviation and quantiles per channel, colored-tissue fraction and two gradient summaries. They are averaged over tiles, one vector per patient. No tumor annotation, nuclei segmentation, stain normalization, artifact detector or deep encoder is implemented. Tissue is not equivalent to tumor; pathologist QC is necessary before malignant-cell or clinical claims. Pixel dimensions and MPP are recorded so another team can reproduce extraction.

Color handling: convert source ICC-profiled thumbnails and tiles to sRGB before QC and feature extraction. If the source ICC is absent, retain native RGB and flag the assumption in the patient manifest. Do not embed oversized scanner profiles into derived PNGs. This is color management, not stain normalization. Implementation correction before outcome evaluation: an initial extraction run exposed a Pillow error on an oversized embedded ICC profile. The exporter was corrected and all patients were reprocessed with the same color policy; no model results were used to choose it.

## RNA definition and sample linkage

Score = mean log2(TPM+1) for VIM/FN1/CDH2/ZEB1/ZEB2/SNAI1/SNAI2/TWIST1 minus mean log2(TPM+1) for CDH1/EPCAM/KRT8/KRT18/KRT19. These genes form a prespecified exploratory composite, not a validated or universal EMT assay. All genes must be present once with finite, nonnegative unstranded TPM. No missing values are imputed. This score is unbounded and is never presented as a 0-1 biological percentage.

WSI and RNA are joined by TCGA patient and primary-tumor status. Diagnostic slides and RNA aliquots may come from different blocks, preservation conditions or spatial regions. Exact co-registration and temporal equivalence are not established. Bulk mesenchymal expression can reflect fibroblasts and other stromal cells. No longitudinal EMT progression or drug sensitivity is inferred.

## Reproducibility and reporting

Keep raw GDC query response, planned cohort, download receipts, file checksums, tile manifest, patient manifest, gene TPMs, features, per-patient out-of-fold predictions, fold assignments, code/configuration hashes and environment versions. Generated reports must name the real database, retrieval date, flow, missingness, selection method, uncertainty and clinical limitations. Synthetic demonstration files stay separate in `outputs/`; real results live in `outputs/real_pilot/`.

The reporting crosswalk in `docs/PILOT_REPORTING_CHECKLIST.md` follows TRIPOD+AI reporting principles. This does not imply full checklist compliance or validate the design. Patient/public involvement, pathology adjudication, external validation, prospective clinical utility and institutional governance remain pending. Use deidentified public data only; do not reidentify donors. Each institution must determine its own ethics/data-governance obligations; this project does not assert an ethics exemption or approval.

## Sources and attribution

- GDC API retrieval: https://docs.gdc.cancer.gov/API/Users_Guide/Search_and_Retrieval/
- GDC downloads: https://docs.gdc.cancer.gov/API/Users_Guide/Downloading_Files/
- TCGA acknowledgement: https://www.cancer.gov/ccg/research/genome-sequencing/tcga/using-tcga-data/citing
- TRIPOD+AI: https://www.bmj.com/content/385/bmj-2023-078378
- EMT research consensus: https://www.nature.com/articles/s41580-020-0237-9

Results are based on data generated by the TCGA Research Network: https://www.cancer.gov/tcga. Access is through GDC open endpoints; this is not a claim that all TCGA data have a Creative Commons license. Review repository data-use policies for downstream use.
