# Why Stromal Correction Matters

Bulk tumor RNA-seq mixes malignant cells, fibroblasts, endothelial cells, immune cells, and normal tissue. Many mesenchymal genes used in EMT signatures are also highly expressed by fibroblasts and CAFs.

## Risk

A sample can look EMT-high because it contains many stromal cells, even if malignant cells are not truly undergoing EMT. This can lead to false target hypotheses.

## v1 strategy

The atlas reports:

- `emt_high`
- `stromal_high`
- `tumor_cell_emt_candidate`
- `stromal_inflated_emt_candidate`

This does not fully solve deconvolution, but it makes the confound visible.

## Recommended validation

Use single-cell datasets from CancerSEA, TISCH2, HTAN, or GEO to confirm whether target expression is present in malignant EMT-like cells rather than only CAFs or macrophages.

