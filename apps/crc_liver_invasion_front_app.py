from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed" / "crc_liver_invasion_front_v1"
DOCS = ROOT / "docs" / "crc_liver_invasion_front"
FIGURES = DATA / "figures"
DELIVERABLES = ROOT / "deliverables" / "crc_liver_invasion_front_presentation_pack"


def read_table(name: str) -> pd.DataFrame:
    path = DATA / name
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path, sep="\t")


def render_css(st) -> None:
    st.markdown(
        """
        <style>
        :root { --ink:#17212b; --muted:#60707c; --line:#d8dee4; --panel:#f4f6f7; --green:#477b4b; --red:#a63d47; --amber:#9c6a17; --blue:#276c96; }
        .stApp { background:#fff; color:var(--ink); }
        .block-container { max-width:1320px; padding-top:1.25rem; padding-bottom:3rem; }
        h1,h2,h3 { color:var(--ink); letter-spacing:0 !important; }
        h1 { font-size:2.05rem !important; }
        h2 { font-size:1.42rem !important; }
        h3 { font-size:1.05rem !important; }
        [data-testid="stMetric"] { background:var(--panel); border:1px solid var(--line); border-radius:6px; padding:.8rem 1rem; min-height:108px; }
        .hypothesis { border-left:5px solid var(--green); background:var(--panel); padding:.9rem 1rem; border-radius:0 6px 6px 0; margin:.4rem 0 1rem; }
        .boundary { border-left:5px solid var(--amber); background:#fbf7ed; padding:.9rem 1rem; border-radius:0 6px 6px 0; margin:.4rem 0 1rem; }
        .supported { color:var(--green); font-weight:700; }
        .unsupported { color:var(--red); font-weight:700; }
        [data-testid="stDataFrame"] { border:1px solid var(--line); border-radius:4px; }
        @media (max-width:740px) { .block-container { padding-left:1rem; padding-right:1rem; } h1 { font-size:1.55rem !important; } [data-testid="stMetric"] { min-height:92px; } }
        </style>
        """,
        unsafe_allow_html=True,
    )


def download(st, label: str, path: Path, mime: str) -> None:
    if path.exists():
        st.download_button(label, path.read_bytes(), path.name, mime, icon=":material/download:", width="stretch")


def main() -> None:
    import streamlit as st

    st.set_page_config(page_title="CRC Liver Invasion Front", page_icon=":material/hub:", layout="wide")
    render_css(st)

    @st.cache_data(show_spinner=False)
    def load_data() -> dict[str, pd.DataFrame]:
        return {
            "summary": read_table("interface_section_summary.tsv"),
            "front": read_table("front_vs_core_statistics.tsv"),
            "importance": read_table("model_feature_importance.tsv"),
            "ablation": read_table("feature_group_ablation.tsv"),
            "edges": read_table("edge_type_summary.tsv"),
            "coverage": read_table("signature_coverage.tsv"),
            "reference": pd.read_csv(DATA / "reference" / "gse225857_scrna_reference_audit.tsv", sep="\t")
            if (DATA / "reference" / "gse225857_scrna_reference_audit.tsv").exists()
            else pd.DataFrame(),
        }

    frames = load_data()
    metrics_path = DATA / "model_metrics.json"
    metrics = json.loads(metrics_path.read_text(encoding="utf-8")) if metrics_path.exists() else {}

    st.sidebar.header("Evidence view")
    audience = st.sidebar.segmented_control("Audience", ["Research", "Pathology", "Interview"], default="Research")
    st.sidebar.divider()
    st.sidebar.markdown("**Project artifacts**")
    download(st.sidebar, "Executed report", DOCS / "executed_project_report.md", "text/markdown")
    download(st.sidebar, "Detailed plan", DOCS / "detailed_project_plan.md", "text/markdown")
    download(st.sidebar, "Pathology review", DOCS / "pathology_review_template.tsv", "text/tab-separated-values")
    st.sidebar.markdown("**Presentation pack**")
    download(st.sidebar, "Interpretation slides", DELIVERABLES / "CRC_Liver_Invasion_Front_Interpretation_Presentation.pptx", "application/vnd.openxmlformats-officedocument.presentationml.presentation")
    download(st.sidebar, "Complete project reference", DELIVERABLES / "CRC_Liver_Invasion_Front_Complete_Project_Reference.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    download(st.sidebar, "Interview Q&A", DELIVERABLES / "CRC_Liver_Invasion_Front_Interview_QA.pdf", "application/pdf")

    st.title("CRC Liver-Metastasis Invasion-Front Model")
    st.caption("Compartment-aware heterogeneous graphs across the tumour-liver interface")
    st.markdown(
        '<div class="hypothesis"><strong>Central hypothesis.</strong> Partial-EMT CRC cells occupy distinct hepatocyte-contact or fibroblast-rich interface ecosystems, with separable macrophage, endothelial, ECM and glycolytic gradients.</div>',
        unsafe_allow_html=True,
    )

    summary = frames["summary"]
    liver_summary = summary[summary["site"].eq("liver_metastasis")] if not summary.empty else summary
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Visium sections", int(len(summary)) if not summary.empty else 0, help="Four primary CRC and two liver-metastasis sections")
    m2.metric("Liver interface spots", f"{int(liver_summary['interface_spots'].sum()):,}" if not liver_summary.empty else "0")
    m3.metric("Cross-section ROC AUC", f"{metrics.get('roc_auc', float('nan')):.3f}" if metrics else "Pending")
    m4.metric("Permutation P", f"{metrics.get('permutation_p', float('nan')):.3f}" if metrics else "Pending")

    boundary_text = {
        "Research": "Interface and growth-pattern assignments are marker-plus-spatial weak labels. Spot-level statistics are descriptive because sections, not spots, are independent biological units.",
        "Pathology": "Desmoplastic-like and replacement-like fields require H&E boundary tracing and consensus HGP percentage scoring before use as reference labels.",
        "Interview": "The strongest design choice is a signed interface with section-held-out validation; the strongest limitation is only two liver-metastasis sections.",
    }
    st.markdown(f'<div class="boundary"><strong>Evidence boundary.</strong> {boundary_text[audience]}</div>', unsafe_allow_html=True)

    overview, interface, graph, model, evidence = st.tabs(["Overview", "Interface biology", "Graph evidence", "Model audit", "Methods & claims"])
    with overview:
        st.image(FIGURES / "workflow_overview.png", width="stretch")
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Supported")
            st.markdown("<span class='supported'>Public-data findings</span>", unsafe_allow_html=True)
            st.markdown("- Spatially coherent malignant, hepatocyte and niche programmes.\n- Auditable tumour/liver fronts in public liver sections.\n- Cross-section testing of typed graph-context features.\n- Ranked experimental hypotheses for interface perturbation.")
        with c2:
            st.subheader("Not established")
            st.markdown("<span class='unsupported'>Clinical and causal claims</span>", unsafe_allow_html=True)
            st.markdown("- Patient prognosis or treatment response.\n- Pathologist-confirmed histological growth pattern.\n- Functional ligand-receptor signalling.\n- EMT as a sufficient cause of liver invasion.")
        if not summary.empty:
            st.subheader("Section audit")
            st.dataframe(summary, hide_index=True, width="stretch")

    with interface:
        st.image(FIGURES / "interface_maps.png", caption="Compartment calls and signed distance maps; outlined spots lie within the interface window.", width="stretch")
        st.image(FIGURES / "interface_gradient_profiles.png", caption="Programme profiles from tumour core through the inferred boundary into adjacent liver.", width="stretch")
        front = frames["front"]
        if not front.empty:
            st.subheader("Tumour front versus tumour core")
            chart = front.set_index("program")[["front_minus_core"]].sort_values("front_minus_core")
            st.bar_chart(chart, horizontal=True, color="#276c96", height=360)
            st.dataframe(front, hide_index=True, width="stretch")

    with graph:
        st.image(FIGURES / "heterograph_interface_excerpt.png", caption="A contiguous L1 interface subgraph. Dark edges mark direct malignant-hepatocyte contacts.", width="stretch")
        edges = frames["edges"]
        if not edges.empty:
            families = edges.groupby("edge_family", as_index=False)["edge_count"].sum().sort_values("edge_count", ascending=False)
            st.subheader("Typed edge families")
            st.bar_chart(families.set_index("edge_family"), horizontal=True, color="#78589d", height=350)
            st.dataframe(edges, hide_index=True, width="stretch")
        st.markdown("**Interaction axes retained for perturbation design:** CCL18-PITPNM3, SPP1-CD44/ITGAV, TGF-beta-TGFBR2, CXCL12-CXCR4, HGF-MET, VEGFA-KDR, ANGPT2-TEK, COL1A1-ITGA2 and GAS6-AXL.")

    with model:
        st.image(FIGURES / "interface_model_interpretation.png", width="stretch")
        importance = frames["importance"]
        ablation = frames["ablation"]
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Feature coefficients")
            st.dataframe(importance.head(25), hide_index=True, width="stretch")
        with c2:
            st.subheader("Feature-group ablation")
            st.dataframe(ablation, hide_index=True, width="stretch")
        st.caption("Coefficients and AUC changes are predictive associations in two public sections. They are not causal effect estimates.")

    with evidence:
        st.subheader("Executed evidence stack")
        evidence_table = pd.DataFrame(
            [
                ["GSE225857", "10x Visium FFPE", "4 primary + 2 liver metastasis sections", "Executed"],
                ["GSE225857", "scRNA-seq", "immune and non-immune references", "Available for next deconvolution benchmark"],
                ["Zenodo 7520789", "GeoMx CTA", "48 AOIs, 4 matched patients", "Downloaded; region labels not machine-readable"],
                ["CRLM ISS 2026", "targeted ISS", "26 samples, pathologist-reviewed fronts", "External validation target"],
            ],
            columns=["Dataset", "Modality", "Scale", "Status"],
        )
        st.dataframe(evidence_table, hide_index=True, width="stretch")
        st.subheader("Signature coverage")
        if not frames["coverage"].empty:
            st.dataframe(frames["coverage"], hide_index=True, width="stretch")
        st.subheader("Study-matched single-cell reference")
        if not frames["reference"].empty:
            st.dataframe(frames["reference"], hide_index=True, width="stretch")
        st.subheader("Methodological advantages")
        st.markdown("- CRC-lineage gating separates malignant pEMT from fibroblast RNA.\n- Signed distance preserves spatial direction.\n- Typed edges keep biological relation identity.\n- Leave-section-out testing prevents spot leakage across training and test sets.\n- Permutation and ablation expose fragile models.")

    st.divider()
    st.caption("Research use only. This workbench does not provide diagnosis, prognosis or treatment selection.")


if __name__ == "__main__":
    main()
