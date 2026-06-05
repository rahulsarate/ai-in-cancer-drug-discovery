from __future__ import annotations

import argparse
from pathlib import Path

from spatial_emt_niche_gnn.tenx_visium import TENX_LUNG_LUSC, prepare_10x_lung_lusc


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Download and prepare public 10x CytAssist FFPE lung squamous cell carcinoma data.")
    p.add_argument("--raw-dir", default="data/raw/spatial/10x")
    p.add_argument("--out-dir", default="data/processed/spatial_emt_niche_gnn_10x_lung_lusc")
    return p


def main() -> None:
    args = parser().parse_args()
    expression, metadata = prepare_10x_lung_lusc(args.raw_dir, args.out_dir)
    citation = Path(args.out_dir) / "dataset_source.tsv"
    citation.parent.mkdir(parents=True, exist_ok=True)
    citation.write_text(
        "field\tvalue\n" + "\n".join(f"{key}\t{value}" for key, value in TENX_LUNG_LUSC.items()) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {expression}")
    print(f"Wrote {metadata}")
    print(f"Wrote {citation}")


if __name__ == "__main__":
    main()
