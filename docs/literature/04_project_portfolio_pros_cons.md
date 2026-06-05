# Project Portfolio, Pros, Cons, and Data Availability

## 1. Pan-Cancer EMT State Atlas

Goal: classify tumor samples and single cells into epithelial, partial EMT, mesenchymal, stromal-inflated, immune-rich, CAF/TAM-supported, hypoxic, and ferroptosis-window states.

Public data:

- TCGA/GDC/UCSC Xena for bulk expression and clinical metadata.
- CancerSEA for single-cell functional state benchmarking.
- TISCH2 and HTAN for TME and single-cell/spatial validation.

Pros:

- Strong flagship GitHub project.
- Easy for clinicians and scientists to understand.
- Creates reusable evidence tables for target ranking.

Cons:

- Bulk EMT can be confounded by fibroblast/CAF content.
- Cross-cancer batch effects and normalization choices matter.

## 2. Stroma-Corrected EMT Score

Goal: separate tumor-cell EMT from stromal/fibroblast contamination in bulk RNA-seq.

Public data:

- TCGA/Xena bulk RNA-seq.
- TISCH2 and HTAN single-cell references.
- Cell-type signatures from published deconvolution tools.

Pros:

- Very doable.
- Solves a real problem in EMT literature.
- Good package-oriented GitHub release.

Cons:

- Less visually exciting than deep learning.
- Depends on quality of reference signatures.

## 3. Spatial EMT Niche Graph Model

Goal: predict EMT/metastasis-promoting neighborhoods from spatial transcriptomics or histology-linked spatial data.

Public data:

- HTAN.
- Public 10x Visium tumor datasets.
- GEO spatial transcriptomics.
- HEST-style histology-spatial resources where available.

Pros:

- High creativity and advanced-science value.
- Directly models CAF, TAM, hypoxia, ECM, and immune-exclusion niches.

Cons:

- Spatial datasets are smaller and heterogeneous.
- Needs careful visual validation and biological interpretation.

## 4. EMT-Ferroptosis Vulnerability Engine

Goal: identify EMT-high tumors or cell lines that may be sensitive to ferroptosis-axis targeting.

Public data:

- TCGA/Xena for EMT and ferroptosis signatures.
- DepMap/CCLE for expression and dependency.
- PRISM/GDSC/CTRP for drug response.
- LINCS for perturbation reversal.

Pros:

- Creative and biologically specific.
- Can discover state-dependent vulnerabilities.

Cons:

- Ferroptosis phenotypes vary strongly by context and assay.
- Direct druggability of some nodes is challenging.

## 5. EMT Immune-Evasion Combination Recommender

Goal: rank rational combinations such as AXL/TAM plus checkpoint blockade, TGF-beta plus immunotherapy, CAF/TAM targeting plus cytotoxic T-cell restoration.

Public data:

- TISCH2 for immune/TME states.
- TCGA immune deconvolution.
- Public immunotherapy response cohorts from GEO/cBioPortal.
- Open Targets and ClinicalTrials.gov for clinical evidence.

Pros:

- High clinical relevance.
- Connects EMT with immuno-oncology.

Cons:

- Public immunotherapy cohorts are heterogeneous.
- Combination recommendations require safety and mechanistic care.

## 6. CRISPR-Based EMT Target Prioritizer

Goal: find genes selectively essential in EMT-high or partial-EMT cancer models while avoiding pan-essential targets.

Public data:

- DepMap Achilles.
- CCLE expression and lineage metadata.
- Project Score / BioGRID ORCS for orthogonal screens.

Pros:

- Strong target-discovery logic.
- Quantitative and reproducible.

Cons:

- CRISPR screens usually measure growth, not invasion.
- EMT-high labels for cell lines require careful construction.

## 7. LINCS EMT Drug-Reversal Engine

Goal: identify perturbagens that reverse EMT/metastatic signatures or push cells out of partial EMT states.

Public data:

- LINCS/CLUE L1000.
- CMap tools.
- TCGA/single-cell EMT signatures as query inputs.

Pros:

- Good GitHub tool.
- Fast hypothesis generation for repurposing.

Cons:

- Signature reversal is hypothesis-generating only.
- L1000 cell contexts may not match metastatic tumor biology.

## 8. EMT Target Knowledge Graph

Goal: build a graph linking genes, pathways, drugs, dependencies, cancer types, metastasis evidence, safety, and literature.

Public data:

- Open Targets.
- ChEMBL.
- DGIdb.
- PubMed.
- ClinicalTrials.gov.
- DepMap/PRISM/LINCS.

Pros:

- Useful community resource.
- Explainable and extensible.

Cons:

- Requires curation discipline.
- Can become shallow if evidence quality is not graded.

## Recommended build order

1. Stroma-corrected EMT score.
2. Pan-cancer EMT state atlas.
3. Target ranker starter release.
4. EMT-ferroptosis vulnerability engine.
5. CRISPR EMT target prioritizer.
6. Spatial EMT niche graph model.

