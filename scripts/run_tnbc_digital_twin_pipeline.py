from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class PipelineStep:
    name: str
    command: list[str]
    required_outputs: list[str]
    group: str = "core"
    default_enabled: bool = True


STEPS = [
    PipelineStep(
        name="download_public_resources",
        command=["scripts/fetch_tnbc_nac_public_resources.py"],
        required_outputs=["data/processed/tnbc_digital_twin/tnbc_nac_geo_download_audit.tsv"],
        group="download",
        default_enabled=False,
    ),
    PipelineStep(
        name="prepare_geo_metadata",
        command=["scripts/prepare_tnbc_nac_geo_metadata.py"],
        required_outputs=["data/processed/tnbc_digital_twin/tnbc_nac_geo_sample_metadata.tsv"],
    ),
    PipelineStep(
        name="build_gene_expression",
        command=["scripts/build_tnbc_nac_gene_expression.py"],
        required_outputs=["data/processed/tnbc_digital_twin/tnbc_nac_gene_expression_build_report.md"],
    ),
    PipelineStep(
        name="score_digital_twin_features",
        command=["scripts/score_tnbc_nac_digital_twin_features.py"],
        required_outputs=["data/processed/tnbc_digital_twin/tnbc_nac_emt_digital_twin_model_table.tsv"],
    ),
    PipelineStep(
        name="train_response_model",
        command=["scripts/train_tnbc_nac_response_model.py"],
        required_outputs=["data/processed/tnbc_digital_twin/tnbc_nac_response_model_report.md"],
    ),
    PipelineStep(
        name="analyze_gse43816_longitudinal_shift",
        command=["scripts/analyze_gse43816_longitudinal_emt_shift.py"],
        required_outputs=["data/processed/tnbc_digital_twin/gse43816_longitudinal/gse43816_clinician_style_digital_twin_report.md"],
    ),
    PipelineStep(
        name="calibrate_transition_priors",
        command=["scripts/calibrate_tnbc_emt_transition_rates.py"],
        required_outputs=["data/processed/tnbc_digital_twin/transition_calibration/gse43816_transition_calibration_report.md"],
    ),
    PipelineStep(
        name="simulate_therapy_digital_twin",
        command=["scripts/simulate_tnbc_emt_digital_twin.py"],
        required_outputs=["data/processed/tnbc_digital_twin/tnbc_digital_twin_therapy_simulation_report.md"],
    ),
    PipelineStep(
        name="analyze_residual_persister_biology",
        command=["scripts/analyze_tnbc_residual_persister_biology.py"],
        required_outputs=["data/processed/tnbc_digital_twin/residual_persister_biology/residual_persister_biology_report.md"],
    ),
    PipelineStep(
        name="import_gse164715_scrna",
        command=["scripts/import_gse164715_persister_scrna.py"],
        required_outputs=["data/processed/tnbc_digital_twin/gse164715_persister_scrna/gse164715_persister_scrna_import_report.md"],
        group="scrna",
        default_enabled=False,
    ),
    PipelineStep(
        name="filter_gse164715_human_cells",
        command=["scripts/filter_gse164715_human_malignant_scrna.py"],
        required_outputs=["data/processed/tnbc_digital_twin/gse164715_human_filter/gse164715_human_dominant_filter_report.md"],
        group="scrna",
        default_enabled=False,
    ),
    PipelineStep(
        name="annotate_gse164715_targeted_clusters",
        command=["scripts/annotate_gse164715_scrna_targeted_clusters.py"],
        required_outputs=["data/processed/tnbc_digital_twin/gse164715_targeted_annotation/gse164715_targeted_annotation_report.md"],
    ),
    PipelineStep(
        name="prepare_external_validation_hooks",
        command=["scripts/validate_tnbc_external_response_dataset.py"],
        required_outputs=["data/processed/tnbc_digital_twin/external_validation/external_validation_input_templates.md"],
    ),
    PipelineStep(
        name="prepare_gse163882_external_validation",
        command=["scripts/prepare_gse163882_external_validation.py"],
        required_outputs=["data/processed/tnbc_digital_twin/external_validation/gse163882/gse163882_external_preparation_report.md"],
    ),
    PipelineStep(
        name="validate_gse163882_external_response",
        command=[
            "scripts/validate_tnbc_external_response_dataset.py",
            "--external-expression",
            "data/processed/tnbc_digital_twin/external_validation/gse163882/gse163882_tnbc_external_expression_log2tpm.tsv",
            "--external-metadata",
            "data/processed/tnbc_digital_twin/external_validation/gse163882/gse163882_tnbc_external_metadata.tsv",
            "--external-dataset-id",
            "GSE163882_TNBC_TPM",
            "--out-dir",
            "data/processed/tnbc_digital_twin/external_validation/gse163882",
        ],
        required_outputs=["data/processed/tnbc_digital_twin/external_validation/gse163882/external_validation_report.md"],
    ),
    PipelineStep(
        name="build_platform_normalization_diagnostics",
        command=["scripts/build_tnbc_platform_normalization_diagnostics.py"],
        required_outputs=["data/processed/tnbc_digital_twin/platform_normalization/tnbc_platform_normalization_diagnostics_report.md"],
    ),
    PipelineStep(
        name="build_same_vs_cross_platform_reports",
        command=["scripts/build_tnbc_same_vs_cross_platform_reports.py"],
        required_outputs=[
            "data/processed/tnbc_digital_twin/tnbc_same_platform_response_model_report.md",
            "data/processed/tnbc_digital_twin/tnbc_cross_platform_external_validation_report.md",
        ],
    ),
    PipelineStep(
        name="audit_response_labels",
        command=["scripts/audit_tnbc_response_labels.py"],
        required_outputs=["data/processed/tnbc_digital_twin/response_label_audit/tnbc_response_label_audit_report.md"],
    ),
    PipelineStep(
        name="curate_response_labels",
        command=["scripts/curate_tnbc_response_labels.py"],
        required_outputs=["data/processed/tnbc_digital_twin/response_label_curation/tnbc_response_label_curation_signoff_report.md"],
    ),
    PipelineStep(
        name="train_curated_response_model",
        command=[
            "scripts/train_tnbc_nac_response_model.py",
            "--model-table",
            "data/processed/tnbc_digital_twin/response_label_curation/tnbc_curated_response_model_table.tsv",
            "--out-dir",
            "data/processed/tnbc_digital_twin/response_label_curation/curated_model",
        ],
        required_outputs=["data/processed/tnbc_digital_twin/response_label_curation/curated_model/tnbc_nac_response_model_report.md"],
    ),
    PipelineStep(
        name="validate_leave_dataset_out",
        command=["scripts/validate_tnbc_leave_dataset_out.py"],
        required_outputs=["data/processed/tnbc_digital_twin/leave_dataset_out_validation/tnbc_leave_dataset_out_validation_report.md"],
    ),
    PipelineStep(
        name="bootstrap_external_response_metrics",
        command=["scripts/bootstrap_tnbc_response_model_metrics.py"],
        required_outputs=["data/processed/tnbc_digital_twin/response_model_robustness/gse163882_external_metric_bootstrap_report.md"],
    ),
    PipelineStep(
        name="validate_gse164715_marker_panels",
        command=["scripts/validate_gse164715_targeted_marker_panels.py"],
        required_outputs=["data/processed/tnbc_digital_twin/gse164715_marker_validation/gse164715_marker_panel_validation_report.md"],
    ),
    PipelineStep(
        name="review_gse164715_ambiguity",
        command=["scripts/review_gse164715_ambiguous_compartments.py"],
        required_outputs=["data/processed/tnbc_digital_twin/gse164715_ambiguity_review/gse164715_ambiguity_review_report.md"],
    ),
    PipelineStep(
        name="build_validation_memo",
        command=["scripts/build_tnbc_digital_twin_validation_memo.py"],
        required_outputs=["docs/tnbc_digital_twin_emt_plasticity/validation_memo.md"],
    ),
    PipelineStep(
        name="build_manuscript_draft",
        command=["scripts/build_tnbc_manuscript_draft.py"],
        required_outputs=["docs/tnbc_digital_twin_emt_plasticity/manuscript_draft_tnbc_emt_digital_twin.md"],
    ),
    PipelineStep(
        name="build_final_report_and_full_manuscript",
        command=["scripts/build_tnbc_final_report_and_manuscript.py"],
        required_outputs=[
            "docs/tnbc_digital_twin_emt_plasticity/final_project_report_tnbc_emt_digital_twin.md",
            "docs/tnbc_digital_twin_emt_plasticity/manuscript_full_draft_tnbc_emt_digital_twin.md",
        ],
    ),
    PipelineStep(
        name="build_manuscript_results_bundle",
        command=["scripts/build_tnbc_manuscript_results_bundle.py"],
        required_outputs=["docs/tnbc_digital_twin_emt_plasticity/manuscript_bundle/tnbc_manuscript_results_bundle_summary.md"],
    ),
    PipelineStep(
        name="freeze_final_outputs",
        command=["scripts/freeze_tnbc_final_outputs.py", "--release-name", "tnbc_digital_twin_freeze_2026-06-15"],
        required_outputs=["docs/tnbc_digital_twin_emt_plasticity/frozen_releases/tnbc_digital_twin_freeze_2026-06-15/README.md"],
    ),
]


def enabled_steps(args: argparse.Namespace) -> list[PipelineStep]:
    selected = []
    start_seen = args.start_at is None
    stop_after_seen = False
    for step in STEPS:
        if args.start_at == step.name:
            start_seen = True
        if not start_seen:
            continue
        if step.group == "download" and not args.include_downloads:
            continue
        if step.group == "scrna" and not args.include_scrna:
            continue
        if not step.default_enabled and step.group not in {"download", "scrna"}:
            continue
        selected.append(step)
        if args.stop_after == step.name:
            stop_after_seen = True
            break
    if args.stop_after and not stop_after_seen:
        raise SystemExit(f"--stop-after step not reached or not enabled: {args.stop_after}")
    return selected


def output_status(step: PipelineStep) -> dict[str, object]:
    outputs = []
    for rel in step.required_outputs:
        path = ROOT / rel
        outputs.append({"path": rel, "exists": path.exists(), "bytes": path.stat().st_size if path.exists() else 0})
    return {"step": step.name, "outputs": outputs, "complete": all(item["exists"] and item["bytes"] > 0 for item in outputs)}


def run_step(step: PipelineStep, dry_run: bool, skip_existing: bool) -> dict[str, object]:
    command = [sys.executable, *step.command]
    started = time.time()
    record: dict[str, object] = {
        "step": step.name,
        "command": command,
        "started_epoch": started,
        "dry_run": dry_run,
    }
    current_status = output_status(step)
    if skip_existing and current_status["complete"]:
        print(f"[tnbc-pipeline] {step.name}: skipped existing outputs", flush=True)
        record.update({"returncode": 0, "elapsed_seconds": 0.0, "skipped_existing": True, **current_status})
        return record
    print(f"[tnbc-pipeline] {step.name}: {' '.join(command)}", flush=True)
    if dry_run:
        record.update({"returncode": None, "elapsed_seconds": 0.0, "skipped_existing": False, **current_status})
        return record
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    elapsed = time.time() - started
    record.update(
        {
            "returncode": result.returncode,
            "elapsed_seconds": elapsed,
            "skipped_existing": False,
            "stdout_tail": result.stdout[-4000:],
            "stderr_tail": result.stderr[-4000:],
            **output_status(step),
        }
    )
    if result.stdout:
        print(result.stdout[-2000:], flush=True)
    if result.stderr:
        print(result.stderr[-2000:], file=sys.stderr, flush=True)
    if result.returncode != 0:
        raise SystemExit(f"Pipeline step failed: {step.name}")
    return record


def write_reports(records: list[dict[str, object]], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "pipeline": "tnbc_emt_digital_twin",
        "records": records,
    }
    (out_dir / "tnbc_digital_twin_pipeline_run_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    lines = [
        "# TNBC Digital-Twin Pipeline Run Report",
        "",
        "| Step | Return code | Elapsed seconds | Skipped existing | Complete | Required outputs |",
        "| --- | ---: | ---: | --- | --- | --- |",
    ]
    for record in records:
        outputs = record.get("outputs", [])
        output_text = "<br>".join(f"`{item['path']}`" for item in outputs) if isinstance(outputs, list) else ""
        lines.append(
            f"| `{record['step']}` | {record.get('returncode', 'NA')} | {float(record.get('elapsed_seconds', 0.0)):.1f} | "
            f"{record.get('skipped_existing', False)} | {record.get('complete', False)} | {output_text} |"
        )
    (out_dir / "tnbc_digital_twin_pipeline_run_report.md").write_text("\n".join(lines), encoding="utf-8")


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Run the TNBC EMT digital-twin pipeline in reproducible dependency order.")
    p.add_argument("--out-dir", default="data/processed/tnbc_digital_twin/pipeline_runs")
    p.add_argument("--include-downloads", action="store_true", help="Include GEO/PubMed download step. By default the runner uses local data.")
    p.add_argument("--include-scrna", action="store_true", help="Include long GSE164715 raw scRNA import/filter steps.")
    p.add_argument("--start-at", choices=[step.name for step in STEPS])
    p.add_argument("--stop-after", choices=[step.name for step in STEPS])
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--skip-existing", action="store_true", help="Do not rerun steps whose required outputs already exist.")
    return p


def main() -> None:
    args = parser().parse_args()
    steps = enabled_steps(args)
    if not steps:
        raise SystemExit("No pipeline steps selected.")
    records = [run_step(step, dry_run=args.dry_run, skip_existing=args.skip_existing) for step in steps]
    write_reports(records, ROOT / args.out_dir)
    print(f"[tnbc-pipeline] wrote run report to {ROOT / args.out_dir}")


if __name__ == "__main__":
    main()
