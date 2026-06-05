from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from spatial_emt_niche_gnn.deconvolution import estimate_marker_proxy_compartments


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Estimate marker-proxy cell/niche compartment proportions from spatial scores.")
    p.add_argument("--scores", required=True)
    p.add_argument("--out-dir", required=True)
    return p


def main() -> None:
    args = parser().parse_args()
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    scored = pd.read_csv(args.scores, sep="\t")
    table = estimate_marker_proxy_compartments(scored)
    table.to_csv(out / "cell_type_proxy_proportions.tsv", sep="\t", index=False)
    table["dominant_compartment"].value_counts().rename_axis("dominant_compartment").reset_index(name="spot_count").to_csv(
        out / "cell_type_proxy_summary.tsv", sep="\t", index=False
    )
    print(f"Wrote {out / 'cell_type_proxy_proportions.tsv'}")


if __name__ == "__main__":
    main()
