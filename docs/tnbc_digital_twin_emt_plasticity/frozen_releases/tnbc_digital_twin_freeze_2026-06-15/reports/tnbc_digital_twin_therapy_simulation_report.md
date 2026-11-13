# TNBC EMT Digital-Twin Therapy Simulation

## Purpose

Simulate four EMT/plasticity compartments under neoadjuvant chemotherapy using the original archetypes plus `GSE43816` calibrated transition-rate priors.

## Baseline Archetype Summary

| archetype                  |   initial_tumor_burden |   final_tumor_burden |   tumor_burden_ratio |   initial_resistant_fraction |   final_resistant_fraction |   emt_shift_delta |   persister_delta |   therapy_selection_pressure |   residual_disease_probability_proxy |
|:---------------------------|-----------------------:|---------------------:|---------------------:|-----------------------------:|---------------------------:|------------------:|------------------:|-----------------------------:|-------------------------------------:|
| chemo_sensitive_epithelial |                      1 |            0.0751759 |            0.0751759 |                         0.28 |                   0.991911 |          0.304106 |          0.407806 |                     0.711911 |                             0.48892  |
| mesenchymal_persister_high |                      1 |            0.612971  |            0.612971  |                         0.76 |                   0.998477 |          0.114424 |          0.124052 |                     0.238477 |                             0.786677 |
| plastic_residual_risk      |                      1 |            0.388852  |            0.388852  |                         0.6  |                   0.997218 |          0.136581 |          0.260637 |                     0.397218 |                             0.663034 |

## Calibrated-Prior Summary

| archetype                  |   initial_tumor_burden |   final_tumor_burden |   tumor_burden_ratio |   initial_resistant_fraction |   final_resistant_fraction |   emt_shift_delta |   persister_delta |   therapy_selection_pressure |   residual_disease_probability_proxy |
|:---------------------------|-----------------------:|---------------------:|---------------------:|-----------------------------:|---------------------------:|------------------:|------------------:|-----------------------------:|-------------------------------------:|
| chemo_sensitive_epithelial |                      1 |             0.276271 |             0.276271 |                         0.28 |                   0.81067  |         0.326948  |          0.203722 |                     0.53067  |                             0.54515  |
| mesenchymal_persister_high |                      1 |             0.725501 |             0.725501 |                         0.76 |                   0.98477  |         0.0509974 |          0.173773 |                     0.22477  |                             0.844457 |
| plastic_residual_risk      |                      1 |             0.599185 |             0.599185 |                         0.6  |                   0.966966 |         0.134263  |          0.232703 |                     0.366966 |                             0.769641 |

## Final-State Uncertainty

| archetype                  |   tumor_burden_median |   tumor_burden_q025 |   tumor_burden_q975 |   persister_fraction_estimate_median |   persister_fraction_estimate_q025 |   persister_fraction_estimate_q975 |   plasticity_index_median |   plasticity_index_q025 |   plasticity_index_q975 |   resistant_fraction_median |   resistant_fraction_q025 |   resistant_fraction_q975 |
|:---------------------------|----------------------:|--------------------:|--------------------:|-------------------------------------:|-----------------------------------:|-----------------------------------:|--------------------------:|------------------------:|------------------------:|----------------------------:|--------------------------:|--------------------------:|
| chemo_sensitive_epithelial |              0.275472 |            0.256922 |            0.292245 |                             0.254603 |                           0.227852 |                           0.280267 |                  0.451084 |                0.412189 |                0.491252 |                    0.811377 |                  0.776541 |                  0.846449 |
| mesenchymal_persister_high |              0.72388  |            0.692809 |            0.751808 |                             0.375579 |                           0.337972 |                           0.412434 |                  0.482641 |                0.44195  |                0.525098 |                    0.984792 |                  0.978474 |                  0.988494 |
| plastic_residual_risk      |              0.597002 |            0.571417 |            0.623489 |                             0.354083 |                           0.319145 |                           0.385419 |                  0.517088 |                0.47557  |                0.559549 |                    0.966995 |                  0.955349 |                  0.97436  |

## Plot

![Calibrated uncertainty](C:/Users/HP/OneDrive/Documents/AI in Cancer Drug Discovery/docs/tnbc_digital_twin_emt_plasticity/assets/therapy_simulation/tnbc_calibrated_simulation_uncertainty.png)

## Interpretation

- Calibrated parameters are used as priors, not fixed clinical constants.
- Refined persister layers reduce persister kill and increase therapy-induced entry into the `P` compartment.
- The uncertainty band reflects parameter perturbation around the sparse 7-patient `GSE43816` calibration.