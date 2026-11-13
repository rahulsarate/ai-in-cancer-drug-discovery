# Detailed Work Plan

## Project name

**DTEP-TNBC: Digital Twin of EMT Plasticity Under Neoadjuvant Chemotherapy in Triple-Negative Breast Cancer**

## Final objective

Build and validate a patient-specific digital twin that predicts whether neoadjuvant chemotherapy drives TNBC tumors toward EMT-associated resistant states and whether those states predict pathological residual disease.

## Phase 0: Project locking and setup

### Step 0.1: Fix the clinical setting

Use only:

- Disease: triple-negative breast cancer.
- Treatment window: neoadjuvant chemotherapy before surgery.
- Main endpoint: pathological complete response versus residual disease.
- Secondary endpoints: residual cancer burden, relapse-free survival, distant metastasis, overall survival if available.

### Step 0.2: Define the first version boundary

Version 1 should not attempt to solve every TNBC treatment question. It should answer one precise question:

> Given baseline and early-treatment molecular features, can we identify patients whose tumors are becoming EMT-plastic and resistant under NAC?

### Step 0.3: Create project folders

Recommended structure:

```text
docs/tnbc_digital_twin_emt_plasticity/
data/raw/tnbc_nac/
data/processed/tnbc_digital_twin/
configs/tnbc_digital_twin.yml
src/tnbc_digital_twin/
scripts/tnbc_*.py
tests/test_tnbc_digital_twin.py
```

## Phase 1: Literature and biological framework

### Step 1.1: TNBC NAC clinical background

Collect and summarize:

- Standard NAC regimens in TNBC.
- pCR as a prognostic endpoint.
- Residual cancer burden as a graded endpoint.
- How immunotherapy and platinum therapy affect response in modern TNBC cohorts.
- Known predictors of pCR and residual disease.

Output:

- `docs/tnbc_digital_twin_emt_plasticity/literature_map.md`

### Step 1.2: EMT plasticity biology in TNBC

Build a TNBC-specific marker and pathway map.

Core epithelial markers:

- `CDH1`
- `EPCAM`
- `KRT5`
- `KRT8`
- `KRT14`
- `KRT18`
- `KRT19`
- `CLDN3`
- `CLDN4`

Core mesenchymal markers:

- `VIM`
- `FN1`
- `CDH2`
- `S100A4`
- `SPARC`
- `ITGA5`
- `ITGB1`
- `MMP2`
- `MMP9`

EMT transcription factors:

- `SNAI1`
- `SNAI2`
- `ZEB1`
- `ZEB2`
- `TWIST1`
- `TWIST2`

Hybrid E/M and plasticity regulators:

- `GRHL2`
- `OVOL1`
- `OVOL2`
- `JAG1`
- `NOTCH1`
- `NUMB`

Therapy-resistance and persister pathways:

- `AXL`
- `MERTK`
- `GAS6`
- `TGFB1`
- `TGFBR1`
- `TGFBR2`
- `YAP1`
- `WWTR1`
- `STAT3`
- `JAK1`
- `JAK2`
- `HIF1A`
- `ALDH1A1`
- `PROM1`
- `CD44`

Output:

- EMT marker dictionary.
- Resistance pathway table.
- TNBC EMT state definition table.

## Phase 2: Public dataset discovery

### Step 2.1: Build a TNBC NAC dataset inventory

Prioritize datasets with:

- Pretreatment biopsy.
- On-treatment biopsy.
- Surgery/residual tumor sample.
- pCR or residual disease labels.
- TNBC subtype labels.
- Expression data.

Data types to search:

- Bulk RNA-seq.
- Microarray.
- Single-cell RNA-seq.
- Spatial transcriptomics.
- Imaging/radiomics.
- Organoid or ex vivo drug response.

Likely repositories:

- GEO.
- ArrayExpress.
- dbGaP-controlled cohorts if available through collaborators.
- cBioPortal.
- TCGA-BRCA for baseline TNBC reference only.
- METABRIC for baseline/survival reference only.
- Human Tumor Atlas Network for spatial/single-cell references.
- DepMap and PRISM for TNBC cell-line drug-response support.

Output:

- `docs/tnbc_digital_twin_emt_plasticity/dataset_inventory.tsv`

### Step 2.2: Classify datasets by use

Use four evidence tiers:

| Tier | Use | Example |
| --- | --- | --- |
| A | Main training and validation | TNBC NAC with pCR labels |
| B | EMT biology calibration | TNBC scRNA/spatial datasets |
| C | Drug-response support | TNBC organoids/cell lines |
| D | External context | TCGA/METABRIC baseline TNBC |

Output:

- Dataset readiness matrix.

## Phase 3: Data model and feature dictionary

### Step 3.1: Define patient-level table

Required columns:

- `patient_id`
- `sample_id`
- `timepoint`
- `age`
- `stage`
- `grade`
- `er_status`
- `pr_status`
- `her2_status`
- `tnbc_confirmed`
- `nac_regimen`
- `cycle_number`
- `pcr_status`
- `residual_cancer_burden`
- `followup_months`
- `relapse_status`

### Step 3.2: Define sample-level molecular features

Feature blocks:

- EMT signatures.
- Hybrid E/M signatures.
- Stemness signatures.
- Proliferation signatures.
- Hypoxia signatures.
- TGF-beta signaling.
- AXL/TAM signaling.
- Immune cytotoxicity.
- Immune checkpoint expression.
- CAF/stromal signatures.
- Macrophage/TAM signatures.

### Step 3.3: Define digital-twin outputs

Required output columns:

- `epithelial_fraction_estimate`
- `hybrid_fraction_estimate`
- `mesenchymal_fraction_estimate`
- `persister_fraction_estimate`
- `plasticity_index`
- `emt_shift_delta`
- `therapy_selection_pressure`
- `pcr_probability`
- `residual_disease_probability`
- `dominant_resistance_axis`
- `prediction_confidence`

Output:

- `docs/tnbc_digital_twin_emt_plasticity/variable_manifest.tsv`

## Phase 4: EMT scoring pipeline

### Step 4.1: Start with existing EMT scoring code

Reuse the current repository's EMT-state scoring modules where possible:

- `src/emt_state_atlas/scoring.py`
- `src/emt_state_atlas/signatures.py`
- `src/emt_state_atlas/therapy.py`
- `src/emt_state_atlas/clinical.py`

### Step 4.2: Add TNBC-specific signatures

Add or configure:

- Basal-like TNBC marker score.
- Claudin-low/EMT-like TNBC score.
- Immune-hot versus immune-cold score.
- AXL/TAM family activity score.
- TGF-beta/CAF niche score.
- Persister/stem-like score.

### Step 4.3: Generate patient EMT score table

For every sample:

- Calculate epithelial score.
- Calculate mesenchymal score.
- Calculate partial EMT score.
- Calculate stromal correction features.
- Calculate immune/TME context.
- Calculate therapy-resistance pathway activity.

Output:

- `data/processed/tnbc_digital_twin/tnbc_emt_scores.tsv`

## Phase 5: Build the first digital twin

### Step 5.1: Define state compartments

Use four compartments:

- `E`: epithelial-like chemo-sensitive cells.
- `H`: hybrid E/M plastic cells.
- `M`: mesenchymal-like resistant cells.
- `P`: persister/stem-like drug-tolerant cells.

### Step 5.2: Define transition rules

Core transitions:

- `E -> H`: therapy stress, TGF-beta, hypoxia, CAF signals.
- `H -> M`: sustained EMT pressure, AXL/YAP/TGF-beta activation.
- `H -> E`: MET-like reversion when stress decreases.
- `E -> P`: acute therapy-induced persister formation.
- `H -> P`: plastic stem-like persister formation.
- `P -> H`: reactivation after therapy pressure changes.

### Step 5.3: Define therapy effects

NAC should affect states differently:

| State | Growth | Chemo kill | Risk |
| --- | ---: | ---: | --- |
| E | High | High | Shrinkage but selection pressure |
| H | Medium | Medium-low | Adaptation and relapse |
| M | Low-medium | Low | Invasion and residual disease |
| P | Low/dormant | Very low | Late relapse reservoir |

### Step 5.4: Implement ODE equations

Initial model:

```text
dE/dt = rE*E*(1-N/K) - kE(t)*E - aEH*E + aHE*H - aEP*E
dH/dt = rH*H*(1-N/K) - kH(t)*H + aEH*E - aHE*H - aHM*H - aHP*H + aPH*P
dM/dt = rM*M*(1-N/K) - kM(t)*M + aHM*H
dP/dt = rP*P*(1-N/K) - kP(t)*P + aEP*E + aHP*H - aPH*P
```

Where:

```text
N = E + H + M + P
K = patient-specific carrying capacity estimated from tumor burden
kX(t) = therapy kill rate during NAC exposure
aXY = state transition rate from X to Y
```

Output:

- First ODE simulator.
- Synthetic patient simulation.
- Plots of state fractions over NAC cycles.

## Phase 6: Personalization

### Step 6.1: Estimate initial state fractions

Use:

- EMT scores.
- Hybrid score.
- Stemness score.
- Deconvolution if available.
- Histology tumor cellularity.

### Step 6.2: Estimate transition rates

Use:

- T0 to T1 changes if longitudinal data exists.
- Pseudotime/RNA velocity if scRNA-seq exists.
- Literature priors if only baseline data exists.
- Bayesian updating as new data arrives.

### Step 6.3: Estimate therapy sensitivity

Use:

- Observed tumor volume change.
- pCR/residual disease labels.
- Expression-derived proliferation score.
- Drug-response priors from TNBC cell lines/organoids.

Output:

- Patient-specific model parameter table.

## Phase 7: Prediction layer

### Step 7.1: Define prediction targets

Primary:

- pCR versus residual disease.

Secondary:

- high versus low residual cancer burden.
- relapse-free survival.
- EMT-high residual disease.
- likelihood of resistant persister expansion.

### Step 7.2: Train baseline models

Start with interpretable baselines:

- Logistic regression.
- Elastic net.
- Random forest.
- XGBoost.
- Cox model if survival data exists.

### Step 7.3: Compare against digital-twin features

Compare:

- Clinical features only.
- Baseline molecular features only.
- EMT scores only.
- Digital-twin simulated features.
- Combined model.

Key question:

> Do dynamic EMT/plasticity features improve prediction of residual disease beyond baseline markers?

Output:

- Model performance table.
- Feature importance report.

## Phase 8: Therapy simulation experiments

### Step 8.1: Simulate NAC pressure

Simulate:

- Standard chemotherapy schedule.
- Strong early cytotoxic pressure.
- Delayed response.
- Incomplete kill of hybrid/M/P states.

### Step 8.2: Simulate research combination hypotheses

For hypothesis generation only:

- NAC + AXL/TAM-axis suppression.
- NAC + TGF-beta pathway suppression.
- NAC + FAK/SRC/integrin-axis suppression.
- NAC + hypoxia/stress-response suppression.
- NAC + immune activation in immune-excluded EMT-high tumors.

Output:

- Ranked simulated strategies by predicted reduction of H/M/P residual fraction.

## Phase 9: Dashboard and reports

### Step 9.1: Research dashboard

Dashboard tabs:

- Patient overview.
- EMT state distribution.
- Therapy trajectory.
- Digital-twin simulation.
- Resistance drivers.
- Prediction uncertainty.
- Data quality.

### Step 9.2: Clinician-facing mock report

Report sections:

- Patient/sample context.
- Current EMT plasticity state.
- Predicted pCR/residual disease risk.
- Dominant resistance axis.
- Confidence and limitations.
- Suggested research follow-up.

Output:

- `docs/tnbc_digital_twin_emt_plasticity/clinician_report_template.md`

## Phase 10: Validation

### Step 10.1: Technical validation

Check:

- Reproducibility across runs.
- Batch sensitivity.
- Missing data behavior.
- Parameter identifiability.
- Robustness of EMT scoring.

### Step 10.2: Biological validation

Check whether predicted resistant states match:

- Residual tumor gene expression.
- Protein marker staining.
- Organoid drug response.
- Spatial niches.
- Known TNBC resistance biology.

### Step 10.3: Clinical validation

Metrics:

- AUROC for pCR prediction.
- AUPRC for residual disease prediction.
- Calibration curve.
- Decision curve analysis.
- Hazard ratio for relapse-free survival if available.
- Net improvement over baseline clinical model.

Output:

- Retrospective validation report.

## Phase 11: Manuscript or thesis structure

Suggested chapters:

1. Clinical problem: residual disease in TNBC after NAC.
2. EMT plasticity and non-genetic therapy resistance.
3. Dataset assembly and preprocessing.
4. EMT scoring and state definition.
5. Digital twin model construction.
6. Patient-specific calibration.
7. Prediction of pCR/residual disease.
8. Therapy simulation and resistance hypotheses.
9. Validation and limitations.
10. Clinical and research translation.

## Immediate 10-task sprint

1. Create TNBC NAC dataset inventory.
2. Create TNBC EMT marker dictionary.
3. Identify 3-5 public cohorts for first analysis.
4. Reuse existing EMT scoring pipeline on TNBC-like data.
5. Define pCR/residual disease labels.
6. Build synthetic E/H/M/P ODE simulator.
7. Fit simulator to toy TNBC patient trajectories.
8. Add digital-twin feature outputs.
9. Train first pCR prediction baseline.
10. Generate one mock clinician report.

