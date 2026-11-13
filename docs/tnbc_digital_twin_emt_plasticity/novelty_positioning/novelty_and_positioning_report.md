# Novelty and Literature Positioning Report

## Bottom Line

The project is novel primarily by integration and governance. Individual ingredients exist in the literature: TNBC NAC response endpoints, EMT plasticity biology, drug-tolerant persister biology, imaging-based breast cancer digital twins, QSP/virtual-patient oncology twins, and digital-twin credibility reviews. What is less common is a TNBC NAC workflow that combines EMT-state dynamics, persister biology, longitudinal transition priors, single-cell persister/niche review, response-label curation, platform-aware external validation, and clinician-style reporting boundaries in one reproducible package.

## Novel Contributions

1. It is TNBC NAC-specific but biologically state-centered, not only endpoint-centered.
2. It treats EMT as a dynamic epithelial-hybrid-mesenchymal-persister state space.
3. It separates tumor-cell persister, stress-tolerance, and niche-persister layers.
4. It calibrates transition priors from paired pre/post-NAC TNBC samples.
5. It audits and curates response labels instead of assuming public metadata are clean.
6. It separates same-platform, cross-platform, raw, percentile, z-score, and quantile-calibrated validation.
7. It integrates a species-filtered single-cell persister layer but explicitly preserves ambiguous compartments.
8. It defines clinician-style reporting rules that forbid treatment recommendations and emphasize uncertainty.

## Similar Reports and How This Project Differs

| Comparator                       | Similar to this project                                                                               | Different from this project                                                                                                                      |
|:---------------------------------|:------------------------------------------------------------------------------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------|
| pCR/RCB outcome literature       | Defines why pCR/residual disease matters.                                                             | Does not model dynamic EMT or persister state transitions.                                                                                       |
| EMP/EMT plasticity reviews       | Frames EMT as a continuum linked to resistance.                                                       | Usually conceptual, not an executable TNBC NAC digital-twin pipeline.                                                                            |
| Drug-tolerant persister reviews  | Highlights reversible survivor states and relapse reservoirs.                                         | Not TNBC NAC-specific and usually not linked to response-model validation.                                                                       |
| MRI-based TNBC NAC digital twins | Builds patient-specific NAC response twins in TNBC.                                                   | Primarily imaging/tumor-growth centered rather than transcriptomic EMT/persister state biology.                                                  |
| QSP / virtual-patient IO twins   | Uses mechanistic simulation and virtual patients for oncology decisions.                              | Usually immune/QSP-focused, not EMT/persister digital-state reporting in TNBC NAC.                                                               |
| Oncology DT scoping reviews      | Identifies validation, governance, and credibility requirements.                                      | Broad review layer, not a disease-specific executable pipeline.                                                                                  |
| This TNBC EMT digital twin       | Uses accepted response endpoints, public cohorts, state modeling, and external validation principles. | Combines EMT/persister state dynamics, curated labels, cross-platform validation, and single-cell ambiguity governance in one TNBC NAC workflow. |

## Capability Matrix

| resource                         |   TNBC NAC |   EMT/EMP states |   Persister biology |   Longitudinal shift |   Single-cell layer |   Label curation |   Platform-aware validation |   Clinician report rules |
|:---------------------------------|-----------:|-----------------:|--------------------:|---------------------:|--------------------:|-----------------:|----------------------------:|-------------------------:|
| pCR/RCB outcome literature       |          2 |                0 |                   0 |                    0 |                   0 |                1 |                           0 |                        1 |
| EMP/EMT plasticity reviews       |          1 |                2 |                   1 |                    0 |                   1 |                0 |                           0 |                        0 |
| Drug-tolerant persister reviews  |          0 |                1 |                   2 |                    0 |                   1 |                0 |                           0 |                        0 |
| MRI-based TNBC NAC digital twins |          2 |                0 |                   0 |                    2 |                   0 |                0 |                           1 |                        1 |
| QSP / virtual-patient IO twins   |          1 |                0 |                   0 |                    1 |                   0 |                0 |                           1 |                        1 |
| Oncology DT scoping reviews      |          0 |                0 |                   0 |                    1 |                   0 |                0 |                           1 |                        2 |
| This TNBC EMT digital twin       |          2 |                2 |                   2 |                    2 |                   2 |                2 |                           2 |                        2 |

## Interpretation

The closest comparator is MRI-based TNBC NAC digital-twin work, because it also creates patient-specific neoadjuvant treatment twins in TNBC. The key difference is biological resolution: the MRI twin is stronger for growth and treatment-response simulation, while this project is stronger for transcriptomic EMT/persister state interpretation and research-report governance.

EMP and DTP reviews motivate the biological premise but do not provide an executable TNBC NAC validation pipeline. Oncology digital-twin reviews define credibility needs but are not disease-specific implementations. QSP/virtual-patient immuno-oncology work provides mechanistic simulation philosophy but does not focus on TNBC NAC EMT/persister state transitions.

## Charts Generated

- `assets/novelty_matrix_heatmap.png`
- `assets/novelty_positioning_map.png`
- `assets/evidence_stack.png`
- `assets/four_state_digital_twin_diagram.png`

## Sources Used

- [CTNeoBC pCR pooled analysis](https://pubmed.ncbi.nlm.nih.gov/24529560/): pCR endpoint context.
- [Residual cancer burden long-term outcomes](https://pubmed.ncbi.nlm.nih.gov/34902335/): Residual disease prognostic context.
- [KEYNOTE-522 overall survival](https://pubmed.ncbi.nlm.nih.gov/39282906/): Modern TNBC NAC/chemo-immunotherapy context.
- [MRI-based TNBC NAC digital twins](https://pmc.ncbi.nlm.nih.gov/articles/PMC11976917/): Closest TNBC NAC digital twin comparator.
- [From virtual patients to digital twins in immuno-oncology](https://www.nature.com/articles/s41746-024-01188-4): Mechanistic/QSP digital twin comparator.
- [Advancing precision oncology with digital and virtual twins](https://www.mdpi.com/2072-6694/16/22/3817): Scoping review and credibility context.
- [Update on epithelial-mesenchymal plasticity in cancer progression](https://pmc.ncbi.nlm.nih.gov/articles/PMC10872224/): EMP biology context.
- [Drug-tolerant persister cells in cancer](https://www.nature.com/articles/s41467-025-66376-6): Persister biology and translation gaps.