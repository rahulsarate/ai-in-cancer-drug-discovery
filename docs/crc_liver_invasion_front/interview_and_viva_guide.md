# Interview and Viva Guide

## Thirty-Second Pitch

I built a compartment-aware spatial graph model of the colorectal cancer-liver
metastasis interface. It separates malignant pEMT from fibroblast-driven
mesenchymal signal, assigns a signed 300-micrometre interface, and represents
hepatocyte, macrophage, fibroblast, endothelial, ECM, metabolic and
ligand-receptor context as typed relations. A leave-section-out baseline achieved
ROC AUC 0.908 with a section-aware permutation P of 0.0196, but I treat it as a
weak-label research result because only two liver sections and no pathologist HGP
labels are available.

## Core Questions

### Why use a heterogeneous graph?

Physical proximity, tumour-hepatocyte contact, ligand-receptor opportunity and a
metabolic gradient are not equivalent relationships. Typed edges preserve that
semantics and allow relation-specific ablation.

### How did you prevent stromal RNA from becoming malignant EMT?

pEMT requires concurrent epithelial, mesenchymal and CRC-lineage evidence. A
mesenchymal-high, malignant-low, fibroblast-high spot receives a stromal-
inflation warning and is excluded from malignant model training.

### Why is the interface approximately 300 micrometres?

The implementation uses three Visium graph hops at roughly 100 micrometres per
spot-centre step. This mirrors the 300-micrometre tumour- and liver-front regions
used in recent pathologist-reviewed CRLM spatial work. It remains an
approximation and is sensitivity-tested.

### Is this a GNN?

V1 is an interpretable typed message-passing baseline: features are aggregated
separately by relation and classified with regularized logistic regression. A
deep relational GNN would be unjustified with only two liver sections.

### What was the most important negative result?

pEMT, glycolysis and hypoxia were not uniformly higher at the inferred tumour
front; they were higher in malignant core spots. This argues against a simplistic
invasive-ring story and prioritizes pathology and perturbation validation.

### Why is AUC 0.908 not enough?

The labels are weak spatial proxies and the independent unit count is two
sections, not 3,439 patients. The AUC shows transfer between these sections, not
clinical generalization.

### What are the top next experiments?

Consensus HGP annotation, multiplex protein validation across signed distance
bands, matched deconvolution including a liver reference, independent CRLM
sections, and perturbation of macrophage/hepatocyte versus fibroblast/ECM axes.

### What is the main technical contribution?

An end-to-end reproducible pipeline that turns public Visium matrices into an
auditable signed interface, typed graph, leakage-aware classifier, ablation
analysis, figures and review-ready evidence tables.
