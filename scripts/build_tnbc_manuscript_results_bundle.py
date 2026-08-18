from __future__ import annotations

import argparse
import shutil
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


def copy_if_exists(src: Path, dst_dir: Path) -> str:
    if not src.exists():
        return "missing"
    dst_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst_dir / src.name)
    return "copied"


def read_table(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path, sep="\t")


def write_summary(processed: Path, out_dir: Path) -> None:
    external = read_table(processed / "external_validation" / "gse163882" / "external_validation_metrics.tsv")
    marker = read_table(processed / "gse164715_marker_validation" / "gse164715_marker_panel_direction_checks.tsv")
    label_audit = read_table(processed / "response_label_audit" / "tnbc_response_label_audit_summary.tsv")
    label_curation = read_table(processed / "response_label_curation" / "tnbc_response_label_curation_table.tsv")
    curated_metrics = read_table(processed / "response_label_curation" / "curated_model" / "tnbc_nac_response_model_metrics.tsv")
    lodo = read_table(processed / "leave_dataset_out_validation" / "tnbc_leave_dataset_out_metrics.tsv")
    robust = read_table(processed / "response_model_robustness" / "gse163882_external_metric_bootstrap_intervals.tsv")
    curation_summary = pd.DataFrame()
    if not label_curation.empty:
        curation_summary = (
            label_curation.groupby(["dataset_id", "locked_composite_response", "curation_decision"], dropna=False)
            .size()
            .reset_index(name="samples")
            .sort_values(["dataset_id", "locked_composite_response", "curation_decision"])
        )
    lines = [
        "# Manuscript-Ready Results Bundle: TNBC EMT Digital Twin",
        "",
        "## Current Manuscript Claim Level",
        "",
        "The project supports a research-prototype claim: EMT/TME/persister digital-twin features can be scored reproducibly in TNBC NAC cohorts, show interpretable therapy-induced state shifts, and have encouraging but platform-sensitive external validation on `GSE163882`.",
        "",
        "It does not yet support clinical decision-making claims.",
        "",
        "## External Validation Metrics",
        "",
        external.to_markdown(index=False) if not external.empty else "No external metrics available.",
        "",
        "## External Metric Bootstrap Intervals",
        "",
        robust.to_markdown(index=False) if not robust.empty else "No bootstrap intervals available.",
        "",
        "## Response Label Audit Summary",
        "",
        label_audit.to_markdown(index=False) if not label_audit.empty else "No response-label audit available.",
        "",
        "## Locked Response-Label Curation",
        "",
        curation_summary.to_markdown(index=False) if not curation_summary.empty else "No response-label curation available.",
        "",
        "## Curated-Label Sensitivity Metrics",
        "",
        curated_metrics.to_markdown(index=False) if not curated_metrics.empty else "No curated-label metrics available.",
        "",
        "## Additional Leave-Dataset-Out Validation",
        "",
        lodo.to_markdown(index=False) if not lodo.empty else "No leave-dataset-out validation available.",
        "",
        "## GSE164715 Marker-Panel Validation",
        "",
        marker.to_markdown(index=False) if not marker.empty else "No marker-panel validation available.",
        "",
        "## Reproducibility",
        "",
        "Run the complete local pipeline with:",
        "",
        "```powershell",
        "python scripts\\run_tnbc_digital_twin_pipeline.py --skip-existing",
        "```",
        "",
        "For fresh data downloads and long scRNA import steps, add `--include-downloads --include-scrna`.",
        "",
        "## Remaining Before Submission",
        "",
        "1. Final expert/author review of locked response-label curation decisions.",
        "2. Final expert/author review of GSE164715 ambiguity language.",
        "3. Manuscript polishing, citation formatting, and journal/thesis formatting.",
        "4. Additional external cohorts remain valuable but are no longer required for a research-prototype manuscript claim.",
    ]
    (out_dir / "tnbc_manuscript_results_bundle_summary.md").write_text("\n".join(lines), encoding="utf-8")


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Build a manuscript-ready TNBC digital-twin results bundle.")
    p.add_argument("--processed-dir", default="data/processed/tnbc_digital_twin")
    p.add_argument("--docs-dir", default="docs/tnbc_digital_twin_emt_plasticity")
    p.add_argument("--out-dir", default="docs/tnbc_digital_twin_emt_plasticity/manuscript_bundle")
    return p


def main() -> None:
    args = parser().parse_args()
    processed = ROOT / args.processed_dir
    docs = ROOT / args.docs_dir
    out_dir = ROOT / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    sources = [
        processed / "tnbc_same_platform_response_model_report.md",
        processed / "tnbc_cross_platform_external_validation_report.md",
        processed / "platform_normalization" / "tnbc_platform_normalization_diagnostics_report.md",
        processed / "external_validation" / "gse163882" / "external_validation_report.md",
        processed / "gse164715_marker_validation" / "gse164715_marker_panel_validation_report.md",
        processed / "gse164715_ambiguity_review" / "gse164715_ambiguity_review_report.md",
        processed / "response_model_robustness" / "gse163882_external_metric_bootstrap_report.md",
        processed / "response_label_audit" / "tnbc_response_label_audit_report.md",
        processed / "response_label_curation" / "tnbc_response_label_curation_signoff_report.md",
        processed / "response_label_curation" / "curated_model" / "tnbc_nac_response_model_report.md",
        processed / "leave_dataset_out_validation" / "tnbc_leave_dataset_out_validation_report.md",
        docs / "validation_memo.md",
        docs / "response_label_curation_signoff.md",
        docs / "gse164715_ambiguity_review.md",
        docs / "manuscript_draft_tnbc_emt_digital_twin.md",
        docs / "final_project_report_tnbc_emt_digital_twin.md",
        docs / "manuscript_full_draft_tnbc_emt_digital_twin.md",
        docs / "build_status.md",
    ]
    index_rows = []
    for src in sources:
        index_rows.append({"source": str(src.relative_to(ROOT)), "status": copy_if_exists(src, out_dir)})
    pd.DataFrame(index_rows).to_csv(out_dir / "bundle_file_index.tsv", sep="\t", index=False)
    write_summary(processed, out_dir)
    print(pd.DataFrame(index_rows).to_string(index=False))


if __name__ == "__main__":
    main()
