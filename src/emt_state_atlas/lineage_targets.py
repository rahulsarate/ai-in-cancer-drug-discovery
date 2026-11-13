from __future__ import annotations

from pathlib import Path

import pandas as pd

from .cancer_groups import REQUESTED_CANCER_GROUPS
from .reports import table_to_markdown


LINEAGE_TO_GROUP = {
    "Ovary/Fallopian Tube": "Ovarian Cancer",
    "Breast": "Breast Cancer",
    "Bowel": "Colon / Intestine Cancer",
    "Pancreas": "Pancreatic Cancer",
    "CNS/Brain": "Brain Tumors",
    "Prostate": "Prostate Cancer",
    "Skin": "Skin Cancer",
    "Lung": "Lung Cancer",
    "Esophagus/Stomach": "Oesophageal Cancer",
    "Myeloid": "Blood Tumors",
    "Lymphoid": "Blood Tumors",
    "Head and Neck": "Head and Neck Cancer",
}


def target_from_column(column: str) -> str:
    return str(column).split(" (", 1)[0].split("|", 1)[0].upper()


def add_model_cancer_groups(models: pd.DataFrame) -> pd.DataFrame:
    out = models.copy()
    out["cancer_group"] = "Other / Not Requested"
    for source_col in ["OncotreeLineage", "OncotreePrimaryDisease", "SampleCollectionSite", "CCLEName"]:
        if source_col not in out.columns:
            continue
        text = out[source_col].fillna("").astype(str)
        for key, group in LINEAGE_TO_GROUP.items():
            out.loc[text.str.contains(key, case=False, regex=False), "cancer_group"] = group
    return out


def summarize_depmap_by_cancer_group(gene_effect: pd.DataFrame, models: pd.DataFrame) -> pd.DataFrame:
    id_col = gene_effect.columns[0]
    effects = gene_effect.rename(columns={id_col: "ModelID"}).copy()
    effects["ModelID"] = effects["ModelID"].astype(str)
    model_groups = add_model_cancer_groups(models)
    merged = effects.merge(model_groups[["ModelID", "CellLineName", "OncotreeLineage", "OncotreePrimaryDisease", "cancer_group"]], on="ModelID", how="left")
    target_cols = [col for col in merged.columns if col not in {"ModelID", "CellLineName", "OncotreeLineage", "OncotreePrimaryDisease", "cancer_group"}]
    rows = []
    for group in REQUESTED_CANCER_GROUPS:
        part = merged[merged["cancer_group"].eq(group)]
        for col in target_cols:
            values = pd.to_numeric(part[col], errors="coerce").dropna()
            if values.empty:
                continue
            rows.append(
                {
                    "cancer_group": group,
                    "target": target_from_column(col),
                    "cell_lines": int(values.shape[0]),
                    "mean_gene_effect": float(values.mean()),
                    "median_gene_effect": float(values.median()),
                    "dependency_fraction_lt_minus_0_5": float((values < -0.5).mean()),
                    "strong_dependency_fraction_lt_minus_1": float((values < -1.0).mean()),
                }
            )
    return pd.DataFrame(rows).sort_values(["cancer_group", "dependency_fraction_lt_minus_0_5", "mean_gene_effect"], ascending=[True, False, True])


def merge_lineage_targets(disease_targets: pd.DataFrame, depmap_summary: pd.DataFrame) -> pd.DataFrame:
    if disease_targets.empty or depmap_summary.empty:
        return disease_targets
    merged = disease_targets.merge(depmap_summary, on=["cancer_group", "target"], how="left")
    merged["lineage_evidence_note"] = merged.apply(_lineage_note, axis=1)
    return merged


def write_lineage_target_report(depmap_summary: pd.DataFrame, merged_targets: pd.DataFrame, out_path: str | Path) -> Path:
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Cancer-Lineage Target Evidence",
        "",
        "This layer joins DepMap model lineage annotations to EMT target evidence so disease-group target cards can show cell-line dependency context.",
        "",
        "## DepMap Lineage Dependency Summary",
        "",
        table_to_markdown(depmap_summary.head(80)),
        "",
        "## Disease-Group Target Recommendations with Lineage Evidence",
        "",
        table_to_markdown(merged_targets.head(80)),
    ]
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


def _lineage_note(row: pd.Series) -> str:
    if pd.isna(row.get("cell_lines")):
        return "no_matching_depmap_lineage_models"
    if row.get("dependency_fraction_lt_minus_0_5", 0) >= 0.25:
        return "lineage_dependency_supported"
    if row.get("cell_lines", 0) < 5:
        return "few_matching_cell_lines"
    return "lineage_dependency_limited_or_context_specific"
