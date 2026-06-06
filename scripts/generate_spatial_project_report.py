from __future__ import annotations

from pathlib import Path

import pandas as pd


STATUS_PATH = Path("data/processed/spatial_emt_niche_gnn_project_status/spatial_project_status_summary.tsv")
DETAIL_PATH = Path("data/processed/spatial_emt_niche_gnn_project_status/spatial_project_status_detail.tsv")
COMPARISON_PATH = Path("data/processed/spatial_emt_niche_gnn_comparison/spatial_cancer_cohort_summary.tsv")
BLOCKERS_PATH = Path("data/processed/spatial_emt_niche_gnn_blockers/blocker_solution_manifest.tsv")
METASTASIS_PATH = Path("data/processed/spatial_emt_niche_gnn_blockers/metastasis_progression_candidates.tsv")
GSE274557_SCALEUP_PATH = Path("data/processed/spatial_emt_niche_gnn_blockers/gse274557_scaleup_summary.tsv")
GSE274557_SITE_PATH = Path("data/processed/spatial_emt_niche_gnn_geo_met_pdac_gse274557_fullprep/gse274557_full_site_summary.tsv")
GSE274557_PATIENT_GRAPH_PATH = Path("data/processed/spatial_emt_niche_gnn_geo_met_pdac_gse274557_patient_batches/gse274557_patient_graph_batch_summary.tsv")
GSE154778_DECONV_PATH = Path("data/processed/spatial_emt_niche_gnn_geo_met_pdac_gse274557/gse154778_scrna_deconv/reference_deconvolution_nnls_summary.tsv")
OUT_PATH = Path("docs/spatial_emt_niche_gnn/project_report.md")


def fmt_pct(value: float) -> str:
    return f"{float(value):.1f}%"


def fmt_num(value: float) -> str:
    if pd.isna(value):
        return ""
    return f"{int(value):,}" if float(value).is_integer() else f"{float(value):.3f}"


def clean_text(value: object) -> str:
    if pd.isna(value):
        return ""
    return str(value)


def read_table(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path, sep="\t")


def top_cohort_rows(comparison: pd.DataFrame) -> list[str]:
    if comparison.empty:
        return ["No cohort comparison table was found."]
    cols = [
        "run",
        "spots",
        "emt_niche_fraction",
        "tumor_cell_emt_fraction",
        "stromal_inflated_fraction",
        "mean_ecm_remodeling",
        "mean_angiogenesis",
        "edges",
        "ligand_receptor_edges",
        "hypoxia_gradient_edges",
        "ecm_gradient_edges",
        "histology_similarity_edges",
    ]
    present = [col for col in cols if col in comparison.columns]
    rows = [
        "| Cohort | Spots | EMT niche fraction | Tumor-cell EMT fraction | Stromal-inflated fraction | Mean ECM | Mean angiogenesis | Edges | LR edges | Hypoxia edges | ECM edges | Histology edges |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for _, row in comparison[present].iterrows():
        rows.append(
            "| "
            + " | ".join(
                [
                    str(row.get("run", "")),
                    fmt_num(row.get("spots", 0)),
                    f"{float(row.get('emt_niche_fraction', 0)):.3f}",
                    f"{float(row.get('tumor_cell_emt_fraction', 0)):.3f}",
                    f"{float(row.get('stromal_inflated_fraction', 0)):.3f}",
                    f"{float(row.get('mean_ecm_remodeling', 0)):.3f}",
                    f"{float(row.get('mean_angiogenesis', 0)):.3f}",
                    fmt_num(row.get("edges", 0)),
                    fmt_num(row.get("ligand_receptor_edges", 0)),
                    fmt_num(row.get("hypoxia_gradient_edges", 0)),
                    fmt_num(row.get("ecm_gradient_edges", 0)),
                    fmt_num(row.get("histology_similarity_edges", 0)),
                ]
            )
            + " |"
        )
    return rows


def status_rows(status: pd.DataFrame) -> list[str]:
    rows = ["| Phase | Completion |", "| --- | ---: |"]
    for _, row in status.iterrows():
        rows.append(f"| {row['phase']} | {fmt_pct(row['completion_percent'])} |")
    return rows


def remaining_rows(detail: pd.DataFrame) -> list[str]:
    if detail.empty:
        return ["No detailed status table was found."]
    remaining = detail[~detail["status"].eq("done")].copy()
    rows = ["| Task | Status | Why It Still Matters |", "| --- | --- | --- |"]
    why = {
        "HEST-1k manifest/reproducibility plan": "Needed for multimodal scale and H&E-linked validation.",
        "cell2location/Tangram/RCTD/stereoscope deconvolution": "Needed to separate malignant EMT from CAF/stromal mixtures.",
        "Candidate niche labels": "Needed before claims move beyond weak-label biology.",
        "Histology-similarity edges": "Needed to fuse transcriptomic neighborhoods with tissue morphology.",
        "HTAN spatial datasets": "Needed for external validation beyond 10x/GEO examples.",
        "Additional GEO Visium cancer cohorts": "Needed for broader generalization and disease diversity.",
        "SpatialTME/SCAR public atlas feasibility": "Needed to compare against public immune/stromal spatial atlases.",
        "Matched scRNA-seq references": "Needed for real deconvolution and compartment-level claims.",
        "Metastasis/progression cohorts": "First cohort done; matched primary-metastatic PDAC remains the important scale-up.",
        "Pathology foundation embeddings": "Needed for richer H&E features beyond color/stain proxies.",
    }
    for _, row in remaining.iterrows():
        rows.append(f"| {row['task']} | {row['status']} | {why.get(row['task'], 'Needed for publication-grade robustness.')} |")
    return rows


def blocker_rows(blockers: pd.DataFrame) -> list[str]:
    if blockers.empty:
        return ["No blocker manifest was found."]
    rows = ["| Blocker | Current Solution | Status | Next Action |", "| --- | --- | --- | --- |"]
    for _, row in blockers.iterrows():
        rows.append(f"| {row['blocker']} | {row['solution']} | {row['status']} | {row['next_action']} |")
    return rows


def metastasis_rows(metastasis: pd.DataFrame) -> list[str]:
    if metastasis.empty:
        return ["No metastasis candidate table was found."]
    rows = ["| Accession | Disease | Samples | Pipeline Status | Output |", "| --- | --- | --- | --- | --- |"]
    for _, row in metastasis.iterrows():
        rows.append(
            f"| {row['accession']} | {row['disease']} | {row['samples']} | "
            f"{clean_text(row.get('pipeline_status', ''))} | {clean_text(row.get('pipeline_output', ''))} |"
        )
    return rows


def gse274557_rows(site_summary: pd.DataFrame) -> list[str]:
    if site_summary.empty:
        return ["Full GSE274557 site summary has not been generated yet."]
    rows = [
        "| Site | Spots | EMT niche fraction | Stromal-inflated fraction | Tumor-cell EMT fraction | Mean CAF/TAM | Mean hypoxia | Mean ECM |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for _, row in site_summary.iterrows():
        rows.append(
            "| "
            + " | ".join(
                [
                    str(row.get("site_label", "")),
                    fmt_num(row.get("spots", 0)),
                    f"{float(row.get('emt_niche_fraction', 0)):.3f}",
                    f"{float(row.get('stromal_inflated_fraction', 0)):.3f}",
                    f"{float(row.get('tumor_cell_emt_fraction', 0)):.3f}",
                    f"{float(row.get('mean_caf_tam_niche', 0)):.3f}",
                    f"{float(row.get('mean_hypoxia', 0)):.3f}",
                    f"{float(row.get('mean_ecm_remodeling', 0)):.3f}",
                ]
            )
            + " |"
        )
    return rows


def patient_graph_rows(batch_summary: pd.DataFrame) -> list[str]:
    if batch_summary.empty:
        return ["Patient-batched graph summary has not been generated yet."]
    rows = ["| Patient | Samples | Spots | Edges | Test accuracy |", "| --- | ---: | ---: | ---: | ---: |"]
    for _, row in batch_summary.iterrows():
        rows.append(
            f"| {row['patient_id']} | {fmt_num(row['samples'])} | {fmt_num(row['spots'])} | "
            f"{fmt_num(row['edges'])} | {float(row['test_accuracy']):.3f} |"
        )
    return rows


def scrna_deconv_rows(deconv: pd.DataFrame) -> list[str]:
    if deconv.empty:
        return ["Real scRNA deconvolution summary has not been generated yet."]
    cols = [
        "sample_id",
        "site_label",
        "spots",
        "mean_tumor_epithelial_pdac_scrna",
        "mean_tumor_mesenchymal_plastic_scrna",
        "mean_caf_myofibroblast_scrna",
        "mean_tam_spp1_macrophage_scrna",
        "mean_t_cell_cytotoxic_scrna",
    ]
    rows = [
        "| Sample | Site | Spots | Epithelial tumor | Mesenchymal-plastic tumor | CAF | TAM | T cell |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for _, row in deconv[cols].iterrows():
        rows.append(
            f"| {row['sample_id']} | {row['site_label']} | {fmt_num(row['spots'])} | "
            f"{float(row['mean_tumor_epithelial_pdac_scrna']):.3f} | "
            f"{float(row['mean_tumor_mesenchymal_plastic_scrna']):.3f} | "
            f"{float(row['mean_caf_myofibroblast_scrna']):.3f} | "
            f"{float(row['mean_tam_spp1_macrophage_scrna']):.3f} | "
            f"{float(row['mean_t_cell_cytotoxic_scrna']):.3f} |"
        )
    return rows


def write_report() -> None:
    status = read_table(STATUS_PATH)
    detail = read_table(DETAIL_PATH)
    comparison = read_table(COMPARISON_PATH)
    blockers = read_table(BLOCKERS_PATH)
    metastasis = read_table(METASTASIS_PATH)
    scaleup = read_table(GSE274557_SCALEUP_PATH)
    gse_site = read_table(GSE274557_SITE_PATH)
    patient_graph = read_table(GSE274557_PATIENT_GRAPH_PATH)
    scrna_deconv = read_table(GSE154778_DECONV_PATH)

    overall = status.loc[status["phase"].eq("overall"), "completion_percent"].iloc[0] if not status.empty else 0
    total_spots = int(comparison["spots"].sum()) if "spots" in comparison else 0
    total_edges = int(comparison["edges"].sum()) if "edges" in comparison else 0

    lines = [
        "# Spatial EMT Niche GNN Project Report",
        "",
        "## Executive Summary",
        "",
        f"The project is currently {fmt_pct(overall)} complete by the weighted implementation tracker.",
        f"It has processed {total_spots:,} spatial spots and {total_edges:,} graph edges across demo, 10x public cancer, GEO pancreatic cancer, and GEO brain-metastasis cohorts.",
        "The core value is an interpretable pipeline for weak-label discovery of EMT, partial EMT, stromal contamination, CAF/TAM/hypoxic niches, ECM remodeling, angiogenesis, and ferroptosis-window signals in spatial transcriptomics.",
        "",
        "All current outputs are research hypotheses only. They are not diagnostic, prognostic, or treatment recommendations.",
        "",
        "## Completion Chart",
        "",
        *status_rows(status),
        "",
        "## Implemented System",
        "",
        "- Standardized public Visium and GEO cohorts into expression and spatial metadata tables.",
        "- Exported lightweight AnnData-style h5ad files for downstream spatial workflows.",
        "- Implemented EMT, partial EMT, stromal, immune, CAF/TAM, hypoxia, ECM remodeling, angiogenesis, and ferroptosis scores.",
        "- Implemented marker-proxy and NNLS-reference deconvolution paths.",
        "- Built typed spatial graphs with kNN/radius, ligand-receptor, hypoxia-gradient, and ECM-gradient edges.",
        "- Built heterogeneous compartment graphs for tumor, CAF, TAM, endothelial, T cell, hypoxic, ECM-rich, and ferroptosis-window nodes.",
        "- Trained a dependency-light graph-aware logistic baseline for reproducible MVP benchmarking.",
        "- Added H&E tile color/stain-proxy feature extraction for 10x tissue images.",
        "- Added first real histology-similarity graph edges in the 10x breast cohort.",
        "- Added GSE274557 matched Pt-1 primary/liver/peritoneal metastatic PDAC pilot.",
        "- Downloaded, standardized, and scored the full 55-sample non-PDX GSE274557 cohort locally.",
        "- Completed patient-batched graph/model summaries for all 13 GSE274557 non-PDX patients.",
        "- Added PDAC marker-reference NNLS deconvolution summary for the matched metastatic pilot.",
        "- Added real GSE154778 scRNA-derived marker-assigned reference and NNLS deconvolution summary.",
        "",
        "## Cohort Results",
        "",
        *top_cohort_rows(comparison),
        "",
        "## Metastasis And Progression Work",
        "",
        *metastasis_rows(metastasis),
        "",
        "## Full GSE274557 Scoring Scale-Up",
        "",
        (
            f"Full non-PDX status: {int(scaleup['raw_sample_complete'].iloc[0])}/{int(scaleup['non_pdx_samples'].iloc[0])} "
            f"samples downloaded for {int(scaleup['patients'].iloc[0])} patients."
            if not scaleup.empty
            else "Full GSE274557 scale-up status has not been generated yet."
        ),
        "",
        *gse274557_rows(gse_site),
        "",
        "## Full GSE274557 Patient-Batched Graphs",
        "",
        *patient_graph_rows(patient_graph),
        "",
        "## Real scRNA-Based Deconvolution",
        "",
        "Reference: GSE154778 PDAC primary and metastatic scRNA-seq, marker-assigned into major compartments.",
        "",
        *scrna_deconv_rows(scrna_deconv),
        "",
        "## Blocker Solutions",
        "",
        *blocker_rows(blockers),
        "",
        "External access and expert-review execution details are consolidated in `docs/spatial_emt_niche_gnn/external_blocker_resolution_playbook.md`.",
        "The pathologist operations pack includes reviewer roles, sourcing options, calibration batches, high-impact overlap review, and a recruitment email.",
        "",
        "## Remaining Work",
        "",
        *remaining_rows(detail),
        "",
        "## Next Execution Order",
        "",
        "1. Install a dedicated Python/R deconvolution environment for Tangram, cell2location, and RCTD.",
        "2. Expand the real scRNA reference with GSE155698 and GSE205013, then compare against the GSE154778 reference.",
        "3. Download one HTAN WUSTL PDAC spatial sample from the portal and adapt it into the standard expression/metadata format.",
        "4. Run histology-similarity edges across every cohort with local H&E tiles, then compare against pathologist regions.",
        "5. Use the pathologist review template to annotate invasive edge, necrosis/hypoxia, stroma-rich, tumor-rich, immune-rich, and vessel-rich regions.",
        "6. Evaluate pathology foundation embeddings after the color/stain-proxy baseline is stable.",
        "",
        "## Publication Direction",
        "",
        "The strongest first manuscript angle is not claiming a final GNN biomarker. It is a reproducible open pipeline showing how EMT-like tumor-cell plasticity, stromal inflation, CAF/TAM crosstalk, hypoxia, ECM remodeling, and metastasis-associated niches can be separated and stress-tested across public spatial cohorts.",
        "",
        "## Key Public Resources",
        "",
        "- 10x public Visium cancer examples.",
        "- GEO GSE274103 treatment-naive pancreatic cancer Visium.",
        "- GEO GSE179572 human brain metastasis Visium.",
        "- GEO GSE274557 metastatic pancreatic cancer, prioritized for next matched-site validation.",
        "- HEST-1k, pending authenticated metadata/image access.",
        "- HTAN spatial transcriptomics portal, pending selected atlas ingestion.",
        "",
        "## Clinical Caveats",
        "",
        "- A high EMT score in a Visium spot can reflect malignant EMT, CAF/stromal admixture, or both.",
        "- Partial EMT is a plasticity proxy, not a tumor-cell identity label.",
        "- Current labels are weak labels generated from transcriptomic proxies.",
        "- Survival or treatment implications require independent clinical annotation and expert review.",
    ]
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    write_report()
