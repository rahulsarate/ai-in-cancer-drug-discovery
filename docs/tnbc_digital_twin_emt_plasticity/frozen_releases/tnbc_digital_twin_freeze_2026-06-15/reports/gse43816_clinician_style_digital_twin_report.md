# Clinician-Style Digital Twin Report

## Case Context

- Dataset: `GSE43816` longitudinal TNBC neoadjuvant chemotherapy cohort.
- Patient pair: `6`.
- Pretreatment sample: `GSM1071662`.
- Post-treatment/surgery sample: `GSM1071663`.
- Use: research interpretation only, not a clinical treatment recommendation.

## Digital-Twin Readout

| Feature | Before | After | Change | Before pctile | After pctile | Cohort mean delta 95% CI |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| emt score | -1.739 | -1.142 | 0.597 | 7.1 | 14.3 | -1.096 to 0.304 |
| hybrid fraction estimate | 0.048 | 0.086 | 0.038 | 14.3 | 21.4 | -0.002 to 0.092 |
| mesenchymal fraction estimate | 0.010 | 0.023 | 0.013 | 7.1 | 14.3 | -0.167 to 0.042 |
| persister fraction estimate | 0.740 | 0.708 | -0.032 | 100.0 | 92.9 | -0.087 to 0.027 |
| plasticity index | 0.789 | 0.795 | 0.006 | 92.9 | 100.0 | -0.017 to 0.044 |
| therapy selection pressure | 0.324 | 0.374 | 0.051 | 7.1 | 21.4 | -0.047 to 0.063 |
| residual disease probability proxy | 0.567 | 0.601 | 0.034 | 14.3 | 35.7 | -0.035 to 0.025 |

## Resistance Axis

- Dominant pretreatment axis: `stemness_persister`.
- Dominant post-treatment axis: `stemness_persister`.
- Summary interpretation: this paired sample shows **increased post-therapy resistance pressure**.

## Practical Interpretation

- Plasticity index change: `0.006`.
- Therapy-selection-pressure change: `0.051`.
- Residual-disease-risk proxy change: `0.034`.
- If this were a prospective research case, the appropriate follow-up would be molecular review of the post-treatment residual compartment, not automatic therapy selection.

## Visual Summary

![Selected patient state fractions](C:/Users/HP/OneDrive/Documents/AI in Cancer Drug Discovery/docs/tnbc_digital_twin_emt_plasticity/assets/gse43816_longitudinal/gse43816_patient_6_state_fractions.png)

![Paired cohort shifts](C:/Users/HP/OneDrive/Documents/AI in Cancer Drug Discovery/docs/tnbc_digital_twin_emt_plasticity/assets/gse43816_longitudinal/gse43816_paired_feature_shifts.png)

## Limitations

- The cohort has only 7 paired patients.
- Percentiles are relative to the 14 available `GSE43816` samples, not a population reference range.
- Uncertainty intervals are bootstrap intervals around the cohort mean paired delta.
- GEO response labels are unavailable for this dataset, so this analysis measures therapy-induced plasticity, not pCR prediction.
- The digital-twin state fractions are expression-derived proxies and require calibration with larger longitudinal cohorts, pathology, and ideally single-cell/spatial data.