from __future__ import annotations

from pathlib import Path

import pandas as pd

from .reports import table_to_markdown


COMPARTMENT_KEYWORDS = {
    "malignant": ["malignant", "tumor", "tumour", "cancer", "epithelial malignant", "carcinoma", "leukemia", "lymphoma", "melanoma"],
    "caf_stromal": ["caf", "fibroblast", "stromal", "myofibroblast", "stellate", "mesenchymal stromal"],
    "myeloid_tam": ["tam", "macrophage", "myeloid", "monocyte", "dendritic", "dc", "microglia"],
    "t_cell": ["t cell", "t-cell", "cd4", "cd8", "nk", "cytotoxic", "lymphocyte"],
    "b_cell": ["b cell", "b-cell", "plasma"],
    "endothelial": ["endothelial", "vascular", "pericyte"],
    "normal_epithelial": ["normal epithelial", "epithelial", "ductal", "acinar", "club", "basal"],
}

MALIGNANT_POSITIVE = {"malignant", "tumor", "tumour", "cancer", "true", "yes", "1", "aneuploid", "cnv_high"}
MALIGNANT_NEGATIVE = {"non-malignant", "nonmalignant", "normal", "false", "no", "0", "diploid", "cnv_low"}
CNV_COLUMNS = ["cnv_score", "copykat_score", "infercnv_score", "aneuploidy_score", "malignancy_score"]

SOURCE_REQUIREMENTS = [
    {
        "source": "TISCH2",
        "required_files": "cell metadata with cell type; expression matrix or gene-by-cell table",
        "best_use": "tumor microenvironment cell-type annotation, CAF/TAM separation, gene expression by cell type",
        "access_note": "Use TISCH2 dataset download page; import exported cell metadata and expression table.",
    },
    {
        "source": "3CA",
        "required_files": "curated cell annotations; malignant-cell labels; expression matrix or summarized gene table",
        "best_use": "curated malignant-cell and cancer-type single-cell validation",
        "access_note": "Use 3CA public download links and keep original dataset/cancer metadata.",
    },
    {
        "source": "HTAN",
        "required_files": "Level 3/4 single-cell or spatial-derived cell tables; Synapse/Gen3 selected files",
        "best_use": "matched human tumor atlas validation with clinical/spatial context",
        "access_note": "Export selected files from HTAN portal, then use Synapse or Gen3 credentials for download.",
    },
    {
        "source": "CancerSEA",
        "required_files": "CancerSEA PCG expression matrix",
        "best_use": "malignant/cancer-cell EMT functional validation",
        "access_note": "Already downloaded for the selected disease groups in this project.",
    },
]


def infer_compartment(row: pd.Series, cell_type_col: str = "cell_type", malignant_col: str = "malignant_status") -> str:
    malignant = str(row.get(malignant_col, "")).strip().lower()
    cell_type = str(row.get(cell_type_col, "")).strip().lower()
    if malignant in MALIGNANT_POSITIVE:
        return "malignant"
    if malignant in MALIGNANT_NEGATIVE and not cell_type:
        return "non_malignant_unknown"
    for compartment, keywords in COMPARTMENT_KEYWORDS.items():
        if any(keyword in cell_type for keyword in keywords):
            return compartment
    return "unknown"


def infer_malignancy_confidence(row: pd.Series, malignant_col: str = "malignant_status") -> str:
    malignant = str(row.get(malignant_col, "")).strip().lower()
    cnv_values = [pd.to_numeric(row.get(col), errors="coerce") for col in CNV_COLUMNS if col in row.index]
    cnv_values = [float(value) for value in cnv_values if pd.notna(value)]
    if malignant in MALIGNANT_POSITIVE and cnv_values:
        return "high_annotation_plus_cnv"
    if malignant in MALIGNANT_POSITIVE:
        return "medium_annotation_only"
    if cnv_values and max(cnv_values) >= 0.5:
        return "medium_cnv_only"
    if malignant in MALIGNANT_NEGATIVE:
        return "non_malignant_annotation"
    return "unknown"


def normalize_annotation_columns(
    scores: pd.DataFrame,
    dataset: str | None = None,
    source: str | None = None,
    cancer_group: str | None = None,
) -> pd.DataFrame:
    frame = scores.copy()
    rename_map = {}
    for candidate in ["cell", "cell_name", "barcode", "Cell", "CellID", "cell_id"]:
        if candidate in frame.columns and "sample_id" not in frame.columns:
            rename_map[candidate] = "sample_id"
    for candidate in ["annotation", "celltype", "cell_type_major", "major_cell_type", "CellType", "cell_type_annotation"]:
        if candidate in frame.columns and "cell_type" not in frame.columns:
            rename_map[candidate] = "cell_type"
    for candidate in ["malignancy", "is_malignant", "tumor_status", "malignant", "malignant_call", "cnv_call"]:
        if candidate in frame.columns and "malignant_status" not in frame.columns:
            rename_map[candidate] = "malignant_status"
    frame = frame.rename(columns=rename_map)
    if "sample_id" not in frame.columns:
        frame["sample_id"] = frame.index.astype(str)
    if "dataset" not in frame.columns:
        frame["dataset"] = dataset or "annotated_single_cell_export"
    if "source" not in frame.columns:
        frame["source"] = source or "user_export"
    if "cancer_group" not in frame.columns:
        frame["cancer_group"] = cancer_group or "Unknown"
    if "cell_type" not in frame.columns:
        frame["cell_type"] = ""
    if "malignant_status" not in frame.columns:
        frame["malignant_status"] = ""
    frame["cell_compartment"] = frame.apply(infer_compartment, axis=1)
    frame["malignancy_confidence"] = frame.apply(infer_malignancy_confidence, axis=1)
    return frame


def add_malignant_stromal_emt_calls(scores: pd.DataFrame, group_col: str = "dataset") -> pd.DataFrame:
    frame = scores.copy()
    if "emt_score" not in frame.columns:
        frame["emt_score"] = pd.NA
    if "stromal_fibroblast" not in frame.columns:
        frame["stromal_fibroblast"] = pd.NA
    if "caf_tam_niche" not in frame.columns:
        frame["caf_tam_niche"] = pd.NA
    frame["emt_score"] = pd.to_numeric(frame["emt_score"], errors="coerce")
    frame["stromal_fibroblast"] = pd.to_numeric(frame["stromal_fibroblast"], errors="coerce")
    frame["caf_tam_niche"] = pd.to_numeric(frame["caf_tam_niche"], errors="coerce")

    if group_col not in frame.columns:
        group_col = "source"
    frame["emt_high_annotated"] = False
    frame["stromal_high_annotated"] = False
    for _, idx in frame.groupby(group_col, dropna=False).groups.items():
        part = frame.loc[idx]
        emt_cut = part["emt_score"].quantile(0.75)
        stromal_cut = part["stromal_fibroblast"].quantile(0.75)
        frame.loc[idx, "emt_high_annotated"] = part["emt_score"] >= emt_cut
        frame.loc[idx, "stromal_high_annotated"] = part["stromal_fibroblast"] >= stromal_cut

    frame["tumor_intrinsic_emt_call"] = frame["cell_compartment"].eq("malignant") & frame["emt_high_annotated"]
    frame["caf_stromal_emt_call"] = frame["cell_compartment"].eq("caf_stromal") & frame["emt_high_annotated"]
    frame["tam_myeloid_emt_like_call"] = frame["cell_compartment"].eq("myeloid_tam") & frame["emt_high_annotated"]
    frame["caf_tam_context_emt_call"] = frame["cell_compartment"].isin(["caf_stromal", "myeloid_tam"]) & (
        frame["emt_high_annotated"] | (frame["caf_tam_niche"] >= frame["caf_tam_niche"].quantile(0.75))
    )
    frame["stromal_mimic_warning"] = frame["cell_compartment"].eq("caf_stromal") | (
        frame["stromal_high_annotated"] & ~frame["cell_compartment"].eq("malignant")
    )
    frame["emt_source_label"] = "not_emt_high"
    frame.loc[frame["tumor_intrinsic_emt_call"], "emt_source_label"] = "tumor_intrinsic_emt"
    frame.loc[frame["caf_stromal_emt_call"], "emt_source_label"] = "caf_stromal_emt"
    frame.loc[frame["tam_myeloid_emt_like_call"], "emt_source_label"] = "tam_myeloid_emt_like"
    frame.loc[frame["emt_high_annotated"] & frame["stromal_mimic_warning"], "emt_source_label"] = "stromal_mimic_or_mixed_emt"
    frame.loc[
        frame["emt_high_annotated"] & frame["cell_compartment"].isin(["myeloid_tam", "t_cell", "b_cell"]),
        "emt_source_label",
    ] = "immune_context_emt_like"
    return frame


def summarize_compartments(scores: pd.DataFrame) -> pd.DataFrame:
    group_cols = [col for col in ["source", "dataset", "cancer_group", "cell_compartment", "malignant_status"] if col in scores.columns]
    metrics = [col for col in ["emt_score", "partial_emt_score", "stromal_fibroblast", "caf_tam_niche", "hypoxia"] if col in scores.columns]
    if not group_cols:
        return pd.DataFrame()
    summary = (
        scores.groupby(group_cols, dropna=False)
        .agg(
            cells=("sample_id", "count"),
            emt_high_fraction=("emt_high_annotated", "mean"),
            tumor_intrinsic_emt_fraction=("tumor_intrinsic_emt_call", "mean"),
            caf_stromal_emt_fraction=("caf_stromal_emt_call", "mean"),
            tam_myeloid_emt_like_fraction=("tam_myeloid_emt_like_call", "mean"),
            caf_tam_context_emt_fraction=("caf_tam_context_emt_call", "mean"),
            stromal_mimic_warning_fraction=("stromal_mimic_warning", "mean"),
            **{f"{metric}_mean": (metric, "mean") for metric in metrics},
        )
        .reset_index()
        .sort_values(["cancer_group", "cells"], ascending=[True, False])
    )
    return summary


def summarize_tumor_vs_stroma(scores: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (source, group), part in scores.groupby(["source", "cancer_group"], dropna=False):
        malignant = part[part["cell_compartment"].eq("malignant")]
        stromal = part[part["cell_compartment"].eq("caf_stromal")]
        tam = part[part["cell_compartment"].eq("myeloid_tam")]
        datasets = (
            ";".join(sorted(part["dataset"].dropna().astype(str).replace("", pd.NA).dropna().unique()))
            if "dataset" in part.columns
            else ""
        )
        rows.append(
            {
                "source": source,
                "datasets": datasets,
                "cancer_group": group,
                "cells": len(part),
                "malignant_cells": len(malignant),
                "caf_stromal_cells": len(stromal),
                "tam_myeloid_cells": len(tam),
                "tumor_intrinsic_emt_cells": int(malignant["tumor_intrinsic_emt_call"].sum()) if not malignant.empty else 0,
                "caf_stromal_emt_cells": int(stromal["caf_stromal_emt_call"].sum()) if not stromal.empty else 0,
                "tam_myeloid_emt_like_cells": int(tam["tam_myeloid_emt_like_call"].sum()) if not tam.empty else 0,
                "malignant_emt_score_mean": malignant["emt_score"].mean() if not malignant.empty else pd.NA,
                "caf_stromal_emt_score_mean": stromal["emt_score"].mean() if not stromal.empty else pd.NA,
                "tam_myeloid_emt_score_mean": tam["emt_score"].mean() if not tam.empty else pd.NA,
                "malignant_vs_stromal_emt_delta": (
                    malignant["emt_score"].mean() - stromal["emt_score"].mean()
                    if not malignant.empty and not stromal.empty
                    else pd.NA
                ),
                "interpretation": _tumor_stroma_interpretation(malignant, stromal),
            }
        )
    return pd.DataFrame(rows).sort_values(["source", "cancer_group"]).reset_index(drop=True)


def source_requirements_table() -> pd.DataFrame:
    return pd.DataFrame(SOURCE_REQUIREMENTS)


def write_annotated_single_cell_report(
    compartment_summary: pd.DataFrame,
    tumor_vs_stroma: pd.DataFrame,
    source_requirements: pd.DataFrame,
    out_path: str | Path,
) -> Path:
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Annotated Single-Cell EMT Separation Layer",
        "",
        "This layer starts the explicit separation of malignant-cell EMT from CAF/stromal EMT and immune-context EMT-like signal.",
        "",
        "## Tumor versus Stroma Summary",
        "",
        table_to_markdown(tumor_vs_stroma),
        "",
        "## Compartment-Level EMT Summary",
        "",
        table_to_markdown(compartment_summary.head(80)),
        "",
        "## External Export Requirements",
        "",
        table_to_markdown(source_requirements),
        "",
        "## Interpretation Boundary",
        "",
        "The compartment calls are only as reliable as the source cell-type and malignancy annotations. CNV-based malignant-cell calls are preferred when available.",
    ]
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


def _tumor_stroma_interpretation(malignant: pd.DataFrame, stromal: pd.DataFrame) -> str:
    if malignant.empty and stromal.empty:
        return "no_malignant_or_stromal_cells_available"
    if malignant.empty:
        return "stromal_only_or_missing_malignant_annotation"
    if stromal.empty:
        return "malignant_available_no_caf_stromal_comparator"
    delta = malignant["emt_score"].mean() - stromal["emt_score"].mean()
    if pd.isna(delta):
        return "insufficient_emt_scores"
    if delta > 0.25:
        return "tumor_intrinsic_emt_enriched"
    if delta < -0.25:
        return "caf_stromal_emt_enriched"
    return "mixed_or_shared_emt_signal"
