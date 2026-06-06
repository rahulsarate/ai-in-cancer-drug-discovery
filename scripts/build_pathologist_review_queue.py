from __future__ import annotations

from pathlib import Path

import pandas as pd


INPUTS = [
    Path("data/processed/spatial_emt_niche_gnn_10x_breast/spatial_emt_niche_scores.tsv"),
    Path("data/processed/spatial_emt_niche_gnn_geo_met_pdac_gse274557/spatial_emt_niche_scores.tsv"),
    Path("data/processed/spatial_emt_niche_gnn_geo_met_pdac_gse274557_fullprep/spatial_emt_niche_scores.tsv"),
]
OUT = Path("data/processed/spatial_emt_niche_gnn_pathology_review")
REVIEW_CLASSES = [
    "tumor_rich_epithelial",
    "invasive_edge",
    "stroma_rich_caf_rich",
    "necrosis_hypoxia",
    "immune_tam_rich",
    "vessel_angiogenic",
    "artifact_acellular",
    "mixed_ambiguous",
]


def zrank(series: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce").fillna(0)
    if numeric.std() == 0:
        return pd.Series(0.0, index=series.index)
    return (numeric - numeric.mean()) / numeric.std()


def load_candidate_rows(path: Path, max_per_group: int = 8) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    use_cols = [
        "spot_id",
        "sample_id",
        "cohort",
        "cancer_type",
        "disease",
        "patient_id",
        "site_label",
        "progression_label",
        "x",
        "y",
        "pixel_x",
        "pixel_y",
        "epithelial",
        "mesenchymal",
        "emt_score",
        "partial_emt_score",
        "stromal_contamination_risk",
        "immune_context",
        "caf_tam_niche",
        "hypoxia",
        "ecm_remodeling",
        "angiogenesis",
        "ferroptosis_window",
        "tumor_cell_emt_candidate",
        "stromal_inflated_emt_candidate",
        "emt_niche_label",
        "tile_brightness_mean",
        "hematoxylin_proxy_mean",
        "eosin_proxy_mean",
        "tissue_dark_fraction",
    ]
    header = pd.read_csv(path, sep="\t", nrows=0).columns.tolist()
    cols = [col for col in use_cols if col in header]
    df = pd.read_csv(path, sep="\t", usecols=cols)
    for col in ["patient_id", "site_label", "progression_label"]:
        if col not in df:
            df[col] = ""

    score_defs = {
        "tumor_emt_high": ["emt_score", "partial_emt_score", "epithelial"],
        "stromal_inflated_emt": ["stromal_contamination_risk", "caf_tam_niche", "mesenchymal"],
        "caf_tam_hypoxic": ["caf_tam_niche", "hypoxia", "immune_context"],
        "ecm_invasive_edge_proxy": ["ecm_remodeling", "partial_emt_score", "stromal_contamination_risk"],
        "angiogenic_vessel_proxy": ["angiogenesis", "hypoxia"],
        "ferroptosis_window_proxy": ["ferroptosis_window", "emt_score"],
    }
    candidates = []
    for label, columns in score_defs.items():
        present = [col for col in columns if col in df]
        if not present:
            continue
        priority = sum(zrank(df[col]) for col in present)
        ranked = df.assign(ai_suggested_review_class=label, ai_review_priority=priority)
        group_cols = [col for col in ["cohort", "sample_id", "site_label"] if col in ranked]
        top = (
            ranked.sort_values("ai_review_priority", ascending=False)
            .groupby(group_cols, dropna=False)
            .head(max_per_group)
            .copy()
        )
        candidates.append(top)
    if not candidates:
        return pd.DataFrame()
    result = pd.concat(candidates, ignore_index=True)
    result = result.sort_values("ai_review_priority", ascending=False)
    result = result.drop_duplicates(["spot_id", "ai_suggested_review_class"])
    result["source_scores_path"] = str(path)
    return result


def add_expert_fields(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.insert(0, "review_id", [f"REV-{i:05d}" for i in range(1, len(df) + 1)])
    df["expert_region_class_options"] = "|".join(REVIEW_CLASSES)
    df["expert_region_class"] = ""
    df["expert_confidence_options"] = "low|medium|high"
    df["expert_confidence"] = ""
    df["expert_emt_morphology_score_0_3"] = ""
    df["expert_stromal_score_0_3"] = ""
    df["expert_hypoxia_necrosis_score_0_3"] = ""
    df["expert_immune_score_0_3"] = ""
    df["expert_vessel_score_0_3"] = ""
    df["expert_artifact_flag_yes_no"] = ""
    df["expert_action_options"] = "accept_ai_label|revise_label|exclude_artifact|needs_second_review"
    df["expert_action"] = ""
    df["expert_notes"] = ""
    return df


def main() -> None:
    frames = [load_candidate_rows(path) for path in INPUTS]
    queue = pd.concat([frame for frame in frames if not frame.empty], ignore_index=True)
    if queue.empty:
        raise SystemExit("No spatial EMT score tables were found for pathologist queue generation.")
    queue = queue.sort_values("ai_review_priority", ascending=False).head(600)
    queue = add_expert_fields(queue)
    summary = (
        queue.groupby(["cohort", "ai_suggested_review_class"], dropna=False)
        .size()
        .reset_index(name="review_items")
        .sort_values(["cohort", "review_items"], ascending=[True, False])
    )
    OUT.mkdir(parents=True, exist_ok=True)
    queue.to_csv(OUT / "pathologist_review_queue.tsv", sep="\t", index=False)
    summary.to_csv(OUT / "pathologist_review_queue_summary.tsv", sep="\t", index=False)
    print(f"Wrote {OUT / 'pathologist_review_queue.tsv'}")


if __name__ == "__main__":
    main()
