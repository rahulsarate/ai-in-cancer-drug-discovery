# TNBC NAC Response Label Audit

## Purpose

Create a reproducible audit table for response labels used in TNBC NAC modeling. This is not a substitute for manual curation, but it identifies evidence columns, confidence levels, and rows needing review.

## Summary

| dataset_id   | standard_response         | tnbc_confirmed_or_likely   | response_label_confidence   | audit_flag                                  |   samples |
|:-------------|:--------------------------|:---------------------------|:----------------------------|:--------------------------------------------|----------:|
| GSE163882    | pcr_or_good_response      | False                      | high                        | not_tnbc_likely                             |        42 |
| GSE163882    | pcr_or_good_response      | True                       | high                        | ok                                          |        38 |
| GSE163882    | residual_or_poor_response | False                      | high                        | not_tnbc_likely                             |        90 |
| GSE163882    | residual_or_poor_response | True                       | high                        | ok                                          |        52 |
| GSE18864     | pcr_or_good_response      | True                       | high                        | ok                                          |         8 |
| GSE18864     | residual_or_poor_response | True                       | high                        | ok                                          |        16 |
| GSE18864     | unknown                   | True                       | unlabeled                   | missing_standard_response                   |        60 |
| GSE25055     | pcr_or_good_response      | False                      | high                        | not_tnbc_likely                             |        19 |
| GSE25055     | pcr_or_good_response      | False                      | high                        | not_tnbc_likely;residual_text_but_pcr_label |        55 |
| GSE25055     | pcr_or_good_response      | True                       | high                        | ok                                          |        40 |
| GSE25055     | pcr_or_good_response      | True                       | high                        | residual_text_but_pcr_label                 |        13 |
| GSE25055     | residual_or_poor_response | False                      | high                        | not_tnbc_likely                             |       120 |
| GSE25055     | residual_or_poor_response | True                       | high                        | ok                                          |        63 |
| GSE25065     | pcr_or_good_response      | False                      | high                        | not_tnbc_likely                             |        26 |
| GSE25065     | pcr_or_good_response      | False                      | high                        | not_tnbc_likely;residual_text_but_pcr_label |        48 |
| GSE25065     | pcr_or_good_response      | True                       | high                        | ok                                          |        24 |
| GSE25065     | pcr_or_good_response      | True                       | high                        | residual_text_but_pcr_label                 |        22 |
| GSE25065     | residual_or_poor_response | False                      | high                        | not_tnbc_likely                             |        59 |
| GSE25065     | residual_or_poor_response | True                       | high                        | ok                                          |        19 |
| GSE45898     | pcr_or_good_response      | True                       | high                        | ok                                          |         2 |
| GSE45898     | residual_or_poor_response | True                       | high                        | ok                                          |         8 |

## Manual Curation Rules

- Keep `pCR` or RCB-0/I as `pcr_or_good_response`.
- Keep residual disease, non-pCR, RCB-II/III, poor/minor/no response as `residual_or_poor_response`.
- Miller-Payne grade 4-5 is currently treated as good response; grade 1-3 as poor response.
- Any row with an audit flag other than `ok` should be manually checked before manuscript claims.