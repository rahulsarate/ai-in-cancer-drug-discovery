from __future__ import annotations

import argparse
from pathlib import Path

from spatial_emt_niche_gnn.data import make_demo_spatial_dataset, write_spatial_manifest


PUBLIC_SPATIAL_SOURCES = [
    {
        "source": "10x Visium Discovery Hub",
        "dataset_family": "public_10x_visium_cancer",
        "url": "https://www.10xgenomics.com/visium-discovery-hub",
        "recommended_use": "Starter Visium cancer slides with standardized Space Ranger outputs.",
        "risk_note": "Vendor examples are clean but may not represent independent clinical cohorts.",
    },
    {
        "source": "HEST-1k",
        "dataset_family": "hest_1k_histology_spatial",
        "url": "https://github.com/mahmoodlab/hest",
        "recommended_use": "Scale-up multimodal spatial transcriptomics plus H&E foundation embeddings.",
        "risk_note": "Large multimodal data; use selected cancer cohorts first.",
    },
    {
        "source": "HTAN Data Portal",
        "dataset_family": "htan_spatial_cancer",
        "url": "https://data.humantumoratlas.org/",
        "recommended_use": "External validation with disease-specific cancer atlases.",
        "risk_note": "Portal exports vary by assay and study; metadata harmonization is non-trivial.",
    },
    {
        "source": "GEO",
        "dataset_family": "geo_visium_cancer",
        "url": "https://www.ncbi.nlm.nih.gov/geo/",
        "recommended_use": "Independent published spatial cohorts.",
        "risk_note": "Formats vary widely; require dataset-specific adapters.",
    },
]


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Create spatial data manifest and optional synthetic demo dataset.")
    p.add_argument("--out-dir", default="data/processed/spatial_emt_niche_gnn_demo")
    p.add_argument("--make-demo", action="store_true", help="Generate a synthetic Visium-like demo matrix.")
    return p


def main() -> None:
    args = parser().parse_args()
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    rows = list(PUBLIC_SPATIAL_SOURCES)
    if args.make_demo:
        expression, metadata = make_demo_spatial_dataset(out)
        rows.append(
            {
                "source": "synthetic_demo",
                "dataset_family": "demo_spatial_emt_niche",
                "url": "",
                "expression_path": str(expression),
                "metadata_path": str(metadata),
                "recommended_use": "Smoke-test the complete spatial EMT niche graph workflow.",
                "risk_note": "Synthetic data are for pipeline validation only, not biological claims.",
            }
        )
    manifest = write_spatial_manifest(rows, out / "spatial_manifest.tsv")
    print(f"Wrote {out / 'spatial_manifest.tsv'} ({len(manifest)} rows)")


if __name__ == "__main__":
    main()
