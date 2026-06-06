from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


COHORTS = [
    {
        "label": "synthetic_demo",
        "expression": "data/processed/spatial_emt_niche_gnn_demo/demo_spatial_expression.tsv",
        "metadata": "data/processed/spatial_emt_niche_gnn_demo/demo_spatial_metadata.tsv",
        "out_dir": "data/processed/spatial_emt_niche_gnn_demo",
        "skip_edge_ablation": False,
    },
    {
        "label": "10x_breast_ffpe_idc",
        "expression": "data/processed/spatial_emt_niche_gnn_10x_breast/10x_breast_cancer_signature_expression.tsv",
        "metadata": "data/processed/spatial_emt_niche_gnn_10x_breast/10x_breast_cancer_spatial_metadata.tsv",
        "out_dir": "data/processed/spatial_emt_niche_gnn_10x_breast",
        "skip_edge_ablation": False,
    },
    {
        "label": "10x_lung_lusc_cytassist",
        "expression": "data/processed/spatial_emt_niche_gnn_10x_lung_lusc/10x_lung_lusc_signature_expression.tsv",
        "metadata": "data/processed/spatial_emt_niche_gnn_10x_lung_lusc/10x_lung_lusc_spatial_metadata.tsv",
        "out_dir": "data/processed/spatial_emt_niche_gnn_10x_lung_lusc",
        "skip_edge_ablation": False,
    },
    {
        "label": "geo_pdac_gse274103",
        "expression": "data/processed/spatial_emt_niche_gnn_geo_pdac/geo_pdac_gse274103_signature_expression.tsv",
        "metadata": "data/processed/spatial_emt_niche_gnn_geo_pdac/geo_pdac_gse274103_spatial_metadata.tsv",
        "out_dir": "data/processed/spatial_emt_niche_gnn_geo_pdac",
        "skip_edge_ablation": True,
    },
    {
        "label": "geo_brain_met_gse179572",
        "expression": "data/processed/spatial_emt_niche_gnn_geo_brain_met/geo_brain_met_gse179572_signature_expression.tsv",
        "metadata": "data/processed/spatial_emt_niche_gnn_geo_brain_met/geo_brain_met_gse179572_spatial_metadata.tsv",
        "out_dir": "data/processed/spatial_emt_niche_gnn_geo_brain_met",
        "skip_edge_ablation": True,
    },
    {
        "label": "10x_prostate_ffpe",
        "expression": "data/processed/spatial_emt_niche_gnn_10x_prostate/10x_prostate_signature_expression.tsv",
        "metadata": "data/processed/spatial_emt_niche_gnn_10x_prostate/10x_prostate_spatial_metadata.tsv",
        "out_dir": "data/processed/spatial_emt_niche_gnn_10x_prostate",
        "skip_edge_ablation": False,
    },
    {
        "label": "10x_ovarian_ffpe",
        "expression": "data/processed/spatial_emt_niche_gnn_10x_ovarian/10x_ovarian_signature_expression.tsv",
        "metadata": "data/processed/spatial_emt_niche_gnn_10x_ovarian/10x_ovarian_spatial_metadata.tsv",
        "out_dir": "data/processed/spatial_emt_niche_gnn_10x_ovarian",
        "skip_edge_ablation": False,
    },
    {
        "label": "10x_colorectal_intestinal_ffpe",
        "expression": "data/processed/spatial_emt_niche_gnn_10x_colorectal/10x_colorectal_signature_expression.tsv",
        "metadata": "data/processed/spatial_emt_niche_gnn_10x_colorectal/10x_colorectal_spatial_metadata.tsv",
        "out_dir": "data/processed/spatial_emt_niche_gnn_10x_colorectal",
        "skip_edge_ablation": False,
    },
]


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Rerun local spatial cohorts with the current scoring and graph code.")
    p.add_argument("--only", nargs="*", default=None, help="Optional cohort labels to rerun.")
    p.add_argument("--ablation-epochs", type=int, default=50)
    p.add_argument("--skip-edge-ablation-all", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    return p


def main() -> None:
    args = parser().parse_args()
    wanted = set(args.only or [])
    selected = [cohort for cohort in COHORTS if not wanted or cohort["label"] in wanted]
    if not selected:
        raise SystemExit("No cohorts selected.")
    for cohort in selected:
        expression = Path(cohort["expression"])
        metadata = Path(cohort["metadata"])
        if not expression.exists() or not metadata.exists():
            print(f"Skipping {cohort['label']}: missing expression or metadata")
            continue
        cmd = [
            sys.executable,
            "scripts/run_spatial_cohort_workflow.py",
            "--expression",
            str(expression),
            "--metadata",
            str(metadata),
            "--out-dir",
            cohort["out_dir"],
            "--ablation-epochs",
            str(args.ablation_epochs),
        ]
        if args.skip_edge_ablation_all or cohort["skip_edge_ablation"]:
            cmd.append("--skip-edge-ablation")
        print(f"Rerunning {cohort['label']}")
        print(" ".join(cmd))
        if not args.dry_run:
            subprocess.run(cmd, check=True)
    if not args.dry_run:
        subprocess.run([sys.executable, "scripts/compare_spatial_cancer_cohorts.py"], check=True)
        subprocess.run([sys.executable, "scripts/spatial_project_status.py"], check=True)
        subprocess.run([sys.executable, "scripts/generate_spatial_project_report.py"], check=True)


if __name__ == "__main__":
    main()
