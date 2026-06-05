from __future__ import annotations

from pathlib import Path

import pandas as pd


TASKS = [
    ("starter", "10x public Visium cancer datasets: breast, lung, prostate, ovarian, colorectal", 16, "done"),
    ("starter", "HEST-1k manifest/reproducibility plan", 8, "partial"),
    ("starter", "TCGA EMT signatures reused as bulk reference", 8, "done"),
    ("workflow_ingestion", "Standardize Visium tables and coordinates", 10, "done"),
    ("workflow_ingestion", "AnnData-style processed_h5ad export", 8, "done"),
    ("workflow_ingestion", "Image tile storage/extraction", 8, "done"),
    ("workflow_ingestion", "QC: detected genes, counts, tissue spots, batch/platform labels", 8, "done"),
    ("workflow_scoring", "EMT, partial EMT, hypoxia, CAF/TAM, ferroptosis scoring", 10, "done"),
    ("workflow_scoring", "ECM and angiogenesis scoring", 6, "partial"),
    ("workflow_scoring", "cell2location/Tangram/RCTD/stereoscope deconvolution", 12, "blocked_external_reference"),
    ("workflow_scoring", "Marker-proxy and NNLS deconvolution fallback", 6, "done"),
    ("workflow_scoring", "Candidate niche labels", 8, "partial"),
    ("workflow_graph", "Spot spatial kNN/radius graph", 8, "done"),
    ("workflow_graph", "Ligand-receptor edges", 8, "done"),
    ("workflow_graph", "ECM/hypoxia gradient edges", 8, "partial"),
    ("workflow_graph", "Histology-similarity edges", 8, "partial"),
    ("workflow_graph", "Heterogeneous compartment graph", 10, "done"),
    ("validation", "HTAN spatial datasets", 10, "partial"),
    ("validation", "Additional GEO Visium cancer cohorts", 10, "partial"),
    ("validation", "SpatialTME/SCAR public atlas feasibility", 8, "partial"),
    ("advanced", "Matched scRNA-seq references", 12, "pending"),
    ("advanced", "Metastasis/progression cohorts", 10, "implemented_first_cohort"),
    ("advanced", "Pathology foundation embeddings", 10, "pending"),
]

STATUS_MULTIPLIER = {
    "done": 1.0,
    "partial": 0.5,
    "blocked_external_reference": 0.25,
    "implemented_first_cohort": 0.7,
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
        "HEST-1k manifest/reproducibility plan": "2-4 days",
        "Image tile storage/extraction": "3-5 days",
        "ECM and angiogenesis scoring": "1 day",
        "cell2location/Tangram/RCTD/stereoscope deconvolution": "2-4 weeks after matched scRNA reference",
        "Candidate niche labels": "3-7 days with pathology/deconvolution",
        "ECM/hypoxia gradient edges": "1-2 days",
        "Histology-similarity edges": "1-2 weeks",
        "HTAN spatial datasets": "2-4 weeks",
        "Additional GEO Visium cancer cohorts": "1-2 weeks",
        "SpatialTME/SCAR public atlas feasibility": "3-5 days",
        "Matched scRNA-seq references": "3-6 weeks",
        "Metastasis/progression cohorts": "first cohort implemented; 1-3 weeks for matched primary/metastatic PDAC scale-up",
        "Pathology foundation embeddings": "3-6 weeks",
    }
    for _, row in remaining.iterrows():
        lines.append(f"| {row['task']} | {row['status']} | {estimates.get(row['task'], 'TBD')} |")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
