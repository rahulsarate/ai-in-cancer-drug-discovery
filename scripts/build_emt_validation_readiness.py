from __future__ import annotations

import argparse
from pathlib import Path

from emt_state_atlas.validation_readiness import validation_readiness_table, write_validation_readiness_report


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Build validation cohort readiness table for the EMT atlas.")
    p.add_argument("--out", default="data/processed/pan_cancer_emt_state_atlas/validation/validation_cohort_readiness.tsv")
    p.add_argument("--report-out", default="docs/pan_cancer_emt_state_atlas/reports/pan_cancer_emt_validation_readiness_report.md")
    return p


def main() -> None:
    args = parser().parse_args()
    frame = validation_readiness_table()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(out, sep="\t", index=False)
    write_validation_readiness_report(frame, args.report_out)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
