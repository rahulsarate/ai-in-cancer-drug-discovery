# EMT-ViSTA Interview and Viva Guide

## Thirty-Second Answer

EMT-ViSTA is a multimodal research pipeline that learns spatial EMT and tumour
microenvironment scores from routine H&E using paired spatial transcriptomics.
Its novelty is risk-aware partial-EMT prediction: it requires joint epithelial
and mesenchymal evidence, predicts stromal contamination separately, quantifies
uncertainty, and abstains on unreliable regions. The first real held-out lung
and colorectal benchmarks showed that handcrafted and ImageNet features were
insufficient, while the engineering and safety framework worked as intended.

## Core Questions

### Why predict programs instead of individual genes?

Programs are more stable under spatial-transcriptomic dropout and more closely
match the biological question. They also reduce output dimensionality. The
trade-off is that signature choice can bias the target, so signatures and
scoring rules must be versioned and externally validated.

### Why is partial EMT difficult?

Hybrid epithelial/mesenchymal expression can arise from a malignant cell state
or from mixing epithelial tumour cells with fibroblasts in one spot. EMT-ViSTA
uses malignant gating, a separate stromal-risk output, confidence tiers, and a
pure-stroma false-positive metric to distinguish these possibilities.

### Why use center and context tiles?

The center captures local tumour morphology. The context captures glands,
desmoplasia, immune aggregates, vessels, necrosis, and invasive-front geometry.
The two scales are concatenated and spatial-neighbor features add local tissue
organization.

### Why start with PCA plus ridge rather than a large neural network?

It is a reproducible, regularized baseline that exposes data leakage and domain
shift. A larger model is justified only if it beats stain, texture, ImageNet,
and pathology-foundation controls on patient-level holdouts.

### How is uncertainty estimated?

Multiple models are trained on bootstrap resamples. Their prediction mean is the
estimate and their spread is an uncertainty proxy. Selective-risk curves test
whether abstaining on uncertain spots actually lowers error.

### What are the main metrics?

For continuous programs: Spearman correlation, Pearson correlation, MAE, and
R-squared. For partial EMT: AUPRC above prevalence, calibration error, and
pure-stroma false-positive rate. Generalization is evaluated on complete held-out
datasets, with patient-level and institution-level splits required next.

### What did the first benchmark find?

The handcrafted graph model reached a median held-out Spearman of 0.014; its
best program was epithelial at 0.310. ResNet50 reached -0.086 median Spearman.
Neither met the predefined 0.35 median gate or the partial-EMT safety/performance
bundle. Both passed the pure-stroma false-positive threshold.

### Is this a failed project?

No. It is a successful falsification of two weak baselines and an operational
platform for the next experiment. A project would fail scientifically if it
hid negative results, leaked test slides, or treated attractive maps as proof.

### Why might generic ResNet50 be worse than handcrafted features?

ImageNet features are optimized for natural images, and a small sampled cohort
can expose stain and dataset shifts. Handcrafted color and tissue-density
features may preserve coarse morphology more directly. A pathology foundation
model is the correct learned-representation comparison.

### What makes this project novel?

The contribution is not merely H&E-to-expression regression. It combines
dynamic partial-EMT targets, explicit malignant-versus-stromal ambiguity,
multi-scale morphology, spatial context, calibrated abstention, and predefined
biological safety gates in lung and colorectal transfer experiments.

### What would make it publication ready?

Full pathology-foundation extraction, multi-patient leave-one-patient-out
validation, matched scRNA-based deconvolution, blinded pathologist labels, an
untouched external institution, and prospective assay-triage analysis. The
predefined gates must pass without changing them after seeing test results.

## Tooling Answers

| Tool | Role | Advantage | Limitation |
|---|---|---|---|
| pandas/NumPy | Tables and numerical processing | Transparent and portable | Memory-bound at very large scale |
| scikit-learn | PCA, ridge, neighbors, metrics | Strong reproducible baselines | Limited end-to-end representation learning |
| PyTorch/torchvision | Learned image encoders | Standard model ecosystem | CPU extraction is slow |
| timm | H-Optimus-compatible model adapter | Broad pathology/ViT support | Model weights can have access terms |
| Transformers | Phikon-v2 inference | Public pretrained pathology features | License and GPU requirements must be checked |
| Matplotlib/seaborn | Maps and scientific figures | Reproducible static output | Not a WSI viewer |
| GeoJSON | Hotspot exchange | Interoperable with spatial tools | Coordinates still require slide metadata |
| pytest | Regression and safety tests | Prevents silent workflow breakage | Does not establish biological validity |

## Common Challenge Questions

### How do you prevent leakage?

Split by dataset or patient before model fitting; fit PCA and calibration on
training data only; keep held-out cancer datasets untouched until final
evaluation; never let neighboring spots from the same slide cross random train
and test splits.

### How would you improve domain generalization?

Use stain augmentation and normalization as explicit ablations, pathology
foundation encoders, hierarchical cancer-specific heads, balanced cohorts,
leave-center-out evaluation, and domain-adversarial learning. Improvement must
be verified on new centers rather than inferred from internal validation.

### How could this help drug discovery?

Reliable maps could identify EMT/TME niches for laser-capture profiling,
spatial target validation, pharmacodynamic biomarker studies, and region-aware
sample selection. The model ranks regions for investigation; it does not select
therapy for a patient.

## Final One-Line Conclusion

EMT-ViSTA has completed its executable MVP and honestly rejected its first two
image baselines; the next decisive experiment is adequately powered,
patient-level pathology-foundation validation with pathologist and scRNA-based
ground truth.
