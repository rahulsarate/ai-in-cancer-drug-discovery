from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Summarize per-spot NNLS reference deconvolution by cohort metadata.")
    p.add_argument("--deconvolution", required=True)
    p.add_argument("--metadata", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--groups", nargs="*", default=["cohort", "patient_id", "sample_id", "site_label", "progression_label"])
    return p


def main() -> None:
    args = parser().parse_args()
    deconv = pd.read_csv(args.deconvolution, sep="\t")
    metadata = pd.read_csv(args.metadata, sep="\t")
    table = deconv.merge(metadata, on="spot_id", how="left")
    cell_cols = [
        col
        for col in deconv.columns
        if col not in {"spot_id", "nnls_residual", "deconvolution_method"}
    ]
    group_cols = [col for col in args.groups if col in table.columns]
    summary = (
        table.groupby(group_cols, dropna=False)
        .agg(
            spots=("spot_id", "count"),
            mean_nnls_residual=("nnls_residual", "mean"),
            **{f"mean_{col}": (col, "mean") for col in cell_cols},
        )
        .reset_index()
    )
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(out, sep="\t", index=False)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
