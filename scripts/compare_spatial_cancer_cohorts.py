from __future__ import annotations

from pathlib import Path

import pandas as pd

from compare_spatial_demo_vs_real import summarize_run, write_interpretation


RUNS = [
    ("synthetic_demo", "data/processed/spatial_emt_niche_gnn_demo"),
    ("10x_breast_ffpe_idc", "data/processed/spatial_emt_niche_gnn_10x_breast"),
    ("10x_lung_lusc_cytassist", "data/processed/spatial_emt_niche_gnn_10x_lung_lusc"),
    ("geo_pdac_gse274103", "data/processed/spatial_emt_niche_gnn_geo_pdac"),
    ("geo_brain_met_gse179572", "data/processed/spatial_emt_niche_gnn_geo_brain_met"),
    ("10x_prostate_ffpe", "data/processed/spatial_emt_niche_gnn_10x_prostate"),
    ("10x_ovarian_ffpe", "data/processed/spatial_emt_niche_gnn_10x_ovarian"),
    ("10x_colorectal_intestinal_ffpe", "data/processed/spatial_emt_niche_gnn_10x_colorectal"),
]


def main() -> None:
    rows = [summarize_run(label, Path(folder)) for label, folder in RUNS]
    summary = pd.DataFrame(rows)
    out = Path("data/processed/spatial_emt_niche_gnn_comparison/spatial_cancer_cohort_summary.tsv")
    out.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(out, sep="\t", index=False)
    write_interpretation(summary, out.with_suffix(".md"), title="Spatial EMT Niche Multi-Cancer Cohort Comparison")
    print(f"Wrote {out}")
    print(f"Wrote {out.with_suffix('.md')}")


if __name__ == "__main__":
    main()
