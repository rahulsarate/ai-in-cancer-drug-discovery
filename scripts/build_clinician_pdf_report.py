from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages


ROOT = Path(__file__).resolve().parents[1]


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Build clinician-facing PDF report directly from atlas tables.")
    p.add_argument("--out", default="docs/pan_cancer_emt_state_atlas/clinician_pan_cancer_emt_state_atlas_report.pdf")
    return p


def read(path: str) -> pd.DataFrame:
    return pd.read_csv(ROOT / path, sep="\t", low_memory=False)


def add_text_page(pdf: PdfPages, title: str, bullets: list[str]) -> None:
    fig = plt.figure(figsize=(8.5, 11))
    fig.patch.set_facecolor("white")
    plt.axis("off")
    fig.text(0.08, 0.92, title, fontsize=20, weight="bold", color="#1F4E79")
    y = 0.84
    for bullet in bullets:
        fig.text(0.10, y, f"- {bullet}", fontsize=11, wrap=True)
        y -= 0.055
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


def add_table_page(pdf: PdfPages, title: str, frame: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(11, 8.5))
    ax.axis("off")
    ax.set_title(title, loc="left", fontsize=16, weight="bold", color="#1F4E79", pad=16)
    display = frame.copy()
    for col in display.columns:
        if pd.api.types.is_numeric_dtype(display[col]):
            display[col] = display[col].map(lambda value: "" if pd.isna(value) else f"{value:.3g}")
    table = ax.table(cellText=display.values, colLabels=display.columns, loc="center", cellLoc="left")
    table.auto_set_font_size(False)
    table.set_fontsize(7.5)
    table.scale(1, 1.35)
    for (row, _), cell in table.get_celld().items():
        if row == 0:
            cell.set_text_props(weight="bold", color="white")
            cell.set_facecolor("#1F4E79")
        else:
            cell.set_facecolor("#F7F9FB" if row % 2 == 0 else "white")
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    args = parser().parse_args()
    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    group = read("data/processed/pan_cancer_emt_state_atlas/cards/cancer_group_state_summary.tsv")
    clinical = read("data/processed/pan_cancer_emt_state_atlas/clinical/clinical_group_summary.tsv")
    targets = read("data/processed/pan_cancer_emt_state_atlas/lineage_targets/disease_target_recommendations_with_lineage_evidence.tsv")
    pathology = read("data/processed/pan_cancer_emt_state_atlas/pathology/pathology_review_queue.tsv")
    annotated = read("data/processed/pan_cancer_emt_state_atlas/annotated_single_cell/tumor_vs_stroma_emt_summary.tsv")
    with PdfPages(out) as pdf:
        add_text_page(
            pdf,
            "Pan-Cancer EMT State Atlas",
            [
                "Clinician-facing research summary. Not a treatment recommendation.",
                "Current build: EMT states, confidence, clinical screens, single-cell validation, spatial pathology queue, and target hypotheses.",
                "New validation milestone: first real 3CA annotated dataset imported for Head and Neck Cancer.",
                "Use boundary: all findings require independent validation and pathology review before clinical interpretation.",
            ],
        )
        add_table_page(pdf, "Disease-Group EMT Summary", group[["cancer_group", "sample_count", "mesenchymal_like_fraction", "stromal_dominant_fraction", "high_confidence_fraction"]].head(12))
        add_table_page(pdf, "Clinical Readiness", clinical[["cancer_group", "sample_count", "survival_events", "stage_available_fraction", "treatment_outcome_available_fraction", "stromal_warning_fraction"]].head(12))
        add_table_page(pdf, "Annotated Single-Cell Tumor vs Stroma", annotated.head(12))
        add_table_page(pdf, "Top Disease Target Hypotheses with Lineage Evidence", targets[["cancer_group", "target", "family", "disease_priority_score", "cell_lines", "lineage_evidence_note"]].head(24))
        add_table_page(pdf, "Spatial Pathology Review Queue", pathology[["run", "cancer_group", "pathology_priority_score", "review_focus", "minimum_review_regions"]].head(8))
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
