# Pancreatic cancer image analysis and EMT research

## Real-data pilot (new)

### Reports and GitHub contents

- [Real-data pilot presentation](../output/pdf/pancreatic_cancer_real_data_pilot.pdf)
- [Resources, efficiency and accuracy report](../output/pdf/pancreatic_project_resources_efficiency_accuracy.pdf)
- [Original project concept presentation](../output/pdf/pancreatic_cancer_project_presentation.pdf)
- [Measured pilot results](outputs/real_pilot/PILOT_REPORT.md)

The Git repository includes code, protocols, tests, the executed real-data result/audit snapshot, an image gallery and four representative tissue tiles plus two slide overviews. Large raw SVS/RNA downloads, all other derived tiles, synthetic model binaries and ZIP delivery packages remain local. Run the acquisition and analysis commands below to reproduce the complete 768-tile dataset. Rebuilding figures, benchmarks or presentations requires those full inputs; reviewing the saved reports and dashboard does not. The local full-data ZIP is a separate delivery artifact, not a Git-tracked dataset.

The project now includes a separate **TCGA-PAAD real public-data technical pilot**. See [pilot protocol](docs/PILOT_PROTOCOL.md) and [reporting crosswalk](docs/PILOT_REPORTING_CHECKLIST.md). The original synthetic demonstration below remains separate; it is not evidence for the real pilot.

```powershell
python -m pip install -r requirements-pilot.txt
python acquire_pilot.py
python run_real_pilot.py
python summarize_real_pilot.py
python -m pytest tests -q
python -m streamlit run pilot_app.py --server.address 127.0.0.1
```

The acquisition defaults to 24 real patients and approximately 3.55 GB of open GDC slides/RNA. It saves an immutable cohort plan before processing, verifies MD5/size and reuses verified files on rerun. Retain approximately 5 GB free for raw data, tiles and reports. Do not commit raw clinical research files to Git; the pilot data directory is ignored. If the GDC inventory changes, retain the existing plan or version a new cohort rather than silently changing this study. `--refresh` requeries metadata; it refuses to overwrite an existing different cohort plan.

`run_real_pilot.py` extracts physical-resolution-aware tissue tiles, preserves exact stage/edition, computes a clearly labeled exploratory bulk RNA composite and evaluates a fixed regression baseline with held-out source-site folds. It does not train a four-stage model when stage-count requirements fail, and it does not reuse the synthetic model. No clinical inference artifact is released. The real results dashboard is `pilot_app.py`; `app.py` is the original demonstration workbench.

Real outputs: `outputs/real_pilot/pilot_results.json`, patient/tile manifests, source TPM values, features, out-of-fold predictions, real-image gallery and evaluation figure. `summarize_real_pilot.py` creates `PILOT_REPORT.md` and a blank expert-review template without replacing completed reviews. Raw SVS/RNA files, GDC inventory, cohort plan and receipts are in `data/real_pilot/`; final images are in `thumbnails_srgb/` and `tiles_srgb/`. Use the tile manifest as the authoritative image list; earlier intermediate directories are not analysis inputs. The revised real-data presentation is in the workspace's `output/pdf/` folder. Preserve `outputs/real_pilot/environment_versions.txt` with each analysis.

The same-patient slide/RNA join does not establish the same tissue block. Tiles are not pathologist-confirmed tumor regions. This is a resource-bounded technical pilot, not a powered clinical study, a validated EMT assay or a treatment-response model. TCGA Research Network attribution is retained in the outputs.

To regenerate the real-data presentation after analysis, install `requirements-report.txt` and run `python create_pilot_presentation.py` (uses Windows Arial fonts). The packaged real-data pilot includes retained sRGB tissue tiles and thumbnails, audit manifests, results and presentation. Large source SVS/RNA files remain in the local workspace and are reproducible using the acquisition script; they are not duplicated into the ZIP.

---

## Original synthetic demonstration

A self-contained, runnable research project for pancreatic ductal adenocarcinoma (PDAC). Input: reviewed H&E pathology tiles from one patient. Outputs: stage-associated class votes, an assay-associated EMT estimate, quality checks, evaluation reports, and educational therapeutic discussion context. This is an interpretable image-feature/random-forest baseline, not a trained medical device or deep-learning foundation model.

**This original demonstration uses artificial data; no clinically validated weights are included.** The separate real TCGA pilot is described above. A single pathology image cannot establish full anatomical stage, resectability, or EMT progression. The synthetic demo verifies software only. It deliberately encodes artificial correlations and its metrics must never be reported as cancer detection performance.

## Run on Windows

Open PowerShell in this project directory. Python 3.11 or newer is recommended.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe make_demo.py
.\.venv\Scripts\python.exe pipeline.py train --manifest data/demo/manifest.csv --out outputs
.\.venv\Scripts\python.exe pipeline.py predict --model outputs/model.joblib --images data/demo/DEMO_0_000_0.png data/demo/DEMO_0_000_1.png
.\.venv\Scripts\python.exe -m pytest tests -q
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1
```

Linux/macOS: replace `.\.venv\Scripts\python.exe` with `.venv/bin/python`. Launch from this folder. The dashboard reads `outputs/model.joblib`; train into that directory to use it. Keep the interface local with deidentified images. Joblib uses pickle: load only model files you created or trust.

## Files and workflow

| File | Purpose |
|---|---|
| `pipeline.py` | Image QC, feature extraction, patient aggregation, training, evaluation, inference CLI |
| `make_demo.py` | 80 artificial patients, two tiles each; software testing only |
| `app.py` | Local upload, research report download, independent clinical-context panel |
| `context.py` | Source-linked educational discussion topics |
| `data/manifest_template.csv` | Required input schema |
| `docs/PROTOCOL.md` | Detailed research plan, endpoints, validation, milestones |
| `docs/MODEL_CARD.md` | Intended use, exclusions, risks, acceptance gates |
| `tests/test_pipeline.py` | Integration, patient leakage, QC and context checks |
| `outputs/metrics.json` | Held-out performance, patient split IDs, versions, seed, manifest hash |
| `outputs/model.joblib` | Local trained baseline and feature schema |
| `outputs/prediction.json` | Patient-level inference report |

## Supply real data

Copy the template, adding one row per tile. Paths are relative to the manifest file. Example (illustrative values only):

```csv
patient_id,image_path,stage,emt_score,emt_assay,site_id
P001,tiles/P001_01.png,II,0.42,validated_panel_v1,SITE_A
P001,tiles/P001_02.png,II,0.42,validated_panel_v1,SITE_A
```

All patient rows must agree on labels and site. Provide stages I/II/III/IV only after confirmed PDAC diagnosis; stage 0 and non-PDAC disease are outside scope. EMT labels must use one documented, harmonized assay definition on [0,1]; there is no universal biological EMT percentage. Image features are averaged across each patient's tiles before splitting or fitting. Use a single pretreatment specimen/timepoint per patient; repeat biopsies need a longitudinal protocol. Exact cross-patient duplicate image bytes are rejected. Near duplicates and mislabeled patients still need manual/data-governance checks.

Train with `python pipeline.py train --manifest data/real_manifest.csv --out outputs`. The CLI requires at least ten patients per class solely to make stratified 60/20/20 splitting feasible. This is not an adequate clinical sample-size recommendation. No missing labels are imputed. All enrolled cases must have both endpoints; document selection bias from this complete-case design.

## Interpretation

`stage_association` is a research association with supplied labels, not clinical stage. Votes are uncalibrated random-forest outputs. `emt_assay_association` is a cross-sectional predicted assay score, not an EMT rate or progression. `outside_training_feature_range` is a crude warning, not a validated out-of-distribution detector. All outputs require research review even if this flag is false. The model does not identify cancer versus benign tissue: only confirmed PDAC cases are eligible.

Treatment context uses clinician-entered resectability only. It does not use image predictions, offer doses, rank drugs, or infer response. Clinical staging needs imaging/pathology and TNM information; therapeutic planning also needs the patient's condition, goals and molecular assessment. See [NCI staging](https://www.cancer.gov/types/pancreatic/stages) and [NCI professional treatment summary](https://www.cancer.gov/types/pancreatic/hp/pancreatic-treatment-pdq). EMT definitions follow the [TEMTIA consensus](https://www.nature.com/articles/s41580-020-0237-9). Sources reviewed 13 November 2026.
