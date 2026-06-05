# Pathology and Literature Grounding for Spatial EMT Niches

## Why Pathology Grounding Matters

Visium spots are mixtures of multiple cells. A high EMT score can mean malignant
cell plasticity, but it can also mean that the spot overlaps fibroblast-rich
stroma, invasive edge, necrosis/hypoxia, macrophage-rich inflammation, or tissue
processing artifacts. Therefore, every EMT-niche claim should be interpreted
with three layers:

1. transcriptomic EMT and partial EMT scores;
2. spatial/pathology context such as tumor core, invasive edge, stroma, necrosis,
   lymphoid aggregate, airway/ductal structures, or desmoplastic regions;
3. deconvolution or orthogonal cell typing to separate malignant, CAF, TAM,
   epithelial, endothelial, and immune signal.

## Practical Pathologist-Style Region Labels

Use these region labels when manual or computational pathology annotation is
available:

- `tumor_core`
- `invasive_edge`
- `desmoplastic_stroma`
- `caf_rich_stroma`
- `macrophage_rich_inflammation`
- `tertiary_lymphoid_structure`
- `necrosis_or_hypoxia`
- `normal_epithelium_or_airway`
- `ductal_or_panIN_region`
- `low_tissue_or_artifact`

In v1, these labels are not automatically inferred from H&E. They should be
added from pathologist annotations, Loupe exports, QuPath/HistomicsML regions,
or future pathology foundation model outputs.

## Literature-Derived Interpretation Rules

### Breast Visium and Pathology Annotation

Recent computational pathology annotation work in breast cancer spatial
transcriptomics shows that H&E-derived tissue annotation can improve
interpretation of Visium gene-expression clusters and deconvolution outputs.
For this project, that supports adding a `pathology_region` column before
claiming that an EMT-high region is malignant-cell EMT rather than stromal
mixture.

### PDAC

PDAC spatial literature repeatedly emphasizes desmoplastic, immunosuppressive,
and fibrotic tumor microenvironments. A 2025 integrated PDAC atlas combined
single-cell RNA-seq, Visium, bulk RNA-seq, and Xenium data and highlighted
POSTN-positive fibroblasts and SPP1-positive macrophages as spatially correlated
features of the PDAC TME. For our EMT niche model, this makes
`CAF/TAM + SPP1/POSTN + partial EMT` a high-priority but contamination-sensitive
pattern.

GEO GSE274103 provides treatment-naive PDAC FFPE Visium samples. These are
useful for first validation, but pathologist region labels are not bundled in
the matrix files, so v1 outputs remain weak-label biology.

### Lung Cancer

Lung cancer spatial transcriptomics studies show strong spatial heterogeneity
across malignant, immune, stromal, and normal/background lung compartments. A
2024 NSCLC single-cell/spatial atlas integrated nearly 900,000 single cells with
spatial transcriptomics across treatment-naive lung tumors. For our model, lung
sections require special caution because airway/normal epithelial regions,
tertiary lymphoid structures, necrosis, and tumor/stroma boundaries can all
change EMT and immune scores.

## Model Rules Added From Literature

- Treat `partial_emt_score` as a plasticity signal, not a malignancy label.
- Treat `stromal_inflated_emt_candidate` as a warning flag.
- Promote `tumor_cell_emt_candidate` only when EMT is high and stromal risk is
  not high.
- In PDAC, inspect CAF/TAM and SPP1/POSTN-like circuits before interpreting EMT
  as cancer-cell intrinsic.
- In lung cancer, inspect immune/TLS and airway/background context before
  interpreting immune or epithelial programs.
- Never use edge attention or graph weights alone as biological proof; require
  edge ablation, shuffled-coordinate controls, and pathology/deconvolution.

## Sources

- Computational pathology annotation enhances the resolution and interpretation
  of breast cancer spatial transcriptomics data. npj Precision Oncology, 2025.
- Wu et al. Integrating multi-modal transcriptomics identifies cellular subtypes
  with distinct roles in PDAC progression. Cell Oncology, 2025.
- GEO GSE274103: Spatial transcriptomics on treatment-naive pancreatic ductal
  adenocarcinoma patients.
- De Zuani et al. Single-cell and spatial transcriptomics analysis of non-small
  cell lung cancer. Nature Communications, 2024.
- AI-powered spatial cell phenomics enhances risk stratification in non-small
  cell lung cancer. Nature Communications, 2025.
