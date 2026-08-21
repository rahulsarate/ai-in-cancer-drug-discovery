# EMT-ViSTA: Risk-Aware Virtual Spatial Staining of Epithelial-Mesenchymal Plasticity From H&E

## Article Status

Working methods and preliminary-results draft. The current evidence supports a
software and negative-baseline report, not a clinical-performance manuscript.

## Abstract

**Background:** Epithelial-mesenchymal plasticity is spatially heterogeneous and
interacts with fibroblasts, macrophages, hypoxia, and extracellular matrix.
Spatial transcriptomics can measure these programs but is not routine, creating
interest in virtual staining from H&E. Stromal admixture creates a major safety
problem because fibroblast-rich regions can mimic tumour-cell EMT.

**Methods:** We developed EMT-ViSTA, a reproducible multimodal pipeline that
aligns H&E with spatial transcriptomics; constructs epithelial, mesenchymal,
partial-EMT, CAF, TAM-SPP1, hypoxia, ECM-remodeling, and stromal-risk targets;
extracts center and context image representations; trains bootstrapped multitask
models with spatial-neighbor refinement; and exports uncertainty-aware maps.
Partial-EMT predictions are gated by epithelial evidence and stromal risk. Five
public 10x cancer datasets provided 16,862 scored spots. Breast and prostate
were assigned to training, ovarian to validation, and lung squamous plus
intestinal/colorectal cancer to held-out technical testing.

**Results:** A handcrafted morphology model evaluated on 1,024 held-out spots
had median Spearman correlation 0.014 across eight programs; epithelial score
was best at 0.310. A generic ResNet50 representation evaluated on 256 held-out
spots had median Spearman -0.086. Neither representation met predefined
correlation, partial-EMT discrimination, calibration, or uncertainty-abstention
criteria. Both met the pure-stroma false-positive criterion. Phikon-v2 inference
was operationally verified on a small sample but was not sufficiently scaled for
performance claims.

**Conclusions:** EMT-ViSTA provides an operational, contamination-aware framework
for H&E-to-EMT research, but its first two controls do not generalize adequately
to held-out lung and colorectal data. The negative result demonstrates why
attractive spatial maps must not be interpreted without patient-level external
validation, pathology-foundation comparisons, and compartment-resolved ground
truth.

## Introduction

Cancer EMT is better represented as dynamic epithelial-mesenchymal plasticity
with multiple partial states than as a binary transition. These states may
support invasion, metastatic dissemination, resistance, and adaptation, but
their identification in human tissue is complicated by spatial heterogeneity
and non-malignant mesenchymal cells. H&E provides morphology at clinical scale,
whereas spatial transcriptomics provides molecularly resolved but costly
measurements. Their alignment enables supervised visual-omics models.

Existing H&E-to-spatial-expression work demonstrates feasibility at scale but
also highlights cross-organ, platform, and cohort effects. We hypothesized that
a targeted program-level model could be more stable than whole-transcriptome
prediction, provided that partial EMT is separated from stromal admixture and
that uncertainty is treated as an output rather than an afterthought.

## Methods

### Study Design

The study was designed as a retrospective public-data technical validation.
Dataset-level assignment was fixed before model evaluation. The intended unit
for future inference is the patient; the present public examples include too few
patients for clinical generalization claims.

### Molecular Targets

Expression-based program scores were constructed for epithelial,
mesenchymal, CAF, TAM-SPP1, hypoxia, ECM remodeling, and related tissue
programs. Partial EMT required joint epithelial and mesenchymal activity. A
stromal contamination score summarized non-malignant mesenchymal evidence.
Supervised eligibility and confidence tiers prevented low-information or
high-contamination spots from being treated as equivalent ground truth.

### Histology Representations

At each aligned coordinate, center and larger-context tiles were extracted.
Representations included 44 handcrafted color, texture, stain-proxy, and tissue
density features; 4,096 concatenated center/context ImageNet ResNet50 features;
and pathology-foundation adapters for Phikon-v2 and H-Optimus-0. Extraction was
batched and bounded to support workstation runs.

### Model

The v1 model concatenated image and mean k-nearest spatial-neighbor features.
PCA plus ridge regression was fit in bootstrap ensembles for all primary
targets. Ensemble spread supplied an uncertainty proxy. Prediction gates
combined molecular confidence, stromal risk, and uncertainty to produce
abstention and malignant-gated partial-EMT outputs.

### Evaluation

Continuous programs were evaluated with Spearman and Pearson correlation, MAE,
and R-squared. Partial EMT was evaluated with AUPRC relative to prevalence,
expected calibration error, and pure-stroma false-positive rate. Selective-risk
analysis tested whether excluding uncertain spots improved error. Predefined
go/no-go criteria required a median held-out Spearman of at least 0.35, at least
four programs above 0.35, partial-EMT AUPRC improvement of at least 0.15, stroma
false-positive rate below 0.15, calibration error below 0.10, and error
improvement of at least 0.15 under uncertainty-based abstention.

## Results

### Cohort Assembly and Software Validation

The pipeline assembled 16,862 scored spots from five aligned public cancer
datasets. All numbered pipeline stages ran independently, including pair
generation, feature extraction, training, inference, evaluation, H&E overlay,
GeoJSON export, and manuscript-figure generation. Twenty-eight repository tests
passed.

### Held-Out Performance

The handcrafted graph-refined model passed 2 of 7 reported gates, including
test-metric presence and the pure-stroma false-positive threshold. Its median
test Spearman was 0.014. Epithelial score was the strongest target at 0.310 but
remained below the predefined 0.35 threshold. Partial-EMT AUPRC above prevalence
was 0.103 and calibration error was 0.113.

The ResNet50 graph-refined model also passed 2 of 7 gates. Median test Spearman
was -0.086, partial-EMT AUPRC above prevalence was 0.075, and calibration error
was 0.144. These results provide no evidence that generic ImageNet features
improve cross-cancer molecular prediction in this sampled experiment.

### Spatial Outputs

The software generated aligned H&E overlays for all five datasets and GeoJSON
hotspot files. Because molecular-performance gates failed, these outputs are
visualizations of model hypotheses and uncertainty rather than validated virtual
stains.

## Discussion

This preliminary study contributes a safety-oriented experimental design and an
honest negative benchmark. It shows that an end-to-end virtual-stain system can
be operational while its biological model remains inadequate. The result is
consistent with the risk that stain, organ, and platform shifts dominate small
visual-omics experiments.

The strongest next test is not a larger head on the same features. It is a
controlled pathology-foundation comparison at full spot scale, followed by
leave-patient-out and leave-center-out validation. Compartment-resolved labels
from matched single-cell references and blinded pathology regions are required
to determine whether a predicted partial-EMT signal belongs to malignant cells,
the invasive front, or adjacent reactive stroma.

## Limitations

- The first benchmark contains few slides and uses bounded spot samples.
- Lung and colorectal tests are dataset-level technical holdouts, not
  independent multi-patient cohorts.
- Spatial-transcriptomic targets are weak labels affected by spot mixing.
- Pathology-foundation inference was not yet run at benchmark scale on CUDA.
- No blinded pathologist or prospective clinical endpoint was available.
- Correlation does not establish mechanistic EMT or metastatic potential.

## Conclusion

EMT-ViSTA is ready as an open research framework and not ready as a molecular or
clinical assay. Its predefined criteria correctly reject the first handcrafted
and generic learned-image baselines. Future claims depend on pathology-specific
representations, patient-level external validation, and malignant-compartment
ground truth.

## Data and Code Availability

Code, configurations, tests, compact reports, and example figures are intended
for GitHub. Large public datasets, model caches, and generated spot-level files
remain local and are reproduced through manifests and numbered scripts.

## Reporting Checklist Before Submission

- Replace technical holdouts with multi-patient cohorts and report patient IDs.
- Complete full-scale pathology-foundation benchmarks and licenses.
- Add blinded pathologist agreement and annotation protocol.
- Add deconvolution sensitivity analysis.
- Add confidence intervals and patient-level bootstrap tests.
- Freeze the statistical analysis plan before external evaluation.
- Include model cards, failure cases, and intended-use statement.
