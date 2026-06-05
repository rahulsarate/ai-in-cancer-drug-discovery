from __future__ import annotations

from pathlib import Path

import pandas as pd


def write_paper_figure_tables(
    scored: pd.DataFrame,
    edges: pd.DataFrame,
    predictions: pd.DataFrame,
    interpretation: dict[str, pd.DataFrame],
    out_dir: str | Path,
) -> None:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    scored.merge(predictions, on="spot_id", how="left").to_csv(out / "figure_1_spatial_emt_map.tsv", sep="\t", index=False)
    edges.to_csv(out / "figure_2_spatial_graph_edges.tsv", sep="\t", index=False)
    for name, table in interpretation.items():
        table.to_csv(out / f"figure_3_{name}.tsv", sep="\t", index=False)


def write_research_article_stub(out: str | Path) -> None:
    text = """# Spatial Graph Learning Reveals EMT-Permissive Tumor Niches

## Abstract

Epithelial-to-mesenchymal transition (EMT) is spatially patterned by tumor
microenvironment neighborhoods, including CAFs, TAMs, hypoxia, ECM remodeling,
and immune exclusion. We developed a spatial EMT niche graph workflow that
integrates spatial transcriptomics, EMT/TME scoring, typed spatial graphs,
weak-label-aware graph learning, and perturbation-based interpretability to map
EMT-permissive regions and prioritize targetable metastatic circuits.

## Introduction

Metastatic competence is not simply a cell-intrinsic transcriptional state.
Partial EMT tumor cells often appear near stromal, inflammatory, hypoxic, and
matrix-remodeling niches. Public spatial transcriptomics datasets now make it
possible to model these neighborhoods directly.

## Methods

Spatial expression matrices are standardized into spot-by-gene tables with
coordinate metadata. EMT, partial EMT, stromal, CAF/TAM, immune, hypoxia, and
ferroptosis programs are scored per spot. Weak EMT-niche labels are generated
from tumor-cell EMT candidates, partial EMT, and microenvironment context while
preserving stromal-contamination flags. Typed graphs connect spots by physical
proximity, hypoxia gradients, and ligand-receptor-like niche signals. A graph
message-passing baseline predicts EMT-niche probability and is evaluated using
held-out spots or leave-cohort-out validation.

## Results To Generate

1. Spatial maps of EMT, partial EMT, stromal-inflated EMT, and predicted EMT niches.
2. Edge-type summaries showing CAF/TAM, hypoxia, and spatial-neighborhood structure.
3. Graph model performance compared with non-spatial baselines.
4. Edge-ablation and feature-perturbation reports identifying niche drivers.
5. Targetable circuit hypotheses such as AXL/GAS6, TGF-beta/SMAD, YAP/TEAD, FAK/SRC/integrins, SPP1-integrin/CD44, CXCL12-CXCR4, CSF1-CSF1R, and HIF1A/CA9.

## Discussion

This project treats model outputs as hypothesis-generating maps rather than
clinical recommendations. The main limitations are weak labels, spot-level
mixtures, cross-cohort batch effects, and the need for expert pathology review.
Future versions should add cell-type deconvolution, pathology foundation model
embeddings, heterogeneous graph transformers, and external validation on HTAN,
HEST-1k, 10x Visium, and GEO cohorts.
"""
    path = Path(out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
