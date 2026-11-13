# Pan-Cancer EMT State Atlas

## One-line vision

Build a simple, interpretable atlas that tells clinicians and researchers where each tumor sample sits on the epithelial, hybrid EMT, mesenchymal, stromal-inflamed, therapy-resistant, and metastasis-associated state landscape across cancers.

## Why this project matters

Epithelial-mesenchymal transition (EMT) is linked to invasion, metastasis, immune evasion, stemness, drug tolerance, and recurrence risk. In practice, EMT is hard to use because the signal is mixed across tumor cells, fibroblasts, immune cells, hypoxia, and tissue context. This project turns EMT from a vague concept into a transparent atlas with clear sample-level cards, cancer-type summaries, spatial maps, therapy hypotheses, and research-ready exports.

The project is not intended to make treatment decisions at v1. It is a research and translational decision-support layer that can help users ask better questions, select cohorts, generate biomarker hypotheses, and prioritize validation experiments.

## End-user promise

The end user should never need to understand batch correction, UMAPs, Cox models, or deconvolution before getting value. They should be able to open the atlas and answer:

- Is this sample mostly epithelial, hybrid, or mesenchymal?
- Is the EMT signal likely tumor-intrinsic or mostly stromal/fibroblast contamination?
- Which cancer types show the strongest EMT-risk pattern?
- Which EMT-high groups are linked to poor survival, metastasis, immune exclusion, hypoxia, CAF/TAM niches, or therapy resistance?
- Which targets, drugs, pathways, and validation assays should be considered next?
- Which public cohorts support the finding?

## Core product idea

Each sample, cancer type, gene, drug, and target gets an "EMT State Card":

- **State**: epithelial, hybrid E/M, mesenchymal, stromal-dominant, immune-inflamed EMT, hypoxic EMT, proliferative EMT, or uncertain.
- **Confidence**: high, medium, low, with reason.
- **Contamination check**: fibroblast/CAF/stroma warning.
- **Clinical associations**: survival, stage, metastatic label, recurrence where available.
- **Biology**: TGF-beta, AXL/GAS6, integrin/FAK/SRC, YAP/TAZ, hypoxia, ECM remodeling, TAM/CAF signals.
- **Actionability**: targetability, public compounds, DepMap/PRISM support, normal tissue safety caution.
- **Evidence links**: datasets, papers, reproducible outputs.

## Scientific premise

The atlas should treat EMT as a spectrum rather than a binary switch. The most clinically interesting state may not be the extreme mesenchymal state, but the hybrid E/M state: cells can keep epithelial survival and collective-growth properties while gaining invasion, plasticity, therapy tolerance, and immune remodeling. The atlas therefore separates:

- Tumor-cell EMT from stromal EMT-like signal.
- Full mesenchymal EMT from hybrid/partial EMT.
- EMT state from EMT consequence, such as metastasis, survival, immune suppression, and drug response.
- Pan-cancer common programs from cancer-type-specific programs.

## Main users

- **Clinicians and translational oncologists**: cohort-level risk interpretation, biomarker context, trial hypothesis generation.
- **Cancer biologists**: EMT state discovery, pathway and target prioritization.
- **Bioinformaticians**: reproducible scoring, cross-dataset benchmarking, downloadable tables.
- **Drug discovery teams**: EMT-high vulnerabilities, combination ideas, resistance mechanisms.
- **Pathologists**: spatial and morphology-linked EMT maps for tumor front, stroma, and invasive niches.

## Literature grounding

Key takeaways from current resources and literature:

- TCGA remains the broadest bulk pan-cancer foundation, with over 20,000 primary cancer and matched normal samples across 33 cancer types, publicly available through GDC and related portals.
- EMTome already provides pan-cancer EMT genes, signatures, multiomics, interactomes, immune profiles, drug sensitivity, and clinical outcomes, so this project must go beyond static signature lookup.
- CancerSEA provides single-cell functional states including EMT, invasion, metastasis, hypoxia, inflammation, proliferation, stemness, quiescence, and others across malignant cancer cells.
- TISCH2 provides large tumor single-cell resources with curated tumor microenvironment annotations, useful for separating malignant EMT from CAF/TAM context.
- HTAN adds longitudinal, spatial, imaging, single-cell, and multiomics tumor atlas data, which is essential for tumor transitions over space and time.
- HEST-1k and related spatial-histology datasets make it possible to connect EMT programs to H&E morphology and tissue architecture.
- Comparative EMT scoring literature shows no single score is enough; 76GS, KS, MLR, and custom gene-set methods capture different aspects of the epithelial-hybrid-mesenchymal spectrum.

## Novelty

The novelty is not "another EMT score." The novelty is a clinician-simple, researcher-rigorous EMT state atlas that combines:

- Multi-score consensus instead of one EMT signature.
- Hybrid EMT detection as a first-class state.
- Tumor-intrinsic EMT confidence using stromal, CAF, immune, and deconvolution controls.
- Pan-cancer and cancer-specific views in the same interface.
- Single-cell and spatial validation layers.
- Therapy and target evidence from DepMap, PRISM, LINCS, Open Targets, ChEMBL, DGIdb, and normal tissue resources.
- Morphology-aware EMT mapping with H&E/spatial transcriptomics where available.
- Human-readable evidence cards, not only plots.
- Researcher exports plus clinician-facing summaries.

## Minimum lovable product

The v1 atlas should have five simple screens or report sections:

1. **Cancer Type Map**: rank cancers by EMT-high fraction, hybrid fraction, stromal warning, and survival association.
2. **Sample Card**: a single sample's EMT state, confidence, warnings, pathways, and matched cohort percentile.
3. **State Explorer**: compare epithelial, hybrid, mesenchymal, stromal-dominant, immune-inflamed, and hypoxic EMT groups.
4. **Target/Drug Ideas**: prioritize targets and compounds for EMT-high or hybrid-EMT cancers.
5. **Evidence Browser**: show which datasets, signatures, and validation layers support each claim.

## Project phases

### Phase 0: Scope lock and evidence map, 1 week

- Finalize cancer types, data sources, state labels, and first-use cases.
- Decide v1 outputs: Markdown reports first, Streamlit/Dash app second.
- Build a source manifest with access status, license, download path, and expected fields.

### Phase 1: Bulk pan-cancer atlas, 2 to 3 weeks

- Use TCGA/Xena/GDC expression plus clinical metadata.
- Score epithelial, mesenchymal, hybrid EMT, stromal, CAF, TAM, immune, hypoxia, proliferation, and angiogenesis programs.
- Generate cancer-type summaries, sample cards, plots, and survival associations.
- Add confidence labels and contamination warnings.

### Phase 2: Single-cell validation, 3 to 4 weeks

- Validate state signatures in CancerSEA, 3CA, TISCH2, HTAN, and selected GEO cohorts.
- Separate malignant cells from CAFs, immune cells, endothelial cells, and normal epithelial cells.
- Identify recurrent tumor-intrinsic EMT markers versus TME-driven markers.
- Build state marker tables for each cancer type.

### Phase 3: Spatial and pathology layer, 4 to 6 weeks

- Reuse the existing spatial EMT niche GNN work.
- Add 10x Visium, HTAN, HEST-1k, and selected GEO spatial cohorts.
- Map EMT-high niches, tumor-front regions, CAF/TAM neighborhoods, hypoxic regions, and ECM-rich regions.
- Connect H&E tile features or pathology foundation-model embeddings to EMT states.

### Phase 4: Functional and therapeutic layer, 3 to 5 weeks

- Link EMT states to DepMap CRISPR dependency, PRISM drug sensitivity, LINCS reversal, Open Targets, ChEMBL, DGIdb, Human Protein Atlas, and GTEx.
- Prioritize target families: AXL/GAS6/TYRO3/MERTK, TGF-beta/SMAD, integrin/FAK/SRC, YAP/TAZ/TEAD, JAK/STAT, hypoxia/VEGF, ferroptosis/lipid metabolism, ECM remodeling, immune checkpoints.
- Create "validation assay suggestions" for each target: invasion assay, organoid assay, drug combination, CRISPR perturbation, spatial IHC marker panel.

### Phase 5: User-facing atlas, 3 to 4 weeks

- Build Streamlit or Dash v1.
- Make all outputs downloadable as TSV, JSON, PNG, and Markdown.
- Add clinician mode with plain-language cards and researcher mode with full methods.
- Add quality-control banners for low-confidence, stromal-dominant, or underpowered cancer types.

### Phase 6: Manuscript and deployment, 2 to 3 weeks

- Write a methods paper or preprint.
- Package reproducible workflows.
- Create example notebooks for three cancers: breast, lung, pancreatic/colorectal.
- Host static reports or a lightweight app.

## Suggested technical stack

- **Python**: pandas, numpy, scipy, scikit-learn, lifelines, statsmodels.
- **Single-cell**: scanpy, anndata, decoupler, harmonypy or scvi-tools where needed.
- **Pathway scoring**: GSVA-style scoring, ssGSEA, AUCell, singscore, custom z-score consensus.
- **Survival**: lifelines Cox models, Kaplan-Meier summaries, stratified analyses by cancer type.
- **Spatial**: squidpy, scanpy, anndata, networkx, PyTorch Geometric if graph learning is needed.
- **Visualization**: matplotlib, seaborn, plotly, altair.
- **App**: Streamlit first for speed; Dash later if more controlled UX is needed.
- **Data storage**: TSV/Parquet for tables, h5ad for single-cell/spatial, JSON for cards.
- **Reproducibility**: Snakemake or simple script stages first; Nextflow only if scaling to many large cohorts.

## Recommended repository structure

```text
docs/pan_cancer_emt_state_atlas/
  README.md
  data_manifest_seed.tsv
  execution_checklist.md
configs/
  pan_cancer_emt_state_atlas.yml
src/
  emt_state_atlas/
    cards.py
    consensus.py
    contamination.py
    therapy.py
    app_export.py
scripts/
  build_pan_cancer_emt_atlas.py
  build_emt_state_cards.py
  build_single_cell_state_validation.py
  build_spatial_emt_pathology_layer.py
  build_therapy_evidence_layer.py
```

## Databases and datasets to use

See `data_manifest_seed.tsv` in this folder for the first source map. Priority order:

1. TCGA/GDC/Xena bulk expression and survival.
2. CancerSEA and 3CA malignant-cell single-cell validation.
3. TISCH2 and HTAN TME validation.
4. 10x Visium, HTAN spatial, HEST-1k, selected GEO spatial cohorts.
5. DepMap, PRISM, LINCS, Open Targets, ChEMBL, DGIdb for function and actionability.
6. Human Protein Atlas, GTEx, HPA pathology, and OncoKB/CIViC-style evidence for safety and interpretation where allowed.

## Functional information layer

Each EMT state should be annotated with:

- **Core gene programs**: epithelial junctions, ECM, motility, wound healing, TGF-beta, hypoxia, angiogenesis, stemness, proliferation.
- **Cellular context**: tumor cell, CAF, TAM, endothelial, immune-inflamed, immune-excluded.
- **Clinical context**: survival, stage, grade, metastatic site, treatment history where available.
- **Therapeutic context**: targetability, dependency, drug sensitivity, perturbational reversal, normal tissue risk.
- **Validation context**: whether the signal appears in bulk, single-cell, spatial, and morphology layers.

## Creative ideas that make it different

- **EMT Weather Report**: cancer-type dashboard with "clear epithelial," "hybrid storm," "stromal fog," and "hypoxic pressure" labels, translated into sober scientific language in export.
- **Tumor State Compass**: one visual with four axes: epithelial integrity, mesenchymal motility, stromal support, immune/hypoxic pressure.
- **Contamination Traffic Light**: green means likely tumor-intrinsic, yellow means mixed, red means likely stromal-dominant.
- **State Twin Finder**: find public tumors or cell lines most similar to a user's sample.
- **Therapy Hypothesis Builder**: "For EMT-high + AXL-high + low normal-tissue risk, consider AXL/GAS6 axis validation; supporting datasets: X, Y, Z."
- **Spatial Invasion Ring**: show EMT gradients from tumor core to invasive edge to stroma.
- **Assay Menu**: every computational target comes with a minimal experimental validation plan.

## Validation strategy

- Compare multiple EMT scores and require consensus for high-confidence labels.
- Benchmark against CancerSEA functional EMT/invasion/metastasis states.
- Confirm tumor-cell origin in single-cell malignant cells.
- Penalize states driven mostly by CAF/stromal signatures.
- Test cancer-type-specific survival models instead of relying only on pan-cancer pooled models.
- Validate spatial co-localization with CAF/TAM/hypoxia niches.
- Compare EMT-high cell lines against DepMap/PRISM sensitivity and dependency patterns.
- Use held-out datasets and leave-one-cancer-type-out checks where possible.

## Advantages

- Interpretable and easy to explain.
- Built on public data.
- Useful for both clinicians and researchers.
- Separates EMT biology from stromal artifacts.
- Produces immediate reusable outputs: reports, plots, TSVs, cards, app views.
- Extends naturally into target ranking, spatial biology, and drug discovery.
- Strong publication potential because it bridges bulk, single-cell, spatial, clinical, and therapy evidence.

## Risks and safeguards

- **Risk**: bulk EMT may reflect fibroblasts.
  **Safeguard**: stromal warning, deconvolution, single-cell malignant-cell validation.

- **Risk**: EMT scores disagree.
  **Safeguard**: consensus score plus method-specific display.

- **Risk**: pan-cancer pooling hides disease-specific biology.
  **Safeguard**: cancer-type-specific state models and summaries.

- **Risk**: drug-sensitivity associations are not clinical proof.
  **Safeguard**: label outputs as hypotheses and attach assay suggestions.

- **Risk**: app simplicity may hide uncertainty.
  **Safeguard**: show confidence, evidence count, and warnings on every card.

## First execution commands

The existing repository already contains a basic EMT state atlas pipeline. Start with:

```powershell
$env:PYTHONPATH="src"
python scripts/run_tcga_xena_atlas.py `
  --expression data/processed/tcga_xena_v1/signature_expression.tsv `
  --metadata data/raw/xena/Survival_SupplementalTable_S1_20171025_xena_sp `
  --out-dir data/processed/tcga_xena_v1
```

Then extend it with:

```powershell
$env:PYTHONPATH="src"
python scripts/run_single_cell_validation.py `
  --expression data/raw/single_cell/example_expression.tsv `
  --metadata data/raw/single_cell/example_metadata.tsv `
  --out-dir data/processed/pan_cancer_emt_state_atlas_single_cell
```

## Key public sources

- TCGA program: https://www.cancer.gov/ccg/research/genome-sequencing/tcga
- GDC portal: https://portal.gdc.cancer.gov/
- UCSC Xena: https://xena.ucsc.edu/
- EMTome: https://www.nature.com/articles/s41416-020-01178-9
- CancerSEA: https://academic.oup.com/nar/article/47/D1/D900/5133662
- TISCH2: https://pmc.ncbi.nlm.nih.gov/articles/PMC9825603/
- HTAN data portal: https://data.humantumoratlas.org/
- Curated Cancer Cell Atlas: https://www.weizmann.ac.il/sites/3CA/
- HEST-1k: https://huggingface.co/papers/2406.16192
- DepMap: https://depmap.org/portal/
- LINCS/CLUE: https://clue.io/lincs
- Open Targets: https://platform.opentargets.org/
- ChEMBL: https://www.ebi.ac.uk/chembl/
- DGIdb: https://www.dgidb.org/
