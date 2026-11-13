# Execution Checklist

## MVP definition

The first successful version is complete when a user can open one report or app, choose a cancer type, and see:

- EMT-high, hybrid-EMT, epithelial, and uncertain sample fractions.
- Survival association per state where metadata supports it.
- Stromal contamination warning.
- Top pathways and candidate targets per state.
- Evidence links to bulk, single-cell, and functional datasets.
- Downloadable sample-level scores and state cards.

## Work packages

### WP1: Source manifest and reproducibility

- [ ] Lock source versions and URLs.
- [ ] Create `configs/pan_cancer_emt_state_atlas.yml`.
- [ ] Define local paths for raw, processed, reports, plots, and cards.
- [ ] Add data-access notes for controlled or large sources.
- [ ] Add a "small demo mode" that runs without large downloads.

### WP2: EMT consensus scoring

- [ ] Keep current epithelial, mesenchymal, partial EMT, stromal, immune, CAF/TAM, and hypoxia scores.
- [ ] Add consensus score using at least three methods: simple z-score, KS/ssGSEA-style score, and literature signature score.
- [ ] Add state labels: epithelial, hybrid, mesenchymal, stromal-dominant, immune-inflamed EMT, hypoxic EMT, uncertain.
- [ ] Add confidence logic from signature agreement, gene coverage, sample quality, and contamination risk.

### WP3: Clinical and cohort summaries

- [ ] Add cancer-type summary table.
- [ ] Add stage, grade, metastatic label, recurrence label where available.
- [ ] Add Cox/Kaplan-Meier outputs by cancer type.
- [ ] Add warnings for low sample size or missing survival data.

### WP4: Single-cell validation

- [ ] Ingest CancerSEA or selected 3CA/TISCH2 datasets.
- [ ] Score malignant cells and non-malignant cells separately.
- [ ] Identify markers that are tumor-cell-intrinsic versus CAF/stromal.
- [ ] Export per-cancer state marker tables.

### WP5: Spatial and pathology layer

- [ ] Reuse existing spatial EMT niche scoring.
- [ ] Add spatial state cards for spots/regions.
- [ ] Add invasive-edge and stromal-neighborhood summaries.
- [ ] Add morphology or H&E tile feature hooks where HEST/HTAN/10x images are available.

### WP6: Functional and therapeutic layer

- [ ] Join target-ranker outputs to EMT states.
- [ ] Add DepMap dependency by EMT-high cell-line groups.
- [ ] Add PRISM/LINCS drug evidence.
- [ ] Add Open Targets, ChEMBL, DGIdb, HPA, and GTEx evidence fields.
- [ ] Export target/drug evidence cards.

### WP7: User experience

- [ ] Build Markdown report first.
- [ ] Build Streamlit atlas app after report outputs are stable.
- [ ] Add clinician mode: simple state card and evidence warnings.
- [ ] Add researcher mode: methods, plots, downloadable tables, code provenance.
- [ ] Add "explain this state" text that is generated from structured fields, not free-form claims.

## Decision rules

### State labels

- **Epithelial**: high epithelial score, low mesenchymal score, low hybrid score.
- **Hybrid E/M**: epithelial and mesenchymal programs both active, stromal risk not dominant.
- **Mesenchymal**: high mesenchymal score, low epithelial score, tumor-intrinsic evidence preferred.
- **Stromal-dominant**: high EMT score but fibroblast/CAF/stroma score explains the signal.
- **Immune-inflamed EMT**: EMT-high with high immune/TAM/checkpoint context.
- **Hypoxic EMT**: EMT-high with strong hypoxia/angiogenesis context.
- **Uncertain**: low gene coverage, score disagreement, weak metadata, or severe contamination.

### Confidence labels

- **High**: score consensus, good gene coverage, non-stromal validation, enough cohort support.
- **Medium**: some score agreement or limited validation.
- **Low**: score disagreement, stromal-dominant signal, low gene coverage, or small cohort.

## Deliverables

- `emt_scores.tsv`
- `cancer_type_summary.tsv`
- `survival_associations.tsv`
- `state_marker_summary.tsv`
- `sample_cards/*.json`
- `sample_cards/*.md`
- `target_cards/*.md`
- `pan_cancer_emt_state_atlas_report.md`
- `pan_cancer_emt_state_atlas_app/`

## Timeline

| Week | Goal | Deliverable |
| --- | --- | --- |
| 1 | Finalize scope and source manifest | Locked manifest and config |
| 2 | TCGA/Xena MVP scoring | Sample scores and cancer summaries |
| 3 | Clinical associations | Survival and stage reports |
| 4 | State cards | Sample and cancer-type cards |
| 5 | CancerSEA/3CA validation | Single-cell validation report |
| 6 | TISCH2/HTAN TME checks | Contamination and TME report |
| 7 | Spatial prototype | Spatial EMT map and niche summary |
| 8 | Functional target layer | Target/drug evidence cards |
| 9 | Streamlit app v1 | Local interactive atlas |
| 10 | QA and documentation | Reproducible tutorial and demo |
| 11 | Manuscript figures | Publication-ready figures |
| 12 | Final release | Versioned atlas package |

## First three implementation tasks

1. Create `configs/pan_cancer_emt_state_atlas.yml` with source paths, output paths, state thresholds, and enabled modules.
2. Add `src/emt_state_atlas/consensus.py` for multi-method EMT state consensus and confidence labels.
3. Add `src/emt_state_atlas/cards.py` plus `scripts/build_emt_state_cards.py` to generate user-facing Markdown and JSON cards from existing score tables.
