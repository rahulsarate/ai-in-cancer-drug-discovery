from __future__ import annotations

import argparse
from pathlib import Path

from spatial_emt_niche_gnn.tenx_visium import GEO_PDAC_GSE274103, prepare_geo_pdac_gse274103


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Download and prepare GEO GSE274103 treatment-naive PDAC Visium data.")
    p.add_argument("--raw-dir", default="data/raw/spatial/geo")
    p.add_argument("--out-dir", default="data/processed/spatial_emt_niche_gnn_geo_pdac")
    p.add_argument("--max-samples", type=int, default=0, help="Optional quick-test limit.")
    return p


def main() -> None:
    args = parser().parse_args()
    expression, metadata = prepare_geo_pdac_gse274103(
        args.raw_dir,
        args.out_dir,
        max_samples=args.max_samples or None,
    )
    citation = Path(args.out_dir) / "dataset_source.tsv"
    citation.parent.mkdir(parents=True, exist_ok=True)
    citation.write_text(
        "field\tvalue\n" + "\n".join(f"{key}\t{value}" for key, value in GEO_PDAC_GSE274103.items()) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {expression}")
    print(f"Wrote {metadata}")
    print(f"Wrote {citation}")


if __name__ == "__main__":
    main()
