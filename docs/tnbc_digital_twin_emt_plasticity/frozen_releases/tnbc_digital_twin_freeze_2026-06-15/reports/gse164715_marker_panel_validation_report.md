# GSE164715 Targeted Marker-Panel Validation

## Purpose

Validate whether targeted annotations show expected marker-score enrichment. This is a directional marker-panel check, not a full single-cell atlas annotation.

- Direction-check pass rate: 1.000

## Annotation Marker Means

| targeted_annotation   |   angiogenesis |        caf |   ecm_remodeling |   epithelial |   immune_total |   mesenchymal |   stromal_fibroblast |   t_cell_cytotoxic |   tam_spp1 |   tnbc_persister_niche |   tnbc_persister_tumor_refined |
|:----------------------|---------------:|-----------:|-----------------:|-------------:|---------------:|--------------:|---------------------:|-------------------:|-----------:|-----------------------:|-------------------------------:|
| ambiguous_human       |     -0.054429  | -0.0571405 |     -0.0343341   |   -0.19637   |     -0.04962   |    -0.0689733 |           -0.0423816 |         -0.0388835 | -0.0754436 |             -0.0518545 |                     -0.141031  |
| endothelial_like      |      0.496414  | -0.0182341 |     -0.0421907   |   -0.0558036 |     -0.0438954 |    -0.0431813 |           -0.038903  |         -0.0334596 | -0.0516037 |              0.530986  |                     -0.0144263 |
| immune_like           |     -0.0746396 | -0.0593272 |     -0.000258021 |   -0.442099  |      0.560762  |     0.0703526 |           -0.0756778 |          0.398417  |  0.721425  |             -0.0838687 |                     -0.0810105 |
| malignant_like        |     -0.0325411 | -0.0358429 |     -0.0183336   |    0.31546   |     -0.047104  |     0.0547747 |           -0.0348663 |         -0.0294332 | -0.0518403 |             -0.0404604 |                      0.173028  |
| stromal_like          |     -0.0544031 |  0.412136  |      0.234543    |   -0.0693412 |     -0.050775  |     0.027902  |            0.385331  |         -0.036009  | -0.0600778 |             -0.0569416 |                     -0.0594755 |

## Direction Checks

| targeted_annotation   | expected_marker_score        |   annotation_mean |   other_annotations_mean |   marker_margin | passes_direction_check   |
|:----------------------|:-----------------------------|------------------:|-------------------------:|----------------:|:-------------------------|
| malignant_like        | epithelial                   |         0.31546   |              -0.190903   |       0.506364  | True                     |
| malignant_like        | mesenchymal                  |         0.0547747 |              -0.00347497 |       0.0582496 | True                     |
| malignant_like        | tnbc_persister_tumor_refined |         0.173028  |              -0.0739859  |       0.247014  | True                     |
| endothelial_like      | angiogenesis                 |         0.496414  |              -0.0540032  |       0.550417  | True                     |
| endothelial_like      | tnbc_persister_niche         |         0.530986  |              -0.0582813  |       0.589268  | True                     |
| stromal_like          | stromal_fibroblast           |         0.385331  |              -0.0479572  |       0.433288  | True                     |
| stromal_like          | caf                          |         0.412136  |              -0.0426362  |       0.454772  | True                     |
| stromal_like          | ecm_remodeling               |         0.234543  |              -0.0237791  |       0.258322  | True                     |
| immune_like           | immune_total                 |         0.560762  |              -0.0478486  |       0.608611  | True                     |
| immune_like           | t_cell_cytotoxic             |         0.398417  |              -0.0344463  |       0.432864  | True                     |
| immune_like           | tam_spp1                     |         0.721425  |              -0.0597413  |       0.781166  | True                     |

## Plot

![Marker validation heatmap](C:/Users/HP/OneDrive/Documents/AI in Cancer Drug Discovery/docs/tnbc_digital_twin_emt_plasticity/assets/gse164715_marker_validation/gse164715_marker_panel_heatmap.png)

## Interpretation

- Positive marker margins support the targeted annotation.
- Failed margins should trigger review before publication-grade single-cell claims.
- Ambiguous cells are expected to remain heterogeneous and are not forced into lineage claims.