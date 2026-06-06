from __future__ import annotations

from pathlib import Path

import pandas as pd


QUEUE = Path("data/processed/spatial_emt_niche_gnn_pathology_review/pathologist_review_queue.tsv")
OUT = Path("data/processed/spatial_emt_niche_gnn_pathology_review")


REVIEWER_ROLES = [
    {
        "role": "lead_pathologist",
        "preferred_profile": "board-certified pathologist with GI, thoracic, breast, or translational cancer pathology experience",
        "responsibility": "calibrate rubric, score high-impact cases, adjudicate disagreements",
        "minimum_cases": 120,
        "priority": "highest",
    },
    {
        "role": "second_pathologist_or_fellow",
        "preferred_profile": "second attending, pathology fellow, or senior resident under supervision",
        "responsibility": "independent overlap scoring and disagreement discovery",
        "minimum_cases": 100,
        "priority": "high",
    },
    {
        "role": "computational_pathology_scientist",
        "preferred_profile": "computational pathologist or cancer biologist familiar with spatial transcriptomics",
        "responsibility": "check whether morphology labels support transcriptomic interpretation",
        "minimum_cases": 80,
        "priority": "medium",
    },
]

SOURCING_OPTIONS = [
    {
        "option": "academic_pathology_collaborator",
        "best_for": "publication-grade morphology validation and coauthorship",
        "speed": "2-8 weeks",
        "cost": "collaboration/coauthorship or consulting honorarium",
        "strength": "highest credibility, can adjudicate nuanced invasive-edge and stromal contamination calls",
        "risk": "slowest to arrange",
        "recommended_use": "primary route",
    },
    {
        "option": "institutional_tumor_board_or_translational_pathology_core",
        "best_for": "disease-specific expert review",
        "speed": "2-6 weeks",
        "cost": "core/service fee or collaboration",
        "strength": "clinical context and disease-specific morphology expertise",
        "risk": "may require IRB/data-use review even for public data",
        "recommended_use": "primary route if available",
    },
    {
        "option": "pathpresenter_case_share",
        "best_for": "remote expert review of H&E regions",
        "speed": "1-4 weeks after slide/region prep",
        "cost": "platform/account dependent",
        "strength": "pathologist-friendly viewing workflow",
        "risk": "needs image packaging and access control",
        "recommended_use": "best remote review workflow",
    },
    {
        "option": "qupath_offline_review_pack",
        "best_for": "open-source, reproducible research annotation",
        "speed": "1-2 weeks after ROI export",
        "cost": "free software plus expert time",
        "strength": "transparent, scriptable, research-friendly",
        "risk": "less convenient for non-technical reviewers",
        "recommended_use": "best open-source route",
    },
    {
        "option": "verified_expert_network",
        "best_for": "small blinded pilot when academic review is delayed",
        "speed": "days to 2 weeks",
        "cost": "paid per expert/task",
        "strength": "fast access to credential-screened professionals if pathology expertise is available",
        "risk": "must verify specialty, licensing, and conflict-of-interest; not final clinical ground truth",
        "recommended_use": "backup pilot route",
    },
]


def assign_batches(queue: pd.DataFrame) -> pd.DataFrame:
    queue = queue.sort_values(["ai_review_priority", "review_id"], ascending=[False, True]).copy()
    queue["review_phase"] = "primary"
    queue["required_reviewers"] = 1
    queue["blind_ai_scores"] = "yes"
    queue["adjudication_trigger"] = "low_confidence_or_disagreement"

    calibration_ids = queue.head(60).index
    queue.loc[calibration_ids, "review_phase"] = "calibration"
    queue.loc[calibration_ids, "required_reviewers"] = 3
    queue.loc[calibration_ids, "adjudication_trigger"] = "all_calibration_cases_discussed"

    high_impact_mask = queue["ai_suggested_review_class"].isin(
        ["tumor_emt_high", "ecm_invasive_edge_proxy", "stromal_inflated_emt"]
    )
    high_impact_ids = queue[high_impact_mask].head(120).index
    queue.loc[high_impact_ids, "required_reviewers"] = queue.loc[high_impact_ids, "required_reviewers"].clip(lower=2)

    queue["batch_id"] = "BATCH_PRIMARY"
    queue.loc[queue["review_phase"].eq("calibration"), "batch_id"] = "BATCH_CALIBRATION"
    queue.loc[
        queue["review_phase"].eq("primary") & queue["ai_suggested_review_class"].eq("tumor_emt_high"),
        "batch_id",
    ] = "BATCH_TUMOR_EMT"
    queue.loc[
        queue["review_phase"].eq("primary") & queue["ai_suggested_review_class"].eq("stromal_inflated_emt"),
        "batch_id",
    ] = "BATCH_STROMAL_EMT"
    queue.loc[
        queue["review_phase"].eq("primary") & queue["ai_suggested_review_class"].eq("ecm_invasive_edge_proxy"),
        "batch_id",
    ] = "BATCH_INVASIVE_EDGE"
    queue.loc[
        queue["review_phase"].eq("primary") & queue["ai_suggested_review_class"].eq("caf_tam_hypoxic"),
        "batch_id",
    ] = "BATCH_CAF_TAM_HYPOXIA"
    return queue


def write_recruitment_email(out: Path) -> None:
    text = """# Pathologist Review Recruitment Email

Subject: Request for expert review of public spatial transcriptomics H&E regions in cancer EMT/metastasis project

Dear Dr. [Name],

We are building an open, reproducible research pipeline for spatial EMT and
metastatic niche discovery using public cancer spatial transcriptomics data.
The current pipeline identifies candidate tumor EMT, invasive-edge,
stroma-rich/CAF-rich, hypoxia/necrosis, immune/TAM-rich, and vessel-rich
regions. We need expert pathology review to test whether these weak labels are
morphologically plausible and to separate tumor-cell EMT from stromal
contamination.

The review task is research-only and not clinical diagnosis. We would provide a
small blinded calibration set first, then a prioritized review queue with
0-3 scoring fields and confidence ratings. The expected first commitment is
about 60 calibration regions, followed by an optional 100-150 high-impact
regions if the workflow is useful.

We would be grateful for either formal collaboration/coauthorship discussion or
a paid consulting/service arrangement, depending on your preference and
institutional requirements.

Best,
[Name]
"""
    (out / "pathologist_recruitment_email.md").write_text(text, encoding="utf-8")


def write_sop(out: Path) -> None:
    text = """# Pathologist Review SOP

## Review Principles

1. Score morphology without using transcriptomic values first.
2. Mark artifact/acellular regions before assigning biological labels.
3. Use 0-3 scores for EMT-like morphology, stroma, hypoxia/necrosis, immune
   richness, and vessel richness.
4. Use `mixed_ambiguous` when a spot/region cannot separate tumor from stroma.
5. Use `needs_second_review` when morphology is plausible but uncertain.

## Minimum Quality Bar

- Calibration set: all reviewers score the same 60 cases.
- High-impact classes: at least two reviewers for tumor EMT, invasive edge, and
  stromal-inflated EMT.
- Adjudication: lead pathologist resolves cases with disagreement, low
  confidence, or model/pathology mismatch.

## Consensus Rule

Use confidence-weighted agreement. If reviewers disagree between tumor EMT and
stromal-rich/CAF-rich, keep the case as `mixed_ambiguous` unless the lead
pathologist adjudicates it.
"""
    (out / "pathologist_review_sop.md").write_text(text, encoding="utf-8")


def main() -> None:
    if not QUEUE.exists():
        raise SystemExit(f"Missing review queue: {QUEUE}")
    OUT.mkdir(parents=True, exist_ok=True)
    queue = pd.read_csv(QUEUE, sep="\t")
    batches = assign_batches(queue)
    batch_summary = (
        batches.groupby(["batch_id", "review_phase", "ai_suggested_review_class"], dropna=False)
        .agg(review_items=("review_id", "count"), required_reviewers=("required_reviewers", "max"))
        .reset_index()
        .sort_values(["review_phase", "batch_id", "review_items"], ascending=[True, True, False])
    )
    batches.to_csv(OUT / "pathologist_review_batches.tsv", sep="\t", index=False)
    batch_summary.to_csv(OUT / "pathologist_review_batch_summary.tsv", sep="\t", index=False)
    pd.DataFrame(REVIEWER_ROLES).to_csv(OUT / "pathologist_reviewer_roles.tsv", sep="\t", index=False)
    pd.DataFrame(SOURCING_OPTIONS).to_csv(OUT / "pathologist_sourcing_options.tsv", sep="\t", index=False)
    write_recruitment_email(OUT)
    write_sop(OUT)
    print(f"Wrote pathologist review ops pack to {OUT}")


if __name__ == "__main__":
    main()
