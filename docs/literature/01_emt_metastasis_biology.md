# EMT, Partial EMT, and Metastasis Biology

## Working model

EMT should be modeled as a spectrum of plastic tumor states rather than a binary epithelial-to-mesenchymal switch. For metastasis, the most interesting states are often partial or hybrid epithelial/mesenchymal states because they can preserve epithelial adhesion while gaining motility, stress tolerance, immune evasion, and therapy resistance.

## Key concepts for the atlas

- **Epithelial state**: high CDH1/EPCAM/keratins/claudins; often linked to proliferative primary tumor regions.
- **Mesenchymal state**: high VIM/FN1/CDH2/ZEB/SNAI/TWIST/MMPs/integrins; linked to invasion, matrix remodeling, drug resistance, and immune remodeling.
- **Partial EMT / hybrid E-M**: co-expression of epithelial and mesenchymal programs; likely important for CTC clusters, collective invasion, and metastatic fitness.
- **MET/recolonization**: metastatic outgrowth often requires partial return toward epithelial growth programs.
- **TME-driven EMT**: CAFs, TAMs, hypoxia, ECM stiffness, TGF-beta, IL-6, TNF, SPP1, CXCL12, and GAS6-AXL can maintain invasive states.
- **Clinical caveat**: bulk EMT scores can be inflated by stromal fibroblast and CAF expression, so any bulk RNA-seq atlas must include stromal correction.

## Literature anchors

- Nature Reviews Cancer review on EMT tumor states and therapeutic targeting: https://www.nature.com/articles/s41568-025-00873-0
- CancerSEA single-cell functional state atlas: https://pmc.ncbi.nlm.nih.gov/articles/PMC6324047/
- TISCH/TISCH2 tumor immune single-cell resources: https://pmc.ncbi.nlm.nih.gov/articles/PMC7778907/ and https://pmc.ncbi.nlm.nih.gov/articles/PMC9825603/
- LINCS/CMap perturbational expression resource: https://pmc.ncbi.nlm.nih.gov/articles/PMC5990023/
- DepMap Achilles dependency mapping: https://depmap.org/portal/achilles
- PRISM drug repurposing viability resource: https://depmap.org/repurposing/

## Project implication

The atlas should output multiple interpretable axes:

1. epithelial score
2. mesenchymal score
3. EMT score
4. partial EMT score
5. stromal/fibroblast contamination score
6. immune context score
7. CAF/TAM niche score
8. hypoxia score
9. ferroptosis sensitivity/resistance window

These scores become inputs to survival analysis, patient stratification, spatial modeling, drug reversal, and target prioritization.

