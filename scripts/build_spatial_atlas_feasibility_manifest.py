from __future__ import annotations

from pathlib import Path

import pandas as pd


ATLASES = [
    {
        "resource": "SpatialTME",
        "url": "https://www.spatialtme.yelab.site/",
        "scope": "296 spatial slides across 19 cancer types with histology and TME annotations.",
        "fit_for_project": "Useful comparator for immune/stromal spatial niches and CAF/TAM validation.",
        "download_status": "portal_review_required",
        "next_action": "Identify downloadable 10x Visium matrix files and map them to standard expression/metadata tables.",
    },
    {
        "resource": "SCAR",
        "url": "https://scaratlas.com/",
        "scope": "Cancer single-cell and spatial atlas resource; SCAR_ST includes human cancer ST datasets.",
        "fit_for_project": "Useful dataset discovery layer for additional pancreatic, breast, lung, ovarian, prostate, and colorectal cohorts.",
        "download_status": "portal_review_required",
        "next_action": "Use SCAR_ST dataset detail pages to identify GEO/SRA source accessions for direct reproducible download.",
    },
    {
        "resource": "SpatialDB",
        "url": "https://spatialomics.org/SpatialDB/",
        "scope": "Curated spatial transcriptomics database across tissues and species.",
        "fit_for_project": "Useful cross-check for whether chosen cohorts have independent curated source metadata.",
        "download_status": "feasibility_manifest_ready",
        "next_action": "Cross-reference current GEO/10x/HTAN cohorts against SpatialDB entries.",
    },
    {
        "resource": "SMTdb",
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC12596269/",
        "scope": "Cancer spatial meta-transcriptome resource with hundreds of tumor/normal slices.",
        "fit_for_project": "Potential future pan-cancer validation resource if processed matrices are downloadable.",
        "download_status": "literature_review_ready",
        "next_action": "Check supplementary data availability and source accession mapping.",
    },
]


def main() -> None:
    out = Path("data/processed/spatial_emt_niche_gnn_blockers/spatial_atlas_feasibility.tsv")
    out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(ATLASES).to_csv(out, sep="\t", index=False)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
