from __future__ import annotations

import pandas as pd

from emt_state_atlas.export_bundles import build_export_bundles
from emt_state_atlas.app_tables import group_small_cohort_warnings, state_comparison_table
from emt_state_atlas.annotated_single_cell import (
    add_malignant_stromal_emt_calls,
    normalize_annotation_columns,
    source_requirements_table,
    summarize_tumor_vs_stroma,
)
from emt_state_atlas.clinical import (
    clinical_group_summary,
    clinical_warnings,
    covariate_adjusted_event_screen,
    survival_by_stratum,
)
from emt_state_atlas.pathology import (
    build_pathology_review_queue,
    merge_pathology_labels,
    pathology_feature_checklist,
    pathology_label_template,
)
from emt_state_atlas.lineage_targets import add_model_cancer_groups, summarize_depmap_by_cancer_group
from emt_state_atlas.therapy import disease_group_target_recommendations
from emt_state_atlas.validation_layers import aggregate_cancersea_validation, integrate_spatial_summary, marker_table


def test_clinical_layer_builds_group_warnings_and_survival_screen() -> None:
    scores = pd.DataFrame(
        {
            "cancer_group": ["Breast Cancer"] * 40,
            "event": [1] * 10 + [0] * 30,
            "time": list(range(10, 50)),
            "emt_score": list(range(40)),
            "partial_emt_score": list(reversed(range(40))),
            "stromal_warning": [False] * 25 + [True] * 15,
            "confidence_label": ["high"] * 20 + ["low"] * 20,
            "ajcc_pathologic_tumor_stage": ["Stage II"] * 40,
            "histological_grade": ["G2"] * 40,
        }
    )

    summary = clinical_group_summary(scores)
    warnings = clinical_warnings(summary)
    survival = survival_by_stratum(scores)
    covariate = covariate_adjusted_event_screen(scores)

    assert summary.loc[0, "sample_count"] == 40
    assert "high_stromal_inflation_risk" in warnings.loc[0, "warnings"]
    assert set(survival["method"]) == {"median_split_event_rate_screen"}
    assert {"emt_score", "partial_emt_score"}.issubset(set(survival["score"]))
    assert set(covariate["method"]) == {"covariate_stratified_median_event_rate_screen"}


def test_validation_layers_aggregate_single_cell_and_spatial_contexts() -> None:
    cancersea = pd.DataFrame(
        {
            "dataset": ["EXP0053", "EXP0054"],
            "cancer_group": ["Breast Cancer", "Breast Cancer"],
            "emt_score_count": [100, 50],
            "emt_score_mean": [0.2, 0.5],
            "partial_emt_score_mean": [0.1, 0.2],
        }
    )
    bulk = pd.DataFrame({"cancer_group": ["Breast Cancer"], "sample_count": [1000], "mesenchymal_like_fraction": [0.3]})
    validation = aggregate_cancersea_validation(cancersea, bulk)

    spatial = pd.DataFrame(
        {
            "run": ["10x_breast_ffpe_idc"],
            "spots": [2500],
            "emt_niche_fraction": [0.26],
            "tumor_cell_emt_fraction": [0.11],
            "stromal_inflated_fraction": [0.14],
            "mean_caf_tam": [0.2],
            "mean_hypoxia": [0.3],
            "mean_predicted_emt_niche_probability": [0.4],
            "edges": [1000],
        }
    )
    run_level, group_level = integrate_spatial_summary(spatial)

    assert validation.loc[0, "single_cells_or_profiles"] == 150
    assert validation.loc[0, "single_cell_emt_score_mean"] == (0.2 * 100 + 0.5 * 50) / 150
    assert len(marker_table()) >= 10
    assert run_level.loc[0, "cancer_group"] == "Breast Cancer"
    assert "CAF/stromal-rich EMT" in run_level.loc[0, "spatial_context"]
    assert group_level.loc[0, "total_spots"] == 2500


def test_disease_group_target_recommendations_uses_state_context() -> None:
    ranking = pd.DataFrame(
        {
            "target": ["AXL", "PTK2"],
            "family": ["AXL_TAM", "FAK_SRC_integrin"],
            "priority_score": [0.8, 0.6],
        }
    )
    groups = pd.DataFrame(
        {
            "cancer_group": ["Head and Neck Cancer"],
            "mesenchymal_like_fraction": [0.5],
            "stromal_dominant_fraction": [0.2],
            "hybrid_fraction": [0.1],
            "high_confidence_fraction": [0.3],
        }
    )

    recs = disease_group_target_recommendations(ranking, groups, top_n_per_group=2)

    assert list(recs["target"]) == ["AXL", "PTK2"]
    assert recs.loc[0, "disease_priority_score"] > recs.loc[1, "disease_priority_score"]
    assert "validation_assays" in recs.columns


def test_annotated_single_cell_separates_malignant_and_stromal_emt() -> None:
    raw = pd.DataFrame(
        {
            "sample_id": ["c1", "c2", "c3", "c4", "c5", "c6"],
            "cell_type": ["malignant", "malignant", "CAF", "fibroblast", "T cell", "macrophage"],
            "malignant_status": ["malignant", "malignant", "non-malignant", "non-malignant", "non-malignant", "non-malignant"],
            "emt_score": [2.0, 1.5, 2.2, 1.8, 0.1, 0.2],
            "partial_emt_score": [0.8, 0.6, 0.9, 0.7, 0.0, 0.1],
            "stromal_fibroblast": [0.1, 0.2, 2.0, 1.8, 0.1, 0.1],
            "caf_tam_niche": [0.1, 0.2, 1.4, 1.1, 0.4, 0.9],
        }
    )
    normalized = normalize_annotation_columns(raw, source="TISCH2", dataset="demo", cancer_group="Pancreatic Cancer")
    called = add_malignant_stromal_emt_calls(normalized)
    summary = summarize_tumor_vs_stroma(called)

    assert set(called["cell_compartment"]) >= {"malignant", "caf_stromal", "t_cell", "myeloid_tam"}
    assert {"tam_myeloid_emt_like_call", "caf_tam_context_emt_call", "malignancy_confidence"}.issubset(called.columns)
    assert summary.loc[0, "malignant_cells"] == 2
    assert summary.loc[0, "caf_stromal_cells"] == 2
    assert len(source_requirements_table()) == 4


def test_pathology_queue_excludes_demo_and_prioritizes_real_spatial_runs() -> None:
    spatial = pd.DataFrame(
        {
            "run": ["synthetic_demo", "10x_breast_ffpe_idc"],
            "cancer_group": ["Demo / Synthetic", "Breast Cancer"],
            "spots": [100, 2500],
            "emt_niche_fraction": [0.9, 0.25],
            "tumor_cell_emt_fraction": [0.9, 0.12],
            "stromal_inflated_fraction": [0.0, 0.14],
            "mean_hypoxia": [0.0, 0.1],
            "mean_caf_tam": [0.0, 0.1],
            "mean_predicted_emt_niche_probability": [0.9, 0.3],
        }
    )
    queue = build_pathology_review_queue(spatial)

    assert list(queue["run"]) == ["10x_breast_ffpe_idc"]
    assert "caf_stromal_interface" in queue.loc[0, "review_focus"]
    assert len(pathology_feature_checklist()) >= 5


def test_pathology_label_template_and_merge_marks_reviewed_regions() -> None:
    queue = pd.DataFrame(
        {
            "run": ["10x_breast_ffpe_idc"],
            "cancer_group": ["Breast Cancer"],
            "minimum_review_regions": [2],
            "review_status": ["pending_pathologist_review"],
        }
    )
    template = pathology_label_template(queue)
    labels = template.copy()
    labels.loc[:, "reviewer_id"] = "pathologist_1"
    labels.loc[0, "invasive_edge_label"] = "yes"
    labels.loc[1, "invasive_edge_label"] = "no"
    labels.loc[:, "tumor_intrinsic_emt_label"] = ["present", "positive"]

    merged = merge_pathology_labels(queue, labels)

    assert len(template) == 2
    assert merged.loc[0, "review_status"] == "expert_review_complete"
    assert merged.loc[0, "reviewed_regions"] == 2
    assert merged.loc[0, "invasive_edge_label_fraction"] == 0.5
    assert merged.loc[0, "tumor_intrinsic_emt_label_fraction"] == 1.0


def test_export_bundle_manifest_records_missing_and_existing_files(tmp_path) -> None:
    root = tmp_path / "project"
    (root / "docs/pan_cancer_emt_state_atlas").mkdir(parents=True)
    (root / "docs/pan_cancer_emt_state_atlas/work_done_and_remaining_status.md").write_text("status", encoding="utf-8")

    manifest = build_export_bundles(root, tmp_path / "exports")

    assert (tmp_path / "exports/clinician_bundle.zip").exists()
    assert (tmp_path / "exports/researcher_bundle.zip").exists()
    assert {True, False}.issubset(set(manifest["exists"]))


def test_lineage_targets_and_app_tables_build_expected_summaries() -> None:
    models = pd.DataFrame(
        {
            "ModelID": ["ACH-1", "ACH-2"],
            "CellLineName": ["A", "B"],
            "OncotreeLineage": ["Breast", "Lung"],
            "OncotreePrimaryDisease": ["Breast Cancer", "Non-Small Cell Lung Cancer"],
        }
    )
    gene_effect = pd.DataFrame({"ModelID": ["ACH-1", "ACH-2"], "AXL (558)": [-0.8, -0.1], "PTK2 (5747)": [-0.2, -0.7]})
    summary = summarize_depmap_by_cancer_group(gene_effect, models)
    grouped = add_model_cancer_groups(models)

    scores = pd.DataFrame(
        {
            "sample_id": ["s1", "s2", "s3"],
            "cancer_group": ["Breast Cancer", "Breast Cancer", "Lung Cancer"],
            "consensus_emt_state": ["epithelial", "mesenchymal", "mesenchymal"],
            "emt_score": [0.1, 1.2, 0.9],
            "partial_emt_score": [0.2, 0.8, 0.7],
        }
    )
    state_table = state_comparison_table(scores)
    warnings = group_small_cohort_warnings(
        pd.DataFrame(
            {
                "cancer_group": ["Breast Cancer"],
                "sample_count": [20],
                "high_confidence_fraction": [0.1],
                "stromal_dominant_fraction": [0.3],
            }
        )
    )

    assert set(grouped["cancer_group"]) == {"Breast Cancer", "Lung Cancer"}
    assert {"Breast Cancer", "Lung Cancer"}.issubset(set(summary["cancer_group"]))
    assert state_table["state_fraction"].max() == 1.0
    assert "small_cohort" in warnings.loc[0, "app_warning"]
