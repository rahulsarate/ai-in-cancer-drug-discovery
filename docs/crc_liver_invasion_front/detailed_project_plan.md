# Detailed Scientific and Execution Plan

## Project Question

Which malignant-cell states and host-niche interactions are enriched within the
first approximately 300 micrometres of a colorectal liver metastasis, and which
signals distinguish direct hepatocyte replacement from a fibroblast-rich
desmoplastic boundary?

## Central Hypothesis

The invasive front is not a single EMT-high ring. It is a structured transition
in which partial-EMT malignant cells encounter one of at least two ecological
solutions:

1. a macrophage/hepatocyte-injury and vessel-co-option programme with direct
   tumour-hepatocyte contact; or
2. an activated-fibroblast, ECM and angiogenic programme that separates tumour
   from liver parenchyma.

Glycolysis and hypoxia are expected to vary orthogonally to these growth
patterns and may identify metabolically vulnerable subregions.

## Specific Aims

### Aim 1: Build an auditable tumour-liver coordinate system

Execution:

- normalize each Visium section independently;
- score colorectal malignant, epithelial, mesenchymal, hepatocyte and niche
  programmes;
- require malignant context before calling partial EMT;
- flag fibroblast-driven mesenchymal signal;
- locate malignant-hepatocyte contacts in a six-neighbour spatial graph;
- assign tumour-front and liver-front bands out to three graph hops.

Success criteria:

- both liver sections contain a resolved interface;
- at least 50 spots per section occur in an interface band;
- compartment maps are spatially coherent on H&E coordinates;
- signature coverage exceeds 60% for core lineage programmes.

Failure solution:

If direct contact is absent, preserve `interface_not_resolved`; do not create a
false boundary. A later pathology mask can provide the missing boundary.

### Aim 2: Construct a biological heterogeneous graph

Node types:

- malignant epithelial;
- malignant partial EMT;
- hepatocyte;
- MRC1/CCL18-like macrophage;
- activated fibroblast;
- endothelial;
- other or low-confidence mixtures.

Node attributes:

- lineage confidence and margin;
- interface side and signed distance;
- ECM-rich and glycolytic-zone flags;
- stromal-inflation and mixed-lineage warnings;
- all programme scores.

Edge families:

- physical spatial neighbours;
- cross-compartment contacts;
- direct tumour-hepatocyte contacts;
- ECM and glycolysis up-gradient edges;
- CCL18-PITPNM3, SPP1-CD44/ITGAV, TGF-beta-TGFBR2,
  CXCL12-CXCR4, HGF-MET, VEGFA-KDR, ANGPT2-TEK, COL1A1-ITGA2 and
  GAS6-AXL co-expression edges.

The ligand-receptor edges represent spatial co-expression opportunities, not
demonstrated signalling.

### Aim 3: Learn reproducible invasion-front context

The first model is an interpretable typed message-passing baseline:

1. aggregate target-node programmes separately by edge family;
2. concatenate local and typed-neighbour features;
3. fit balanced regularized logistic regression;
4. hold out one liver section at a time;
5. shuffle front labels within sections for a permutation null;
6. remove feature groups to measure ablation loss.

Why not begin with a deep GNN:

Two liver sections do not justify a high-capacity neural network. The baseline
tests whether the graph formulation carries transferable signal. A relational
GAT or HGT becomes appropriate after at least 20-30 independently annotated
sections are available.

### Aim 4: Separate discovery from validation

Discovery and spatial modelling use GSE225857. The open GeoMx CTA counts from
Zenodo 7520789 are downloaded but not assigned undocumented AOI labels. Planned
external validation uses PRJEB71493 and the 26-sample ISS CRLM interface cohort
when reusable processed matrices and region labels are available.

## Key Parameters and Sensitivity Analyses

| Parameter | Default | Sensitivity test | Biological meaning |
|---|---:|---:|---|
| Spatial neighbours | 6 | 4, 8, 12 | Visium local topology |
| Front width | 3 hops | 2, 4, 5 | approximately 200-500 micrometres |
| Lineage score threshold | 0.55 | 0.50-0.70 | compartment precision/recall |
| pEMT threshold | 0.58 | 0.50-0.75 | hybrid-state stringency |
| LR high expression | 80th percentile | 70th, 90th | interaction sparsity |
| Gradient threshold | 1 within-section SD | 0.5, 1.5 SD | strong spatial transition |
| Logistic C | 0.5 | 0.1, 1.0 | regularization |

## Novelty

1. The interface is treated as a signed spatial coordinate rather than a region
   category.
2. Malignant pEMT is gated by colorectal lineage evidence.
3. Host and tumour compartments coexist in a typed graph with interpretable edge
   semantics.
4. Metabolic and matrix gradients become directional graph relations.
5. Growth-pattern biology is represented as falsifiable proxies tied to human
   review, not as opaque clustering.
6. Validation holds out entire tissue sections and includes a section-aware null.

## Expected Outputs and Inference Rules

Strong output:

- reproducible cross-section AUC above 0.70;
- permutation P below 0.05;
- similar gradient directions in L1 and L2;
- ablation loss concentrated in a biologically coherent feature group.

Weak output:

- high spot-level AUC but poor leave-section-out AUC;
- opposing directions between L1 and L2;
- predictions dominated by hepatocyte score or boundary-defining features;
- extensive stromal-inflation warnings.

Only the first pattern supports a transferable invasion-front hypothesis. It
still does not support patient outcome or treatment claims.

## Experimental Follow-Up

- multiplex IF/IHC across manually traced 300-micrometre bands;
- spatial proteomics for MRC1, CCL18, SPP1, FAP, POSTN, CD31, CA9 and GLUT1;
- CRC organoid-liver slice co-culture with macrophage and fibroblast perturbation;
- CRISPRi or antibody perturbation of top ligand-receptor axes;
- isotope tracing for glucose/lactate across tumour-front and tumour-core regions;
- prospective pathology scoring of desmoplastic and replacement HGP percentage.

## Time Required for Publication-Grade Extension

| Work package | Time |
|---|---:|
| Current public-data baseline | completed in the repository |
| Pathologist annotation of six H&E sections | 1-2 weeks |
| Add 20+ external CRLM sections | 3-6 weeks after data access |
| scRNA-reference deconvolution benchmark | 2-3 weeks |
| Relational GNN and nested cohort validation | 4-6 weeks |
| Multiplex pathology validation | 8-16 weeks |
| Manuscript revision and figure audit | 3-4 weeks |
