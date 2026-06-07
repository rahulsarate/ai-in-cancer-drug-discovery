from __future__ import annotations

from pathlib import Path

import pandas as pd


OUT = Path("data/processed/spatial_emt_niche_gnn_htan")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    template = pd.DataFrame(
        [
            {
                "htan_data_file_id": "",
                "sample_id": "HT264P1",
                "atlas": "HTAN WUSTL",
                "cancer_type": "pancreatic_cancer",
                "assay": "10x Visium spatial transcriptomics",
                "access_type": "synapse_or_gen3",
                "synapse_id": "",
                "gen3_guid": "",
                "expected_file_role": "matrix_or_spatial_metadata_or_image",
                "portal_export_date": "",
                "download_status": "pending_portal_file_selection",
                "local_target_dir": "data/raw/spatial/htan/wustl_pdac/HT264P1",
                "notes": "Fill from HTAN portal Download selected files export.",
            }
        ]
    )
    template.to_csv(OUT / "htan_selected_file_manifest_template.tsv", sep="\t", index=False)
    print(f"Wrote {OUT / 'htan_selected_file_manifest_template.tsv'}")


if __name__ == "__main__":
    main()
