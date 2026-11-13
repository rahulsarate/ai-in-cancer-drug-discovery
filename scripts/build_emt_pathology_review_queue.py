from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from emt_state_atlas.pathology import (
    build_pathology_review_queue,
    merge_pathology_labels,
    pathology_feature_checklist,
    pathology_label_template,
    write_pathology_report,
)


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Build pathology review queue for spatial EMT validation.")
    p.add_argument("--spatial-run", default="data/processed/pan_cancer_emt_state_atlas/validation/spatial_run_summary.tsv")
    p.add_argument("--out-dir", default="data/processed/pan_cancer_emt_state_atlas/pathology")
    p.add_argument("--report-out", default="docs/pan_cancer_emt_state_atlas/reports/pan_cancer_emt_pathology_review_report.md")
    p.add_argument("--labels", help="Optional expert pathology label TSV/CSV to merge into the queue.")
    p.add_argument("--top-n", type=int, default=80)
    return p


def main() -> None:
    args = parser().parse_args()
    spatial_run = pd.read_csv(args.spatial_run, sep="\t", low_memory=False)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    queue = build_pathology_review_queue(spatial_run, top_n=args.top_n)
    if args.labels:
        label_path = Path(args.labels)
        labels = pd.read_csv(label_path, sep="\t" if label_path.suffix.lower() != ".csv" else ",")
        queue = merge_pathology_labels(queue, labels)
    checklist = pathology_feature_checklist()
    template = pathology_label_template(queue)
    queue.to_csv(out_dir / "pathology_review_queue.tsv", sep="\t", index=False)
    checklist.to_csv(out_dir / "pathology_review_checklist.tsv", sep="\t", index=False)
    template.to_csv(out_dir / "pathology_label_template.tsv", sep="\t", index=False)
    write_pathology_report(queue, checklist, args.report_out)
    print(f"Wrote pathology review queue to {out_dir}")


if __name__ == "__main__":
    main()
