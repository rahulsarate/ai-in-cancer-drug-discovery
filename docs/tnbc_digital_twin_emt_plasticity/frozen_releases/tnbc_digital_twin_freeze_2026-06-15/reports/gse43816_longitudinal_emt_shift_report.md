# GSE43816 Longitudinal EMT-Shift Analysis

## Objective

Quantify paired before-versus-after neoadjuvant chemotherapy shifts in EMT plasticity and digital-twin state estimates for TNBC samples.

## Cohort

- Paired patients analyzed: 7.
- Timepoints: pretreatment biopsy (`T0`) and post-treatment/tumorectomy sample (`T2`).
- Dataset response labels are not available, so this is a therapy-induced state-shift analysis.

## Key Shift Summary

| feature                            |   pairs |   mean_delta |   median_delta |   patients_increased |   patients_decreased |   largest_increase_patient |   largest_decrease_patient |
|:-----------------------------------|--------:|-------------:|---------------:|---------------------:|---------------------:|---------------------------:|---------------------------:|
| emt_score                          |       7 |  -0.262834   |     0.0320822  |                    4 |                    3 |                          6 |                          1 |
| hybrid_fraction_estimate           |       7 |   0.0374367  |     0.0382179  |                    4 |                    3 |                          1 |                          2 |
| mesenchymal_fraction_estimate      |       7 |  -0.04915    |    -0.0298618  |                    3 |                    4 |                          2 |                          1 |
| partial_emt_score                  |       7 |   0.304971   |    -0.07969    |                    3 |                    4 |                          1 |                          2 |
| persister_fraction_estimate        |       7 |  -0.0243048  |    -0.0269648  |                    2 |                    5 |                          4 |                          1 |
| plasticity_index                   |       7 |   0.0131319  |     0.00608417 |                    4 |                    3 |                          4 |                          2 |
| residual_disease_probability_proxy |       7 |  -0.00568873 |    -0.0136374  |                    3 |                    4 |                          5 |                          4 |
| resistant_fraction_estimate        |       7 |  -0.0360181  |     0.0187239  |                    5 |                    2 |                          2 |                          1 |
| therapy_selection_pressure         |       7 |   0.0093031  |     0.0257119  |                    4 |                    3 |                          1 |                          4 |

## Bootstrap Uncertainty

| feature                            |   pairs |   mean_delta |   median_delta |   delta_mean_q025 |   delta_mean_q975 |
|:-----------------------------------|--------:|-------------:|---------------:|------------------:|------------------:|
| emt_score                          |       7 |  -0.262834   |     0.0320822  |       -1.09638    |         0.304013  |
| hybrid_fraction_estimate           |       7 |   0.0374367  |     0.0382179  |       -0.00237772 |         0.0919335 |
| mesenchymal_fraction_estimate      |       7 |  -0.04915    |    -0.0298618  |       -0.166731   |         0.0421228 |
| partial_emt_score                  |       7 |   0.304971   |    -0.07969    |       -0.0914577  |         0.850667  |
| persister_fraction_estimate        |       7 |  -0.0243048  |    -0.0269648  |       -0.087302   |         0.0272542 |
| plasticity_index                   |       7 |   0.0131319  |     0.00608417 |       -0.0172317  |         0.043735  |
| residual_disease_probability_proxy |       7 |  -0.00568873 |    -0.0136374  |       -0.0349394  |         0.0249937 |
| resistant_fraction_estimate        |       7 |  -0.0360181  |     0.0187239  |       -0.160998   |         0.0433401 |
| therapy_selection_pressure         |       7 |   0.0093031  |     0.0257119  |       -0.0466435  |         0.0627813 |

## Selected Report Patient

`Patient 6` was selected because it had the highest weighted post-therapy risk-shift score.

## Plots

![Paired feature shifts](C:/Users/HP/OneDrive/Documents/AI in Cancer Drug Discovery/docs/tnbc_digital_twin_emt_plasticity/assets/gse43816_longitudinal/gse43816_paired_feature_shifts.png)

![Feature delta heatmap](C:/Users/HP/OneDrive/Documents/AI in Cancer Drug Discovery/docs/tnbc_digital_twin_emt_plasticity/assets/gse43816_longitudinal/gse43816_delta_heatmap.png)

![Dominant resistance axes](C:/Users/HP/OneDrive/Documents/AI in Cancer Drug Discovery/docs/tnbc_digital_twin_emt_plasticity/assets/gse43816_longitudinal/gse43816_resistance_axis_shift.png)