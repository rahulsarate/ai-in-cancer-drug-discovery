from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from emt_state_atlas.validation_layers import (
    aggregate_cancersea_validation,
    integrate_spatial_summary,
    marker_table,
    write_single_cell_report,
    write_spatial_cards,
    write_spatial_report,
)


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Build single-cell and spatial validation layers for the EMT atlas.")
    p.add_argument("--bulk-group-summary", default="data/processed/pan_cancer_emt_state_atlas/cards/cancer_group_state_summary.tsv")
    p.add_argument("--cancersea-summary", default="data/processed/pan_cancer_emt_state_atlas/single_cell_cancersea/cancersea_state_summary.tsv")
    p.add_argument("--cancersea-manifest", default="data/processed/pan_cancer_emt_state_atlas/single_cell_cancersea/cancersea_manifest.tsv")
    p.add_argument("--spatial-summary", default="data/processed/spatial_emt_niche_gnn_comparison/spatial_cancer_cohort_summary.tsv")
    p.add_argument("--out-dir", default="data/processed/pan_cancer_emt_state_atlas/validation")
    p.add_argument("--single-cell-report-out", default="docs/pan_cancer_emt_state_atlas/reports/pan_cancer_emt_single_cell_validation_report.md")
    p.add_argument("--spatial-report-out", default="docs/pan_cancer_emt_state_atlas/reports/pan_cancer_emt_spatial_report.md")
    return p


def read_optional(path: str) -> pd.DataFrame:
    p = Path(path)
    if not p.exists():
        return pd.DataFrame()
    return pd.read_csv(p, sep="\t", low_memory=False)


def main() -> None:
    args = parser().parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    bulk = read_optional(args.bulk_group_summary)
    cancersea = read_optional(args.cancersea_summary)
    manifest = read_optional(args.cancersea_manifest)
    spatial = read_optional(args.spatial_summary)

    validation = aggregate_cancersea_validation(cancersea, bulk)
    markers = marker_table()
    validation.to_csv(out_dir / "single_cell_group_validation_summary.tsv", sep="\t", index=False)
    markers.to_csv(out_dir / "tumor_intrinsic_marker_table.tsv", sep="\t", index=False)
    write_single_cell_report(validation, markers, manifest, args.single_cell_report_out)

    run_level, group_level = integrate_spatial_summary(spatial)
    run_level.to_csv(out_dir / "spatial_run_summary.tsv", sep="\t", index=False)
    group_level.to_csv(out_dir / "spatial_group_summary.tsv", sep="\t", index=False)
    write_spatial_cards(run_level, "data/processed/pan_cancer_emt_state_atlas/cards/spatial_md")
    write_spatial_report(run_level, group_level, args.spatial_report_out)
    print(f"Wrote validation layers to {out_dir}")


if __name__ == "__main__":
    main()
