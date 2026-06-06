from __future__ import annotations

from pathlib import Path

import pandas as pd


TASKS = [
    ("starter", "10x public Visium cancer datasets: breast, lung, prostate, ovarian, colorectal", 16, "done"),
    ("starter", "HEST-1k manifest/reproducibility plan", 8, "hf_access_check_implemented_auth_required"),
    ("starter", "TCGA EMT signatures reused as bulk reference", 8, "done"),
    ("workflow_ingestion", "Standardize Visium tables and coordinates", 10, "done"),
    ("workflow_ingestion", "AnnData-style processed_h5ad export", 8, "done"),
    ("workflow_ingestion", "Image tile storage/extraction", 8, "done"),
    ("workflow_ingestion", "QC: detected genes, counts, tissue spots, batch/platform labels", 8, "done"),
    ("workflow_scoring", "EMT, partial EMT, hypoxia, CAF/TAM, ferroptosis scoring", 10, "done"),
    ("workflow_scoring", "ECM and angiogenesis scoring", 6, "done"),
    ("workflow_scoring", "cell2location/Tangram/RCTD/stereoscope deconvolution", 12, "advanced_environment_installed"),
    ("workflow_scoring", "Marker-proxy and NNLS deconvolution fallback", 6, "done"),
    ("workflow_scoring", "Candidate niche labels", 8, "review_ops_ready"),
    ("workflow_graph", "Spot spatial kNN/radius graph", 8, "done"),
    ("workflow_graph", "Ligand-receptor edges", 8, "done"),
    ("workflow_graph", "ECM/hypoxia gradient edges", 8, "done"),
    ("workflow_graph", "Histology-similarity edges", 8, "implemented_first_cohort"),
    ("workflow_graph", "Heterogeneous compartment graph", 10, "done"),
    ("validation", "HTAN spatial datasets", 10, "client_check_ready_credentials_required"),
    ("validation", "Additional GEO Visium cancer cohorts", 10, "implemented_multiple_cohorts"),
    ("validation", "SpatialTME/SCAR public atlas feasibility", 8, "feasibility_manifest_ready"),
    ("advanced", "Matched scRNA-seq references", 12, "real_reference_v1"),
    ("advanced", "Metastasis/progression cohorts", 10, "full_graph_complete"),
    ("advanced", "Pathology foundation embeddings", 10, "baseline_ready_foundation_access_check"),
]

STATUS_MULTIPLIER = {
    "done": 1.0,
    "access_required": 0.5,
    "hf_access_check_implemented_auth_required": 0.7,
    "partial": 0.5,
    "blocked_external_reference": 0.25,
    "environment_blocked_after_real_reference": 0.65,
    "advanced_environment_installed": 0.85,
    "reference_candidates_ready": 0.55,
    "real_reference_v1": 0.8,
    "marker_reference_ready": 0.4,
    "manifest_ready": 0.6,
    "portal_download_pending": 0.65,
    "client_check_ready_credentials_required": 0.72,
    "template_ready": 0.65,
    "review_queue_ready": 0.8,
    "review_ops_ready": 0.85,
    "embedding_baseline_ready": 0.65,
    "baseline_ready_foundation_access_check": 0.72,
    "implemented_first_cohort": 0.7,
    "implemented_multiple_cohorts": 0.75,
    "matched_pilot_implemented": 0.85,
    "full_scoring_complete": 0.9,
    "full_graph_complete": 1.0,
    "feasibility_manifest_ready": 0.8,
    "pending": 0.0,
}


def main() -> None:
    rows = [
        {
            "phase": phase,
            "task": task,
            "weight": weight,
            "status": status,
            "credit": weight * STATUS_MULTIPLIER[status],
        }
        for phase, task, weight, status in TASKS
    ]
    detail = pd.DataFrame(rows)
    summary = (
        detail.groupby("phase", dropna=False)
        .agg(total_weight=("weight", "sum"), completed_credit=("credit", "sum"))
        .reset_index()
    )
    summary["completion_percent"] = (100 * summary["completed_credit"] / summary["total_weight"]).round(1)
    total = pd.DataFrame(
        [
            {
                "phase": "overall",
                "total_weight": detail["weight"].sum(),
                "completed_credit": detail["credit"].sum(),
                "completion_percent": round(100 * detail["credit"].sum() / detail["weight"].sum(), 1),
            }
        ]
    )
    out = Path("data/processed/spatial_emt_niche_gnn_project_status")
    out.mkdir(parents=True, exist_ok=True)
    detail.to_csv(out / "spatial_project_status_detail.tsv", sep="\t", index=False)
    pd.concat([summary, total], ignore_index=True).to_csv(out / "spatial_project_status_summary.tsv", sep="\t", index=False)
    write_markdown(detail, pd.concat([summary, total], ignore_index=True), out / "spatial_project_status_report.md")
    print(f"Wrote {out / 'spatial_project_status_summary.tsv'}")


def write_markdown(detail: pd.DataFrame, summary: pd.DataFrame, out: Path) -> None:
    remaining = detail[~detail["status"].eq("done")].copy()
    lines = [
        "# Spatial EMT Niche GNN Project Status",
        "",
        "## Completion Chart",
        "",
        "| Phase | Completion % |",
        "| --- | ---: |",
    ]
    for _, row in summary.iterrows():
        lines.append(f"| {row['phase']} | {row['completion_percent']} |")
    lines.extend(
        [
            "",
            "## Remaining Work and Estimated Time",
            "",
            "| Task | Status | Estimated time |",
            "| --- | --- | --- |",
        ]
    )
    estimates = {
        "HEST-1k manifest/reproducibility plan": "access checker ready; metadata cache after HF terms/token",
        "Image tile storage/extraction": "3-5 days",
        "ECM and angiogenesis scoring": "1 day",
        "cell2location/Tangram/RCTD/stereoscope deconvolution": "Tangram/RCTD environment ready; cell2location runtime check needs WSL/Linux/GPU",
        "Candidate niche labels": "review queue and reviewer ops pack ready; 3-7 days with expert review",
        "ECM/hypoxia gradient edges": "1-2 days",
        "Histology-similarity edges": "first cohort implemented; 3-7 days for all image-backed cohorts",
        "HTAN spatial datasets": "target manifest and access checker ready; Synapse/Gen3 credentials required",
        "Additional GEO Visium cancer cohorts": "multiple cohorts implemented; 1-2 weeks for broader disease expansion",
        "SpatialTME/SCAR public atlas feasibility": "feasibility manifest ready; adapter after source accession selection",
        "Matched scRNA-seq references": "GSE154778 real reference v1 complete; add GSE155698/GSE205013 for robustness",
        "Metastasis/progression cohorts": "full patient-batched graph complete; next leave-patient validation",
        "Pathology foundation embeddings": "baseline and HF access checker ready; model terms/token required for foundation upgrade",
    }
    for _, row in remaining.iterrows():
        lines.append(f"| {row['task']} | {row['status']} | {estimates.get(row['task'], 'TBD')} |")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
