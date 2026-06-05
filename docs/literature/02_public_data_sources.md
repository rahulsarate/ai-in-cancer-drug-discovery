# Public Data Sources

## Bulk tumor and survival data

### TCGA via GDC

- Portal: https://portal.gdc.cancer.gov/
- API: https://gdc.cancer.gov/developers/gdc-application-programming-interface-api
- Best use: tumor RNA-seq, clinical data, survival endpoints, mutation/CNV integration.
- Pros: official source, high-quality metadata, broad cancer coverage.
- Cons: file selection can be complex; survival endpoints require careful harmonization.

### UCSC Xena

- Portal: https://xena.ucsc.edu/
- Best use: fast TCGA/GTEx pan-cancer matrix downloads and phenotype files.
- Pros: convenient tabular files, easy for notebooks and teaching.
- Cons: must document exact hub/release and normalization choice.

## Single-cell data

### CancerSEA

- Publication: https://pmc.ncbi.nlm.nih.gov/articles/PMC6324047/
- Best use: benchmarking EMT, invasion, metastasis, stemness, hypoxia, inflammation, and other functional states.
- Pros: directly relevant to EMT/metastasis state scoring.
- Cons: older scRNA-seq compendium; cell annotation quality varies by source dataset.

### TISCH2

- Portal: https://tisch.compbio.cn/
- Publication: https://pmc.ncbi.nlm.nih.gov/articles/PMC9825603/
- Best use: immune, TAM, CAF, TME context at single-cell resolution.
- Pros: many tumor types and curated TME cell annotations.
- Cons: malignant-cell EMT analyses may need dataset-specific filtering.

### HTAN

- Portal: https://humantumoratlas.org/
- Best use: single-cell, spatial, and multi-modal tumor atlas data.
- Pros: strong for tumor ecology and spatial niche modeling.
- Cons: access and formats vary by study.

## Target and perturbation data

### DepMap / Achilles

- Portal: https://depmap.org/portal/
- Achilles: https://depmap.org/portal/achilles
- Best use: CRISPR dependency and cell-line omics.
- Pros: core evidence for whether a target is essential in EMT-high models.
- Cons: dependency often measures proliferation, not invasion/metastasis directly.

### PRISM

- Portal: https://depmap.org/repurposing/
- Best use: drug sensitivity and repurposing across cancer cell lines.
- Pros: links EMT-high cell lines to compound sensitivity.
- Cons: viability assays do not capture anti-invasive effects.

### LINCS / CLUE

- Portal: https://clue.io/lincs
- Publication: https://pmc.ncbi.nlm.nih.gov/articles/PMC5990023/
- Best use: perturbational signatures and EMT signature reversal.
- Pros: very useful for drug repurposing hypotheses.
- Cons: reversal of an expression signature is not proof of anti-metastatic efficacy.

### Open Targets

- Portal: https://platform.opentargets.org/
- Best use: target-disease evidence, tractability, safety signals.
- Pros: strong target prioritization resource.
- Cons: cancer-metastasis-specific evidence may require additional curation.

### ChEMBL and DGIdb

- ChEMBL: https://www.ebi.ac.uk/chembl/
- DGIdb: https://www.dgidb.org/
- Best use: public compound availability, bioactivity, drug-gene interactions.
- Pros: helps prioritize druggable targets.
- Cons: bioactivity data must be filtered by assay relevance and potency.

