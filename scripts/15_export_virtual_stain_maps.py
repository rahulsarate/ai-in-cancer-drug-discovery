from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from emt_virtual_spatial_staining.export import export_geojson, export_he_overlay, export_map_panel, slide_summary


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Export EMT-ViSTA spatial maps and hotspot regions.")
    p.add_argument("--predictions", required=True)
    p.add_argument("--out-dir", required=True)
    return p


def main() -> None:
    args = parser().parse_args()
    predictions = pd.read_csv(args.predictions, sep="\t", low_memory=False)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = slide_summary(predictions)
    summary.to_csv(out_dir / "virtual_stain_slide_summary.tsv", sep="\t", index=False)
    for dataset_id, group in predictions.groupby("dataset_id", sort=False):
        safe_name = "".join(character if character.isalnum() or character in "-_" else "_" for character in str(dataset_id))
        export_geojson(group, out_dir / f"{safe_name}_hotspots.geojson")
        export_map_panel(group, out_dir / f"{safe_name}_virtual_stains.png")
        export_he_overlay(group, out_dir / f"{safe_name}_he_overlay.png")
    print(f"Exported maps for {predictions['dataset_id'].nunique()} datasets to {out_dir}")


if __name__ == "__main__":
    main()
