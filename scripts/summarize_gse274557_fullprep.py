from __future__ import annotations

from pathlib import Path

import pandas as pd


SCORES = Path("data/processed/spatial_emt_niche_gnn_geo_met_pdac_gse274557_fullprep/spatial_emt_niche_scores.tsv")
OUT_DIR = Path("data/processed/spatial_emt_niche_gnn_geo_met_pdac_gse274557_fullprep")


def summarize(groups: list[str], out_name: str) -> None:
    scores = pd.read_csv(SCORES, sep="\t")
    metric_cols = [
        "emt_niche_label",
        "stromal_inflated_emt_candidate",
        "tumor_cell_emt_candidate",
        "partial_emt_score",
        "caf_tam_niche",
        "hypoxia",
        "ecm_remodeling",
        "angiogenesis",
        "ferroptosis_window",
    ]
    group_cols = [col for col in groups if col in scores.columns]
    summary = (
        scores.groupby(group_cols, dropna=False)
        .agg(
            spots=("spot_id", "count"),
            emt_niche_fraction=("emt_niche_label", "mean"),
            stromal_inflated_fraction=("stromal_inflated_emt_candidate", "mean"),
            tumor_cell_emt_fraction=("tumor_cell_emt_candidate", "mean"),
            **{f"mean_{col}": (col, "mean") for col in metric_cols if col.endswith("_score") or col in {"caf_tam_niche", "hypoxia", "ecm_remodeling", "angiogenesis", "ferroptosis_window"}},
        )
        .reset_index()
    )
    path = OUT_DIR / out_name
    summary.to_csv(path, sep="\t", index=False)
    print(f"Wrote {path}")


def main() -> None:
    summarize(["site_label", "progression_label"], "gse274557_full_site_summary.tsv")
    summarize(["patient_id", "site_label", "progression_label"], "gse274557_full_patient_site_summary.tsv")


if __name__ == "__main__":
    main()
