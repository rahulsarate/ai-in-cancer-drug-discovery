from __future__ import annotations

import argparse
from pathlib import Path

from emt_state_atlas.cli import main as emt_cli_main


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Run the EMT atlas v1 workflow on TCGA/Xena-style files.")
    p.add_argument("--expression", required=True)
    p.add_argument("--metadata", required=True)
    p.add_argument("--out-dir", default="data/processed/tcga_xena_v1")
    p.add_argument("--gene-aliases", default="data/raw/gene_aliases/signature_gene_aliases.tsv")
    return p


def main() -> None:
    args = parser().parse_args()
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    import sys

    sys.argv = [
        "emt-score",
        "--expression",
        args.expression,
        "--metadata",
        args.metadata,
        "--out",
        str(out / "emt_scores.tsv"),
        "--summary-out",
        str(out / "cancer_type_summary.tsv"),
        "--survival-out",
        str(out / "survival_associations.tsv"),
        "--validation-out",
        str(out / "output_validation.tsv"),
        "--plots-dir",
        str(out / "plots"),
        "--report-out",
        str(out / "emt_state_atlas_report.md"),
    ]
    if Path(args.gene_aliases).exists():
        sys.argv.extend(["--gene-aliases", args.gene_aliases])
    emt_cli_main()


if __name__ == "__main__":
    main()
