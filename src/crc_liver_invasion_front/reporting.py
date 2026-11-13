from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


def write_executed_report(
    output_path: str | Path,
    manifest: pd.DataFrame,
    interface_summary: pd.DataFrame,
    front_statistics: pd.DataFrame,
    importance: pd.DataFrame,
    metrics: dict[str, object],
) -> Path:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    liver = interface_summary[interface_summary["site"].eq("liver_metastasis")]
    top_programs = front_statistics.sort_values("front_minus_core", ascending=False).head(4)
    top_features = importance.head(6)
    report = f"""# CRC Liver-Metastasis Invasion-Front Model: Executed Report

## Executive Summary

This project constructs biologically typed spatial graphs around the colorectal
cancer-liver interface. It uses {int(manifest['spots_under_tissue'].sum()):,}
public Visium spots from {len(manifest)} sections in GSE225857, including
{int((manifest['site'] == 'liver_metastasis').sum())} liver-metastasis sections.
The interface labels are transparent marker-plus-spatial weak labels, not
pathologist ground truth.

The typed message-passing baseline achieved leave-one-liver-section-out ROC AUC
**{metrics['roc_auc']:.3f}** and average precision **{metrics['average_precision']:.3f}**.
Its within-section permutation P value was **{metrics['permutation_p']:.3f}**.
These values measure reproducibility across two public sections; they do not
establish clinical prediction or causal invasion biology.

## Executed Data

{manifest.to_markdown(index=False)}

An open 48-AOI GeoMx CTA table from four patients (Zenodo 7520789) was also
downloaded. It is retained as an orthogonal validation asset, but it was not
silently assigned tissue labels because the public count file lacks a
machine-readable AOI-to-primary/metastasis annotation.

## Study-Matched Single-Cell Reference

The GSE225857 processed single-cell tables yielded four author-annotated
pseudobulk references from 56,072 cells: 23,954 malignant, 15,093 fibroblast,
14,180 macrophage/myeloid and 2,845 endothelial cells. The metadata/count cell
identifier delimiter was harmonized before aggregation. Hepatocytes were absent
from the author-processed clusters and are reported as unavailable rather than
imputed into the matched reference.

## Interface Construction

The pipeline scores malignant CRC epithelium, partial EMT, hepatocytes,
MRC1/CCL18-like macrophages, activated fibroblasts, endothelial cells, damaged
hepatocytes, ECM remodelling, glycolysis and hypoxia. A spatial boundary is
defined only where high-confidence malignant and hepatocyte compartments touch.
Tumour and liver fronts extend three Visium hops, approximately 300 micrometres,
from that boundary.

{liver.to_markdown(index=False)}

The growth-pattern field is explicitly a proxy. Desmoplastic-like means a
fibroblast/ECM-rich separated interface; replacement-like means stronger direct
tumour-hepatocyte contact with hepatocyte injury. A pathologist must score H&E
sections using consensus HGP criteria before this field can become a reference
label.

## Front-versus-Core Findings

{top_programs.to_markdown(index=False)}

The full statistics table includes rank-biserial effect size, Mann-Whitney P
value and Benjamini-Hochberg FDR. Spot-level significance is descriptive because
spots from one section are not independent patients.

## Model Drivers

{top_features.to_markdown(index=False)}

Features include local programs and typed messages from spatial, compartment
contact, ligand-receptor and ECM/glycolysis-gradient edges. Coefficients indicate
predictive direction in this dataset, not drug targets or causal mechanisms.

## Novel Elements

1. A signed tumour-to-liver coordinate system rather than whole-slide averaging.
2. Separate malignant partial EMT and stromal-inflated EMT labels.
3. Heterogeneous nodes for malignant, hepatocyte, macrophage, fibroblast and
   endothelial compartments.
4. Directional ECM and glycolysis gradient edges.
5. Biologically named ligand-receptor edge families.
6. Leave-section-out validation, within-section permutation and feature-group
   ablation.
7. Pathology-inspired desmoplastic/replacement proxies with an explicit human
   review requirement.

## Supported Claims

- The public sections contain spatially coherent CRC, hepatocyte and niche
  programs that permit an automatically inferred interface.
- An interpretable multivariable graph-context signature can be tested for
  reproducibility between the two liver sections.
- The output produces experimentally testable hypotheses about partial EMT,
  macrophage, fibroblast, endothelial, ECM and metabolic gradients.

## Claims Not Supported

- The model does not predict survival, recurrence or treatment response.
- Weak interface labels are not equivalent to pathologist HGP annotations.
- Ligand-receptor co-expression does not prove signalling.
- Two liver sections are insufficient for a clinical or population-level claim.
- The project does not recommend treatment for any patient.

## Next Experimental Tests

1. Pathologist annotation of tumour boundary and HGP percentage on the H&E image.
2. Multiplex IF/IHC for EPCAM or KRT20, VIM/LAMC2, MRC1/CCL18, FAP/POSTN,
   CD31 and CA9/GLUT1 in the same 300 micrometre bands.
3. Spatial perturbation of CCL18-PITPNM3, SPP1-CD44/ITGAV, TGF-beta and
   CXCL12-CXCR4 axes in CRC liver organoid or precision-cut liver models.
4. Independent validation in PRJEB71493 or the 26-sample ISS CRLM cohort once
   processed matrices and region annotations can be redistributed.

## Reproducibility

Run `python scripts/run_crc_liver_invasion_front.py`. Large raw files remain in
`data/raw/`; derived tables, figures, metrics and this report are reproducible.
"""
    output.write_text(report, encoding="utf-8")
    return output


def write_machine_summary(metrics: dict[str, object], output_path: str | Path) -> Path:
    output = Path(output_path)
    output.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    return output
