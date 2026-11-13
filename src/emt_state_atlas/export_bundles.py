from __future__ import annotations

import zipfile
from pathlib import Path

import pandas as pd


CLINICIAN_FILES = [
    "docs/pan_cancer_emt_state_atlas/work_done_and_remaining_status.md",
    "docs/pan_cancer_emt_state_atlas/project_questions_and_answers.md",
    "docs/pan_cancer_emt_state_atlas/project_highlights.png",
    "docs/pan_cancer_emt_state_atlas/clinician_pan_cancer_emt_state_atlas_report_v2.docx",
    "docs/pan_cancer_emt_state_atlas/clinician_pan_cancer_emt_state_atlas_report.pdf",
    "docs/pan_cancer_emt_state_atlas/pathology_review_handoff.md",
    "docs/pan_cancer_emt_state_atlas/reports/pan_cancer_emt_state_atlas_card_report.md",
    "docs/pan_cancer_emt_state_atlas/reports/pan_cancer_emt_clinical_report.md",
    "docs/pan_cancer_emt_state_atlas/reports/pan_cancer_emt_disease_group_target_report.md",
    "docs/pan_cancer_emt_state_atlas/reports/pan_cancer_emt_lineage_target_report.md",
    "docs/pan_cancer_emt_state_atlas/reports/pan_cancer_emt_validation_readiness_report.md",
    "data/processed/pan_cancer_emt_state_atlas/cards/cancer_group_state_summary.tsv",
    "data/processed/pan_cancer_emt_state_atlas/clinical/clinical_group_summary.tsv",
    "data/processed/pan_cancer_emt_state_atlas/clinical/clinical_warnings.tsv",
    "data/processed/pan_cancer_emt_state_atlas/cards/target_disease_group_recommendations.tsv",
    "data/processed/pan_cancer_emt_state_atlas/lineage_targets/disease_target_recommendations_with_lineage_evidence.tsv",
    "data/processed/pan_cancer_emt_state_atlas/app/app_group_warnings.tsv",
    "data/processed/pan_cancer_emt_state_atlas/validation/validation_cohort_readiness.tsv",
]

RESEARCHER_FILES = [
    *CLINICIAN_FILES,
    "docs/pan_cancer_emt_state_atlas/reports/pan_cancer_emt_single_cell_validation_report.md",
    "docs/pan_cancer_emt_state_atlas/reports/pan_cancer_emt_annotated_single_cell_report.md",
    "docs/pan_cancer_emt_state_atlas/reports/pan_cancer_emt_spatial_report.md",
    "docs/pan_cancer_emt_state_atlas/reports/pan_cancer_emt_pathology_review_report.md",
    "data/processed/pan_cancer_emt_state_atlas/cards/emt_scores_with_consensus.tsv",
    "data/processed/pan_cancer_emt_state_atlas/clinical/clinical_survival_by_group.tsv",
    "data/processed/pan_cancer_emt_state_atlas/clinical/clinical_covariate_adjusted_screen.tsv",
    "data/processed/pan_cancer_emt_state_atlas/clinical/clinical_multivariable_cox_models.tsv",
    "data/processed/pan_cancer_emt_state_atlas/annotated_single_cell/external_portal_download_manifest.tsv",
    "data/processed/pan_cancer_emt_state_atlas/annotated_single_cell/3ca_dataset_manifest.tsv",
    "data/processed/pan_cancer_emt_state_atlas/annotated_single_cell/tumor_vs_stroma_emt_summary.tsv",
    "data/processed/pan_cancer_emt_state_atlas/annotated_single_cell/annotated_compartment_summary.tsv",
    "data/processed/pan_cancer_emt_state_atlas/validation/spatial_run_summary.tsv",
    "data/processed/pan_cancer_emt_state_atlas/pathology/pathology_review_queue.tsv",
    "data/processed/pan_cancer_emt_state_atlas/pathology/pathology_label_template.tsv",
    "data/processed/pan_cancer_emt_state_atlas/app/app_state_comparison.tsv",
    "data/processed/pan_cancer_emt_state_atlas/lineage_targets/depmap_lineage_target_dependency.tsv",
]


def build_export_bundles(root: str | Path, out_dir: str | Path) -> pd.DataFrame:
    root = Path(root)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for bundle_name, files in [
        ("clinician_bundle", CLINICIAN_FILES),
        ("researcher_bundle", RESEARCHER_FILES),
    ]:
        zip_path = out / f"{bundle_name}.zip"
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for rel in files:
                path = root / rel
                exists = path.exists()
                rows.append({"bundle": bundle_name, "path": rel, "exists": exists})
                if exists:
                    archive.write(path, arcname=rel)
        rows.append({"bundle": bundle_name, "path": str(zip_path), "exists": zip_path.exists()})
    manifest = pd.DataFrame(rows)
    manifest.to_csv(out / "export_bundle_manifest.tsv", sep="\t", index=False)
    return manifest
