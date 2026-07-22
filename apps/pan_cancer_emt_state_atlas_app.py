from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCORES = ROOT / "data/processed/pan_cancer_emt_state_atlas/cards/emt_scores_with_consensus.tsv"
DEFAULT_STATE_SUMMARY = ROOT / "data/processed/pan_cancer_emt_state_atlas/cards/cancer_type_state_summary.tsv"
DEFAULT_GROUP_SUMMARY = ROOT / "data/processed/pan_cancer_emt_state_atlas/cards/cancer_group_state_summary.tsv"
DEFAULT_REQUESTED_GROUPS = ROOT / "data/processed/pan_cancer_emt_state_atlas/cards/requested_cancer_groups.tsv"
DEFAULT_TARGETS = ROOT / "data/processed/target_ranker_real_evidence_v1/target_ranking.tsv"
DEFAULT_DISEASE_TARGETS = ROOT / "data/processed/pan_cancer_emt_state_atlas/cards/target_disease_group_recommendations.tsv"
DEFAULT_CLINICAL = ROOT / "data/processed/pan_cancer_emt_state_atlas/clinical/clinical_group_summary.tsv"
DEFAULT_CLINICAL_SURVIVAL = ROOT / "data/processed/pan_cancer_emt_state_atlas/clinical/clinical_survival_by_group.tsv"
DEFAULT_CLINICAL_COVARIATE = ROOT / "data/processed/pan_cancer_emt_state_atlas/clinical/clinical_covariate_adjusted_screen.tsv"
DEFAULT_CLINICAL_COX = ROOT / "data/processed/pan_cancer_emt_state_atlas/clinical/clinical_multivariable_cox_models.tsv"
DEFAULT_CLINICAL_WARNINGS = ROOT / "data/processed/pan_cancer_emt_state_atlas/clinical/clinical_warnings.tsv"
DEFAULT_SINGLE_CELL = ROOT / "data/processed/pan_cancer_emt_state_atlas/validation/single_cell_group_validation_summary.tsv"
DEFAULT_ANNOTATED_SC = ROOT / "data/processed/pan_cancer_emt_state_atlas/annotated_single_cell/tumor_vs_stroma_emt_summary.tsv"
DEFAULT_ANNOTATED_COMPARTMENTS = ROOT / "data/processed/pan_cancer_emt_state_atlas/annotated_single_cell/annotated_compartment_summary.tsv"
DEFAULT_SC_REQUIREMENTS = ROOT / "data/processed/pan_cancer_emt_state_atlas/annotated_single_cell/external_single_cell_source_requirements.tsv"
DEFAULT_MARKERS = ROOT / "data/processed/pan_cancer_emt_state_atlas/validation/tumor_intrinsic_marker_table.tsv"
DEFAULT_SPATIAL_GROUP = ROOT / "data/processed/pan_cancer_emt_state_atlas/validation/spatial_group_summary.tsv"
DEFAULT_SPATIAL_RUN = ROOT / "data/processed/pan_cancer_emt_state_atlas/validation/spatial_run_summary.tsv"
DEFAULT_PATHOLOGY_QUEUE = ROOT / "data/processed/pan_cancer_emt_state_atlas/pathology/pathology_review_queue.tsv"
DEFAULT_PATHOLOGY_CHECKLIST = ROOT / "data/processed/pan_cancer_emt_state_atlas/pathology/pathology_review_checklist.tsv"
DEFAULT_APP_WARNINGS = ROOT / "data/processed/pan_cancer_emt_state_atlas/app/app_group_warnings.tsv"
DEFAULT_STATE_COMPARISON = ROOT / "data/processed/pan_cancer_emt_state_atlas/app/app_state_comparison.tsv"
DEFAULT_PORTAL_MANIFEST = ROOT / "data/processed/pan_cancer_emt_state_atlas/annotated_single_cell/external_portal_download_manifest.tsv"
DEFAULT_3CA_MANIFEST = ROOT / "data/processed/pan_cancer_emt_state_atlas/annotated_single_cell/3ca_dataset_manifest.tsv"
DEFAULT_LINEAGE_TARGETS = ROOT / "data/processed/pan_cancer_emt_state_atlas/lineage_targets/disease_target_recommendations_with_lineage_evidence.tsv"
DEFAULT_EXPORT_MANIFEST = ROOT / "data/processed/pan_cancer_emt_state_atlas/exports/export_bundle_manifest.tsv"
DEFAULT_CLINICIAN_BUNDLE = ROOT / "data/processed/pan_cancer_emt_state_atlas/exports/clinician_bundle.zip"
DEFAULT_RESEARCHER_BUNDLE = ROOT / "data/processed/pan_cancer_emt_state_atlas/exports/researcher_bundle.zip"
DEFAULT_CLINICIAN_DOCX = ROOT / "docs/pan_cancer_emt_state_atlas/clinician_pan_cancer_emt_state_atlas_report.docx"
DEFAULT_CLINICIAN_DOCX_V2 = ROOT / "docs/pan_cancer_emt_state_atlas/clinician_pan_cancer_emt_state_atlas_report_v2.docx"
DEFAULT_CLINICIAN_PDF = ROOT / "docs/pan_cancer_emt_state_atlas/clinician_pan_cancer_emt_state_atlas_report.pdf"
DEFAULT_REPORT = ROOT / "docs/pan_cancer_emt_state_atlas/reports/pan_cancer_emt_state_atlas_card_report.md"
DEFAULT_THERAPY_REPORT = ROOT / "docs/pan_cancer_emt_state_atlas/reports/pan_cancer_emt_therapeutic_evidence_report.md"
DEFAULT_CLINICAL_REPORT = ROOT / "docs/pan_cancer_emt_state_atlas/reports/pan_cancer_emt_clinical_report.md"
DEFAULT_SINGLE_CELL_REPORT = ROOT / "docs/pan_cancer_emt_state_atlas/reports/pan_cancer_emt_single_cell_validation_report.md"
DEFAULT_ANNOTATED_SC_REPORT = ROOT / "docs/pan_cancer_emt_state_atlas/reports/pan_cancer_emt_annotated_single_cell_report.md"
DEFAULT_SPATIAL_REPORT = ROOT / "docs/pan_cancer_emt_state_atlas/reports/pan_cancer_emt_spatial_report.md"
DEFAULT_PATHOLOGY_REPORT = ROOT / "docs/pan_cancer_emt_state_atlas/reports/pan_cancer_emt_pathology_review_report.md"
DEFAULT_DISEASE_TARGET_REPORT = ROOT / "docs/pan_cancer_emt_state_atlas/reports/pan_cancer_emt_disease_group_target_report.md"
DEFAULT_LINEAGE_TARGET_REPORT = ROOT / "docs/pan_cancer_emt_state_atlas/reports/pan_cancer_emt_lineage_target_report.md"
DEFAULT_PROJECT_QA = ROOT / "docs/pan_cancer_emt_state_atlas/project_questions_and_answers.md"
DEFAULT_HIGHLIGHTS_FIGURE = ROOT / "docs/pan_cancer_emt_state_atlas/project_highlights.png"


@pd.api.extensions.register_dataframe_accessor("emt_app")
class _AtlasFrameAccessor:
    def __init__(self, frame: pd.DataFrame):
        self._frame = frame

    def numeric_cols(self, preferred: list[str]) -> list[str]:
        return [col for col in preferred if col in self._frame.columns and pd.api.types.is_numeric_dtype(self._frame[col])]


def read_table(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path, sep=None, engine="python")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else "Report not found."


def table_download(st, label: str, frame: pd.DataFrame, filename: str) -> None:
    if frame.empty:
        return
    st.download_button(label, frame.to_csv(sep="\t", index=False), file_name=filename, mime="text/tab-separated-values")


def file_download(st, label: str, path: Path, mime: str) -> None:
    if path.exists():
        st.download_button(label, path.read_bytes(), file_name=path.name, mime=mime)


def state_palette() -> dict[str, str]:
    return {
        "epithelial": "#2b8cbe",
        "hybrid_e_m": "#7b3294",
        "mesenchymal": "#c51b7d",
        "stromal_dominant": "#8c6d31",
        "immune_inflamed_emt": "#238b45",
        "hypoxic_emt": "#d95f0e",
        "uncertain": "#737373",
    }


def main() -> None:
    import streamlit as st

    st.set_page_config(page_title="Pan-Cancer EMT State Atlas", layout="wide")
    st.title("Pan-Cancer EMT State Atlas")

    mode = st.sidebar.radio("Mode", ["Clinician", "Researcher"], horizontal=True)
    sample_query = st.sidebar.text_input("Sample search", "")
    with st.sidebar.expander("Advanced data paths", expanded=False):
        scores_path = Path(st.text_input("Scores", str(DEFAULT_SCORES)))
        summary_path = Path(st.text_input("Cancer summary", str(DEFAULT_STATE_SUMMARY)))
        group_summary_path = Path(st.text_input("Cancer group summary", str(DEFAULT_GROUP_SUMMARY)))
        targets_path = Path(st.text_input("Target ranking", str(DEFAULT_TARGETS)))

    scores = read_table(scores_path)
    summary = read_table(summary_path)
    group_summary = read_table(group_summary_path)
    requested_groups = read_table(DEFAULT_REQUESTED_GROUPS)
    targets = read_table(targets_path)
    disease_targets = read_table(DEFAULT_DISEASE_TARGETS)
    clinical = read_table(DEFAULT_CLINICAL)
    clinical_survival = read_table(DEFAULT_CLINICAL_SURVIVAL)
    clinical_covariate = read_table(DEFAULT_CLINICAL_COVARIATE)
    clinical_cox = read_table(DEFAULT_CLINICAL_COX)
    clinical_warnings = read_table(DEFAULT_CLINICAL_WARNINGS)
    single_cell = read_table(DEFAULT_SINGLE_CELL)
    annotated_sc = read_table(DEFAULT_ANNOTATED_SC)
    annotated_compartments = read_table(DEFAULT_ANNOTATED_COMPARTMENTS)
    sc_requirements = read_table(DEFAULT_SC_REQUIREMENTS)
    markers = read_table(DEFAULT_MARKERS)
    spatial_group = read_table(DEFAULT_SPATIAL_GROUP)
    spatial_run = read_table(DEFAULT_SPATIAL_RUN)
    pathology_queue = read_table(DEFAULT_PATHOLOGY_QUEUE)
    pathology_checklist = read_table(DEFAULT_PATHOLOGY_CHECKLIST)
    app_warnings = read_table(DEFAULT_APP_WARNINGS)
    state_comparison = read_table(DEFAULT_STATE_COMPARISON)
    portal_manifest = read_table(DEFAULT_PORTAL_MANIFEST)
    three_ca_manifest = read_table(DEFAULT_3CA_MANIFEST)
    lineage_targets = read_table(DEFAULT_LINEAGE_TARGETS)
    export_manifest = read_table(DEFAULT_EXPORT_MANIFEST)

    if scores.empty:
        st.error(f"No scores table found at {scores_path}")
        return

    cancer_groups = sorted(scores["cancer_group"].fillna("Other / Not Requested").astype(str).unique()) if "cancer_group" in scores.columns else []
    preferred_groups = [group for group in requested_groups.get("cancer_group", pd.Series(dtype=str)).tolist() if group in cancer_groups]
    cancer_types = sorted(scores["cancer_type"].fillna("unknown").astype(str).unique()) if "cancer_type" in scores.columns else []
    states = sorted(scores["consensus_emt_state"].dropna().astype(str).unique()) if "consensus_emt_state" in scores.columns else []
    confidences = sorted(scores["confidence_label"].dropna().astype(str).unique()) if "confidence_label" in scores.columns else []

    selected_groups = st.sidebar.multiselect("Disease groups", cancer_groups, default=preferred_groups)
    selected_cancers = st.sidebar.multiselect("TCGA cancer codes", cancer_types, default=[])
    selected_states = st.sidebar.multiselect("States", states, default=states)
    selected_confidences = st.sidebar.multiselect("Confidence", confidences, default=confidences)

    filtered = scores.copy()
    if selected_groups and "cancer_group" in filtered.columns:
        filtered = filtered[filtered["cancer_group"].fillna("Other / Not Requested").astype(str).isin(selected_groups)]
    if selected_cancers and "cancer_type" in filtered.columns:
        filtered = filtered[filtered["cancer_type"].fillna("unknown").astype(str).isin(selected_cancers)]
    if selected_states and "consensus_emt_state" in filtered.columns:
        filtered = filtered[filtered["consensus_emt_state"].astype(str).isin(selected_states)]
    if selected_confidences and "confidence_label" in filtered.columns:
        filtered = filtered[filtered["confidence_label"].astype(str).isin(selected_confidences)]
    if sample_query.strip() and "sample_id" in filtered.columns:
        query = sample_query.strip().lower()
        filtered = filtered[filtered["sample_id"].astype(str).str.lower().str.contains(query, regex=False)]

    metric_cols = st.columns(4)
    metric_cols[0].metric("Samples", f"{len(filtered):,}")
    metric_cols[1].metric("Disease Groups", f"{filtered['cancer_group'].nunique() if 'cancer_group' in filtered.columns else 0:,}")
    metric_cols[2].metric("High Confidence", f"{int(filtered['confidence_label'].eq('high').sum()) if 'confidence_label' in filtered.columns else 0:,}")
    metric_cols[3].metric("Stromal Warning", f"{int(filtered['stromal_warning'].sum()) if 'stromal_warning' in filtered.columns else 0:,}")
    st.caption("A research atlas for interpreting tumor-intrinsic EMT, stromal mimicry, spatial niches, clinical associations, and target hypotheses across cancer types.")

    bundle_cols = st.columns(2)
    with bundle_cols[0]:
        file_download(st, "Download clinician bundle", DEFAULT_CLINICIAN_BUNDLE, "application/zip")
    with bundle_cols[1]:
        file_download(st, "Download researcher bundle", DEFAULT_RESEARCHER_BUNDLE, "application/zip")
    file_download(st, "Download updated clinician DOCX report", DEFAULT_CLINICIAN_DOCX_V2, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    file_download(st, "Download clinician PDF report", DEFAULT_CLINICIAN_PDF, "application/pdf")

    if mode == "Clinician":
        st.info("Clinician mode emphasizes disease groups, confidence, clinical warnings, and concise target hypotheses. Research-only; not a treatment recommendation.")
    else:
        st.info("Researcher mode exposes validation layers, spatial niche evidence, marker tables, and downloadable working tables.")

    overview_tab, group_tab, cancer_tab, sample_tab, clinical_tab, single_cell_tab, spatial_tab, target_tab, report_tab, guide_tab = st.tabs(
        ["Overview", "Disease Groups", "Cancer Codes", "Samples", "Clinical", "Single-Cell", "Spatial", "Targets", "Reports", "Guide & Q&A"]
    )

    with overview_tab:
        if DEFAULT_HIGHLIGHTS_FIGURE.exists():
            st.image(DEFAULT_HIGHLIGHTS_FIGURE, caption="Current atlas highlights: EMT pressure, stromal caution, annotated 3CA coverage, and tumor-versus-stroma interpretation.", use_container_width=True)
        left, right = st.columns([1, 1])
        with left:
            if "consensus_emt_state" in filtered.columns:
                state_counts = filtered["consensus_emt_state"].value_counts().rename_axis("state").reset_index(name="count")
                st.bar_chart(state_counts.set_index("state"), color="#7b3294")
        with right:
            numeric = filtered.emt_app.numeric_cols(["emt_score", "partial_emt_score", "stromal_contamination_risk", "hypoxia"])
            if numeric:
                st.dataframe(filtered[numeric].describe().T, use_container_width=True)
        st.subheader("Highlights to investigate next")
        highlight_left, highlight_right = st.columns(2)
        if not group_summary.empty and "cancer_group" in group_summary.columns:
            highlight = group_summary.copy()
            for col in ["mesenchymal_like_fraction", "hybrid_fraction", "stromal_dominant_fraction"]:
                if col not in highlight.columns:
                    highlight[col] = 0.0
            highlight["emt_pressure"] = (
                highlight["mesenchymal_like_fraction"].fillna(0)
                + 0.5 * highlight["hybrid_fraction"].fillna(0)
                + 0.25 * highlight["stromal_dominant_fraction"].fillna(0)
            )
            with highlight_left:
                st.caption("Combined EMT pressure")
                st.bar_chart(
                    highlight.sort_values("emt_pressure", ascending=False)
                    .set_index("cancer_group")["emt_pressure"].head(8)
                )
            with highlight_right:
                st.caption("Stromal mimicry caution")
                st.bar_chart(
                    highlight.sort_values("stromal_dominant_fraction", ascending=False)
                    .set_index("cancer_group")["stromal_dominant_fraction"].head(8)
                )
        if not annotated_sc.empty and "source" in annotated_sc.columns:
            validation_view = annotated_sc[annotated_sc["source"].astype(str).eq("3CA")].copy()
            if not validation_view.empty and {"cancer_group", "cells"}.issubset(validation_view.columns):
                st.caption("Real annotated single-cell coverage")
                st.bar_chart(validation_view.set_index("cancer_group")["cells"].sort_values(ascending=False))
        table_download(st, "Download filtered samples", filtered, "filtered_emt_atlas_samples.tsv")
        if not state_comparison.empty:
            st.subheader("State Comparison by Disease Group")
            state_view = state_comparison
            if selected_groups and "cancer_group" in state_view.columns:
                state_view = state_view[state_view["cancer_group"].astype(str).isin(selected_groups)]
            st.dataframe(state_view, use_container_width=True, hide_index=True)
            if {"cancer_group", "consensus_emt_state", "state_fraction"}.issubset(state_view.columns):
                pivot = state_view.pivot_table(index="cancer_group", columns="consensus_emt_state", values="state_fraction", fill_value=0)
                st.bar_chart(pivot)
            table_download(st, "Download state comparison", state_view, "app_state_comparison.tsv")

    with group_tab:
        if requested_groups.empty:
            st.warning("Requested cancer-group mapping not found.")
        else:
            st.dataframe(requested_groups, use_container_width=True, hide_index=True)
        if group_summary.empty:
            st.warning("Cancer-group summary not found.")
        else:
            st.dataframe(group_summary, use_container_width=True, hide_index=True)
            if not app_warnings.empty:
                warning_view = app_warnings
                if selected_groups and "cancer_group" in warning_view.columns:
                    warning_view = warning_view[warning_view["cancer_group"].astype(str).isin(selected_groups)]
                st.dataframe(warning_view, use_container_width=True, hide_index=True)
            chart_cols = [col for col in ["mesenchymal_like_fraction", "hybrid_fraction", "stromal_dominant_fraction"] if col in group_summary.columns]
            if chart_cols and "cancer_group" in group_summary.columns:
                st.bar_chart(group_summary.set_index("cancer_group")[chart_cols])
            table_download(st, "Download disease-group summary", group_summary, "cancer_group_state_summary.tsv")

    with cancer_tab:
        if summary.empty:
            st.warning("Cancer-type summary not found.")
        else:
            st.dataframe(summary, use_container_width=True, hide_index=True)
            chart_cols = [col for col in ["mesenchymal_like_fraction", "hybrid_fraction", "stromal_dominant_fraction"] if col in summary.columns]
            if chart_cols and "cancer_type" in summary.columns:
                st.bar_chart(summary.set_index("cancer_type")[chart_cols].head(20))
            table_download(st, "Download cancer-code summary", summary, "cancer_type_state_summary.tsv")

    with sample_tab:
        display_cols = [
            col
            for col in [
                "sample_id",
                "cancer_group",
                "cancer_type",
                "consensus_emt_state",
                "confidence_label",
                "emt_score",
                "partial_emt_score",
                "stromal_contamination_risk",
                "hypoxia",
                "state_explanation",
            ]
            if col in filtered.columns
        ]
        st.dataframe(filtered[display_cols].head(1000), use_container_width=True, hide_index=True)
        table_download(st, "Download displayed sample table", filtered[display_cols], "emt_sample_search_results.tsv")

    with clinical_tab:
        st.subheader("Clinical Readiness and Warnings")
        if clinical.empty:
            st.warning("Clinical summary not found.")
        else:
            clinical_view = clinical
            if selected_groups and "cancer_group" in clinical_view.columns:
                clinical_view = clinical_view[clinical_view["cancer_group"].astype(str).isin(selected_groups)]
            st.dataframe(clinical_view, use_container_width=True, hide_index=True)
            table_download(st, "Download clinical summary", clinical_view, "clinical_group_summary.tsv")
        if not clinical_warnings.empty:
            st.dataframe(clinical_warnings, use_container_width=True, hide_index=True)
            table_download(st, "Download clinical warnings", clinical_warnings, "clinical_warnings.tsv")
        if mode == "Researcher" and not clinical_survival.empty:
            st.subheader("Survival Screen")
            st.dataframe(clinical_survival, use_container_width=True, hide_index=True)
            table_download(st, "Download survival screen", clinical_survival, "clinical_survival_by_group.tsv")
        if mode == "Researcher" and not clinical_covariate.empty:
            st.subheader("Covariate-Aware Screen")
            st.dataframe(clinical_covariate, use_container_width=True, hide_index=True)
            table_download(st, "Download covariate-aware screen", clinical_covariate, "clinical_covariate_adjusted_screen.tsv")
        if mode == "Researcher" and not clinical_cox.empty:
            st.subheader("Multivariable Cox Models")
            st.dataframe(clinical_cox, use_container_width=True, hide_index=True)
            table_download(st, "Download Cox models", clinical_cox, "clinical_multivariable_cox_models.tsv")

    with single_cell_tab:
        st.subheader("Tumor-Intrinsic EMT Validation")
        if single_cell.empty:
            st.warning("Single-cell validation summary not found.")
        else:
            single_cell_view = single_cell
            if selected_groups and "cancer_group" in single_cell_view.columns:
                single_cell_view = single_cell_view[single_cell_view["cancer_group"].astype(str).isin(selected_groups)]
            st.dataframe(single_cell_view, use_container_width=True, hide_index=True)
            chart_cols = [col for col in ["single_cell_emt_score_mean", "single_cell_partial_emt_score_mean", "single_cell_hypoxia_mean"] if col in single_cell_view.columns]
            if chart_cols and "cancer_group" in single_cell_view.columns:
                st.bar_chart(single_cell_view.set_index("cancer_group")[chart_cols])
            table_download(st, "Download single-cell validation", single_cell_view, "single_cell_group_validation_summary.tsv")
        if mode == "Researcher" and not markers.empty:
            st.subheader("Tumor-Intrinsic and Stromal-Control Markers")
            st.dataframe(markers, use_container_width=True, hide_index=True)
            table_download(st, "Download marker table", markers, "tumor_intrinsic_marker_table.tsv")
        if not annotated_sc.empty:
            st.subheader("Malignant versus CAF/Stromal EMT Separation")
            annotated_view = annotated_sc
            if selected_groups and "cancer_group" in annotated_view.columns:
                annotated_view = annotated_view[annotated_view["cancer_group"].astype(str).isin(selected_groups)]
            st.dataframe(annotated_view, use_container_width=True, hide_index=True)
            table_download(st, "Download tumor-vs-stroma EMT summary", annotated_view, "tumor_vs_stroma_emt_summary.tsv")
        if mode == "Researcher" and not annotated_compartments.empty:
            st.subheader("Compartment-Level EMT Calls")
            st.dataframe(annotated_compartments.head(1000), use_container_width=True, hide_index=True)
            table_download(st, "Download compartment EMT summary", annotated_compartments, "annotated_compartment_summary.tsv")
        if mode == "Researcher" and not sc_requirements.empty:
            st.subheader("TISCH2 / 3CA / HTAN Import Requirements")
            st.dataframe(sc_requirements, use_container_width=True, hide_index=True)
            table_download(st, "Download external source requirements", sc_requirements, "external_single_cell_source_requirements.tsv")
        if mode == "Researcher" and not portal_manifest.empty:
            st.subheader("External Portal Download Manifest")
            st.dataframe(portal_manifest, use_container_width=True, hide_index=True)
            table_download(st, "Download portal manifest", portal_manifest, "external_portal_download_manifest.tsv")
        if mode == "Researcher" and not three_ca_manifest.empty:
            st.subheader("Public 3CA Dataset Manifest")
            st.dataframe(three_ca_manifest, use_container_width=True, hide_index=True)
            table_download(st, "Download 3CA dataset manifest", three_ca_manifest, "3ca_dataset_manifest.tsv")

    with spatial_tab:
        st.subheader("Spatial EMT Niches")
        if spatial_group.empty:
            st.warning("Spatial group summary not found.")
        else:
            spatial_group_view = spatial_group
            if selected_groups and "cancer_group" in spatial_group_view.columns:
                spatial_group_view = spatial_group_view[spatial_group_view["cancer_group"].astype(str).isin(selected_groups)]
            st.dataframe(spatial_group_view, use_container_width=True, hide_index=True)
            chart_cols = [col for col in ["mean_emt_niche_fraction", "mean_tumor_cell_emt_fraction", "mean_stromal_inflated_fraction"] if col in spatial_group_view.columns]
            if chart_cols and "cancer_group" in spatial_group_view.columns:
                st.bar_chart(spatial_group_view.set_index("cancer_group")[chart_cols])
            table_download(st, "Download spatial group summary", spatial_group_view, "spatial_group_summary.tsv")
        if mode == "Researcher" and not spatial_run.empty:
            st.subheader("Spot/Region Cards")
            st.dataframe(spatial_run, use_container_width=True, hide_index=True)
            table_download(st, "Download spatial run summary", spatial_run, "spatial_run_summary.tsv")
        if not pathology_queue.empty:
            st.subheader("Pathology Review Queue")
            pathology_view = pathology_queue
            if selected_groups and "cancer_group" in pathology_view.columns:
                pathology_view = pathology_view[pathology_view["cancer_group"].astype(str).isin(selected_groups)]
            st.dataframe(pathology_view, use_container_width=True, hide_index=True)
            table_download(st, "Download pathology review queue", pathology_view, "pathology_review_queue.tsv")
        if mode == "Researcher" and not pathology_checklist.empty:
            st.subheader("Pathology Review Checklist")
            st.dataframe(pathology_checklist, use_container_width=True, hide_index=True)
            table_download(st, "Download pathology checklist", pathology_checklist, "pathology_review_checklist.tsv")

    with target_tab:
        if targets.empty:
            st.warning("Target ranking not found.")
        else:
            target_cols = [
                col
                for col in [
                    "target",
                    "family",
                    "priority_score",
                    "emt_state_specificity",
                    "metastatic_association",
                    "druggability",
                    "crispr_dependency",
                    "compound_availability",
                    "normal_tissue_safety",
                    "literature_support",
                ]
                if col in targets.columns
            ]
            st.dataframe(targets[target_cols].head(50), use_container_width=True, hide_index=True)
            if "family" in targets.columns and "priority_score" in targets.columns:
                family = targets.groupby("family", dropna=False)["priority_score"].mean().sort_values(ascending=False)
                st.bar_chart(family)
            table_download(st, "Download pan-cancer target ranking", targets, "target_ranking.tsv")
        if not disease_targets.empty:
            st.subheader("Disease-Group Target Cards")
            disease_target_view = disease_targets
            if selected_groups and "cancer_group" in disease_target_view.columns:
                disease_target_view = disease_target_view[disease_target_view["cancer_group"].astype(str).isin(selected_groups)]
            st.dataframe(disease_target_view, use_container_width=True, hide_index=True)
            table_download(st, "Download disease-target recommendations", disease_target_view, "target_disease_group_recommendations.tsv")
        if not lineage_targets.empty:
            st.subheader("Cancer-Lineage Target Evidence")
            lineage_view = lineage_targets
            if selected_groups and "cancer_group" in lineage_view.columns:
                lineage_view = lineage_view[lineage_view["cancer_group"].astype(str).isin(selected_groups)]
            st.dataframe(lineage_view, use_container_width=True, hide_index=True)
            table_download(st, "Download lineage target evidence", lineage_view, "disease_target_recommendations_with_lineage_evidence.tsv")
        if not export_manifest.empty:
            st.subheader("Export Bundle Manifest")
            st.dataframe(export_manifest, use_container_width=True, hide_index=True)

    with report_tab:
        st.markdown(read_text(DEFAULT_REPORT))
        st.divider()
        st.markdown(read_text(DEFAULT_THERAPY_REPORT))
        st.divider()
        st.markdown(read_text(DEFAULT_DISEASE_TARGET_REPORT))
        st.divider()
        st.markdown(read_text(DEFAULT_CLINICAL_REPORT))
        st.divider()
        st.markdown(read_text(DEFAULT_SINGLE_CELL_REPORT))
        st.divider()
        st.markdown(read_text(DEFAULT_ANNOTATED_SC_REPORT))
        st.divider()
        st.markdown(read_text(DEFAULT_SPATIAL_REPORT))
        st.divider()
        st.markdown(read_text(DEFAULT_PATHOLOGY_REPORT))
        st.divider()
        st.markdown(read_text(DEFAULT_LINEAGE_TARGET_REPORT))

    with guide_tab:
        st.subheader("How to use the atlas")
        st.markdown(read_text(DEFAULT_PROJECT_QA))
        file_download(st, "Download project Q&A", DEFAULT_PROJECT_QA, "project_questions_and_answers.md")


if __name__ == "__main__":
    main()
