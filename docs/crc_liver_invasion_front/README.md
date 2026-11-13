# CRC Liver-Metastasis Invasion-Front Model

This project builds heterogeneous spatial graphs around the interface between
colorectal cancer liver metastases and adjacent liver tissue. It is a research
hypothesis engine for studying malignant epithelial plasticity, partial EMT,
hepatocyte injury, macrophage/fibroblast niches, vessels, ECM and glycolytic
gradients.

## Quick Start

```powershell
$env:PYTHONPATH='src'
python scripts\run_crc_liver_invasion_front.py
streamlit run apps\crc_liver_invasion_front_app.py --server.port 8511
```

Large public files are cached under `data/raw/`. Reproducible tables and figures
are written to `data/processed/crc_liver_invasion_front_v1/`.

## Main Outputs

- `spatial_interface_scores.tsv.gz`: spot programs, compartments and distance bands.
- `heterogeneous_nodes.tsv.gz`: typed graph nodes.
- `heterogeneous_edges.tsv.gz`: spatial, contact, signalling and gradient edges.
- `interface_section_summary.tsv`: section-level interface audit.
- `front_vs_core_statistics.tsv`: descriptive tumour-front contrasts.
- `model_metrics.json`: leave-section-out and permutation metrics.
- `feature_group_ablation.tsv`: dependence on biological feature groups.
- `figures/`: interface maps, gradients and model interpretation.

## Interpretation Boundary

The inferred interface is a marker-plus-spatial weak label. It is not a
pathologist annotation. Growth-pattern labels ending in `_proxy` are hypotheses
for review. The model is not diagnostic, prognostic or therapeutic software.
