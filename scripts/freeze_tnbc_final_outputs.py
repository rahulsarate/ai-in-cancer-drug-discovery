from __future__ import annotations

import argparse
import hashlib
import shutil
from datetime import date
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


REPORT_FILES = [
    "docs/tnbc_digital_twin_emt_plasticity/build_status.md",
    "docs/tnbc_digital_twin_emt_plasticity/validation_memo.md",
    "docs/tnbc_digital_twin_emt_plasticity/response_label_curation_signoff.md",
    "docs/tnbc_digital_twin_emt_plasticity/gse164715_ambiguity_review.md",
    "docs/tnbc_digital_twin_emt_plasticity/manuscript_bundle/tnbc_manuscript_results_bundle_summary.md",
    "docs/tnbc_digital_twin_emt_plasticity/final_project_report_tnbc_emt_digital_twin.md",
    "docs/tnbc_digital_twin_emt_plasticity/manuscript_full_draft_tnbc_emt_digital_twin.md",
    "data/processed/tnbc_digital_twin/tnbc_same_platform_response_model_report.md",
    "data/processed/tnbc_digital_twin/tnbc_cross_platform_external_validation_report.md",
    "data/processed/tnbc_digital_twin/response_label_curation/tnbc_response_label_curation_signoff_report.md",
    "data/processed/tnbc_digital_twin/response_label_curation/curated_model/tnbc_nac_response_model_report.md",
    "data/processed/tnbc_digital_twin/leave_dataset_out_validation/tnbc_leave_dataset_out_validation_report.md",
    "data/processed/tnbc_digital_twin/external_validation/gse163882/external_validation_report.md",
    "data/processed/tnbc_digital_twin/response_model_robustness/gse163882_external_metric_bootstrap_report.md",
    "data/processed/tnbc_digital_twin/gse164715_marker_validation/gse164715_marker_panel_validation_report.md",
    "data/processed/tnbc_digital_twin/gse164715_ambiguity_review/gse164715_ambiguity_review_report.md",
    "data/processed/tnbc_digital_twin/gse43816_longitudinal/gse43816_longitudinal_emt_shift_report.md",
    "data/processed/tnbc_digital_twin/gse43816_longitudinal/gse43816_clinician_style_digital_twin_report.md",
    "data/processed/tnbc_digital_twin/tnbc_digital_twin_therapy_simulation_report.md",
    "data/processed/tnbc_digital_twin/residual_persister_biology/residual_persister_biology_report.md",
]

TABLE_FILES = [
    "data/processed/tnbc_digital_twin/tnbc_nac_response_model_metrics.tsv",
    "data/processed/tnbc_digital_twin/response_label_curation/tnbc_response_label_curation_table.tsv",
    "data/processed/tnbc_digital_twin/response_label_curation/tnbc_curated_response_model_table.tsv",
    "data/processed/tnbc_digital_twin/response_label_curation/curated_model/tnbc_nac_response_model_metrics.tsv",
    "data/processed/tnbc_digital_twin/leave_dataset_out_validation/tnbc_leave_dataset_out_metrics.tsv",
    "data/processed/tnbc_digital_twin/external_validation/gse163882/external_validation_metrics.tsv",
    "data/processed/tnbc_digital_twin/response_model_robustness/gse163882_external_metric_bootstrap_intervals.tsv",
    "data/processed/tnbc_digital_twin/gse164715_marker_validation/gse164715_marker_panel_direction_checks.tsv",
    "data/processed/tnbc_digital_twin/gse164715_ambiguity_review/gse164715_sample_stage_ambiguity_review.tsv",
    "data/processed/tnbc_digital_twin/gse164715_ambiguity_review/gse164715_cluster_ambiguity_review.tsv",
]

FIGURE_DIRS = [
    "docs/tnbc_digital_twin_emt_plasticity/assets/gse43816_longitudinal",
    "docs/tnbc_digital_twin_emt_plasticity/assets/therapy_simulation",
    "docs/tnbc_digital_twin_emt_plasticity/assets/platform_normalization",
    "docs/tnbc_digital_twin_emt_plasticity/assets/residual_persister_biology",
    "docs/tnbc_digital_twin_emt_plasticity/assets/gse164715_marker_validation",
    "docs/tnbc_digital_twin_emt_plasticity/assets/gse164715_targeted_annotation",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def copy_one(source: Path, release_root: Path, category: str) -> dict[str, object] | None:
    if not source.exists() or not source.is_file():
        return None
    destination = release_root / category / source.name
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    return {
        "category": category,
        "source": str(source.relative_to(ROOT)),
        "frozen_path": str(destination.relative_to(ROOT)),
        "bytes": destination.stat().st_size,
        "sha256": sha256(destination),
    }


def copy_figures(source_dir: Path, release_root: Path) -> list[dict[str, object]]:
    rows = []
    if not source_dir.exists():
        return rows
    target_dir = release_root / "figures" / source_dir.name
    target_dir.mkdir(parents=True, exist_ok=True)
    for source in sorted(source_dir.glob("*.png")):
        destination = target_dir / source.name
        shutil.copy2(source, destination)
        rows.append(
            {
                "category": "figures",
                "source": str(source.relative_to(ROOT)),
                "frozen_path": str(destination.relative_to(ROOT)),
                "bytes": destination.stat().st_size,
                "sha256": sha256(destination),
            }
        )
    return rows


def write_readme(release_root: Path, manifest: pd.DataFrame) -> None:
    lines = [
        "# Frozen TNBC EMT Digital-Twin Release",
        "",
        f"Freeze date: `{date.today().isoformat()}`",
        "",
        "This folder contains the final report, table, and figure artifacts for manuscript/thesis drafting. Checksums are stored in `freeze_manifest.tsv`.",
        "",
        "## Contents",
        "",
        manifest.groupby("category").size().reset_index(name="files").to_markdown(index=False),
        "",
        "## Scientific Boundary",
        "",
        "These outputs support a research-prototype manuscript claim. They do not support clinical treatment-selection claims.",
        "",
        "## Main Remaining Human Step",
        "",
        "Final author/expert review should verify response-label curation decisions and single-cell ambiguity language before submission.",
    ]
    (release_root / "README.md").write_text("\n".join(lines), encoding="utf-8")


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Freeze final TNBC digital-twin figures and tables for manuscript drafting.")
    p.add_argument("--release-name", default=f"tnbc_digital_twin_freeze_{date.today().isoformat()}")
    p.add_argument("--out-root", default="docs/tnbc_digital_twin_emt_plasticity/frozen_releases")
    return p


def main() -> None:
    args = parser().parse_args()
    release_root = ROOT / args.out_root / args.release_name
    release_root.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = []
    for rel in REPORT_FILES:
        row = copy_one(ROOT / rel, release_root, "reports")
        if row:
            rows.append(row)
    for rel in TABLE_FILES:
        row = copy_one(ROOT / rel, release_root, "tables")
        if row:
            rows.append(row)
    for rel in FIGURE_DIRS:
        rows.extend(copy_figures(ROOT / rel, release_root))
    manifest = pd.DataFrame(rows).sort_values(["category", "source"]) if rows else pd.DataFrame()
    manifest.to_csv(release_root / "freeze_manifest.tsv", sep="\t", index=False)
    write_readme(release_root, manifest)
    print(f"froze {len(manifest)} files into {release_root}")


if __name__ == "__main__":
    main()
