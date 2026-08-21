# EMT-ViSTA

EMT-ViSTA predicts research-grade virtual spatial maps of epithelial state,
mesenchymal state, partial EMT, CAF, TAM, hypoxia, ECM remodeling, and stromal
contamination risk from routine H&E images. It extends the spatial EMT niche
pipeline and preserves uncertainty and abstention in every inference output.

This is a hypothesis-generation and spatial-assay-triage workflow. It is not a
clinical diagnostic, a replacement for molecular assays, or proof of malignant
EMT.

## Design Documents

- [Detailed project plan](detailed_project_plan.md)
- [Student project report](student_project_report.md)
- [Interview and viva guide](interview_and_viva_guide.md)
- [Research article draft](research_article_draft.md)
- [Executed implementation report](implementation_report.md)
- `configs/emt_virtual_spatial_staining.yml`: real five-cohort configuration
- `src/emt_virtual_spatial_staining/`: reusable implementation

## Environment

The tested advanced environment uses Python 3.10:

```powershell
.venv-deconv\Scripts\python.exe -m pip install -e ".[dev,virtualstain,foundation]"
```

H-Optimus-0 is supported but requires accepted HuggingFace terms and an
`HF_TOKEN`. Phikon-v2 is the ungated pathology-foundation fallback. ResNet50 is
an ImageNet learned-image control, not a pathology foundation model.

## Run the MVP

```powershell
.venv-deconv\Scripts\python.exe scripts\run_emt_vista_pipeline.py `
  --config configs\emt_virtual_spatial_staining.yml `
  --backend handcrafted `
  --max-spots-per-dataset 512
```

Run encoder comparisons after the baseline:

```powershell
.venv-deconv\Scripts\python.exe scripts\run_emt_vista_pipeline.py `
  --backend resnet50 --max-spots-per-dataset 128

.venv-deconv\Scripts\python.exe scripts\run_emt_vista_pipeline.py `
  --backend phikon_v2 --max-spots-per-dataset 16
```

Use `h_optimus_0` only after the model terms have been accepted. The 1.1B model
is not practical for a full CPU run; use a CUDA environment for cohort-scale
extraction.

## Real-Data Split

- Train: public 10x breast and prostate examples.
- Validation: public 10x ovarian example.
- Held-out technical test: public 10x lung squamous and colorectal examples.

The split is at dataset/sample level. Spots from one sample are never divided
between training and test sets. These five public product datasets establish
technical feasibility; they are not sufficiently powered clinical cohorts.

## Main Outputs

- `virtual_stain_training_pairs.tsv`: paired coordinates, molecular labels,
  confidence tiers, splits, and source paths.
- `pathology_embeddings_<backend>.tsv`: aligned image representations.
- `emt_vista_predictions.tsv`: virtual stain scores, uncertainty, malignant
  gate, stromal-inflation risk, and abstention.
- `emt_vista_metrics.tsv`: patient/cohort-safe performance metrics.
- `emt_vista_partial_emt_safety.tsv`: partial-EMT precision, calibration, and
  stroma false-positive measurements.
- `emt_vista_go_no_go.tsv`: predefined release gates.
- `maps/*_he_overlay.png`: virtual stains over the actual aligned H&E image.
- `maps/*_hotspots.geojson`: reviewable high-priority coordinates.

Large local matrices, embeddings, and model files remain ignored by Git. Only
code, configuration, documentation, manifests, and small report summaries
belong in a public release.

## Interpretation Rule

A high virtual partial-EMT probability means that morphology resembles regions
where epithelial and mesenchymal programs co-occurred under the training label
definition. It does not prove gene expression. Review tumor probability,
stromal-inflation risk, uncertainty, tissue region, and orthogonal molecular or
pathology evidence before drawing a biological conclusion.

## Current Result

The first held-out lung and colorectal benchmark is an honest negative control.
The handcrafted model reached median test Spearman `0.014`; ResNet50 reached
`-0.086`. Neither passed the predefined molecular-performance gates, although
both passed the pure-stroma false-positive threshold. See the implementation
report for the complete gate table and readiness chart.
