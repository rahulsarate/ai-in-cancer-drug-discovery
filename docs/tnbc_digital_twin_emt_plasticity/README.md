# Digital Twin of EMT Plasticity Under Neoadjuvant Chemotherapy in TNBC

## Locked project scope

This project focuses on **triple-negative breast cancer (TNBC)** patients treated with **neoadjuvant chemotherapy (NAC)** before surgery. The digital twin will model how tumor-cell epithelial-mesenchymal plasticity changes during therapy and whether those changes predict resistant residual disease.

The first version is a **research decision-support prototype**, not a clinical treatment recommendation system.

## Central clinical question

Can a patient-specific digital twin predict, early during neoadjuvant chemotherapy, whether a TNBC tumor is shifting toward hybrid epithelial/mesenchymal, mesenchymal-like, stem-like, or drug-tolerant states that increase the risk of residual disease or relapse?

## Primary use case

At baseline and early on treatment, the system ingests molecular, imaging, and pathology features and outputs:

- Predicted probability of pathological complete response.
- Predicted risk of EMT-associated resistant residual disease.
- Estimated shift in epithelial, hybrid E/M, mesenchymal, and persister cell fractions.
- Most likely biological drivers of resistance.
- Recommended research follow-up, such as early biopsy, organoid testing, or pathway validation.

## Why TNBC under NAC is the right first cancer type

TNBC is clinically aggressive, heterogeneous, and commonly treated with NAC. Pathological complete response after NAC is a strong clinical endpoint, while residual disease is associated with higher relapse risk. TNBC also has strong links to EMT, cancer stemness, immune exclusion, hypoxia, stromal signaling, and therapy resistance. This makes it a strong setting for testing whether dynamic EMT plasticity improves prediction beyond static baseline biomarkers.

## Patient timeline

| Time point | Clinical moment | Data priority |
| --- | --- | --- |
| T0 | Pretreatment biopsy | Baseline tumor state, EMT score, immune/stromal context |
| T1 | Early on-treatment, after 1-2 cycles | Therapy-induced EMT shift and persister expansion |
| T2 | Surgery after NAC | pCR vs residual disease, residual EMT state |
| T3 | Follow-up or relapse | Long-term validation of risk prediction |

## Minimal viable data

The first research prototype should work with:

- Pretreatment bulk RNA-seq or targeted expression panel.
- Early on-treatment expression data if available.
- Clinical treatment metadata.
- Response label: pCR versus residual disease.
- Basic pathology markers: ER, PR, HER2, grade, Ki-67, tumor cellularity.

## Ideal data

The strongest version would include:

- Single-cell RNA-seq at T0 and T1.
- Spatial transcriptomics or multiplex immunofluorescence.
- MRI tumor volume before and during NAC.
- Pathology marker panel: E-cadherin, EPCAM, cytokeratins, vimentin, N-cadherin, ZEB1, SNAIL, TWIST1, AXL, Ki-67.
- Immune and stromal features: CD8, PD-L1, macrophage markers, CAF markers, hypoxia markers.
- ctDNA dynamics.
- Patient-derived organoid or explant drug response.

## Digital twin state variables

The first compartment model tracks:

| State | Meaning | Expected therapy behavior |
| --- | --- | --- |
| E | Epithelial-like, proliferative tumor cells | More likely chemo-sensitive |
| H | Hybrid epithelial/mesenchymal plastic cells | Adaptable, stem-like, relapse-prone |
| M | Mesenchymal-like invasive cells | More drug-resistant and invasive |
| P | Drug-tolerant persister cells | Slow-cycling, therapy-surviving reservoir |

## First model outputs

- `emt_plasticity_score`
- `hybrid_state_fraction`
- `mesenchymal_shift_delta`
- `persister_risk_score`
- `pcr_probability`
- `residual_disease_probability`
- `emt_resistance_risk`
- `dominant_resistance_driver`
- `model_confidence`

## First research hypothesis

TNBC tumors with high baseline hybrid E/M burden or early therapy-induced movement toward hybrid, mesenchymal, hypoxic, AXL-high, TGF-beta-high, or stem-like states will have a higher risk of residual disease after NAC than tumors that remain epithelial/proliferative and show decreasing plasticity.

## Project deliverables

1. TNBC NAC literature map.
2. Public dataset inventory.
3. EMT and resistance marker dictionary.
4. TNBC-specific EMT scoring pipeline.
5. Patient state-transition matrix.
6. ODE compartment digital twin.
7. ML pCR/residual-disease predictor.
8. Therapy simulation module.
9. Research dashboard.
10. Clinician-facing mock report.
11. Retrospective validation report.
12. Manuscript or thesis-ready project report.

