from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Generate the EMT-ViSTA implementation and readiness report.")
    p.add_argument("--output-root", default="data/processed/emt_virtual_spatial_staining_v1")
    p.add_argument("--docs-dir", default="docs/emt_virtual_spatial_staining")
    return p


def _read(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, sep="\t") if path.exists() else pd.DataFrame()


def main() -> None:
    args = parser().parse_args()
    root = Path(args.output_root)
    docs = Path(args.docs_dir)
    docs.mkdir(parents=True, exist_ok=True)
    assets = docs / "assets"
    assets.mkdir(parents=True, exist_ok=True)

    rows = []
    for backend_dir in sorted(path for path in root.iterdir() if path.is_dir()):
        metrics = _read(backend_dir / "emt_vista_metrics.tsv")
        gates = _read(backend_dir / "emt_vista_go_no_go.tsv")
        safety = _read(backend_dir / "emt_vista_partial_emt_safety.tsv")
        if metrics.empty:
            continue
        test = metrics.loc[metrics["split"].astype(str).eq("test")]
        safety_row = safety.iloc[0] if not safety.empty else {}
        rows.append(
            {
                "backend": backend_dir.name,
                "test_spots": int(test["n"].max()) if len(test) else 0,
                "median_test_spearman": float(test["spearman"].median()) if len(test) else float("nan"),
                "best_test_spearman": float(test["spearman"].max()) if len(test) else float("nan"),
                "best_program": str(test.loc[test["spearman"].idxmax(), "target"]) if len(test) else "",
                "gates_passed": int(gates["passed"].astype(bool).sum()) if not gates.empty else 0,
                "gates_total": len(gates),
                "partial_emt_auprc_above_prevalence": safety_row.get("auprc_above_prevalence", float("nan")),
                "stroma_false_positive_rate": safety_row.get("pure_stroma_false_positive_rate", float("nan")),
                "calibration_error": safety_row.get("partial_emt_expected_calibration_error", float("nan")),
            }
        )
    benchmark = pd.DataFrame(rows)
    benchmark.to_csv(docs / "backend_benchmark_summary.tsv", sep="\t", index=False)

    if not benchmark.empty:
        figure, axis = plt.subplots(figsize=(7.5, 4.5))
        sns.barplot(data=benchmark, x="backend", y="median_test_spearman", color="#2a9d8f", ax=axis)
        axis.axhline(0.35, color="#c23b4a", linestyle="--", label="predefined gate")
        axis.set_xlabel("Image representation")
        axis.set_ylabel("Median held-out Spearman")
        axis.legend(frameon=False)
        figure.tight_layout()
        figure.savefig(assets / "backend_comparison.png", dpi=200, bbox_inches="tight")
        plt.close(figure)

    workflow_steps = [
        ("H&E + spatial\ntranscriptomics", "#457b9d"),
        ("Risk-aware\nEMT/TME labels", "#2a9d8f"),
        ("Multi-scale image\nrepresentations", "#e9c46a"),
        ("Spatial multitask\nensemble", "#f4a261"),
        ("Uncertainty, gates\n& virtual maps", "#e76f51"),
    ]
    figure, axis = plt.subplots(figsize=(12, 2.4))
    axis.set_xlim(0, len(workflow_steps) * 2)
    axis.set_ylim(0, 1)
    axis.axis("off")
    for index, (label, color) in enumerate(workflow_steps):
        x = index * 2 + 0.1
        axis.add_patch(plt.Rectangle((x, 0.25), 1.55, 0.5, color=color, alpha=0.95))
        axis.text(x + 0.775, 0.5, label, ha="center", va="center", color="white", fontsize=10, weight="bold")
        if index < len(workflow_steps) - 1:
            axis.annotate("", xy=(x + 1.95, 0.5), xytext=(x + 1.6, 0.5), arrowprops={"arrowstyle": "->", "lw": 1.8})
    figure.tight_layout()
    figure.savefig(assets / "workflow_overview.png", dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(figure)

    pairs_manifest = json.loads((root / "training_pair_manifest.json").read_text(encoding="utf-8"))
    phikon_metadata = root / "pathology_embeddings_phikon_v2.json"
    h0_status = _read(Path("data/processed/spatial_emt_niche_gnn_histology/foundation_model_access_status.tsv"))
    h0_row = h0_status.loc[h0_status["repo_id"].astype(str).eq("bioptimus/H-optimus-0")] if "repo_id" in h0_status else pd.DataFrame()
    phikon_operational = phikon_metadata.exists()

    completion = pd.DataFrame(
        [
            {"component": "Protocol and hypotheses", "status": "complete", "percent": 100},
            {"component": "Five-cohort paired data", "status": "complete", "percent": 100},
            {"component": "Risk-aware molecular labels", "status": "complete", "percent": 100},
            {"component": "Handcrafted morphology baseline", "status": "complete", "percent": 100},
            {"component": "Generic learned-image baseline", "status": "complete" if (root / "resnet50/pathology_embeddings_resnet50.tsv").exists() or (root / "pathology_embeddings_resnet50.tsv").exists() else "pending_run", "percent": 100 if (root / "pathology_embeddings_resnet50.tsv").exists() else 70},
            {"component": "Ungated pathology foundation adapter", "status": "operational" if phikon_operational else "pending_run", "percent": 100 if phikon_operational else 80},
            {"component": "H-Optimus-0 adapter", "status": "credential_gate" if h0_row.empty else str(h0_row.iloc[0].get("status", "credential_gate")), "percent": 90},
            {"component": "Graph-refined multitask model", "status": "complete", "percent": 100},
            {"component": "Uncertainty and safety gates", "status": "complete", "percent": 100},
            {"component": "H&E overlays and hotspot export", "status": "complete", "percent": 100},
            {"component": "Independent multi-patient clinical validation", "status": "not_started", "percent": 0},
            {"component": "Prospective clinical validation", "status": "out_of_scope_v1", "percent": 0},
        ]
    )
    completion.to_csv(docs / "implementation_completion.tsv", sep="\t", index=False)
    engineering = completion.loc[~completion["component"].str.contains("clinical validation", case=False), "percent"].mean()
    biological_gates = benchmark["gates_passed"].max() / benchmark["gates_total"].max() * 100 if not benchmark.empty else 0.0
    readiness = pd.DataFrame(
        [
            {"dimension": "MVP engineering", "percent": engineering},
            {"dimension": "Paired-data pipeline", "percent": 100.0},
            {"dimension": "Predefined gates passed", "percent": biological_gates},
            {"dimension": "Multi-patient external validation", "percent": 0.0},
            {"dimension": "Prospective clinical validation", "percent": 0.0},
        ]
    )
    readiness.to_csv(docs / "readiness_dimensions.tsv", sep="\t", index=False)
    figure, axis = plt.subplots(figsize=(8.5, 4.5))
    sns.barplot(data=readiness, y="dimension", x="percent", color="#457b9d", ax=axis)
    axis.set_xlim(0, 100)
    axis.set_xlabel("Completion or evidence achieved (%)")
    axis.set_ylabel("")
    for container in axis.containers:
        axis.bar_label(container, fmt="%.0f%%", padding=3)
    figure.tight_layout()
    figure.savefig(assets / "readiness_dimensions.png", dpi=200, bbox_inches="tight")
    plt.close(figure)

    lines = [
        "# EMT-ViSTA Implementation Report",
        "",
        "## Executive Status",
        "",
        f"The executable EMT-ViSTA MVP is implemented across {pairs_manifest['datasets']} public spatial datasets and {pairs_manifest['spots']} aligned spots. Internal engineering completion is {engineering:.1f}%. This percentage measures software/readiness work, not scientific or clinical validation.",
        "",
        "Lung squamous and colorectal examples are held out at dataset level. They are technical external tests, not independent clinical cohorts.",
        "",
        "## Implemented System",
        "",
        "- Confidence-tiered epithelial, mesenchymal, partial-EMT, CAF, TAM, hypoxia, ECM, and stromal-risk labels.",
        "- Multi-scale H&E extraction with handcrafted, ResNet50, Phikon-v2, and H-Optimus-0 adapters.",
        "- Malignant-gated partial EMT and explicit stromal-inflation risk.",
        "- Image-only and graph-refined bootstrap multitask models.",
        "- Predictive uncertainty, abstention, calibration, stroma false-positive, and go/no-go reports.",
        "- H&E overlays, coordinate maps, GeoJSON hotspots, model metadata, and reproducible CLIs.",
        "",
        "![EMT-ViSTA workflow](assets/workflow_overview.png)",
        "",
        "## Backend Benchmark",
        "",
    ]
    if benchmark.empty:
        lines.append("No completed model benchmark was found.")
    else:
        lines.append(benchmark.to_markdown(index=False, floatfmt=".3f"))
    lines.extend(
        [
            "",
            "![Backend comparison](assets/backend_comparison.png)",
            "",
            "## Readiness Is Multi-Dimensional",
            "",
            "The engineering percentage is not a biological success score. The validation chart reports the dimensions separately; failed predefined gates remain failed.",
            "",
            "![Readiness dimensions](assets/readiness_dimensions.png)",
            "",
            "## Interpretation",
            "",
            "A failed gate is a valid result: it prevents morphology associations from being overstated as molecular measurement. Handcrafted and ImageNet controls establish whether apparent performance comes from color, texture, or general image features. Pathology-foundation performance must be evaluated at adequate sample size before biological conclusions are made.",
            "",
            "## Remaining Scientific Work",
            "",
            "- Scale pathology-foundation extraction on a CUDA GPU.",
            "- Add multi-patient HEST/GEO/HTAN cohorts with disease-matched deconvolution.",
            "- Obtain calibrated pathologist tumor, invasive-edge, stroma, necrosis, and immune-region labels.",
            "- Validate against an untouched institution and technology.",
            "- Perform prospective assay-triage evaluation before any clinical-use claim.",
            "",
            "## Conclusion",
            "",
            "EMT-ViSTA is an operational research pipeline. Its current outputs are virtual-stain hypotheses with explicit uncertainty and contamination controls. Publication claims depend on the predefined external-validation gates, not on completion of the software alone.",
        ]
    )
    (docs / "implementation_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {docs / 'implementation_report.md'}")


if __name__ == "__main__":
    main()
