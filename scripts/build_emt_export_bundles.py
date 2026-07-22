from __future__ import annotations

import argparse
from pathlib import Path

from emt_state_atlas.export_bundles import build_export_bundles


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Build clinician and researcher export bundles for the EMT atlas.")
    p.add_argument("--root", default=".")
    p.add_argument("--out-dir", default="data/processed/pan_cancer_emt_state_atlas/exports")
    return p


def main() -> None:
    args = parser().parse_args()
    manifest = build_export_bundles(args.root, args.out_dir)
    print(f"Wrote export bundles to {Path(args.out_dir)}")
    print(manifest.tail(2).to_string(index=False))


if __name__ == "__main__":
    main()
