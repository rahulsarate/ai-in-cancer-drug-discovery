# Pan-Cancer EMT Therapeutic Evidence Report

Targets are linked to EMT atlas contexts as research hypotheses for validation.

## Top Targets

| target | family | priority_score | emt_state_specificity | metastatic_association | druggability | crispr_dependency | compound_availability | normal_tissue_safety | literature_support |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AXL | AXL_TAM | 0.658 | 0.5 | 0.5 | 0.687 | 0.136 | 0.647 | 0.971 | 0.967 |
| MERTK | AXL_TAM | 0.564 | 0.5 | 0.5 | 0.728 | 0.141 | 0.417 | 0.917 | 0.411 |
| TYRO3 | AXL_TAM | 0.523 | 0.5 | 0.5 | 0.617 | 0.258 | 0.248 | 0.733 | 0.633 |
| GAS6 | AXL_TAM | 0.508 | 0.5 | 0.5 | 0.617 | 0.142 | 0.172 | 0.914 | 0.633 |
| ITGAV | FAK_SRC_integrin | 0.436 | 0.5 | 0.5 | 0.3 | 0.627 | 0.2 | 0.532 | 0.267 |
| PTK2 | FAK_SRC_integrin | 0.435 | 0.5 | 0.5 | 0.3 | 0.67 | 0.222 | 0.406 | 0.267 |
| ITGB1 | FAK_SRC_integrin | 0.434 | 0.5 | 0.5 | 0.3 | 0.388 | 0.222 | 0.848 | 0.267 |
| SRC | FAK_SRC_integrin | 0.434 | 0.5 | 0.5 | 0.3 | 0.193 | 0.348 | 0.907 | 0.267 |
| PROS1 | AXL_TAM | 0.433 | 0.5 | 0.5 | 0.394 | 0.166 | 0.203 | 0.853 | 0.411 |
| TGFBR1 | TGF_beta_SMAD | 0.41 | 0.5 | 0.5 | 0.25 | 0.242 | 0.246 | 0.871 | 0.317 |
| SLC2A1 | hypoxia_metabolism | 0.406 | 0.5 | 0.5 | 0.233 | 0.624 | 0.145 | 0.551 | 0.233 |
| PXN | FAK_SRC_integrin | 0.403 | 0.5 | 0.5 | 0.3 | 0.413 | 0.17 | 0.608 | 0.267 |
| ITGB3 | FAK_SRC_integrin | 0.403 | 0.5 | 0.5 | 0.3 | 0.168 | 0.214 | 0.901 | 0.267 |
| VCL | FAK_SRC_integrin | 0.402 | 0.5 | 0.5 | 0.3 | 0.372 | 0.17 | 0.662 | 0.267 |
| JAK1 | CAF_TAM_crosstalk | 0.401 | 0.5 | 0.5 | 0.25 | 0.169 | 0.259 | 0.936 | 0.25 |
| SCD | ferroptosis | 0.398 | 0.5 | 0.5 | 0.183 | 0.831 | 0.142 | 0.258 | 0.25 |
| JAK2 | CAF_TAM_crosstalk | 0.396 | 0.5 | 0.5 | 0.25 | 0 | 0.34 | 1 | 0.25 |
| TFRC | ferroptosis | 0.395 | 0.5 | 0.5 | 0.183 | 1 | 0.12 | 0 | 0.25 |
| ITGA5 | FAK_SRC_integrin | 0.394 | 0.5 | 0.5 | 0.3 | 0.19 | 0.177 | 0.852 | 0.267 |
| YAP1 | YAP_TAZ_TEAD | 0.389 | 0.5 | 0.5 | 0.217 | 0.495 | 0.11 | 0.681 | 0.25 |

## Target Families

| family | target_count | mean_priority_score |
| --- | --- | --- |
| AXL_TAM | 5 | 0.537 |
| FAK_SRC_integrin | 8 | 0.418 |
| TGF_beta_SMAD | 1 | 0.41 |
| hypoxia_metabolism | 1 | 0.406 |
| CAF_TAM_crosstalk | 2 | 0.399 |
| ferroptosis | 2 | 0.397 |
| YAP_TAZ_TEAD | 1 | 0.389 |

## Atlas Context Notes

Prioritize targets in cancer types where the matching EMT state is frequent and the confidence/stromal warning profile fits the biological question.

## Highest EMT-Context Cancer Types

| cancer_type | sample_count | mesenchymal_like_fraction | hybrid_fraction | stromal_dominant_fraction | high_confidence_fraction |
| --- | --- | --- | --- | --- | --- |
| DLBC | 48 | 0.979 | 0 | 0.104 | 0.875 |
| SARC | 265 | 0.951 | 0.00377 | 0.74 | 0.215 |
| MESO | 87 | 0.862 | 0.0115 | 0.655 | 0.207 |
| KIRC | 606 | 0.744 | 0.0297 | 0.153 | 0.614 |
| SKCM | 473 | 0.681 | 0 | 0.0846 | 0.596 |
| GBM | 168 | 0.649 | 0 | 0.0536 | 0.595 |
| UCS | 57 | 0.632 | 0.105 | 0.368 | 0.316 |
| TGCT | 139 | 0.547 | 0.0216 | 0.158 | 0.396 |
| HNSC | 566 | 0.498 | 0.0459 | 0.26 | 0.3 |
| unknown | 46 | 0.478 | 0.13 | 0.413 | 0.109 |
| ACC | 79 | 0.342 | 0 | 0.0253 | 0.316 |
| PAAD | 183 | 0.328 | 0.541 | 0.322 | 0.0929 |
