from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, RGBColor


ROOT = Path(__file__).resolve().parents[1]


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Build polished clinician DOCX report for Pan-Cancer EMT State Atlas.")
    p.add_argument("--out", default="docs/pan_cancer_emt_state_atlas/clinician_pan_cancer_emt_state_atlas_report.docx")
    return p


def read(path: str) -> pd.DataFrame:
    return pd.read_csv(ROOT / path, sep="\t", low_memory=False)


def add_heading(doc: Document, text: str, level: int = 1) -> None:
    p = doc.add_heading(text, level=level)
    for run in p.runs:
        run.font.name = "Arial"
        run.font.color.rgb = RGBColor(31, 78, 121)


def add_table(doc: Document, frame: pd.DataFrame, widths: list[float] | None = None) -> None:
    frame = frame.copy()
    table = doc.add_table(rows=1, cols=len(frame.columns))
    table.style = "Table Grid"
    hdr = table.rows[0].cells
    for i, col in enumerate(frame.columns):
        hdr[i].text = str(col)
    for _, row in frame.iterrows():
        cells = table.add_row().cells
        for i, value in enumerate(row):
            cells[i].text = "" if pd.isna(value) else f"{value:.3g}" if isinstance(value, float) else str(value)
    if widths:
        for row in table.rows:
            for i, width in enumerate(widths[: len(row.cells)]):
                row.cells[i].width = Inches(width)
    doc.add_paragraph("")


def clean_label(value: object) -> str:
    text = "" if pd.isna(value) else str(value)
    return text.replace("_", " ").replace(";", ", ")


def emt_source_label(value: object) -> str:
    labels = {
        "caf_stromal_emt_enriched": "CAF/stromal enriched",
        "tumor_intrinsic_emt_enriched": "tumor-cell enriched",
        "mixed_or_shared_emt_signal": "mixed tumor/stroma",
        "malignant_available_no_caf_stromal_comparator": "tumor only comparator",
        "no_malignant_or_stromal_cells_available": "no tumor/stroma comparator",
    }
    return labels.get(str(value), clean_label(value))


def pathway_label(value: object) -> str:
    labels = {
        "AXL_TAM": "AXL/TAM axis",
        "FAK_SRC_integrin": "FAK/SRC-integrin",
        "TGF_beta_SMAD": "TGF-beta/SMAD",
        "hypoxia_metabolism": "hypoxia/metabolism",
    }
    return labels.get(str(value), clean_label(value))


def build_docx(out: Path) -> Path:
    group = read("data/processed/pan_cancer_emt_state_atlas/cards/cancer_group_state_summary.tsv")
    clinical = read("data/processed/pan_cancer_emt_state_atlas/clinical/clinical_group_summary.tsv")
    warnings = read("data/processed/pan_cancer_emt_state_atlas/clinical/clinical_warnings.tsv")
    targets = read("data/processed/pan_cancer_emt_state_atlas/cards/target_disease_group_recommendations.tsv")
    pathology = read("data/processed/pan_cancer_emt_state_atlas/pathology/pathology_review_queue.tsv")

    doc = Document()
    section = doc.sections[0]
    section.top_margin = section.bottom_margin = section.left_margin = section.right_margin = Inches(0.75)
    styles = doc.styles
    styles["Normal"].font.name = "Arial"
    styles["Normal"].font.size = Pt(10)

    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run("Pan-Cancer EMT State Atlas")
    run.bold = True
    run.font.name = "Arial"
    run.font.size = Pt(22)
    run.font.color.rgb = RGBColor(31, 78, 121)
    subtitle = doc.add_paragraph("Clinician-facing research summary. Not a treatment recommendation.")
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER

    add_heading(doc, "Executive Snapshot")
    p = doc.add_paragraph()
    p.add_run("Current status: ").bold = True
    p.add_run("The atlas is approximately 94% complete. It supports disease-group EMT state review, clinical association screening, CancerSEA validation, multi-cancer 3CA annotated single-cell separation, spatial/pathology review queues, and target hypothesis prioritization.")
    doc.add_paragraph("Use boundary: all outputs are research hypotheses requiring independent validation, clinical covariates, and pathology review before clinical interpretation.")

    add_heading(doc, "Disease-Group EMT Summary")
    display = group[["cancer_group", "sample_count", "mesenchymal_like_fraction", "stromal_dominant_fraction", "high_confidence_fraction"]].head(12)
    display.columns = ["Cancer group", "Samples", "Mesenchymal", "Stromal warning", "High confidence"]
    add_table(doc, display, widths=[1.7, 0.8, 1.1, 1.2, 1.2])

    add_heading(doc, "Clinical Readiness")
    clinical_display = clinical[["cancer_group", "sample_count", "survival_events", "event_fraction", "stage_available_fraction", "stromal_warning_fraction"]].head(12)
    clinical_display.columns = ["Cancer group", "Samples", "Events", "Event fraction", "Stage available", "Stromal warning"]
    add_table(doc, clinical_display, widths=[1.55, 0.75, 0.75, 1.05, 1.05, 1.05])
    warning_display = warnings.head(12).copy()
    warning_display.columns = ["Cancer group", "Model warning"]
    warning_display["Model warning"] = warning_display["Model warning"].map(clean_label)
    add_table(doc, warning_display, widths=[2.1, 4.1])

    annotated_path = ROOT / "data/processed/pan_cancer_emt_state_atlas/annotated_single_cell/tumor_vs_stroma_emt_summary.tsv"
    if annotated_path.exists():
        annotated = read("data/processed/pan_cancer_emt_state_atlas/annotated_single_cell/tumor_vs_stroma_emt_summary.tsv")
        annotated_display = annotated[annotated["source"].eq("3CA")][
            ["datasets", "cancer_group", "cells", "malignant_cells", "caf_stromal_cells", "tam_myeloid_cells", "interpretation"]
        ].head(12)
        annotated_display.columns = ["Dataset", "Cancer", "Cells", "Malignant", "CAF/stroma", "TAM/myeloid", "EMT source"]
        annotated_display["EMT source"] = annotated_display["EMT source"].map(emt_source_label)
        add_heading(doc, "Annotated Single-Cell EMT Source Separation")
        add_table(doc, annotated_display, widths=[1.4, 1.4, 0.65, 0.75, 0.75, 0.8, 1.2])

    add_heading(doc, "Top Target Hypotheses")
    target_display = (
        targets.sort_values(["cancer_group", "disease_priority_score"], ascending=[True, False])
        .groupby("cancer_group", dropna=False)
        .head(1)[["cancer_group", "target", "family", "disease_priority_score"]]
        .head(12)
        .copy()
    )
    target_display.columns = ["Cancer", "Target", "Pathway", "Score"]
    target_display["Pathway"] = target_display["Pathway"].map(pathway_label)
    add_table(doc, target_display, widths=[1.8, 0.85, 1.6, 0.75])

    add_heading(doc, "Spatial Pathology Review Priorities")
    path_display = pathology[["run", "cancer_group", "pathology_priority_score", "review_focus", "minimum_review_regions"]].head(8)
    path_display.columns = ["Cohort", "Cancer", "Priority", "Review focus", "Regions"]
    path_display["Review focus"] = path_display["Review focus"].map(clean_label)
    add_table(doc, path_display, widths=[1.55, 1.35, 0.75, 2.1, 0.7])

    add_heading(doc, "Next Actions")
    for item in [
        "Import the next TISCH2/HTAN annotated single-cell export after portal credentials or selected exports are available.",
        "Add CNV/malignancy calls where present to strengthen tumor-cell EMT confidence.",
        "Add treatment covariates and independent validation cohorts to clinical models.",
        "Collect expert pathology labels for invasive edge, CAF/TAM neighborhoods, and hypoxia/necrosis.",
        "Use researcher bundle for reproducible review of tables and model outputs.",
    ]:
        doc.add_paragraph(item, style="List Bullet")

    out.parent.mkdir(parents=True, exist_ok=True)
    doc.save(out)
    return out


def main() -> None:
    args = parser().parse_args()
    out = ROOT / args.out
    print(f"Wrote {build_docx(out)}")


if __name__ == "__main__":
    main()
