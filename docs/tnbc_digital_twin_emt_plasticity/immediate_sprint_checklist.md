# Immediate Sprint Checklist

## Sprint goal

Turn the TNBC NAC digital-twin concept into a runnable first prototype using public data where available and synthetic data where real longitudinal TNBC NAC data is not yet ready.

## Week 1: Lock biology and datasets

- [ ] Confirm exact TNBC NAC question: pCR prediction, residual disease prediction, or early EMT-shift prediction.
- [ ] Complete TNBC NAC dataset search in GEO, ArrayExpress, HTAN, cBioPortal, TCGA, METABRIC, DepMap, and PRISM.
- [ ] Fill `dataset_inventory.tsv` with real accession IDs and access status.
- [ ] Finalize TNBC EMT marker dictionary from `configs/tnbc_digital_twin.yml`.
- [ ] Decide which data source becomes the first Tier A training dataset.

## Week 2: Prepare data and labels

- [ ] Create `data/raw/tnbc_nac/`.
- [ ] Download or place selected expression and metadata files there.
- [ ] Standardize sample metadata to `patient_id`, `sample_id`, `timepoint`, `nac_regimen`, and `pcr_status`.
- [ ] Filter for confirmed TNBC samples.
- [ ] Create a first cleaned metadata table in `data/processed/tnbc_digital_twin/`.

## Week 3: Score EMT and resistance programs

- [ ] Reuse existing EMT scoring functions.
- [ ] Score epithelial, mesenchymal, partial EMT, stromal, immune, CAF, TAM, hypoxia, and proliferation programs.
- [ ] Add TNBC-specific AXL/TAM, TGF-beta, YAP/TAZ, and persister/stemness scores.
- [ ] Generate `tnbc_emt_scores.tsv`.
- [ ] Check whether pCR and residual disease groups differ in baseline or on-treatment EMT features.

## Week 4: Build first digital twin simulator

- [ ] Implement four-state E/H/M/P ODE model.
- [ ] Run synthetic simulations for responder and resistant TNBC archetypes.
- [ ] Estimate initial state fractions from EMT scores.
- [ ] Produce simulated state trajectories across NAC cycles.
- [ ] Export digital-twin features for prediction.

## Week 5: Train first predictor

- [ ] Train clinical-only baseline model.
- [ ] Train EMT-score-only model.
- [ ] Train digital-twin-feature model.
- [ ] Compare AUROC, AUPRC, calibration, and feature importance.
- [ ] Identify whether digital-twin features add value.

## Week 6: Produce communication artifacts

- [ ] Create one mock patient report.
- [ ] Create one research dashboard view.
- [ ] Summarize limitations and missing-data risks.
- [ ] Draft first methods section.
- [ ] Decide whether next sprint should focus on real data expansion, model refinement, or dashboard buildout.

