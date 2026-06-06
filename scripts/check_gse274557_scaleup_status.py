from __future__ import annotations

from pathlib import Path

import pandas as pd


RAW_DIR = Path("data/raw/spatial/geo/GSE274557")
PILOT_MANIFEST = Path("data/processed/spatial_emt_niche_gnn_geo_met_pdac_gse274557/gse274557_sample_manifest.tsv")
FULLPREP_MANIFEST = Path("data/processed/spatial_emt_niche_gnn_geo_met_pdac_gse274557_fullprep/gse274557_sample_manifest.tsv")
OUT = Path("data/processed/spatial_emt_niche_gnn_blockers/gse274557_scaleup_status.tsv")


def main() -> None:
    manifest_path = FULLPREP_MANIFEST if FULLPREP_MANIFEST.exists() else PILOT_MANIFEST
    manifest = pd.read_csv(manifest_path, sep="\t")
    non_pdx = manifest[~manifest["is_pdx"].astype(bool)].copy()
    rows = []
    for _, row in non_pdx.iterrows():
        sample_dir = RAW_DIR / str(row["geo_accession"])
        h5_path = sample_dir / Path(row["h5_url"]).name
        spatial_path = sample_dir / Path(row["spatial_url"]).name
        rows.append(
            {
                "geo_accession": row["geo_accession"],
                "sample_title": row["sample_title"],
                "patient_id": row["patient_id"],
                "site_label": row["site_label"],
                "progression_label": row["progression_label"],
                "manifest_path": str(manifest_path),
                "h5_downloaded": h5_path.exists(),
                "spatial_downloaded": spatial_path.exists(),
                "raw_sample_complete": h5_path.exists() and spatial_path.exists(),
                "h5_bytes": h5_path.stat().st_size if h5_path.exists() else 0,
                "spatial_bytes": spatial_path.stat().st_size if spatial_path.exists() else 0,
            }
        )
    status = pd.DataFrame(rows)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    status.to_csv(OUT, sep="\t", index=False)
    summary = {
        "non_pdx_samples": len(status),
        "raw_sample_complete": int(status["raw_sample_complete"].sum()),
        "patients": status["patient_id"].nunique(),
        "downloaded_bytes": int(status[["h5_bytes", "spatial_bytes"]].sum().sum()),
    }
    pd.DataFrame([summary]).to_csv(OUT.with_name("gse274557_scaleup_summary.tsv"), sep="\t", index=False)
    print(f"Wrote {OUT}")
    print(f"Wrote {OUT.with_name('gse274557_scaleup_summary.tsv')}")


if __name__ == "__main__":
    main()
