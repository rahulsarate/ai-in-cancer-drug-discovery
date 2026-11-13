# GSE164715 Ambiguous-Compartment Review

## Decision Summary

The GSE164715 layer is suitable for targeted digital-twin refinement of malignant-like, stress-tolerant, endothelial, stromal, and immune/niche signals. It should not be described as a complete single-cell atlas or a definitive malignant-cell classifier.

Marker-panel direction checks passed `11` of `11` checks.

## Sample-Level Review

| model   | sample_name        | stage      | targeted_annotation   |   cells |   fraction | review_status                          |
|:--------|:-------------------|:-----------|:----------------------|--------:|-----------:|:---------------------------------------|
| HBCx172 | HBCx172_chemonaive | chemonaive | ambiguous_human       |     922 | 0.657163   | high_ambiguity_review_required         |
| HBCx172 | HBCx172_chemonaive | chemonaive | endothelial_like      |     116 | 0.08268    | supporting_context_only                |
| HBCx172 | HBCx172_chemonaive | chemonaive | immune_like           |      79 | 0.0563079  | supporting_context_only                |
| HBCx172 | HBCx172_chemonaive | chemonaive | malignant_like        |     217 | 0.154669   | supporting_context_only                |
| HBCx172 | HBCx172_chemonaive | chemonaive | stromal_like          |      69 | 0.0491803  | supporting_context_only                |
| HBCx172 | HBCx172_persister  | persister  | ambiguous_human       |     321 | 0.696312   | high_ambiguity_review_required         |
| HBCx172 | HBCx172_persister  | persister  | endothelial_like      |      48 | 0.104121   | niche_layer_interpretable              |
| HBCx172 | HBCx172_persister  | persister  | immune_like           |       4 | 0.00867679 | supporting_context_only                |
| HBCx172 | HBCx172_persister  | persister  | malignant_like        |      63 | 0.136659   | supporting_context_only                |
| HBCx172 | HBCx172_persister  | persister  | stromal_like          |      25 | 0.0542299  | supporting_context_only                |
| HBCx39  | HBCx39_chemonaive  | chemonaive | ambiguous_human       |    1331 | 0.362473   | moderate_ambiguity_report_with_caution |
| HBCx39  | HBCx39_chemonaive  | chemonaive | endothelial_like      |     188 | 0.0511983  | supporting_context_only                |
| HBCx39  | HBCx39_chemonaive  | chemonaive | immune_like           |     230 | 0.0626362  | supporting_context_only                |
| HBCx39  | HBCx39_chemonaive  | chemonaive | malignant_like        |    1331 | 0.362473   | malignant_layer_interpretable          |
| HBCx39  | HBCx39_chemonaive  | chemonaive | stromal_like          |     592 | 0.16122    | niche_layer_interpretable              |
| HBCx39  | HBCx39_persister   | persister  | ambiguous_human       |     869 | 0.358943   | moderate_ambiguity_report_with_caution |
| HBCx39  | HBCx39_persister   | persister  | endothelial_like      |     144 | 0.0594796  | supporting_context_only                |
| HBCx39  | HBCx39_persister   | persister  | immune_like           |     215 | 0.0888063  | supporting_context_only                |
| HBCx39  | HBCx39_persister   | persister  | malignant_like        |    1009 | 0.41677    | malignant_layer_interpretable          |
| HBCx39  | HBCx39_persister   | persister  | stromal_like          |     184 | 0.0760017  | supporting_context_only                |
| HBCx95  | HBCx95_chemonaive  | chemonaive | ambiguous_human       |    1093 | 0.31381    | moderate_ambiguity_report_with_caution |
| HBCx95  | HBCx95_chemonaive  | chemonaive | endothelial_like      |     334 | 0.0958943  | supporting_context_only                |
| HBCx95  | HBCx95_chemonaive  | chemonaive | immune_like           |     204 | 0.0585702  | supporting_context_only                |
| HBCx95  | HBCx95_chemonaive  | chemonaive | malignant_like        |    1534 | 0.440425   | malignant_layer_interpretable          |
| HBCx95  | HBCx95_chemonaive  | chemonaive | stromal_like          |     318 | 0.0913006  | supporting_context_only                |
| HBCx95  | HBCx95_persister   | persister  | ambiguous_human       |     250 | 0.462107   | moderate_ambiguity_report_with_caution |
| HBCx95  | HBCx95_persister   | persister  | endothelial_like      |      61 | 0.112754   | niche_layer_interpretable              |
| HBCx95  | HBCx95_persister   | persister  | immune_like           |      18 | 0.0332717  | supporting_context_only                |
| HBCx95  | HBCx95_persister   | persister  | malignant_like        |     134 | 0.247689   | supporting_context_only                |
| HBCx95  | HBCx95_persister   | persister  | stromal_like          |      78 | 0.144177   | niche_layer_interpretable              |
| HBCx95  | HBCx95_recurrent   | recurrent  | ambiguous_human       |    1616 | 0.328122   | moderate_ambiguity_report_with_caution |
| HBCx95  | HBCx95_recurrent   | recurrent  | endothelial_like      |     392 | 0.0795939  | supporting_context_only                |
| HBCx95  | HBCx95_recurrent   | recurrent  | immune_like           |     300 | 0.0609137  | supporting_context_only                |
| HBCx95  | HBCx95_recurrent   | recurrent  | malignant_like        |    2056 | 0.417462   | malignant_layer_interpretable          |
| HBCx95  | HBCx95_recurrent   | recurrent  | stromal_like          |     561 | 0.113909   | niche_layer_interpretable              |
| HBCx95  | HBCx95_residual    | residual   | ambiguous_human       |    1771 | 0.365985   | moderate_ambiguity_report_with_caution |
| HBCx95  | HBCx95_residual    | residual   | endothelial_like      |     476 | 0.0983674  | supporting_context_only                |
| HBCx95  | HBCx95_residual    | residual   | immune_like           |     276 | 0.0570366  | supporting_context_only                |
| HBCx95  | HBCx95_residual    | residual   | malignant_like        |    1960 | 0.405042   | malignant_layer_interpretable          |
| HBCx95  | HBCx95_residual    | residual   | stromal_like          |     356 | 0.0735689  | supporting_context_only                |
| HBCx95  | HBCx95_resistant   | resistant  | ambiguous_human       |    1518 | 0.304514   | moderate_ambiguity_report_with_caution |
| HBCx95  | HBCx95_resistant   | resistant  | endothelial_like      |     563 | 0.112939   | niche_layer_interpretable              |
| HBCx95  | HBCx95_resistant   | resistant  | immune_like           |     789 | 0.158275   | niche_layer_interpretable              |
| HBCx95  | HBCx95_resistant   | resistant  | malignant_like        |    1679 | 0.33681    | malignant_layer_interpretable          |
| HBCx95  | HBCx95_resistant   | resistant  | stromal_like          |     436 | 0.0874624  | supporting_context_only                |

## Ambiguous Sample/Stage Rows

| model   | sample_name        | stage      | targeted_annotation   |   cells |   fraction | review_status                          |
|:--------|:-------------------|:-----------|:----------------------|--------:|-----------:|:---------------------------------------|
| HBCx172 | HBCx172_chemonaive | chemonaive | ambiguous_human       |     922 |   0.657163 | high_ambiguity_review_required         |
| HBCx172 | HBCx172_persister  | persister  | ambiguous_human       |     321 |   0.696312 | high_ambiguity_review_required         |
| HBCx39  | HBCx39_chemonaive  | chemonaive | ambiguous_human       |    1331 |   0.362473 | moderate_ambiguity_report_with_caution |
| HBCx39  | HBCx39_persister   | persister  | ambiguous_human       |     869 |   0.358943 | moderate_ambiguity_report_with_caution |
| HBCx95  | HBCx95_chemonaive  | chemonaive | ambiguous_human       |    1093 |   0.31381  | moderate_ambiguity_report_with_caution |
| HBCx95  | HBCx95_persister   | persister  | ambiguous_human       |     250 |   0.462107 | moderate_ambiguity_report_with_caution |
| HBCx95  | HBCx95_recurrent   | recurrent  | ambiguous_human       |    1616 |   0.328122 | moderate_ambiguity_report_with_caution |
| HBCx95  | HBCx95_residual    | residual   | ambiguous_human       |    1771 |   0.365985 | moderate_ambiguity_report_with_caution |
| HBCx95  | HBCx95_resistant   | resistant  | ambiguous_human       |    1518 |   0.304514 | moderate_ambiguity_report_with_caution |

## Cluster-Level Review

| targeted_cluster   |   cells | models                | dominant_annotation   |   epithelial |   mesenchymal |   partial_emt_score |   tnbc_persister_tumor_refined |   tnbc_persister_stress_tolerance |   tnbc_persister_niche |   angiogenesis |   stromal_fibroblast |        caf |   ecm_remodeling |   immune_total |   t_cell_cytotoxic |   tam_spp1 |   tnbc_hypoxia |   tnbc_yap_taz |   malignant_like_score |   endothelial_like_score |   stromal_like_score |   immune_like_score | review_status                     |
|:-------------------|--------:|:----------------------|:----------------------|-------------:|--------------:|--------------------:|-------------------------------:|----------------------------------:|-----------------------:|---------------:|---------------------:|-----------:|-----------------:|---------------:|-------------------:|-----------:|---------------:|---------------:|-----------------------:|-------------------------:|---------------------:|--------------------:|:----------------------------------|
| cluster_1          |    9477 | HBCx172,HBCx39,HBCx95 | ambiguous_human       |   -0.395513  |    -0.132986  |          -0.452383  |                      -0.301705 |                        -0.39397   |             -0.110339  |     -0.108551  |           -0.0470038 | -0.103655  |      -0.0852605  |     -0.0474085 |        -0.0572119  | -0.0807404 |     -0.290032  |     -0.388983  |             -0.0444988 |               -0.080766  |           -0.0183651 |          0.00199445 | ambiguous_cluster_review_required |
| cluster_5          |     288 | HBCx172,HBCx39,HBCx95 | endothelial_like      |   -0.0401929 |     0.0568084 |          -0.211269  |                       0.01428  |                        -0.0100501 |              2.18228   |      1.71836   |           -0.0147603 |  0.207196  |       0.00620085 |      0.0589505 |         0.0217569  |  0.0829849 |      0.0769651 |     -0.0455712 |              0.284749  |                2.45879   |            0.303989  |          0.185523   | targeted_cluster_interpretable    |
| cluster_2          |     596 | HBCx39,HBCx95         | immune_like           |   -0.868299  |     0.703634  |          -0.868695  |                       0.145202 |                         0.327974  |             -0.0202535 |      0.0322085 |           -0.0761722 |  0.10817   |       0.285065   |      1.43175   |         0.597223   |  2.38701   |      0.396479  |     -0.50077   |              0.804798  |                0.0702372 |            0.440289  |          2.78583    | targeted_cluster_interpretable    |
| cluster_3          |      18 | HBCx95                | immune_like           |   -0.901399  |     0.186417  |          -0.901399  |                      -0.222907 |                        -0.591603  |             -0.136049  |     -0.147622  |           -0.101983  | -0.115996  |      -0.0866037  |      9.3449    |        11.6444     | -0.0305874 |     -0.407544  |     -0.510583  |              0.191969  |               -0.136049  |           -0.069259  |         12.2079     | targeted_cluster_interpretable    |
| cluster_0          |   16324 | HBCx172,HBCx39,HBCx95 | malignant_like        |    0.263295  |     0.0497002 |          -0.0123002 |                       0.169669 |                         0.217456  |              0.026594  |      0.0317698 |            0.0210368 |  0.0460149 |       0.0319407  |     -0.0362998 |        -0.00212039 | -0.0419584 |      0.152837  |      0.245979  |              0.383315  |                0.102577  |            0.143935  |          0.0510438  | targeted_cluster_interpretable    |
| cluster_4          |      27 | HBCx172,HBCx39,HBCx95 | stromal_like          |   -0.164793  |     0.367563  |          -0.295894  |                       0.109026 |                         0.0727966 |             -0.0892853 |     -0.0480429 |            5.68647   |  4.04217   |       4.31435    |      0.123629  |         0.185198   |  0.151799  |      0.0960861 |     -0.303552  |              0.532505  |               -0.0172852 |            6.85621   |          0.322278   | targeted_cluster_interpretable    |

## Ambiguous Clusters

| targeted_cluster   |   cells | models                | dominant_annotation   |   epithelial |   mesenchymal |   partial_emt_score |   tnbc_persister_tumor_refined |   tnbc_persister_stress_tolerance |   tnbc_persister_niche |   angiogenesis |   stromal_fibroblast |       caf |   ecm_remodeling |   immune_total |   t_cell_cytotoxic |   tam_spp1 |   tnbc_hypoxia |   tnbc_yap_taz |   malignant_like_score |   endothelial_like_score |   stromal_like_score |   immune_like_score | review_status                     |
|:-------------------|--------:|:----------------------|:----------------------|-------------:|--------------:|--------------------:|-------------------------------:|----------------------------------:|-----------------------:|---------------:|---------------------:|----------:|-----------------:|---------------:|-------------------:|-----------:|---------------:|---------------:|-----------------------:|-------------------------:|---------------------:|--------------------:|:----------------------------------|
| cluster_1          |    9477 | HBCx172,HBCx39,HBCx95 | ambiguous_human       |    -0.395513 |     -0.132986 |           -0.452383 |                      -0.301705 |                          -0.39397 |              -0.110339 |      -0.108551 |           -0.0470038 | -0.103655 |       -0.0852605 |     -0.0474085 |         -0.0572119 | -0.0807404 |      -0.290032 |      -0.388983 |             -0.0444988 |                -0.080766 |           -0.0183651 |          0.00199445 | ambiguous_cluster_review_required |

## Publication Rules

- Claim broad targeted compartments only: malignant-like, endothelial-like, stromal-like, immune-like, and ambiguous human.
- Treat `ambiguous_human` as unresolved human-dominant cells, not as a biological state.
- Do not infer exact malignant/stromal/endothelial lineage for high-ambiguity sample-stage rows.
- Emphasize that marker panels validate directionality, not full cell ontology.
- Use HBCx172 and HBCx95 persister/residual claims cautiously because ambiguous fractions are high in some stage rows.