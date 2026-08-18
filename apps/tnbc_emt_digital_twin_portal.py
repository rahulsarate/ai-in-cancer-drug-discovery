"""Interactive research portal for the TNBC EMT digital-twin project.

Run with:
    python -m streamlit run apps/tnbc_emt_digital_twin_portal.py
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "docs" / "tnbc_digital_twin_emt_plasticity"
DATA = ROOT / "data" / "processed" / "tnbc_digital_twin"
NOVELTY_ASSETS = PROJECT / "novelty_positioning" / "assets"
ASSETS = PROJECT / "assets"

EXTERNAL_METRICS = DATA / "external_validation" / "gse163882" / "external_validation_metrics.tsv"
BOOTSTRAP_METRICS = DATA / "response_model_robustness" / "gse163882_external_metric_bootstrap_intervals.tsv"
CURATED_METRICS = DATA / "response_label_curation" / "curated_model" / "tnbc_nac_response_model_metrics.tsv"
LODO_METRICS = DATA / "leave_dataset_out_validation" / "tnbc_leave_dataset_out_metrics.tsv"
GSE43816_SUMMARY = DATA / "gse43816_longitudinal" / "gse43816_shift_summary.tsv"
GSE43502_SUMMARY = DATA / "residual_persister_biology" / "gse43502_recurrence_feature_summary.tsv"
MARKER_CHECKS = DATA / "gse164715_marker_validation" / "gse164715_marker_panel_direction_checks.tsv"
AMBIGUITY_REVIEW = DATA / "gse164715_ambiguity_review" / "gse164715_sample_stage_ambiguity_review.tsv"


FAQS = [
    (
        "What is this project?",
        "It is a research prototype that represents triple-negative breast cancer (TNBC) under neoadjuvant chemotherapy as a changing mixture of epithelial, hybrid, mesenchymal, and drug-tolerant persister states. It synthesizes public transcriptomic cohorts; it is not a clinical decision-support device.",
    ),
    (
        "Why focus on TNBC during neoadjuvant chemotherapy?",
        "TNBC has a meaningful risk of relapse when residual disease remains after neoadjuvant chemotherapy. A binary response label says little about how a tumor may have survived treatment. This project asks which molecular survival state may be enriched instead.",
    ),
    (
        "What do E, H, M, and P mean?",
        "E is epithelial-like and comparatively chemo-sensitive. H is hybrid epithelial-mesenchymal and plastic. M is mesenchymal-like and resistance-associated. P is a drug-tolerant persister program. These are interpretable score-derived research states, not direct histopathology diagnoses.",
    ),
    (
        "What is the strongest independent validation result?",
        "On the independent GSE163882 RNA-seq TPM cohort (n=90), the combined model with external quantile-to-internal calibration had AUROC 0.649, AUPRC 0.714, accuracy 0.656, and Brier score 0.232. The AUROC bootstrap interval was 0.521 to 0.728, which supports cautious, exploratory use rather than a clinical claim.",
    ),
    (
        "Why is calibration shown so prominently?",
        "The training and external datasets were generated on different platforms. A model can appear to work or fail because of scale differences rather than biology. The portal therefore separates raw, percentile, z-score, and quantile-calibrated results instead of presenting one pooled number.",
    ),
    (
        "How was longitudinal change studied?",
        "The GSE43816 paired pre/post-NAC cohort was analyzed as within-patient shifts across seven pairs. Those shifts calibrate transition priors for the state simulator. They are useful biological evidence, but the small sample size means they do not establish universal patient trajectories.",
    ),
    (
        "What did the recurrence-axis analysis add?",
        "GSE43502 was used to compare residual chemoresistant tumors with and without recurrence. AXL/TAM and hypoxia had positive recurrence-minus-no-recurrence mean shifts with bootstrap support. This creates mechanistic hypotheses, not validated prognostic biomarkers.",
    ),
    (
        "What does the single-cell layer contribute?",
        "GSE164715 connects bulk-like scores to a species-filtered single-cell persister and microenvironment layer. Targeted marker-direction checks passed 11 of 11 checks. Ambiguous compartments are intentionally kept visible so the interface does not disguise unresolved annotation.",
    ),
    (
        "Why were response labels curated?",
        "Public response metadata can mix broad good-response labels with pathology evidence of residual disease. The workflow conservatively recoded flagged GSE25055 and GSE25065 rows for a locked sensitivity analysis, then reports that sensitivity separately from the original-label analysis.",
    ),
    (
        "Can a clinician use this to choose treatment today?",
        "No. The portal does not recommend a regimen, predict an individual patient's outcome, or replace multidisciplinary clinical judgment. Its clinician-facing role is to organize transparent biological questions and uncertainty for research discussion.",
    ),
    (
        "How can a clinician use it responsibly?",
        "As a hypothesis-framing view: identify whether an observed tumor profile is dominated by epithelial sensitivity, hybrid plasticity, mesenchymal resistance, persister programs, or niche signals; then consider what additional pathology, molecular, or trial evidence would be needed. No treatment action should follow from this portal alone.",
    ),
    (
        "How can researchers use it?",
        "Researchers can inspect the frozen validation evidence, compare calibration modes, generate mechanistic hypotheses, review unresolved single-cell annotations, and reuse the pipeline as a reproducible scaffold for a new externally validated cohort.",
    ),
    (
        "What is novel here compared with ordinary response models?",
        "The novelty is the integrated workflow: a TNBC NAC-specific E/H/M/P state space, paired transition priors, tumor-versus-stress-versus-niche persister layers, response-label curation, platform-aware validation, single-cell ambiguity governance, and clinician-style reporting limits in one executable package.",
    ),
    (
        "How is this different from an MRI-based digital twin?",
        "MRI-based twins are often strongest for tumor volume and growth-response dynamics. This project is transcriptomic and is designed to interpret EMT plasticity, persister programs, and microenvironment context. The two approaches could become complementary in a future multimodal twin.",
    ),
    (
        "What are the important limitations?",
        "The model uses public, heterogeneous cohorts with limited sample sizes; response labels require curation; cross-platform transport is imperfect; transition priors are estimated from only seven pairs; and targeted single-cell annotations include ambiguous compartments. Prospective, protocol-matched clinical validation is still required.",
    ),
    (
        "What would be required before clinical deployment?",
        "A locked intended-use statement, prospective multi-site validation, clinically curated response and outcome labels, standardized assay and normalization procedures, calibration monitoring, clinician usability testing, regulatory review where applicable, and governance for privacy, fairness, and model updates.",
    ),
    (
        "Can I upload a patient sample into this portal?",
        "No. This version intentionally contains no patient upload or patient-level prediction workflow. It presents cohort-level research evidence and protects against accidental use as an unvalidated diagnostic interface.",
    ),
    (
        "Where are the source data and detailed methods?",
        "The Downloads section contains the final report, full manuscript draft, novelty report, frozen-release documentation, and the presentation deck. The reproducible runner is scripts/run_tnbc_digital_twin_pipeline.py, configured by configs/tnbc_digital_twin.yml.",
    ),
]


@st.cache_data(show_spinner=False)
def read_tsv(path: str) -> pd.DataFrame:
    file_path = Path(path)
    if not file_path.exists():
        return pd.DataFrame()
    return pd.read_csv(file_path, sep="\t")


def format_metric(value: float | int | None, digits: int = 3) -> str:
    if value is None or pd.isna(value):
        return "Not available"
    return f"{float(value):.{digits}f}"


def show_image(path: Path, caption: str) -> None:
    if path.exists():
        st.image(str(path), caption=caption, width="stretch")
    else:
        st.warning(f"Expected visual is unavailable: {path.name}")


def download_file(label: str, path: Path, mime: str) -> None:
    if path.exists():
        st.download_button(
            label,
            data=path.read_bytes(),
            file_name=path.name,
            mime=mime,
            width="stretch",
        )


def section_intro(title: str, text: str) -> None:
    st.title(title)
    st.markdown(f"<p class='section-intro'>{text}</p>", unsafe_allow_html=True)


def best_external_result() -> pd.Series | None:
    metrics = read_tsv(str(EXTERNAL_METRICS))
    if metrics.empty:
        return None
    selected = metrics.loc[
        (metrics["feature_set"] == "combined")
        & (metrics["calibration_method"] == "external_quantile_to_internal")
    ]
    if selected.empty:
        selected = metrics.sort_values("auroc", ascending=False)
    return selected.iloc[0]


def render_overview() -> None:
    result = best_external_result()
    section_intro(
        "TNBC EMT Digital Twin",
        "A transparent research portal for understanding how triple-negative breast cancer may shift under neoadjuvant chemotherapy. It turns public data into a biological state map, not a treatment recommendation.",
    )
    st.markdown(
        "<div class='notice'><strong>Research-use boundary.</strong> This portal contains cohort-level, public-data evidence. It is not validated for individual patient prediction, treatment selection, or clinical decision support.</div>",
        unsafe_allow_html=True,
    )
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Independent cohort", "90 samples", "GSE163882 RNA-seq")
    c2.metric("Best external AUROC", format_metric(result["auroc"]) if result is not None else "-", "quantile calibrated")
    c3.metric("Longitudinal pairs", "7", "GSE43816 pre/post NAC")
    c4.metric("Single-cell marker checks", "11 / 11", "direction checks passed")

    st.subheader("The central idea")
    st.write(
        "Chemotherapy can reduce tumor burden while selecting a different surviving state mixture. Rather than asking only whether a cohort achieved pathological complete response, this project asks which therapy-tolerant programs may become relatively enriched."
    )
    show_image(NOVELTY_ASSETS / "four_state_digital_twin_diagram.png", "The four-state E/H/M/P research representation.")

    st.subheader("Four interpretable states")
    states = [
        ("E", "Epithelial-like", "Relatively chemo-sensitive program", "#1f6f8b"),
        ("H", "Hybrid", "Transitional, plastic program", "#2a9d8f"),
        ("M", "Mesenchymal-like", "Resistance-associated program", "#e76f51"),
        ("P", "Persister", "Drug-tolerant survival program", "#d99a28"),
    ]
    columns = st.columns(4)
    for column, (letter, name, description, color) in zip(columns, states):
        column.markdown(
            f"<div class='state-card' style='border-top-color:{color}'><div class='state-letter' style='color:{color}'>{letter}</div><strong>{name}</strong><br><span>{description}</span></div>",
            unsafe_allow_html=True,
        )

    st.subheader("What was completed")
    left, right = st.columns(2)
    with left:
        st.markdown(
            "- Response-label standardization and locked curation sensitivity analysis\n"
            "- EMT, tumor microenvironment, resistance, and persister signature scoring\n"
            "- Paired pre/post-NAC state-shift analysis and transition-prior calibration\n"
            "- Calibrated therapy simulation with uncertainty bands"
        )
    with right:
        st.markdown(
            "- Residual-disease recurrence-axis exploration with bootstrap intervals\n"
            "- Species-filtered single-cell persister/niche review\n"
            "- Cross-platform external validation and calibration diagnostics\n"
            "- Frozen outputs, manuscript, validation memo, and reproducible runner"
        )


def render_evidence() -> None:
    section_intro(
        "Evidence and Novelty",
        "The project is most distinctive as an integrated and governed workflow. Each individual biological component exists in the literature; their transparent combination for TNBC NAC is the contribution.",
    )
    show_image(NOVELTY_ASSETS / "evidence_stack.png", "The evidence stack joining clinical endpoints, dynamic states, validation, and reporting safeguards.")
    first, second = st.columns(2)
    with first:
        show_image(NOVELTY_ASSETS / "novelty_matrix_heatmap.png", "Capability comparison with adjacent literature and digital-twin approaches.")
    with second:
        show_image(NOVELTY_ASSETS / "novelty_positioning_map.png", "Positioning relative to response literature, EMT/persister work, and oncology digital twins.")

    st.subheader("What is similar, and what is different")
    comparison = pd.DataFrame(
        [
            ["pCR / residual disease studies", "Response outcomes matter", "Usually endpoint-centered; no dynamic E/H/M/P simulator"],
            ["EMT and persister biology", "Mechanisms of plasticity and tolerance", "Often conceptual; not an executable TNBC NAC validation workflow"],
            ["MRI-based TNBC twins", "Patient-specific NAC response framing", "MRI/growth centered rather than transcriptomic EMT/persister interpretation"],
            ["QSP virtual patients", "Mechanistic simulation philosophy", "Typically immune/QSP centered, not TNBC NAC state-reporting"],
            ["This project", "Uses accepted endpoints and public cohorts", "Combines state dynamics, curation, platform-aware validation, single-cell ambiguity review, and reporting limits"],
        ],
        columns=["Comparator", "Shared ground", "Difference"],
    )
    st.dataframe(comparison, hide_index=True, width="stretch")

    st.subheader("Novel contributions")
    st.markdown(
        "1. TNBC NAC-specific, state-centered interpretation rather than a response score alone.\n"
        "2. A four-state epithelial, hybrid, mesenchymal, persister representation.\n"
        "3. Separate tumor-cell, stress-tolerance, and niche-persister layers.\n"
        "4. Transition priors calibrated from paired pre/post-NAC samples.\n"
        "5. Response-label curation and calibration-mode transparency.\n"
        "6. Single-cell evidence with ambiguity preserved instead of silently over-annotated.\n"
        "7. Clinician-facing boundaries that prohibit treatment recommendations."
    )


def render_results() -> None:
    section_intro(
        "Results Explorer",
        "Explore the frozen cohort-level evidence. Metrics are deliberately displayed with cohort, feature-set, calibration, and uncertainty context so that a single attractive number never carries more weight than it should.",
    )
    metrics = read_tsv(str(EXTERNAL_METRICS))
    if metrics.empty:
        st.error("External validation metrics were not found.")
        return

    st.subheader("Independent cross-platform validation")
    feature_options = list(metrics["feature_set"].dropna().unique())
    feature_set = st.selectbox("Feature set", feature_options, index=feature_options.index("combined") if "combined" in feature_options else 0)
    calibration_options = list(metrics.loc[metrics["feature_set"] == feature_set, "calibration_method"].dropna().unique())
    preferred = "external_quantile_to_internal"
    calibration = st.selectbox(
        "Calibration approach",
        calibration_options,
        index=calibration_options.index(preferred) if preferred in calibration_options else 0,
    )
    chosen = metrics.loc[(metrics["feature_set"] == feature_set) & (metrics["calibration_method"] == calibration)].iloc[0]
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("AUROC", format_metric(chosen["auroc"]))
    m2.metric("AUPRC", format_metric(chosen["auprc"]))
    m3.metric("Accuracy", format_metric(chosen["accuracy"]))
    m4.metric("Brier score", format_metric(chosen["brier"]))
    chart = pd.DataFrame({"metric": ["AUROC", "AUPRC", "Accuracy"], "value": [chosen["auroc"], chosen["auprc"], chosen["accuracy"]]}).set_index("metric")
    st.bar_chart(chart, color="#2a9d8f")
    st.caption(
        f"Evaluation: {chosen['test_dataset']}; n={int(chosen['samples'])}; training data: {chosen['train_dataset']}. Lower Brier score is better."
    )

    bootstrap = read_tsv(str(BOOTSTRAP_METRICS))
    selected_bootstrap = bootstrap.loc[
        (bootstrap["feature_set"] == feature_set) & (bootstrap["calibration_method"] == calibration)
    ] if not bootstrap.empty else pd.DataFrame()
    if not selected_bootstrap.empty:
        boot = selected_bootstrap.iloc[0]
        st.info(
            f"Bootstrap context: AUROC {format_metric(boot['auroc_point'])} with 95% interval {format_metric(boot['auroc_q025'])} to {format_metric(boot['auroc_q975'])}; accuracy {format_metric(boot['accuracy_point'])} with interval {format_metric(boot['accuracy_q025'])} to {format_metric(boot['accuracy_q975'])}."
        )

    with st.expander("View all external validation configurations"):
        display_columns = ["feature_set", "calibration_method", "samples", "auroc", "auprc", "accuracy", "brier"]
        st.dataframe(metrics[display_columns].sort_values(["feature_set", "calibration_method"]), hide_index=True, width="stretch")

    st.subheader("Longitudinal state change under therapy")
    long_summary = read_tsv(str(GSE43816_SUMMARY))
    paired_plot, therapy_plot = st.columns(2)
    with paired_plot:
        show_image(ASSETS / "gse43816_longitudinal" / "gse43816_paired_feature_shifts.png", "GSE43816 paired pre/post-NAC feature shifts (seven paired samples).")
    with therapy_plot:
        show_image(ASSETS / "therapy_simulation" / "tnbc_calibrated_simulation_uncertainty.png", "State simulation calibrated from longitudinal shifts, with uncertainty bands.")
    if not long_summary.empty:
        longitudinal_display = long_summary.loc[
            long_summary["feature"].isin(["emt_score", "partial_emt_score", "tnbc_hypoxia", "tnbc_stemness_persister", "therapy_selection_pressure"]),
            ["feature", "pairs", "mean_delta", "median_delta", "patients_increased", "patients_decreased"],
        ]
        st.dataframe(longitudinal_display, hide_index=True, width="stretch")
        st.caption("Positive delta means the post-treatment score was higher than the paired pre-treatment score. Small paired cohorts support hypothesis generation, not universal individual trajectories.")

    st.subheader("Residual disease and recurrence-axis exploration")
    recurrence = read_tsv(str(GSE43502_SUMMARY))
    r1, r2 = st.columns([1.1, 0.9])
    with r1:
        show_image(ASSETS / "residual_persister_biology" / "gse43502_recurrence_bootstrap_intervals.png", "Recurrence versus no-recurrence differences with bootstrap intervals in GSE43502.")
    with r2:
        if not recurrence.empty:
            st.dataframe(
                recurrence.loc[:, ["feature", "delta_recurrence_minus_no_recurrence", "delta_mean_q025", "delta_mean_q975", "bootstrap_probability_delta_gt_0", "mannwhitney_p"]].head(8),
                hide_index=True,
                width="stretch",
            )
    st.caption("These axes are exploratory mechanisms: they are not established recurrence biomarkers and should not be used for prognosis.")


def render_clinical_lens() -> None:
    section_intro(
        "Clinical Lens",
        "A deliberately cautious interface for translating complex molecular evidence into better questions. It is designed to be clinically legible while keeping a firm boundary around what the evidence cannot support.",
    )
    left, right = st.columns(2)
    with left:
        st.subheader("Useful for discussion")
        st.markdown(
            "- Which biology appears to dominate at the cohort level: epithelial sensitivity, plasticity, resistance, persister, or niche context?\n"
            "- Is a therapy-associated state shift plausible enough to motivate additional molecular or pathology review?\n"
            "- What is the relevant uncertainty: labels, platform, cohort size, or compartment identity?\n"
            "- Which trials or mechanistic studies might be relevant to investigate next?"
        )
    with right:
        st.subheader("Not permitted by this evidence")
        st.markdown(
            "- Selecting, withholding, or sequencing treatment\n"
            "- Estimating a patient's probability of pCR, relapse, or survival\n"
            "- Replacing pathology, imaging, molecular tumor board review, or trial eligibility assessment\n"
            "- Treating E/H/M/P score-derived states as pathology diagnoses"
        )

    st.subheader("A responsible clinical-research conversation")
    st.markdown(
        "<div class='workflow'><div><strong>1. Observe</strong><br>Review pathology, imaging, regimen, and response history.</div><div><strong>2. Contextualize</strong><br>Use the portal to frame state and niche hypotheses.</div><div><strong>3. Verify</strong><br>Seek orthogonal pathology, molecular, or trial evidence.</div><div><strong>4. Decide</strong><br>Make care decisions through the clinical team and validated standards.</div></div>",
        unsafe_allow_html=True,
    )

    st.subheader("Interpretation guardrails")
    st.markdown(
        "- The external model discriminates modestly, not decisively; its best AUROC is 0.649 with a broad bootstrap interval.\n"
        "- Public cohort labels and assay platforms differ. Calibration changes performance, so a single score is not portable by default.\n"
        "- The longitudinal transition prior comes from seven pairs. It informs simulation uncertainty rather than defining a patient's future.\n"
        "- Single-cell marker checks are supportive, while ambiguous compartments remain unresolved."
    )


def render_research_lens() -> None:
    section_intro(
        "Research Lens",
        "A practical map of the biological layers, the claims each one can support, and the next experiments that would turn this prototype into a stronger translational resource.",
    )
    annotation_checks = read_tsv(str(MARKER_CHECKS))
    ambiguity = read_tsv(str(AMBIGUITY_REVIEW))
    c1, c2, c3 = st.columns(3)
    c1.metric("Marker-direction checks", f"{int(annotation_checks['passes_direction_check'].sum()) if not annotation_checks.empty else 0} / {len(annotation_checks)}")
    ambiguous_count = int((ambiguity["review_status"].astype(str).str.contains("ambiguity", case=False)).sum()) if not ambiguity.empty else 0
    c2.metric("Ambiguity flags", str(ambiguous_count), "kept visible")
    c3.metric("Validation modes", "4", "raw, percentile, z-score, quantile")

    st.subheader("Evidence architecture")
    st.markdown(
        "<div class='research-grid'><div><strong>Bulk response layer</strong><br>Associates multi-signature state features with NAC response labels.</div><div><strong>Longitudinal layer</strong><br>Estimates within-patient pre/post treatment shifts and transition priors.</div><div><strong>Residual/recurrence layer</strong><br>Surfaces candidate resistance and niche axes in residual disease.</div><div><strong>Single-cell layer</strong><br>Checks whether persister and compartment signals have plausible cell-level support.</div><div><strong>Validation layer</strong><br>Separates curation sensitivity, leave-dataset-out checks, and cross-platform calibration.</div><div><strong>Governance layer</strong><br>Preserves uncertainty, ambiguity, and non-clinical intended-use boundaries.</div></div>",
        unsafe_allow_html=True,
    )

    st.subheader("High-value next studies")
    st.markdown(
        "1. Prospectively collect TNBC NAC biopsies with assay-matched pre-, on-, and post-treatment sampling.\n"
        "2. Pair transcriptomics with pathology-reviewed RCB, pCR, recurrence, regimen, and time-to-event data.\n"
        "3. Add spatial proteogenomics to resolve malignant, stromal, endothelial, and immune niches.\n"
        "4. Test whether AXL/TAM, hypoxia, YAP/TAZ, or persister signals predict response after preregistered calibration.\n"
        "5. Compare transcriptomic state trajectories with MRI tumor dynamics in a multimodal twin.\n"
        "6. Establish prospective calibration drift checks, fairness audits, and a locked model-update policy."
    )
    with st.expander("Review the unresolved single-cell compartments"):
        if ambiguity.empty:
            st.write("No ambiguity review table is available.")
        else:
            st.dataframe(ambiguity, hide_index=True, width="stretch")
        st.caption("The presence of ambiguity is a finding and a governance feature: publication-level claims should not overstate compartment identity.")


def render_questions() -> None:
    section_intro(
        "Project Questions and Answers",
        "Plain-language answers to the questions a clinician, researcher, reviewer, student, or collaborator is most likely to ask. These answers are part of the project record and are available as a downloadable document.",
    )
    query = st.text_input("Search the questions", placeholder="Try: validation, clinician, novelty, persister")
    matching = [item for item in FAQS if query.lower() in f"{item[0]} {item[1]}".lower()] if query else FAQS
    st.caption(f"{len(matching)} question(s) shown")
    for question, answer in matching:
        with st.expander(question):
            st.write(answer)


def render_downloads() -> None:
    section_intro(
        "Reports and Reproducibility",
        "The portal is a guide to the finished package. Download the research record for methods, tables, figures, manuscript writing, and frozen outputs.",
    )
    files = [
        ("Detailed project report", PROJECT / "final_project_report_tnbc_emt_digital_twin.md", "text/markdown"),
        ("Full manuscript draft", PROJECT / "manuscript_full_draft_tnbc_emt_digital_twin.md", "text/markdown"),
        ("Validation memo", PROJECT / "validation_memo.md", "text/markdown"),
        ("Novelty and positioning report", PROJECT / "novelty_positioning" / "novelty_and_positioning_report.md", "text/markdown"),
        ("Project Q&A", PROJECT / "project_questions_and_answers.md", "text/markdown"),
        ("Novelty presentation deck", PROJECT / "novelty_positioning" / "tnbc_emt_digital_twin_novelty_deck.pptx", "application/vnd.openxmlformats-officedocument.presentationml.presentation"),
        ("Frozen release guide", PROJECT / "frozen_releases" / "tnbc_digital_twin_freeze_2026-06-15" / "README.md", "text/markdown"),
    ]
    for index in range(0, len(files), 2):
        columns = st.columns(2)
        for column, (label, path, mime) in zip(columns, files[index:index + 2]):
            with column:
                st.markdown(f"<div class='download-label'><strong>{label}</strong><br><span>{path.name}</span></div>", unsafe_allow_html=True)
                download_file(f"Download {label}", path, mime)

    st.subheader("Reproduce the complete pipeline")
    st.code("python scripts/run_tnbc_digital_twin_pipeline.py --skip-existing", language="bash")
    st.caption("Configuration: configs/tnbc_digital_twin.yml. The frozen release protects the published-style tables and figures from accidental replacement.")


def inject_style() -> None:
    st.markdown(
        """
        <style>
          .stApp { background: #f7f8f4; color: #17222b; }
          [data-testid="stSidebar"] { background: #14213d; }
          [data-testid="stSidebar"] * { color: #f6f7f1 !important; }
          [data-testid="stSidebar"] .stRadio label { padding: 3px 0; }
          .block-container { max-width: 1180px; padding-top: 2.25rem; padding-bottom: 3rem; }
          h1 { color: #14213d; letter-spacing: 0 !important; font-weight: 700; }
          h2, h3 { color: #173b4d; letter-spacing: 0 !important; }
          .section-intro { max-width: 880px; color: #425466; font-size: 1.08rem; line-height: 1.6; margin-bottom: 1.4rem; }
          .notice { background: #e8f4ef; border-left: 5px solid #2a9d8f; padding: 0.85rem 1rem; margin: 0.5rem 0 1.5rem; border-radius: 4px; }
          .state-card { background: #ffffff; min-height: 148px; border: 1px solid #dce3df; border-top: 5px solid; border-radius: 6px; padding: 0.9rem; box-shadow: 0 1px 2px rgba(23, 34, 43, 0.05); }
          .state-card span, .download-label span { color: #62717d; font-size: 0.88rem; line-height: 1.35; }
          .state-letter { font-size: 1.75rem; line-height: 1; font-weight: 750; margin-bottom: 0.5rem; }
          .workflow { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 10px; margin: 0.75rem 0 1.5rem; }
          .workflow > div, .research-grid > div { background: #ffffff; border: 1px solid #dce3df; border-radius: 6px; padding: 0.85rem; line-height: 1.4; }
          .research-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; }
          .download-label { min-height: 64px; padding: 0.75rem 0 0.25rem; }
          [data-testid="stMetric"] { background: #ffffff; border: 1px solid #dce3df; border-radius: 6px; padding: 0.65rem 0.8rem; }
          [data-testid="stMetricLabel"] { color: #52707b; }
          [data-testid="stMetricValue"] { color: #14213d; }
          .stButton > button, .stDownloadButton > button { border-radius: 5px; border: 1px solid #2a9d8f; color: #146b65; background: #ffffff; }
          .stButton > button:hover, .stDownloadButton > button:hover { border-color: #146b65; color: #ffffff; background: #146b65; }
          @media (max-width: 760px) {
            .workflow, .research-grid { grid-template-columns: 1fr; }
            .block-container { padding-top: 1.25rem; }
          }
        </style>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    st.set_page_config(page_title="TNBC EMT Digital Twin", layout="wide")
    inject_style()
    with st.sidebar:
        st.title("TNBC EMT Twin")
        st.caption("Research portal | frozen project evidence")
        page = st.radio(
            "Navigate",
            ["Overview", "Evidence and novelty", "Results explorer", "Clinical lens", "Research lens", "Questions and answers", "Reports and reproducibility"],
            label_visibility="collapsed",
        )
        st.divider()
        st.markdown("**Designed for**")
        st.caption("Clinicians, researchers, trainees, reviewers, and collaborators")
        st.markdown("**Scope**")
        st.caption("Public cohorts only. No patient upload. No treatment advice.")
        st.divider()
        st.caption("Project: EMT plasticity under therapy in triple-negative breast cancer during neoadjuvant chemotherapy.")

    pages = {
        "Overview": render_overview,
        "Evidence and novelty": render_evidence,
        "Results explorer": render_results,
        "Clinical lens": render_clinical_lens,
        "Research lens": render_research_lens,
        "Questions and answers": render_questions,
        "Reports and reproducibility": render_downloads,
    }
    pages[page]()
    st.divider()
    st.caption("TNBC EMT Digital Twin research prototype. Interpret all findings with the project report, validation memo, and intended-use boundaries.")


if __name__ == "__main__":
    main()
