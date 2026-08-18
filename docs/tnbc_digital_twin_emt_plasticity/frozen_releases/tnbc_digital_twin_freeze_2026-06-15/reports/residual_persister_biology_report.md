# Residual and Persister Biology Calibration Report

## GSE43502 Residual Chemoresistant TNBC

This cohort contains residual chemoresistant TNBC samples after neoadjuvant chemotherapy with recurrence/no-recurrence prognosis labels.

### Feature Differences

| feature                     |   recurrence_n |   no_recurrence_n |   recurrence_mean |   no_recurrence_mean |   delta_recurrence_minus_no_recurrence |   recurrence_median |   no_recurrence_median |   delta_mean_q025 |   delta_mean_q975 |   bootstrap_probability_delta_gt_0 |   bootstrap_probability_delta_lt_0 |   mannwhitney_p |
|:----------------------------|---------------:|------------------:|------------------:|---------------------:|---------------------------------------:|--------------------:|-----------------------:|------------------:|------------------:|-----------------------------------:|-----------------------------------:|----------------:|
| tnbc_axl_tam                |             16 |                 9 |        0.186689   |          -0.331891   |                             0.51858    |          0.291894   |              0.0782869 |       0.000297097 |         1.05327   |                             0.975  |                             0.025  |        0.119499 |
| tnbc_hypoxia                |             16 |                 9 |        0.151822   |          -0.269906   |                             0.421728   |          0.0777229  |             -0.217242  |       0.00243107  |         0.841233  |                             0.9758 |                             0.0242 |        0.183378 |
| tnbc_yap_taz                |             16 |                 9 |       -0.144732   |           0.257301   |                            -0.402033   |          0.0972364  |              0.163542  |      -0.833437    |        -0.0134439 |                             0.019  |                             0.981  |        0.20273  |
| partial_emt_score           |             16 |                 9 |       -0.267185   |          -0.360274   |                             0.0930884  |         -0.26529    |             -0.391077  |      -0.231652    |         0.408075  |                             0.7308 |                             0.2692 |        0.294935 |
| therapy_selection_pressure  |             16 |                 9 |        0.561919   |           0.532585   |                             0.0293338  |          0.56278    |              0.566271  |      -0.0914373   |         0.155114  |                             0.6714 |                             0.3286 |        0.630362 |
| emt_score                   |             16 |                 9 |       -0.0230738  |           0.0410201  |                            -0.0640939  |         -0.156542   |              0.0395534 |      -0.658831    |         0.545816  |                             0.4154 |                             0.5846 |        0.671125 |
| caf_tam_niche               |             16 |                 9 |        0.0924622  |          -0.164377   |                             0.256839   |         -0.0103778  |              0.165758  |      -0.269822    |         0.809168  |                             0.819  |                             0.181  |        0.755515 |
| resistant_fraction_estimate |             16 |                 9 |        0.696513   |           0.728843   |                            -0.0323304  |          0.789064   |              0.810088  |      -0.186413    |         0.134917  |                             0.3388 |                             0.6612 |        0.755515 |
| tnbc_tgfb                   |             16 |                 9 |        0.00159191 |          -0.00283006 |                             0.00442196 |          0.00176777 |              0.0993955 |      -0.287568    |         0.31929   |                             0.5142 |                             0.4858 |        0.798907 |
| plasticity_index            |             16 |                 9 |        0.423618   |           0.441486   |                            -0.0178675  |          0.379045   |              0.385046  |      -0.152299    |         0.112036  |                             0.408  |                             0.592  |        0.842929 |
| persister_fraction_estimate |             16 |                 9 |        0.23583    |           0.261537   |                            -0.0257076  |          0.217961   |              0.220171  |      -0.140956    |         0.0828743 |                             0.3288 |                             0.6712 |        0.887448 |
| tnbc_stemness_persister     |             16 |                 9 |        0.0116976  |          -0.0207957  |                             0.0324932  |         -0.0765513  |              0.0226039 |      -0.341119    |         0.415588  |                             0.5708 |                             0.4292 |        0.887448 |

Interpretation note: bootstrap intervals that cross zero should be treated as directionally suggestive only. This cohort has 16 recurrence and 9 no-recurrence samples.

### Dominant Resistance Axes

| prognosis     | dominant_resistance_axis   |   samples |
|:--------------|:---------------------------|----------:|
| no recurrence | axl_tam                    |         1 |
| no recurrence | caf_tam_niche              |         3 |
| no recurrence | tgfb                       |         1 |
| no recurrence | yap_taz                    |         4 |
| recurrence    | axl_tam                    |         4 |
| recurrence    | caf_tam_niche              |         1 |
| recurrence    | hypoxia                    |         6 |
| recurrence    | stemness_persister         |         2 |
| recurrence    | tgfb                       |         1 |
| recurrence    | yap_taz                    |         2 |

![GSE43502 recurrence boxplots](C:/Users/HP/OneDrive/Documents/AI in Cancer Drug Discovery/docs/tnbc_digital_twin_emt_plasticity/assets/residual_persister_biology/gse43502_recurrence_boxplots.png)

![GSE43502 axis counts](C:/Users/HP/OneDrive/Documents/AI in Cancer Drug Discovery/docs/tnbc_digital_twin_emt_plasticity/assets/residual_persister_biology/gse43502_resistance_axis_counts.png)

![GSE43502 bootstrap intervals](C:/Users/HP/OneDrive/Documents/AI in Cancer Drug Discovery/docs/tnbc_digital_twin_emt_plasticity/assets/residual_persister_biology/gse43502_recurrence_bootstrap_intervals.png)

## GSE164715 Persister Metadata

This cohort now has both metadata and a selected raw scRNA import in the local pipeline. The metadata table remains useful for tracking persister/residual/recurrent sample definitions.

| persister_stage   | treatment           |   samples |
|:------------------|:--------------------|----------:|
| chemonaive        | DMSO                |         1 |
| chemonaive        | nan                 |         3 |
| other             | 5FU                 |         7 |
| other             | 5FU_UNC             |         1 |
| other             | UNC                 |         1 |
| persister         | Capecitabine (5-FU) |         3 |
| recurrent         | Capecitabine (5-FU) |         1 |
| residual          | Capecitabine (5-FU) |         1 |
| resistant         | Capecitabine (5-FU) |         1 |

### Supplementary File Availability

| accession   | file_name                                   | url                                                                                                           | notes   |
|:------------|:--------------------------------------------|:--------------------------------------------------------------------------------------------------------------|:--------|
| GSE164715   | GSE164715_RAW.tar                           | https://ftp.ncbi.nlm.nih.gov/geo/series/GSE164nnn/GSE164715/suppl/GSE164715_RAW.tar                           |         |
| GSE164715   | GSE164715_metadata_scRNA_MM468.csv.gz       | https://ftp.ncbi.nlm.nih.gov/geo/series/GSE164nnn/GSE164715/suppl/GSE164715_metadata_scRNA_MM468.csv.gz       |         |
| GSE164715   | GSE164715_metadata_scRNA_PDX.csv.gz         | https://ftp.ncbi.nlm.nih.gov/geo/series/GSE164nnn/GSE164715/suppl/GSE164715_metadata_scRNA_PDX.csv.gz         |         |
| GSE164715   | GSE164715_metadata_scRNA_PDX_HBCx172.csv.gz | https://ftp.ncbi.nlm.nih.gov/geo/series/GSE164nnn/GSE164715/suppl/GSE164715_metadata_scRNA_PDX_HBCx172.csv.gz |         |
| GSE164715   | GSE164715_metadata_scRNA_PDX_HBCx39.csv.gz  | https://ftp.ncbi.nlm.nih.gov/geo/series/GSE164nnn/GSE164715/suppl/GSE164715_metadata_scRNA_PDX_HBCx39.csv.gz  |         |
| GSE164715   | filelist.txt                                | https://ftp.ncbi.nlm.nih.gov/geo/series/GSE164nnn/GSE164715/suppl/filelist.txt                                |         |

## How This Feeds the Digital Twin

- `GSE43502` can calibrate residual/recurrent risk axes after chemotherapy.
- `GSE164715` now supports persister-state marker refinement through the selected raw scRNA import, human/mouse filtering, and targeted annotation layers.
- Recurrence-associated axes should be used to adjust the `P` and therapy-selection-pressure priors, not to make treatment decisions.