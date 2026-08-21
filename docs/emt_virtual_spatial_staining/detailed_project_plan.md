# EMT-ViSTA: EMT Virtual Spatial Staining From Routine H&E

## 1. Project Summary

EMT-ViSTA will predict spatial maps of epithelial state, mesenchymal state,
partial EMT, CAF abundance, TAM abundance, hypoxia, extracellular-matrix (ECM)
remodeling, and prediction uncertainty directly from routine H&E whole-slide
images (WSIs). Spatial transcriptomics and matched single-cell references will
provide training supervision. The final system is a research and assay-triage
tool, not a replacement for spatial transcriptomics, molecular testing, or
pathologist review.

The project extends the current `spatial-emt-niche-gnn` pipeline. Existing gene
program scores, spatial graphs, H&E color/stain proxies, stromal-risk flags, and
weak-label controls become the biological supervision and baseline. The main
new work is pathology-foundation-model feature extraction, multi-scale and
multi-task prediction, malignant-cell gating, calibrated uncertainty, and
external patient-level validation.

Working title:

> EMT-ViSTA: Risk-aware virtual spatial staining of epithelial plasticity and
> tumor microenvironment niches from routine histopathology

## 2. Central Research Question

Can a model trained on paired H&E and spatial transcriptomics recover
reproducible, spatially localized EMT and tumor-microenvironment programs from
H&E alone, while distinguishing malignant-cell plasticity from fibroblast-rich
stromal contamination?

## 3. Specific Aims

1. Build standardized H&E-spatial training pairs at spot, cell-neighborhood,
   and region scales.
2. Create robust molecular supervision for epithelial, mesenchymal, partial
   EMT, CAF, TAM, hypoxia, ECM, angiogenesis, and immune programs.
3. Train a multi-scale pathology model that predicts continuous program scores,
   spatial niche classes, and uncertainty.
4. Prevent false malignant EMT calls through tumor-content estimation,
   deconvolution, epithelial-lineage gating, and explicit stromal-risk outputs.
5. Test patient, cohort, technology, cancer-type, scanner, and staining
   generalization.
6. Demonstrate focused biological use cases in lung and colorectal cancer.

## 4. Primary Hypotheses

| ID | Hypothesis | Testable prediction |
|---|---|---|
| H1 | Routine H&E morphology contains information about spatial EMT and TME programs. | H&E models outperform non-image, prevalence, and color-feature baselines on held-out patients. |
| H2 | Multi-scale context is required for niche prediction. | A tile plus neighborhood model outperforms a single-tile model, especially for CAF, TAM, ECM, and invasive-edge predictions. |
| H3 | Partial EMT is most credible when epithelial identity and mesenchymal activity coexist in a malignant compartment. | Malignant-gated partial EMT has fewer false positives in pure stroma than an ungated mesenchymal score. |
| H4 | Joint prediction of related programs improves biological consistency. | Multi-task learning improves partial EMT, CAF/TAM, and hypoxia prediction relative to separate heads. |
| H5 | Cancer-shared morphology exists, but disease-specific adapters are necessary. | A shared encoder with lung/CRC/cancer-specific adapters outperforms both one universal head and fully separate models. |
| H6 | Spatial graphs improve localization at tissue boundaries. | Graph refinement improves boundary F1 and spatial correlation without excessive smoothing. |
| H7 | Uncertainty can identify unsupported virtual stains. | Selective prediction improves accuracy as low-confidence regions are abstained from. |
| H8 | Virtual maps can identify informative tissue regions for molecular follow-up. | High-confidence, spatially diverse region selection enriches true EMT/TME extremes compared with random sampling. |

## 5. Biological Outputs and Definitions

All primary outputs are continuous scores with confidence intervals. Binary or
ordinal classes are secondary visualization layers and use thresholds learned
only from training data.

| Output | Biological definition | Critical control |
|---|---|---|
| Epithelial | Epithelial lineage, polarity, junction, and keratin program | Separate normal epithelium from malignant epithelium. |
| Mesenchymal | Motility, matrix interaction, EMT transcriptional and invasion program | Do not equate fibroblast abundance with malignant EMT. |
| Partial EMT | Simultaneous epithelial retention and mesenchymal activation | Require malignant/epithelial gating and avoid a one-marker definition. |
| CAF | Fibroblast and activated/desmoplastic fibroblast program | Distinguish smooth muscle, normal stroma, and scar when possible. |
| TAM | Macrophage/myeloid program, including SPP1/TREM2-like states | H&E-only TAM calls may be weak; retain high uncertainty without orthogonal labels. |
| Hypoxia | Hypoxic/glycolytic stress program | Separate viable hypoxic tumor from necrosis and low-quality tissue. |
| ECM remodeling | Collagen, matrix organization, LOX/MMP and desmoplastic program | Strong morphology is expected, but cellular source remains separate. |
| Stromal-risk | Probability that an EMT-like prediction is explained by nonmalignant stroma | This warning is always exported and never hidden. |
| Tumor content | Malignant epithelial probability or fraction | Derived from pathology regions, deconvolution, and copy-number evidence where available. |
| Abstention | Unsupported, out-of-distribution, artifact, or high-uncertainty region | No biological class is emitted as certain for abstained regions. |

Optional secondary outputs are cytotoxic immune context, angiogenesis,
ferroptosis window, invasive-edge probability, necrosis, tertiary lymphoid
structure, and normal airway/crypt/gland probability.

## 6. Data Plan

### 6.1 Training and Technical Development

- HEST-1k paired H&E-spatial profiles for standardized cross-cancer training and
  HEST-Benchmark comparison.
- Existing standardized 10x/GEO cohorts in this repository: breast, lung,
  pancreatic, prostate, ovarian, colorectal, and metastatic cohorts.
- Public 10x Xenium and Visium HD lung and colon data for high-resolution
  technical validation. Single-donor demonstration datasets are not treated as
  clinical validation cohorts.
- Public spatial CRC liver-metastasis samples for invasion-front testing.

### 6.2 Molecular and Cell-Type Supervision

- Disease-matched scRNA-seq references from CELLxGENE, GEO, HTAN, and published
  studies.
- RCTD or cell2location proportions as the primary spot-mixture supervision;
  NNLS marker-proxy proportions remain a baseline.
- Malignant-cell calls from epithelial lineage, inferred CNV, pathology tumor
  regions, and sample-specific marker evidence.
- Pathologist region labels for tumor core, invasive edge, desmoplastic stroma,
  necrosis/hypoxia, immune-rich region, TLS, normal epithelium, and artifact.

### 6.3 Clinical Transfer and External Validation

- TCGA LUAD, LUSC, COAD, and READ H&E, RNA, mutation, and outcome data.
- CPTAC LUAD, LSCC, and COAD pathology plus proteogenomic data as an external
  source and institution shift.
- Spatial cohorts are used for spatial accuracy. TCGA/CPTAC are used only for
  slide-level transfer, association, and external robustness unless matched
  spatial ground truth exists.

### 6.4 Split Rules

- Never split spots or tiles from one patient across training and test sets.
- Primary split: patient-level 70/15/15, stratified by cohort and cancer type.
- Required tests: leave-cohort-out, leave-cancer-out, leave-technology-out, and
  where metadata permit, leave-site/scanner-out.
- Reserve one lung and one colorectal cohort before feature engineering as
  untouched external test sets.

## 7. Label Construction

### 7.1 Expression Processing

1. Harmonize gene symbols and record panel coverage per sample.
2. Apply platform-appropriate normalization; retain raw counts for count-based
   deconvolution and log-normalized values for program scoring.
3. Score several published or curated signatures per biological program.
4. Compute per-sample and cohort-aware percentiles without using test data.
5. Export signature coverage, score stability, and disagreement between
   alternative signatures.

The current `emt_state_atlas` signatures provide an interpretable starting
point. Publication labels should additionally benchmark multiple EMT scoring
systems and cancer-specific partial-EMT programs.

### 7.2 Partial EMT Label

Partial EMT must not be defined as the midpoint of a one-dimensional EMT axis.
The primary continuous label is a learned consensus of:

- epithelial program activity;
- mesenchymal/invasion program activity;
- partial-EMT anchor program;
- malignant epithelial fraction;
- absence of dominant fibroblast explanation; and
- optional cancer-specific programs such as tumor budding or invasive-edge
  markers.

A spot receives a high-confidence partial-EMT label only when epithelial and
mesenchymal programs are both active, malignant evidence is present, and
stromal-risk is below a predefined ceiling. Other spots remain `ambiguous`,
`stromal_inflated`, or `unsupported` rather than being forced into a class.

### 7.3 Confidence Tiers

- Tier A: spatial expression plus deconvolution plus pathology agreement.
- Tier B: spatial expression plus either deconvolution or pathology agreement.
- Tier C: expression-signature proxy only.
- Tier D: conflicting evidence or inadequate gene coverage; exclude from
  supervised training and retain for uncertainty testing.

## 8. Image Preprocessing and Parameters

| Parameter | Initial values to test | Selection rule |
|---|---|---|
| Resolution | 0.5 microns/pixel primary; 1.0 and 2.0 context scales | Match encoder pretraining and preserve nuclei. |
| Center tile | 224 x 224 pixels at 0.5 microns/pixel | Align with H-Optimus/ViT input and HEST spot regions. |
| Context | 448-1024 pixel crop or pooled neighboring tiles | Choose by patient-level validation. |
| Tissue threshold | 50-80% tissue | Tune against artifact false positives. |
| Stain handling | Raw color, Macenko/Vahadane normalized, stain augmentation | Report all three; do not normalize test cohorts using pooled information. |
| Spatial neighbors | k = 6, 8, 12 and radius = 1-2 spot diameters | Choose without crossing tissue gaps. |
| Tile stride | Half-tile for dense WSI inference | Blend overlapping predictions with uncertainty weighting. |
| Embedding | H-Optimus-0 as primary; smaller public encoder as efficiency baseline | Freeze first, then compare parameter-efficient tuning. |

QC must detect blur, pen marks, folds, empty glass, over/under-staining,
out-of-focus regions, tissue tears, cautery, and registration failure.

## 9. Model Architecture

### 9.1 Recommended Model

1. A frozen pathology foundation encoder produces embeddings for center and
   context tiles.
2. A multi-scale fusion transformer combines cellular and architectural views.
3. A spatial graph transformer exchanges information among physically adjacent
   spots or tiles.
4. Shared latent features feed separate continuous program heads.
5. Auxiliary heads predict tumor content, region class, artifact, and
   stromal-risk.
6. A gated partial-EMT head receives predicted epithelial, mesenchymal, tumor,
   and stroma states rather than an unconstrained image embedding alone.
7. Deep ensembles or evidential/heteroscedastic regression produce uncertainty.

### 9.2 Multi-Task Objective

The initial objective is:

```text
L = 1.0 * L_program_regression
  + 0.5 * L_region_classification
  + 0.5 * L_cell_composition
  + 0.3 * L_cross_modal_contrastive
  + 0.2 * L_spatial_consistency
  + 0.3 * L_partial_EMT_gate
  + 0.2 * L_uncertainty_calibration
```

Weights are starting values, not final biological assumptions. Use Huber or
Gaussian negative log-likelihood for continuous scores, focal/BCE loss for
imbalanced classes, and mask losses when a label is missing. Spatial consistency
must be edge-aware so tumor-stroma and necrosis boundaries are not blurred.

### 9.3 Hierarchical Disease Adaptation

Use a shared pan-cancer encoder and shared program heads, followed by small
cancer-specific adapters. Lung adapters include airway, alveolar, TLS, smoking,
and necrosis context. Colorectal adapters include normal crypt, mucosa,
muscularis, tumor budding, desmoplasia, and liver-interface context.

## 10. Required Baselines and Ablations

Baselines:

1. Cohort mean and spatial-neighbor mean without images.
2. Current H&E color/stain proxy features plus ridge regression.
3. ResNet50/ImageNet tile model.
4. Frozen H-Optimus-0 embedding plus ridge/MLP.
5. Frozen embedding plus multi-scale fusion without graph.
6. DeepSpot-style context model where reproducible.
7. Full EMT-ViSTA model.

Required ablations:

- no graph;
- shuffled coordinates;
- no multi-scale context;
- no malignant gate;
- no stromal-risk head;
- single-task instead of multi-task;
- no deconvolution supervision;
- encoder comparison;
- stain normalization and stain augmentation comparison;
- cancer-specific versus shared adapters; and
- attention removed or randomized, followed by perturbation tests.

## 11. Evaluation Framework

### 11.1 Molecular Accuracy

- Per-program Pearson and Spearman correlation.
- Mean absolute error and explained variance.
- Gene-level correlation for marker panels as a secondary endpoint.
- Performance stratified by label confidence and gene coverage.

### 11.2 Spatial Accuracy

- Moran's I agreement and neighborhood enrichment agreement.
- Spatial cross-correlation between predicted and measured maps.
- Boundary F1, IoU, and Dice for region labels where annotations exist.
- Earth mover's distance or optimal-transport distance for spatial pattern
  displacement.
- Hotspot overlap at top 5%, 10%, and 20% of predicted scores.

### 11.3 Partial EMT and Contamination Safety

- Precision-recall within confirmed malignant regions.
- False-positive rate in pathologist-confirmed pure stroma.
- Partial correlation with EMT after controlling for CAF fraction.
- Performance in high- versus low-tumor-purity regions.
- Confusion matrix across malignant partial EMT, stromal-inflated EMT, pure
  stroma, normal epithelium, and artifact.

### 11.4 Calibration and Generalization

- Brier score, expected calibration error, and reliability curves.
- Risk-coverage curve after abstaining from uncertain predictions.
- Performance drop from internal to leave-cohort/cancer/technology/site tests.
- Embedding probes for cohort, scanner, stain, and center leakage.

### 11.5 Clinical Association

On TCGA/CPTAC, aggregate maps into slide-level features: hotspot burden,
invasive-edge enrichment, spatial heterogeneity, niche co-occurrence, and
high-confidence area. Test association with stage, mutation, recurrence, and
survival using adjusted models. These analyses show association and transfer;
they do not validate spatial truth or treatment benefit.

## 12. Predefined Go/No-Go Criteria

Proceed from MVP to publication-scale modeling only if:

- the image model improves median program correlation by at least 0.05 over the
  strongest frozen-embedding linear baseline on held-out patients;
- median Spearman correlation is at least 0.35 for four or more primary
  programs in at least two external cohorts;
- partial-EMT AUPRC exceeds prevalence by at least 0.15 within malignant regions;
- pure-stroma false-positive rate is below 15% at the selected partial-EMT
  threshold;
- expected calibration error is below 0.10 after calibration;
- abstaining on the least-confident 20% improves error by at least 15%; and
- shuffled-coordinate and center-leakage controls do not reproduce the result.

If partial EMT fails but CAF, ECM, or hypoxia succeed, release the system as a
TME virtual staining model and do not claim malignant plasticity prediction.

## 13. Lung Cancer Work Package

Primary question: can H&E reveal the spatial combination of partial EMT,
hypoxia, CAF/TAM organization, and immune exclusion in LUAD/LUSC?

Analyses:

- Validate on HEST lung and public 10x Xenium/Visium lung data.
- Separate tumor, normal airway/alveolar tissue, necrosis, TLS, macrophage-rich
  inflammation, and fibrotic stroma.
- Test associations with EGFR, KRAS, STK11, KEAP1, and TP53 in TCGA/CPTAC.
- Quantify tumor-to-CD8/TLS distance when appropriate spatial labels exist.
- Compare LUAD and LUSC adapters and smoking-associated morphology shifts.

Expected result: CAF/ECM and hypoxia should be more predictable than TAM state
or partial EMT. Multi-scale context should be especially important for TLS,
necrosis, and tumor-stroma boundaries.

## 14. Colorectal Cancer Work Package

Primary question: can H&E identify partial-EMT/tumor-budding regions and
CAF/ECM-rich invasive fronts in primary CRC and colorectal liver metastasis?

Analyses:

- Validate on HEST COAD/READ, public 10x colon data, and CRC liver-metastasis
  spatial cohorts.
- Separate malignant glands, normal crypt/mucosa, immune aggregates,
  desmoplastic stroma, muscularis, necrosis, and liver parenchyma.
- Predict invasive-edge and tumor-budding probability as auxiliary pathology
  tasks.
- Test slide-level associations with MSI, BRAF, KRAS, CMS4-like biology,
  recurrence, and survival in TCGA/CPTAC.
- Compare primary-tumor and liver-interface map distributions.

Expected result: ECM and invasive-edge programs should transfer well;
partial-EMT accuracy will depend strongly on malignant gating and pathologist
annotation of buds and boundaries.

## 15. Expected Results and Interpretation

### Likely Positive Findings

- ECM/desmoplasia will be the most morphology-accessible program.
- Hypoxia will be predictable near viable-necrotic transitions but may be
  confused with processing artifacts.
- CAF abundance will be more predictable than molecular CAF subtype.
- TAM abundance may be moderately predictable; specific TAM states will require
  stronger spatial or immunohistochemical supervision.
- Partial EMT will be the hardest and most scientifically valuable output.
- Multi-scale graph context will improve niche predictions more than isolated
  tumor-cell programs.
- Cross-cancer performance will improve with shared training, while
  cancer-specific adapters preserve organ morphology.

### Valid Inferences

- H&E morphology contains reproducible information associated with a measured
  molecular program.
- Predicted maps can prioritize regions for spatial assays, IHC, or pathology
  review.
- Specific tissue architectures are associated with EMT/TME states.

### Invalid Inferences

- A virtual stain proves gene or protein expression in an individual region.
- A predicted mesenchymal map proves malignant-cell EMT.
- Attention weights prove a biological mechanism.
- Retrospective survival association demonstrates clinical utility.
- A predicted target-rich niche establishes drug response.

## 16. Inference Workflow and Deliverables

### 16.1 WSI Inference

1. Load WSI and magnification metadata.
2. Run tissue and artifact segmentation.
3. Tile at cellular and context scales.
4. Extract and cache foundation-model embeddings.
5. Build within-tissue spatial graph.
6. Predict program scores, tumor/stroma state, and uncertainty.
7. Apply calibration and abstention.
8. Blend overlapping tiles into maps.
9. Export overlays and region-priority tables.

### 16.2 Machine-Readable Outputs

- `virtual_spatial_scores.parquet`: coordinates, all program scores,
  confidence intervals, tumor probability, stromal risk, and QC flags.
- `virtual_spatial_regions.geojson`: hotspots and review regions.
- `virtual_stain_*.ome.tiff`: pyramidal heatmaps aligned to the WSI.
- `slide_summary.tsv`: hotspot burden, spatial heterogeneity, niche adjacency,
  uncertainty, and abstained fraction.
- `model_card.md`: training cohorts, licenses, intended use, failure modes, and
  validation scope.
- `inference_report.html`: interactive H&E and heatmap viewer with warnings.

### 16.3 Scientific Outputs

- Cross-cohort benchmark table.
- Lung and CRC case-study atlases.
- Pathologist review queue containing high-confidence, high-uncertainty, and
  model-disagreement regions.
- Target-overlay table linking predicted niches to the metastasis target ranker.
- Reproducible training configuration, data manifest, and environment lockfile.

## 17. Repository Implementation Plan

Reuse the existing scripts numbered 01-08 and add:

```text
09_build_virtual_stain_training_pairs.py
10_extract_pathology_embeddings.py
11_train_virtual_stain_baselines.py
12_train_emt_vista_multitask.py
13_evaluate_virtual_stains.py
14_infer_virtual_stains_on_wsi.py
15_export_virtual_stain_maps.py
16_generate_emt_vista_paper_figures.py
```

Recommended package modules:

```text
src/emt_virtual_spatial_staining/
  data.py
  labels.py
  tiles.py
  encoders.py
  graph_model.py
  losses.py
  calibration.py
  evaluation.py
  inference.py
  export.py
```

Unit tests must cover patient-safe splitting, spatial registration, partial-EMT
gating, no test-cohort normalization leakage, graph boundary handling,
uncertainty export, and deterministic small-data inference.

## 18. Work Packages and Time

| Work package | Main deliverable | Time |
|---|---|---:|
| WP0: protocol and manifests | Frozen hypotheses, endpoints, cohorts, licenses | 1 week |
| WP1: paired-data builder | QC-approved H&E-spatial pairs | 2-4 weeks |
| WP2: labels and deconvolution | Confidence-tiered molecular labels | 3-5 weeks |
| WP3: embedding baselines | Ridge, MLP, and single-scale benchmark | 2-3 weeks |
| WP4: EMT-ViSTA model | Multi-scale multi-task graph model | 4-7 weeks |
| WP5: validation | Patient/cohort/cancer/technology holdouts | 4-6 weeks |
| WP6: pathology review | Calibrated annotations and error taxonomy | 3-6 weeks, parallel |
| WP7: WSI inference/export | OME-TIFF, GeoJSON, parquet, report | 2-3 weeks |
| WP8: paper and release | Figures, manuscript, model/data cards | 4-6 weeks |

Expected duration: 10-14 weeks for a credible MVP and 24-36 weeks for a
publication-oriented multi-cancer study. Foundation-encoder fine-tuning and
large WSI inference require at least one modern GPU; frozen-embedding baselines
can be developed with substantially less compute.

## 19. Manuscript Plan

Proposed figures:

1. EMT-ViSTA study design and data flow.
2. Label construction, malignant gating, and stromal-contamination controls.
3. Baseline and model performance across biological programs.
4. External, cross-cancer, cross-technology, and calibration results.
5. Lung cancer EMT/immune/hypoxia case study.
6. CRC invasive-front and liver-metastasis case study.
7. Error taxonomy, abstention maps, and pathologist agreement.
8. Assay-triage and target-ranker integration.

Primary paper claim, if all gates pass:

> Risk-aware multi-scale learning from routine H&E can recover selected spatial
> EMT and tumor-microenvironment programs across cancer cohorts, while explicit
> malignant gating and calibrated abstention reduce stromal and domain-shift
> errors.

## 20. Decision Outcomes

### Outcome A: Full Success

EMT, partial EMT, and TME programs generalize across external cohorts. Conclude
that H&E can support research-grade virtual spatial profiling and assay triage,
subject to uncertainty and confirmatory molecular testing.

### Outcome B: TME-Only Success

CAF, ECM, and hypoxia generalize, but malignant partial EMT does not. Conclude
that H&E supports microenvironment mapping but not reliable EMT plasticity
inference. Rename and scope the release accordingly.

### Outcome C: Disease-Specific Success

Models work in lung or CRC but not pan-cancer. Release disease-specific adapters
and avoid universal-model claims.

### Outcome D: Domain Failure

Internal accuracy disappears on external sites or scanners. Conclude that the
model learned cohort or technical signatures; publish the robustness finding
and prioritize domain harmonization and prospective validation.

## 21. Key Literature and Data Resources

- HEST-1k and HEST-Benchmark: https://github.com/mahmoodlab/hest
- HEST paper: https://arxiv.org/abs/2406.16192
- H-Optimus model family: https://www.bioptimus.com/h-optimus
- M-Optimus multimodal concept: https://www.bioptimus.com/introducing-m-optimus
- DeepSpot: https://github.com/ratschlab/DeepSpot
- GDC API and TCGA: https://gdc.cancer.gov/developers/gdc-application-programming-interface-api
- CPTAC pan-cancer data: https://pdc.cancer.gov/pdc/cptac-pancancer
- CELLxGENE datasets: https://cellxgene.cziscience.com/datasets
- DepMap and PRISM: https://depmap.org/portal/data_page/?tab=currentRelease
- Pan-cancer spatial EMT/TME analysis: https://pmc.ncbi.nlm.nih.gov/articles/PMC13198256/
- EMT methods and experimental models: https://pmc.ncbi.nlm.nih.gov/articles/PMC12144846/
- CRC liver-metastasis spatial data: https://www.ncbi.nlm.nih.gov/bioproject/PRJEB71493/

## 22. Final Project Positioning

EMT-ViSTA is deliberately narrower and more falsifiable than a universal
biology foundation model. Its novelty is not model size. Its contribution is a
biologically constrained virtual staining system that predicts a difficult
continuum of tumor plasticity together with its stromal and immune context,
exports uncertainty, and is designed to fail visibly when morphology cannot
support the molecular claim.
