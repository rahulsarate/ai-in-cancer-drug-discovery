from __future__ import annotations

from pathlib import Path

import pandas as pd

from .reports import table_to_markdown


SPATIAL_RUN_TO_GROUP = {
    "10x_breast_ffpe_idc": "Breast Cancer",
    "10x_lung_lusc_cytassist": "Lung Cancer",
    "geo_pdac_gse274103": "Pancreatic Cancer",
    "geo_met_pdac_gse274557_pt1": "Pancreatic Cancer",
    "geo_brain_met_gse179572": "Brain Tumors",
    "10x_prostate_ffpe": "Prostate Cancer",
    "10x_ovarian_ffpe": "Ovarian Cancer",
    "10x_colorectal_intestinal_ffpe": "Colon / Intestine Cancer",
    "synthetic_demo": "Demo / Synthetic",
}


TUMOR_INTRINSIC_MARKERS = [
    {"marker": "VIM", "role": "mesenchymal tumor-cell EMT", "interpretation": "Prioritize when expressed in malignant cells, not only fibroblasts."},
    {"marker": "CDH2", "role": "cadherin switch", "interpretation": "Supports EMT-like adhesion remodeling."},
    {"marker": "ZEB1", "role": "EMT transcription factor", "interpretation": "Useful tumor-intrinsic EMT regulator candidate."},
    {"marker": "ZEB2", "role": "EMT transcription factor", "interpretation": "Useful tumor-intrinsic EMT regulator candidate."},
    {"marker": "SNAI1", "role": "EMT transcription factor", "interpretation": "Often transient; validate with matched epithelial loss."},
    {"marker": "SNAI2", "role": "EMT transcription factor", "interpretation": "Often linked to partial/plastic EMT states."},
    {"marker": "TWIST1", "role": "invasion and plasticity", "interpretation": "Candidate for invasive-edge EMT validation."},
    {"marker": "AXL", "role": "therapy-tolerant EMT axis", "interpretation": "Connects EMT, TAM crosstalk, and drug-response hypotheses."},
    {"marker": "ITGA5", "role": "ECM adhesion", "interpretation": "Supports invasive matrix-interaction programs."},
    {"marker": "FN1", "role": "matrix and EMT", "interpretation": "Strong EMT marker but stromal contamination must be checked."},
    {"marker": "CDH1", "role": "epithelial control", "interpretation": "Loss or low signal supports EMT transition context."},
    {"marker": "EPCAM", "role": "epithelial/malignant control", "interpretation": "Helps distinguish malignant epithelial cells from stromal cells."},
    {"marker": "KRT8", "role": "epithelial lineage control", "interpretation": "Useful for tumor-lineage anchoring in carcinoma datasets."},
    {"marker": "KRT18", "role": "epithelial lineage control", "interpretation": "Useful for tumor-lineage anchoring in carcinoma datasets."},
    {"marker": "COL1A1", "role": "stromal caution marker", "interpretation": "High signal may indicate CAF/fibroblast EMT mimicry."},
    {"marker": "COL1A2", "role": "stromal caution marker", "interpretation": "High signal may indicate CAF/fibroblast EMT mimicry."},
    {"marker": "DCN", "role": "stromal caution marker", "interpretation": "Use to flag fibroblast-driven bulk EMT."},
    {"marker": "LUM", "role": "stromal caution marker", "interpretation": "Use to flag fibroblast-driven bulk EMT."},
    {"marker": "ACTA2", "role": "myofibroblast caution marker", "interpretation": "Supports CAF/myofibroblast context rather than tumor-cell EMT alone."},
    {"marker": "PTPRC", "role": "immune exclusion marker", "interpretation": "Use to rule out immune-cell expression effects."},
]


def aggregate_cancersea_validation(single_cell_summary: pd.DataFrame, bulk_group_summary: pd.DataFrame | None = None) -> pd.DataFrame:
    if single_cell_summary.empty or "cancer_group" not in single_cell_summary.columns:
        return pd.DataFrame()
    frame = single_cell_summary.copy()
    count_col = "emt_score_count"
    rows = []
    for group, part in frame.groupby("cancer_group", dropna=False):
        total = float(part[count_col].sum()) if count_col in part.columns else float(len(part))
        row = {
            "cancer_group": group,
            "cancersea_datasets": part["dataset"].nunique() if "dataset" in part.columns else len(part),
            "single_cells_or_profiles": int(total),
            "tumor_intrinsic_validation": "available",
            "validation_context": "CancerSEA malignant/cancer-cell expression profiles",
        }
        for col in [
            "emt_score_mean",
            "partial_emt_score_mean",
            "stromal_fibroblast_mean",
            "immune_total_mean",
            "caf_tam_niche_mean",
            "hypoxia_mean",
            "ferroptosis_window_mean",
        ]:
            if col in part.columns:
                weights = part[count_col] if count_col in part.columns else None
                row[f"single_cell_{col}"] = (part[col] * weights).sum() / weights.sum() if weights is not None else part[col].mean()
        rows.append(row)
    out = pd.DataFrame(rows)
    if bulk_group_summary is not None and not bulk_group_summary.empty and "cancer_group" in bulk_group_summary.columns:
        cols = [
            col
            for col in [
                "cancer_group",
                "sample_count",
                "emt_score_mean",
                "mesenchymal_like_fraction",
                "stromal_dominant_fraction",
                "high_confidence_fraction",
            ]
            if col in bulk_group_summary.columns
        ]
        out = out.merge(bulk_group_summary[cols], on="cancer_group", how="left", suffixes=("", "_bulk"))
    return out.sort_values(["single_cells_or_profiles", "cancer_group"], ascending=[False, True]).reset_index(drop=True)


def marker_table() -> pd.DataFrame:
    return pd.DataFrame(TUMOR_INTRINSIC_MARKERS)


def integrate_spatial_summary(spatial_summary: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    if spatial_summary.empty:
        return pd.DataFrame(), pd.DataFrame()
    run_level = spatial_summary.copy()
    run_level["cancer_group"] = run_level["run"].map(SPATIAL_RUN_TO_GROUP).fillna("Other / Unmapped")
    run_level["spatial_context"] = run_level.apply(_spatial_context_label, axis=1)
    group_level = (
        run_level[run_level["cancer_group"] != "Demo / Synthetic"]
        .groupby("cancer_group", dropna=False)
        .agg(
            spatial_cohorts=("run", "nunique"),
            total_spots=("spots", "sum"),
            mean_emt_niche_fraction=("emt_niche_fraction", "mean"),
            mean_tumor_cell_emt_fraction=("tumor_cell_emt_fraction", "mean"),
            mean_stromal_inflated_fraction=("stromal_inflated_fraction", "mean"),
            mean_caf_tam=("mean_caf_tam", "mean"),
            mean_hypoxia=("mean_hypoxia", "mean"),
            mean_predicted_emt_niche_probability=("mean_predicted_emt_niche_probability", "mean"),
            total_edges=("edges", "sum"),
        )
        .reset_index()
        .sort_values(["spatial_cohorts", "total_spots"], ascending=[False, False])
    )
    return run_level, group_level


def write_single_cell_report(
    validation: pd.DataFrame,
    markers: pd.DataFrame,
    manifest: pd.DataFrame,
    out_path: str | Path,
) -> Path:
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Pan-Cancer EMT Single-Cell Validation Layer",
        "",
        "CancerSEA datasets were scored as tumor-cell-oriented EMT validation resources for the requested cancer groups.",
        "",
        "## Disease-Group Validation Coverage",
        "",
        table_to_markdown(validation),
        "",
        "## Tumor-Intrinsic Marker Table",
        "",
        table_to_markdown(markers),
        "",
        "## Download Manifest",
        "",
        table_to_markdown(manifest),
        "",
        "## Boundary",
        "",
        "CancerSEA helps test malignant-cell EMT programs. Full malignant-versus-CAF/TAM separation still needs dedicated TISCH2, 3CA, HTAN, or matched single-cell annotations.",
    ]
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


def write_spatial_report(run_level: pd.DataFrame, group_level: pd.DataFrame, out_path: str | Path) -> Path:
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    display_run = run_level[
        [
            col
            for col in [
                "run",
                "cancer_group",
                "spots",
                "emt_niche_fraction",
                "tumor_cell_emt_fraction",
                "stromal_inflated_fraction",
                "mean_caf_tam",
                "mean_hypoxia",
                "mean_predicted_emt_niche_probability",
                "spatial_context",
                "source_page",
            ]
            if col in run_level.columns
        ]
    ]
    lines = [
        "# Pan-Cancer EMT Spatial and Pathology Layer",
        "",
        "Spatial cohorts are summarized as EMT niche, invasive-edge, CAF/TAM neighborhood, and hypoxia-context evidence.",
        "",
        "## Disease-Group Spatial Coverage",
        "",
        table_to_markdown(group_level),
        "",
        "## Spot/Region Cohort Cards",
        "",
        table_to_markdown(display_run),
        "",
        "## Interpretation Boundary",
        "",
        "Spatial EMT niche outputs support regional hypotheses. They still need pathologist review before clinical-grade statements about invasive edge or histologic patterning.",
    ]
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


def write_spatial_cards(run_level: pd.DataFrame, out_dir: str | Path) -> list[Path]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths = []
    for _, row in run_level.iterrows():
        name = str(row.get("run", "spatial_cohort"))
        path = out / f"{name}_spatial_card.md"
        lines = [
            f"# Spatial EMT Region Card: {name}",
            "",
            f"- Disease group: {row.get('cancer_group', 'unknown')}",
            f"- Spots/regions: {row.get('spots', 'not available')}",
            f"- EMT niche fraction: {row.get('emt_niche_fraction', 'not available')}",
            f"- Tumor-cell EMT fraction: {row.get('tumor_cell_emt_fraction', 'not available')}",
            f"- Stromal-inflated fraction: {row.get('stromal_inflated_fraction', 'not available')}",
            f"- CAF/TAM neighborhood score: {row.get('mean_caf_tam', 'not available')}",
            f"- Hypoxia score: {row.get('mean_hypoxia', 'not available')}",
            f"- Context label: {row.get('spatial_context', 'not available')}",
            "",
            "## Use",
            "",
            "Use this as a spatial hypothesis card for invasive-edge, stromal, immune, and hypoxia validation.",
        ]
        if pd.notna(row.get("source_page")):
            lines.extend(["", f"Source: {row.get('source_page')}"])
        path.write_text("\n".join(map(str, lines)) + "\n", encoding="utf-8")
        paths.append(path)
    return paths


def _spatial_context_label(row: pd.Series) -> str:
    labels = []
    if row.get("emt_niche_fraction", 0) >= 0.25:
        labels.append("invasive-edge EMT niche")
    if row.get("stromal_inflated_fraction", 0) >= 0.12:
        labels.append("CAF/stromal-rich EMT")
    if row.get("tumor_cell_emt_fraction", 0) >= 0.10:
        labels.append("tumor-cell EMT region")
    if row.get("mean_hypoxia", 0) > 0:
        labels.append("hypoxia-associated region")
    return "; ".join(labels) if labels else "low/neutral EMT niche signal"
