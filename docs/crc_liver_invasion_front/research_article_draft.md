# A Compartment-Aware Heterogeneous Spatial Graph Model of the Colorectal Cancer Liver-Metastasis Invasion Front

## Abstract

Colorectal cancer liver metastases grow through biologically distinct tumour-host
interfaces, yet spatial analyses can conflate malignant epithelial plasticity
with fibroblast, macrophage and liver-derived RNA. We developed an interpretable
heterogeneous graph workflow that maps malignant colorectal, partial epithelial-
mesenchymal transition (pEMT), hepatocyte, MRC1/CCL18-like macrophage, activated
fibroblast and endothelial programmes across public spatial transcriptomic
sections. Six FFPE Visium sections from GSE225857 (four primary colorectal and
two liver-metastatic sections; 22,260 spots) were normalized and scored within
section. Liver interfaces were inferred from malignant-hepatocyte spatial
contacts and expanded into signed three-hop, approximately 300-micrometre tumour
and liver fronts. Typed graph relations encoded physical proximity,
cross-compartment contact, ligand-receptor co-expression, and directional ECM
and glycolysis gradients. A regularized typed message-passing baseline was
evaluated by leaving out each liver section. The model distinguished malignant
tumour-front from tumour-core spots with ROC AUC 0.908, average precision 0.857
and balanced accuracy 0.831; the observed AUC exceeded 50 within-section label
permutations (P=0.0196). Damaged-hepatocyte and macrophage neighbourhood features
were positively associated with the inferred front, whereas local neighbourhood
pEMT, hypoxia, glycolysis and ECM programmes were more prominent in inferred
malignant core regions. Both sections received mixed/uncertain, rather than
forced desmoplastic or replacement, growth-pattern proxies. This study provides
an auditable hypothesis-generation framework, but the interfaces are weak labels,
the sample size is two liver sections, and pathologist-reviewed growth patterns
and independent cohorts are required before biological or clinical claims.

## Introduction

The tumour-liver boundary is the operative biological unit in colorectal liver
metastasis. Desmoplastic growth separates tumour from hepatocytes with a fibrotic
rim, whereas replacement growth places malignant cells in direct contact with
liver plates and may use vessel co-option. These patterns differ in immune,
stromal and vascular context and can carry prognostic or treatment-response
associations. A spatial model should therefore represent the interface directly,
retain host and malignant compartments, and distinguish pEMT from stromal
mesenchymal signal.

We hypothesized that malignant pEMT, macrophage, fibroblast, endothelial, ECM and
metabolic programmes form reproducible but non-uniform ecosystems around the
tumour-liver interface. We further hypothesized that typed biological messages
would generalize between liver sections better than unstructured spot features.

## Materials and Methods

### Public data

GSE225857 supplied processed 10x Visium FFPE matrices, coordinates and images for
four primary colorectal tumours and two liver metastases. The study's processed
single-cell count tables and author cluster annotations were used to construct
pseudobulk malignant, fibroblast, endothelial and macrophage references. An open
48-AOI GeoMx CTA table from four matched patients was downloaded from Zenodo
7520789, but was not assigned site labels because its count file does not contain
a machine-readable AOI annotation table.

### Normalization and programme scoring

Counts were library-size normalized to 10,000 and log transformed. Curated
programmes were scored as within-section percentile ranks. pEMT combined
epithelial and mesenchymal scores and required colorectal malignant-lineage
support. Mesenchymal-high, malignant-low, fibroblast-high spots were flagged as
stromal-inflated EMT risk.

### Interface detection

Six-neighbour spatial graphs were built from array coordinates. Edges connecting
high-confidence malignant and hepatocyte compartments defined boundary seeds.
Breadth-first graph distance assigned tumour-front and liver-front regions up to
three hops from the boundary. Distances were signed negative on the tumour side
and positive on the liver side. Primary CRC sections were explicitly marked not
applicable for liver-interface analysis.

### Heterogeneous graph

Spot nodes were typed as malignant epithelial, malignant pEMT, hepatocyte,
MRC1/CCL18-like macrophage, activated fibroblast, endothelial or other. Relations
included physical neighbours, compartment contacts, direct tumour-hepatocyte
contacts, ECM and glycolysis up-gradient edges, and positive above-80th-percentile
ligand-receptor co-expression. Signalling and gradient relations were restricted
to the liver interface neighbourhood.

### Predictive validation

Typed neighbour programmes were aggregated separately by relation family and
combined with local programmes. A standardized class-balanced L2 logistic model
predicted tumour-front status among malignant liver-metastasis spots. Each liver
section was held out in turn. Labels were shuffled within section 50 times to
generate a null distribution. Biological feature groups were removed one at a
time for ablation analysis.

## Results

### Cohort and interface resolution

The analysis included 22,260 spots. Liver section L1 contained 303 direct
boundary pairs, 1,562 interface-window spots and 861 malignant tumour-front spots.
L2 contained 452 boundary pairs, 2,597 interface-window spots and 1,130 tumour-
front spots. Both growth-pattern proxies were mixed or uncertain, supporting the
decision not to infer categorical HGP without pathology review.

### Tumour-front programmes

Among malignant spots, damaged-hepatocyte context was higher at the inferred
front than in the core. In contrast, pEMT, glycolysis, hypoxia, activated-
fibroblast and ECM scores were lower at the front in this two-section dataset.
This result rejects a simplistic expectation of a uniformly pEMT-high,
glycolytic invasive ring. It suggests either a host-contact front surrounding a
more metabolically stressed malignant core, section-specific architecture, or
residual weak-label effects. Spot-level P values are descriptive and do not
provide patient-level inference.

### Typed model

The 48-feature baseline analyzed 3,439 malignant spots, including 1,290
tumour-front spots. Leave-section-out ROC AUC was 0.908, average precision 0.857
and balanced accuracy 0.831. The 50-permutation null mean AUC was 0.495 and the
empirical P value was 0.0196. Strong positive front-associated coefficients
included neighbouring damaged-hepatocyte and macrophage programmes and local or
gradient ECM context. Neighbouring hypoxia, pEMT, glycolysis and ECM programmes
were core-associated. These coefficients are predictive associations, not
causal effects.

## Discussion

The principal result is architectural: the public liver sections support a
reproducible host-contact boundary signal, but not the assumed monotonic rise in
pEMT and glycolysis toward that boundary. This creates testable alternatives.
Replacement-like contacts may be marked more by hepatocyte injury and myeloid
context than by a high bulk pEMT score, while the tumour interior may contain
hypoxic and glycolytic pEMT niches. Conversely, the pattern may reflect Visium
spot mixing or imperfect malignant/hepatocyte weak labels. H&E review and
single-cell-aware deconvolution are therefore decisive next experiments.

The model's AUC should not be interpreted as clinical performance. Only two
liver sections were available, the target is an inferred spatial label, and
spots are not independent patients. The result establishes technical transfer
between sections and prioritizes biological measurements.

## Conclusion

An interface-centered heterogeneous graph can separate malignant and host
programmes while preserving interpretable contacts and gradients. In GSE225857,
damaged-hepatocyte and macrophage context characterized the inferred front more
strongly than a uniform increase in pEMT or glycolysis. Independent CRLM cohorts,
consensus HGP review and multiplex perturbation are required to determine whether
this architecture represents a general mechanism.

## Data and Code Availability

All code, manifests, small summary tables and figures are generated in this
repository. Large GSE225857 files remain under `data/raw/` and are reproducibly
downloaded by the workflow. Outputs are for research use only.
