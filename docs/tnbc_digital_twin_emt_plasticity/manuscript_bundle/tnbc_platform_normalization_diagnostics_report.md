# TNBC Platform Normalization Diagnostics

## Purpose

Quantify distribution shifts between the internal array-derived TNBC response-model features and the external RNA-seq TPM-derived validation features before interpreting cross-cohort performance.

## Feature Summary

| cohort                        | feature                         |   n |   missing_fraction |         mean |       std |      median |        q025 |     q975 |
|:------------------------------|:--------------------------------|----:|-------------------:|-------------:|----------:|------------:|------------:|---------:|
| internal_geo_array            | epithelial                      | 396 |                  0 | -0.156345    | 0.581919  | -0.0809353  | -1.52707    | 0.859837 |
| internal_geo_array            | mesenchymal                     | 396 |                  0 |  0.134693    | 0.494483  |  0.0795455  | -0.70553    | 1.07546  |
| internal_geo_array            | emt_score                       | 396 |                  0 |  0.291038    | 0.872703  |  0.260344   | -1.13899    | 2.00403  |
| internal_geo_array            | partial_emt_score               | 396 |                  0 | -0.374938    | 0.461402  | -0.34161    | -1.53502    | 0.348736 |
| internal_geo_array            | stromal_fibroblast              | 396 |                  0 | -0.0292999   | 0.800563  | -0.0832052  | -1.37749    | 1.44894  |
| internal_geo_array            | caf                             | 396 |                  0 | -0.0211889   | 0.73253   | -0.0873754  | -1.23557    | 1.41702  |
| internal_geo_array            | immune_total                    | 396 |                  0 |  0.20154     | 0.732169  |  0.187055   | -1.00766    | 1.62256  |
| internal_geo_array            | tam_spp1                        | 396 |                  0 |  0.17951     | 0.660726  |  0.126774   | -1.07107    | 1.49397  |
| internal_geo_array            | hypoxia                         | 396 |                  0 |  0.35852     | 0.615315  |  0.284309   | -0.68022    | 1.65482  |
| internal_geo_array            | tnbc_axl_tam                    | 396 |                  0 |  0.139727    | 0.529265  |  0.14468    | -0.779615   | 1.19798  |
| internal_geo_array            | tnbc_tgfb                       | 396 |                  0 | -0.0438007   | 0.408759  | -0.0669832  | -0.817823   | 0.922101 |
| internal_geo_array            | tnbc_yap_taz                    | 396 |                  0 |  0.464076    | 0.61717   |  0.508592   | -1.20433    | 1.46164  |
| internal_geo_array            | tnbc_hypoxia                    | 396 |                  0 |  0.439117    | 0.658699  |  0.366053   | -0.740062   | 1.91567  |
| internal_geo_array            | tnbc_stemness_persister         | 396 |                  0 |  0.340018    | 0.52004   |  0.337514   | -0.704476   | 1.38365  |
| internal_geo_array            | tnbc_persister_tumor_refined    | 396 |                  0 |  0.112212    | 0.357324  |  0.110629   | -0.617266   | 0.835003 |
| internal_geo_array            | tnbc_persister_stress_tolerance | 396 |                  0 |  0.0609715   | 0.443729  |  0.0377113  | -0.71429    | 0.869522 |
| internal_geo_array            | tnbc_persister_niche            | 396 |                  0 |  0.00459536  | 0.689561  | -0.093281   | -1.13656    | 1.53871  |
| internal_geo_array            | epithelial_fraction_estimate    | 396 |                  0 |  0.224362    | 0.171539  |  0.188269   |  0.00633781 | 0.659917 |
| internal_geo_array            | hybrid_fraction_estimate        | 396 |                  0 |  0.1571      | 0.0821119 |  0.151773   |  0.0281926  | 0.342478 |
| internal_geo_array            | mesenchymal_fraction_estimate   | 396 |                  0 |  0.316982    | 0.20705   |  0.275929   |  0.0410011  | 0.797534 |
| internal_geo_array            | persister_fraction_estimate     | 396 |                  0 |  0.301556    | 0.150305  |  0.277595   |  0.0762188  | 0.656051 |
| internal_geo_array            | plasticity_index                | 396 |                  0 |  0.458656    | 0.153446  |  0.469983   |  0.169603   | 0.779376 |
| internal_geo_array            | resistant_fraction_estimate     | 396 |                  0 |  0.775638    | 0.171539  |  0.811731   |  0.340083   | 0.993662 |
| internal_geo_array            | therapy_selection_pressure      | 396 |                  0 |  0.620784    | 0.135613  |  0.615583   |  0.350248   | 0.847671 |
| external_gse163882_rnaseq_tpm | epithelial                      |  90 |                  0 | -1.18424e-16 | 0.70002   |  0.057983   | -1.71363    | 1.19358  |
| external_gse163882_rnaseq_tpm | mesenchymal                     |  90 |                  0 |  4.44089e-17 | 0.686393  |  0.031488   | -1.36531    | 1.21142  |
| external_gse163882_rnaseq_tpm | emt_score                       |  90 |                  0 |  1.48647e-16 | 0.780529  | -0.00570917 | -1.45665    | 1.4955   |
| external_gse163882_rnaseq_tpm | partial_emt_score               |  90 |                  0 | -0.299201    | 0.638024  | -0.165492   | -1.71804    | 0.695482 |
| external_gse163882_rnaseq_tpm | stromal_fibroblast              |  90 |                  0 |  2.3253e-16  | 0.848419  |  0.0717356  | -2.01677    | 1.47337  |
| external_gse163882_rnaseq_tpm | caf                             |  90 |                  0 |  2.08167e-16 | 0.836745  |  0.0284997  | -1.78874    | 1.53438  |
| external_gse163882_rnaseq_tpm | immune_total                    |  90 |                  0 | -4.93432e-18 | 0.784098  | -0.0573922  | -1.46347    | 1.60891  |
| external_gse163882_rnaseq_tpm | tam_spp1                        |  90 |                  0 |  3.70074e-17 | 0.706715  |  0.024184   | -1.31747    | 1.18114  |
| external_gse163882_rnaseq_tpm | hypoxia                         |  90 |                  0 | -1.40628e-16 | 0.744584  |  0.00993431 | -1.27391    | 1.33999  |
| external_gse163882_rnaseq_tpm | tnbc_axl_tam                    |  90 |                  0 | -1.06088e-16 | 0.670597  |  0.0769362  | -1.21319    | 1.16904  |
| external_gse163882_rnaseq_tpm | tnbc_tgfb                       |  90 |                  0 | -4.59509e-17 | 0.802562  |  0.184291   | -1.98154    | 0.963147 |
| external_gse163882_rnaseq_tpm | tnbc_yap_taz                    |  90 |                  0 |  9.83164e-16 | 0.933912  |  0.147851   | -2.11437    | 1.24601  |
| external_gse163882_rnaseq_tpm | tnbc_hypoxia                    |  90 |                  0 | -5.92119e-17 | 0.745249  |  0.0659488  | -1.20769    | 1.57197  |
| external_gse163882_rnaseq_tpm | tnbc_stemness_persister         |  90 |                  0 |  8.20331e-17 | 0.589528  | -0.0412495  | -1.0165     | 1.16628  |
| external_gse163882_rnaseq_tpm | tnbc_persister_tumor_refined    |  90 |                  0 |  2.09709e-16 | 0.684285  |  0.052865   | -1.49775    | 0.935431 |
| external_gse163882_rnaseq_tpm | tnbc_persister_stress_tolerance |  90 |                  0 |  1.33227e-16 | 0.784672  |  0.192549   | -2.01764    | 0.969714 |
| external_gse163882_rnaseq_tpm | tnbc_persister_niche            |  90 |                  0 | -3.57739e-17 | 0.715676  |  0.0912738  | -1.6094     | 1.14556  |
| external_gse163882_rnaseq_tpm | epithelial_fraction_estimate    |  90 |                  0 |  0.272538    | 0.184654  |  0.215973   |  0.0180847  | 0.725902 |
| external_gse163882_rnaseq_tpm | hybrid_fraction_estimate        |  90 |                  0 |  0.182473    | 0.0921593 |  0.179226   |  0.0205658  | 0.389756 |
| external_gse163882_rnaseq_tpm | mesenchymal_fraction_estimate   |  90 |                  0 |  0.282317    | 0.207095  |  0.210306   |  0.0301016  | 0.781712 |
| external_gse163882_rnaseq_tpm | persister_fraction_estimate     |  90 |                  0 |  0.262671    | 0.168969  |  0.239295   |  0.0397723  | 0.582864 |
| external_gse163882_rnaseq_tpm | plasticity_index                |  90 |                  0 |  0.445145    | 0.172537  |  0.439171   |  0.142635   | 0.750585 |
| external_gse163882_rnaseq_tpm | resistant_fraction_estimate     |  90 |                  0 |  0.727462    | 0.184654  |  0.784027   |  0.274098   | 0.981915 |
| external_gse163882_rnaseq_tpm | therapy_selection_pressure      |  90 |                  0 |  0.54254     | 0.200849  |  0.532534   |  0.173407   | 0.873725 |

## Internal Versus External Feature Shift

| feature                         |   internal_n |   external_n |   internal_mean |   external_mean |   mean_shift_external_minus_internal |   standardized_mean_shift |   internal_median |   external_median |   ks_statistic |   ks_pvalue |
|:--------------------------------|-------------:|-------------:|----------------:|----------------:|-------------------------------------:|--------------------------:|------------------:|------------------:|---------------:|------------:|
| tnbc_stemness_persister         |          396 |           90 |      0.340018   |     8.20331e-17 |                          -0.340018   |                -0.611685  |         0.337514  |       -0.0412495  |      0.3       | 2.46909e-06 |
| tnbc_hypoxia                    |          396 |           90 |      0.439117   |    -5.92119e-17 |                          -0.439117   |                -0.624361  |         0.366053  |        0.0659488  |      0.290909  | 5.60345e-06 |
| tnbc_yap_taz                    |          396 |           90 |      0.464076   |     9.83164e-16 |                          -0.464076   |                -0.586291  |         0.508592  |        0.147851   |      0.271212  | 3.01908e-05 |
| tnbc_tgfb                       |          396 |           90 |     -0.0438007  |    -4.59509e-17 |                           0.0438007  |                 0.0687756 |        -0.0669832 |        0.184291   |      0.257071  | 9.37115e-05 |
| therapy_selection_pressure      |          396 |           90 |      0.620784   |     0.54254     |                          -0.0782436  |                -0.456593  |         0.615583  |        0.532534   |      0.252525  | 0.000133065 |
| hypoxia                         |          396 |           90 |      0.35852    |    -1.40628e-16 |                          -0.35852    |                -0.524907  |         0.284309  |        0.00993431 |      0.231818  | 0.00060543  |
| tnbc_persister_stress_tolerance |          396 |           90 |      0.0609715  |     1.33227e-16 |                          -0.0609715  |                -0.0956536 |         0.0377113 |        0.192549   |      0.206566  | 0.00320666  |
| hybrid_fraction_estimate        |          396 |           90 |      0.1571     |     0.182473    |                           0.0253728  |                 0.290705  |         0.151773  |        0.179226   |      0.19798   | 0.00540459  |
| persister_fraction_estimate     |          396 |           90 |      0.301556   |     0.262671    |                          -0.0388844  |                -0.243165  |         0.277595  |        0.239295   |      0.195455  | 0.00627443  |
| partial_emt_score               |          396 |           90 |     -0.374938   |    -0.299201    |                           0.0757375  |                 0.136032  |        -0.34161   |       -0.165492   |      0.193434  | 0.00706016  |
| emt_score                       |          396 |           90 |      0.291038   |     1.48647e-16 |                          -0.291038   |                -0.351538  |         0.260344  |       -0.00570917 |      0.191414  | 0.00793438  |
| epithelial_fraction_estimate    |          396 |           90 |      0.224362   |     0.272538    |                           0.0481763  |                 0.270323  |         0.188269  |        0.215973   |      0.181818  | 0.0135816   |
| resistant_fraction_estimate     |          396 |           90 |      0.775638   |     0.727462    |                          -0.0481763  |                -0.270323  |         0.811731  |        0.784027   |      0.181818  | 0.0135816   |
| epithelial                      |          396 |           90 |     -0.156345   |    -1.18424e-16 |                           0.156345   |                 0.242891  |        -0.0809353 |        0.057983   |      0.169697  | 0.025731    |
| immune_total                    |          396 |           90 |      0.20154    |    -4.93432e-18 |                          -0.20154    |                -0.265682  |         0.187055  |       -0.0573922  |      0.163636  | 0.0348311   |
| mesenchymal                     |          396 |           90 |      0.134693   |     4.44089e-17 |                          -0.134693   |                -0.22517   |         0.0795455 |        0.031488   |      0.156061  | 0.050071    |
| tnbc_axl_tam                    |          396 |           90 |      0.139727   |    -1.06088e-16 |                          -0.139727   |                -0.231306  |         0.14468   |        0.0769362  |      0.154545  | 0.053729    |
| mesenchymal_fraction_estimate   |          396 |           90 |      0.316982   |     0.282317    |                          -0.0346647  |                -0.167404  |         0.275929  |        0.210306   |      0.134848  | 0.126187    |
| tnbc_persister_niche            |          396 |           90 |      0.00459536 |    -3.57739e-17 |                          -0.00459536 |                -0.0065392 |        -0.093281  |        0.0912738  |      0.134848  | 0.126187    |
| tnbc_persister_tumor_refined    |          396 |           90 |      0.112212   |     2.09709e-16 |                          -0.112212   |                -0.205568  |         0.110629  |        0.052865   |      0.127778  | 0.166622    |
| tam_spp1                        |          396 |           90 |      0.17951    |     3.70074e-17 |                          -0.17951    |                -0.262401  |         0.126774  |        0.024184   |      0.113131  | 0.282205    |
| stromal_fibroblast              |          396 |           90 |     -0.0292999  |     2.3253e-16  |                           0.0292999  |                 0.0355219 |        -0.0832052 |        0.0717356  |      0.10202   | 0.401871    |
| plasticity_index                |          396 |           90 |      0.458656   |     0.445145    |                          -0.0135116  |                -0.0827556 |         0.469983  |        0.439171   |      0.0944444 | 0.498674    |
| caf                             |          396 |           90 |     -0.0211889  |     2.08167e-16 |                           0.0211889  |                 0.0269454 |        -0.0873754 |        0.0284997  |      0.0868687 | 0.60464     |

## Plots

![Feature shifts](C:/Users/HP/OneDrive/Documents/AI in Cancer Drug Discovery/docs/tnbc_digital_twin_emt_plasticity/assets/platform_normalization/tnbc_platform_feature_shift_diagnostics.png)

![Response balance](C:/Users/HP/OneDrive/Documents/AI in Cancer Drug Discovery/docs/tnbc_digital_twin_emt_plasticity/assets/platform_normalization/gse163882_external_response_balance.png)

## Interpretation Rules

- Large standardized mean shifts or KS statistics indicate platform/cohort effects that can dominate response-model performance.
- Cross-platform external metrics should be interpreted only after reviewing these diagnostics.
- If shifts are large, prefer rank/percentile calibration, same-platform validation, or explicit batch correction before model claims.