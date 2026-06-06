from __future__ import annotations

from pathlib import Path

import pandas as pd


HTAN_WUSTL_PDAC_SAMPLES = [
    "HT264P1",
    "HT270P1",
    "HT284P1",
    "HT288P1",
    "HT224P1",
    "HT231P1",
    "HT231P1-2",
    "HT232P1",
    "HT232P1-2",
    "HT259P1",
    "HT306P1",
    "HT306P1-2",
    "HT306P1-3",
    "HT306P1-4",
    "HT242P1",
]


def main() -> None:
    out_dir = Path("data/processed/spatial_emt_niche_gnn_htan")
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = [
        {
            "atlas": "HTAN WUSTL",
            "sample_id": sample,
            "cancer_type": "pancreatic_cancer",
            "assay": "10x Visium spatial transcriptomics",
            "expected_level": "Level 3 or portal-exported matrix/spatial metadata",
            "portal_url": "https://data.humantumoratlas.org/",
            "reference_note": "Reported as HTAN WUSTL 10x Visium pancreatic cancer files in Nature Communications 2024 tight-junction/PET imaging study.",
            "pipeline_status": "manifest_target_ready_download_pending",
        }
        for sample in HTAN_WUSTL_PDAC_SAMPLES
    ]
    pd.DataFrame(rows).to_csv(out_dir / "htan_wustl_pdac_manifest.tsv", sep="\t", index=False)
    readme = [
        "# HTAN WUSTL PDAC Spatial Manifest",
        "",
        "This manifest selects one HTAN spatial atlas target for external validation.",
        "The next executable step is to use the HTAN Data Portal Files tab to export/download the matching matrix and spatial metadata files, then adapt them to the same `spot_id` expression/metadata tables used by the 10x/GEO workflows.",
        "",
        "Chosen first atlas: HTAN WUSTL 10x Visium pancreatic cancer.",
        "Reason: it matches the current PDAC/metastasis focus and is cited as public HTAN Visium pancreatic cancer material.",
    ]
    (out_dir / "README.md").write_text("\n".join(readme) + "\n", encoding="utf-8")
    print(f"Wrote {out_dir / 'htan_wustl_pdac_manifest.tsv'}")


if __name__ == "__main__":
    main()
