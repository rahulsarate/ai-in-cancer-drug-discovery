from __future__ import annotations

import argparse
from pathlib import Path

from spatial_emt_niche_gnn.data import read_spatial_expression, read_spatial_metadata
from spatial_emt_niche_gnn.export import write_lightweight_h5ad


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Export standardized spatial tables to a lightweight h5ad-style file.")
    p.add_argument("--expression", required=True)
    p.add_argument("--metadata", required=True)
    p.add_argument("--out", required=True)
    return p


def main() -> None:
    args = parser().parse_args()
    out = write_lightweight_h5ad(read_spatial_expression(args.expression), read_spatial_metadata(args.metadata), args.out)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
