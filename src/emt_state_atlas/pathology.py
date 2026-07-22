from __future__ import annotations

from pathlib import Path

import pandas as pd

from .reports import table_to_markdown


REVIEW_FEATURES = [
    {
        "review_feature": "invasive_edge",
        "pathology_question": "Is the EMT-high region at an invasive front or tumor-stroma boundary?",
        "required_marker_or_context": "H&E region annotation; epithelial/tumor boundary; VIM/CDH1/KRT panel if available",
    },
    {
        "review_feature": "caf_stromal_interface",
        "pathology_question": "Is EMT signal dominated by CAF/desmoplastic stroma rather than malignant tumor cells?",
        "required_marker_or_context": "COL1A1/COL1A2/DCN/LUM/ACTA2/FAP markers and H&E stroma score",
    },
    {
        "review_feature": "tam_neighborhood",
        "pathology_question": "Are EMT-high regions adjacent to macrophage/TAM-rich neighborhoods?",
        "required_marker_or_context": "CD68/CD163/SPP1/TREM2 or equivalent macrophage markers",
    },
    {
        "review_feature": "hypoxia_necrosis",
        "pathology_question": "Does EMT signal co-localize with hypoxia, necrosis, or poor perfusion?",
        "required_marker_or_context": "CA9/SLC2A1/LDHA signatures; necrosis/hypoxia region annotation",
    },
    {
        "review_feature": "tumor_intrinsic_emt",
        "pathology_question": "Do malignant epithelial cells themselves express EMT markers?",
        "required_marker_or_context": "EPCAM/KRT lineage markers plus VIM/ZEB1/SNAI2/AXL/ITGA5",
    },
]


def build_pathology_review_queue(spatial_run: pd.DataFrame, top_n: int = 80) -> pd.DataFrame:
    if spatial_run.empty:
        return pd.DataFrame()
    frame = spatial_run.copy()
    if "cancer_group" in frame.columns:
        frame = frame[~frame["cancer_group"].astype(str).str.contains("Demo|Synthetic", case=False, na=False)]
    if "run" in frame.columns:
        frame = frame[~frame["run"].astype(str).str.contains("synthetic|demo", case=False, na=False)]
    for col in [
        "emt_niche_fraction",
        "tumor_cell_emt_fraction",
        "stromal_inflated_fraction",
        "mean_hypoxia",
        "mean_caf_tam",
        "mean_predicted_emt_niche_probability",
        "spots",
    ]:
        if col in frame.columns:
            frame[col] = pd.to_numeric(frame[col], errors="coerce")
    frame["pathology_priority_score"] = (
        frame.get("emt_niche_fraction", 0).fillna(0) * 0.25
        + frame.get("tumor_cell_emt_fraction", 0).fillna(0) * 0.25
        + frame.get("stromal_inflated_fraction", 0).fillna(0) * 0.20
        + frame.get("mean_predicted_emt_niche_probability", 0).fillna(0) * 0.20
        + frame.get("mean_hypoxia", 0).fillna(0).clip(lower=0) * 0.10
    )
    frame["review_focus"] = frame.apply(_review_focus, axis=1)
    frame["review_status"] = "pending_pathologist_review"
    frame["minimum_review_regions"] = frame["spots"].fillna(0).map(lambda spots: 10 if spots >= 1000 else 5)
    cols = [
        col
        for col in [
            "run",
            "cancer_group",
            "spots",
            "pathology_priority_score",
            "review_focus",
            "review_status",
            "minimum_review_regions",
            "emt_niche_fraction",
            "tumor_cell_emt_fraction",
            "stromal_inflated_fraction",
            "mean_caf_tam",
            "mean_hypoxia",
            "mean_predicted_emt_niche_probability",
            "source_page",
        ]
        if col in frame.columns
    ]
    return frame.sort_values("pathology_priority_score", ascending=False)[cols].head(top_n).reset_index(drop=True)


def pathology_feature_checklist() -> pd.DataFrame:
    return pd.DataFrame(REVIEW_FEATURES)


def pathology_label_template(queue: pd.DataFrame) -> pd.DataFrame:
    if queue.empty:
        return pd.DataFrame()
    rows = []
    for _, row in queue.iterrows():
        for region_idx in range(1, int(row.get("minimum_review_regions", 5)) + 1):
            rows.append(
                {
                    "run": row.get("run"),
                    "cancer_group": row.get("cancer_group"),
                    "region_id": f"{row.get('run')}_region_{region_idx:02d}",
                    "reviewer_id": "",
                    "invasive_edge_label": "",
                    "caf_stromal_interface_label": "",
                    "tam_neighborhood_label": "",
                    "hypoxia_necrosis_label": "",
                    "tumor_intrinsic_emt_label": "",
                    "confidence_0_3": "",
                    "notes": "",
                }
            )
    return pd.DataFrame(rows)


def merge_pathology_labels(queue: pd.DataFrame, labels: pd.DataFrame) -> pd.DataFrame:
    if queue.empty or labels.empty or "run" not in labels.columns:
        return queue.copy()
    label_cols = [
        "invasive_edge_label",
        "caf_stromal_interface_label",
        "tam_neighborhood_label",
        "hypoxia_necrosis_label",
        "tumor_intrinsic_emt_label",
    ]
    available = [col for col in label_cols if col in labels.columns]
    if not available:
        return queue.copy()
    lab = labels.copy()
    for col in available:
        lab[col] = lab[col].astype(str).str.lower().isin(["1", "true", "yes", "present", "positive"])
    summary = lab.groupby("run", dropna=False).agg(reviewed_regions=("region_id", "count"), **{f"{col}_fraction": (col, "mean") for col in available}).reset_index()
    merged = queue.merge(summary, on="run", how="left")
    merged["review_status"] = merged["reviewed_regions"].fillna(0).map(lambda n: "expert_review_complete" if n > 0 else "pending_pathologist_review")
    return merged


def write_pathology_report(queue: pd.DataFrame, checklist: pd.DataFrame, out_path: str | Path) -> Path:
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# EMT Spatial Pathology Review Queue",
        "",
        "This queue turns spatial EMT niche outputs into reviewable pathology tasks for invasive edge, CAF/TAM, hypoxia, and tumor-intrinsic EMT validation.",
        "",
        "## Review Queue",
        "",
        table_to_markdown(queue),
        "",
        "## Review Checklist",
        "",
        table_to_markdown(checklist),
        "",
        "## Review Boundary",
        "",
        "This is a research review queue, not diagnostic sign-out. Final region labels require expert pathology review and documented criteria.",
    ]
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


def _review_focus(row: pd.Series) -> str:
    focus = []
    if row.get("tumor_cell_emt_fraction", 0) >= 0.10:
        focus.append("tumor_intrinsic_emt")
    if row.get("stromal_inflated_fraction", 0) >= 0.12:
        focus.append("caf_stromal_interface")
    if row.get("mean_caf_tam", 0) > 0:
        focus.append("tam_neighborhood")
    if row.get("mean_hypoxia", 0) > 0:
        focus.append("hypoxia_necrosis")
    if row.get("emt_niche_fraction", 0) >= 0.25:
        focus.append("invasive_edge")
    return ";".join(focus) if focus else "general_low_priority_review"
