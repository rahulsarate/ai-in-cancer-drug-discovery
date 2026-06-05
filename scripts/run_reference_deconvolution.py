from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from spatial_emt_niche_gnn.data import read_spatial_expression
from spatial_emt_niche_gnn.deconvolution import nnls_reference_deconvolution


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Run NNLS reference deconvolution from a cell-type x gene reference table.")
    p.add_argument("--expression", required=True)
    p.add_argument("--reference", required=True, help="TSV with cell_type plus gene columns.")
    p.add_argument("--out-dir", required=True)
    return p


def main() -> None:
    args = parser().parse_args()
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    expression = read_spatial_expression(args.expression)
    reference = pd.read_csv(args.reference, sep="\t")
    result = nnls_reference_deconvolution(expression, reference)
    result.to_csv(out / "reference_deconvolution_nnls.tsv", sep="\t", index=False)
    print(f"Wrote {out / 'reference_deconvolution_nnls.tsv'}")


if __name__ == "__main__":
    main()
