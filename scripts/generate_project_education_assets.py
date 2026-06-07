from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Polygon
import pandas as pd


ASSET_DIR = Path("docs/assets/project_overview")
STUDENT_REPORT = Path("docs/student_accessible_project_report.md")
INTERVIEW_GUIDE = Path("docs/project_interview_qa_guide.md")

SPATIAL_STATUS = Path("data/processed/spatial_emt_niche_gnn_project_status/spatial_project_status_summary.tsv")
PROJECT_STATUS = Path("data/processed/project_status/completion_summary.tsv")
BLOCKER_AUDIT = Path("data/processed/spatial_emt_niche_gnn_project_status/final_blocker_audit_summary.tsv")
SPATIAL_COHORTS = Path("data/processed/spatial_emt_niche_gnn_comparison/spatial_cancer_cohort_summary.tsv")
TCGA_SUMMARY = Path("data/processed/tcga_xena_v1/cancer_type_summary.tsv")
TARGET_RANKING = Path("data/processed/target_ranker_real_evidence_v1/target_ranking.tsv")


PALETTE = {
    "ink": "#1f2937",
    "muted": "#6b7280",
    "blue": "#2563eb",
    "cyan": "#0891b2",
    "green": "#16a34a",
    "amber": "#d97706",
    "red": "#dc2626",
    "purple": "#7c3aed",
    "gray": "#e5e7eb",
    "light": "#f8fafc",
}


def read(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, sep="\t") if path.exists() else pd.DataFrame()


def savefig(name: str) -> str:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    path = ASSET_DIR / name
    plt.savefig(path, dpi=220, bbox_inches="tight")
    plt.close()
    return f"assets/project_overview/{name}"


def draw_box(ax, x, y, w, h, text, color, fontsize=10):
    box = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.02,rounding_size=0.03",
        facecolor=color,
        edgecolor=PALETTE["ink"],
        linewidth=1.2,
    )
    ax.add_patch(box)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fontsize, color="white", weight="bold")


def project_architecture_chart() -> str:
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_title("Whole Project Architecture", fontsize=18, weight="bold", color=PALETTE["ink"])
    draw_box(ax, 0.05, 0.68, 0.18, 0.13, "Public Data\nTCGA, GEO, 10x,\nDepMap, PRISM,\nLINCS", PALETTE["blue"], 9)
    draw_box(ax, 0.30, 0.78, 0.18, 0.11, "EMT-State\nAtlas", PALETTE["cyan"], 10)
    draw_box(ax, 0.30, 0.55, 0.18, 0.11, "Metastasis\nTarget Ranker", PALETTE["green"], 10)
    draw_box(ax, 0.30, 0.32, 0.18, 0.11, "Spatial EMT\nNiche GNN", PALETTE["purple"], 10)
    draw_box(ax, 0.57, 0.78, 0.18, 0.11, "Scores:\nEMT, partial EMT,\nstroma, immune", PALETTE["amber"], 8)
    draw_box(ax, 0.57, 0.55, 0.18, 0.11, "Evidence:\ndependency,\ndruggability,\nsafety", PALETTE["amber"], 8)
    draw_box(ax, 0.57, 0.32, 0.18, 0.11, "Graphs:\nspots, niches,\nLR edges", PALETTE["amber"], 8)
    draw_box(ax, 0.82, 0.57, 0.14, 0.16, "Research\nHypotheses\n+\nFigures", PALETTE["red"], 9)
    for y in [0.835, 0.605, 0.375]:
        ax.add_patch(FancyArrowPatch((0.23, 0.745), (0.30, y), arrowstyle="-|>", mutation_scale=14, color=PALETTE["ink"]))
    for y in [0.835, 0.605, 0.375]:
        ax.add_patch(FancyArrowPatch((0.48, y), (0.57, y), arrowstyle="-|>", mutation_scale=14, color=PALETTE["ink"]))
        ax.add_patch(FancyArrowPatch((0.75, y), (0.82, 0.65), arrowstyle="-|>", mutation_scale=14, color=PALETTE["ink"]))
    ax.text(0.5, 0.08, "Core principle: separate tumor EMT biology from stromal contamination before proposing targets.", ha="center", fontsize=11, color=PALETTE["ink"])
    return savefig("project_architecture.png")


def completion_chart() -> str:
    project = read(PROJECT_STATUS)
    spatial = read(SPATIAL_STATUS)
    audit = read(BLOCKER_AUDIT)
    rows = []
    if not project.empty:
        rows.extend(project.rename(columns={"project": "label", "completion_percent": "value"})[["label", "value"]].to_dict("records"))
    if not spatial.empty:
        overall = spatial[spatial["phase"].eq("overall")]
        if not overall.empty:
            rows.append({"label": "spatial_emt_niche_gnn", "value": float(overall["completion_percent"].iloc[0])})
    if not audit.empty:
        internal = audit[audit["metric"].eq("internal_blocker_resolution_percent")]
        if not internal.empty:
            rows.append({"label": "internal_blocker_readiness", "value": float(internal["value"].iloc[0])})
    df = pd.DataFrame(rows)
    fig, ax = plt.subplots(figsize=(10, 5))
    colors = [PALETTE["cyan"], PALETTE["green"], PALETTE["purple"], PALETTE["amber"]][: len(df)]
    ax.barh(df["label"], df["value"], color=colors)
    ax.set_xlim(0, 105)
    ax.set_xlabel("Completion percent")
    ax.set_title("Project Completion Snapshot", fontsize=15, weight="bold")
    for i, v in enumerate(df["value"]):
        ax.text(v + 1, i, f"{v:.1f}%", va="center", color=PALETTE["ink"])
    ax.grid(axis="x", alpha=0.2)
    return savefig("completion_snapshot.png")


def cohort_scale_chart() -> str:
    cohorts = read(SPATIAL_COHORTS)
    cohorts = cohorts.sort_values("spots", ascending=True)
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.barh(cohorts["run"], cohorts["spots"], color=PALETTE["purple"], alpha=0.85)
    ax.set_title("Spatial Cohorts Processed", fontsize=15, weight="bold")
    ax.set_xlabel("Spots")
    for i, v in enumerate(cohorts["spots"]):
        ax.text(v + max(cohorts["spots"]) * 0.01, i, f"{int(v):,}", va="center", fontsize=8)
    ax.grid(axis="x", alpha=0.2)
    return savefig("spatial_cohort_scale.png")


def target_ranker_chart() -> str:
    targets = read(TARGET_RANKING).sort_values("priority_score", ascending=False).head(12)
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.bar(targets["target"], targets["priority_score"], color=PALETTE["green"], alpha=0.85)
    ax.set_title("Top Metastasis Target-Ranker Hypotheses", fontsize=15, weight="bold")
    ax.set_ylabel("Priority score")
    ax.tick_params(axis="x", rotation=45)
    ax.grid(axis="y", alpha=0.2)
    return savefig("top_target_ranking.png")


def tcga_emt_chart() -> str:
    tcga = read(TCGA_SUMMARY).sort_values("emt_score_mean", ascending=False).head(10)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(tcga["cancer_type"], tcga["emt_score_mean"], color=PALETTE["cyan"], alpha=0.9)
    ax.set_title("TCGA Cancer Types With High Mean EMT Score", fontsize=15, weight="bold")
    ax.set_ylabel("Mean EMT score")
    ax.tick_params(axis="x", rotation=45)
    ax.grid(axis="y", alpha=0.2)
    return savefig("tcga_high_emt_cancer_types.png")


def emt_cartoon() -> str:
    fig, ax = plt.subplots(figsize=(12, 5.8))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_title("Cartoon: EMT, Stromal Confounding, and Metastatic Niche Formation", fontsize=15, weight="bold")
    stages = [
        (0.12, "Epithelial\ntumor cells", PALETTE["blue"]),
        (0.35, "Partial EMT\nplastic cells", PALETTE["amber"]),
        (0.58, "CAF/TAM/hypoxic\nniche", PALETTE["purple"]),
        (0.82, "Metastatic\nhypothesis", PALETTE["red"]),
    ]
    for x, label, color in stages:
        ax.add_patch(Circle((x, 0.58), 0.09, facecolor=color, edgecolor=PALETTE["ink"], lw=1.2, alpha=0.9))
        ax.text(x, 0.58, label, ha="center", va="center", color="white", weight="bold", fontsize=9)
    for x0, x1 in [(0.21, 0.28), (0.44, 0.51), (0.67, 0.75)]:
        ax.add_patch(FancyArrowPatch((x0, 0.58), (x1, 0.58), arrowstyle="-|>", mutation_scale=18, color=PALETTE["ink"], lw=1.5))
    for x in [0.51, 0.56, 0.62]:
        ax.add_patch(Polygon([[x, 0.30], [x + 0.04, 0.37], [x + 0.01, 0.43], [x - 0.03, 0.39]], facecolor="#94a3b8", edgecolor=PALETTE["ink"], alpha=0.8))
    ax.text(0.58, 0.16, "Stroma can mimic EMT signal,\nso deconvolution and pathology review matter.", ha="center", fontsize=9.5, color=PALETTE["ink"])
    ax.text(0.12, 0.28, "Bulk RNA:\nTCGA EMT atlas", ha="center", fontsize=9.5)
    ax.text(0.35, 0.27, "Targets:\nAXL/TAM, TGF-beta,\nFAK/SRC, ferroptosis", ha="center", fontsize=9.5)
    ax.text(0.82, 0.28, "Spatial graph:\nwho neighbors whom?", ha="center", fontsize=9.5)
    return savefig("emt_metastasis_cartoon.png")


def make_student_report(paths: dict[str, str]) -> None:
    project = read(PROJECT_STATUS)
    spatial = read(SPATIAL_STATUS)
    audit = read(BLOCKER_AUDIT)
    cohorts = read(SPATIAL_COHORTS)
    targets = read(TARGET_RANKING).sort_values("priority_score", ascending=False).head(8)
    tcga = read(TCGA_SUMMARY).sort_values("emt_score_mean", ascending=False).head(8)
    spatial_overall = float(spatial[spatial["phase"].eq("overall")]["completion_percent"].iloc[0])
    internal = float(audit[audit["metric"].eq("internal_blocker_resolution_percent")]["value"].iloc[0])
    lines = [
        "# AI in Cancer Drug Discovery: Student-Friendly Project Report",
        "",
        "## 1. Big Picture",
        "",
        "This project asks a practical research question: can public data and AI/ML help us understand epithelial-to-mesenchymal transition (EMT), metastasis, and target susceptibility in cancer?",
        "",
        "The answer from the current project is: yes, as a hypothesis-generation system. The pipeline does not make clinical recommendations. It builds interpretable scores, graphs, target rankings, and validation queues that students and scientists can inspect.",
        "",
        f"![Project architecture]({paths['architecture']})",
        "",
        "## 2. The Three Main Project Pillars",
        "",
        "| Pillar | What it does | Main output |",
        "| --- | --- | --- |",
        "| EMT-state-atlas | Scores EMT, partial EMT, stromal contamination, immune context, and survival-ready outputs across TCGA/Xena. | `emt_scores.tsv`, `cancer_type_summary.tsv`, survival associations |",
        "| Metastasis-target-ranker | Integrates target evidence from dependency, druggability, compounds, safety risk, and literature. | ranked targets and evidence cards |",
        "| Spatial-EMT-niche-GNN | Scores spatial transcriptomics, builds graphs, interprets niches, prepares deconvolution and pathology review. | spatial scores, graph summaries, model metrics, review queues |",
        "",
        "## 3. Current Completion",
        "",
        f"The two original core projects are complete in the tracker, while the spatial project is {spatial_overall:.1f}% complete by weighted workflow progress. The final blocker audit reports {internal:.1f}% internal engineering readiness for known blockers.",
        "",
        f"![Completion chart]({paths['completion']})",
        "",
        "## 4. Data Used",
        "",
        "The project uses public-data-first design. Large files stay local, while GitHub stores scripts, manifests, documentation, and compact outputs.",
        "",
        "- TCGA/UCSC Xena for bulk cancer EMT-state analysis.",
        "- 10x Genomics public Visium examples for breast, lung, prostate, ovarian, and colorectal cancer.",
        "- GEO pancreatic cancer and brain metastasis spatial cohorts.",
        "- DepMap/PRISM/LINCS/Open Targets/DGIdb/ChEMBL-style evidence for target ranking.",
        "- GSE154778 scRNA-derived reference for first real deconvolution baseline.",
        "",
        f"![Spatial cohort scale]({paths['cohorts']})",
        "",
        "## 5. How EMT Is Scored",
        "",
        "The EMT score compares epithelial and mesenchymal transcriptional programs. A partial EMT score tries to identify mixed/plastic states where epithelial and mesenchymal signals coexist. This matters because metastasis often involves cell plasticity rather than a simple binary switch.",
        "",
        "Important warning: high EMT signal in a tissue spot can come from malignant tumor cells, stromal fibroblasts, CAFs, or mixed spots. That is why the project also scores stromal contamination, CAF/TAM niche, immune context, hypoxia, ECM remodeling, and deconvolution proxies.",
        "",
        f"![TCGA high EMT cancer types]({paths['tcga']})",
        "",
        "## 6. What the Spatial Project Adds",
        "",
        "Bulk RNA tells us what genes are expressed, but spatial transcriptomics asks where those programs occur. The spatial project builds graphs where each spot is a node and edges represent physical neighbors, ligand-receptor links, hypoxia gradients, ECM gradients, or histology similarity.",
        "",
        "This lets us ask questions like:",
        "",
        "- Are EMT-high spots near CAF-rich or TAM-rich regions?",
        "- Are partial EMT regions near invasive-edge-like ECM gradients?",
        "- Are hypoxic niches linked to angiogenesis and ferroptosis windows?",
        "- Which signals are likely tumor-cell EMT versus stromal inflation?",
        "",
        f"![EMT cartoon]({paths['cartoon']})",
        "",
        "## 7. Target-Ranker Findings",
        "",
        "The target ranker prioritizes hypotheses, not drugs for patients. Strong early target families include AXL/TAM signaling, TGF-beta/SMAD, FAK/SRC/integrins, ferroptosis-related genes, CAF/TAM crosstalk, hypoxia metabolism, chromatin regulators, and RNA/P-body regulators.",
        "",
        f"![Target ranking]({paths['targets']})",
        "",
        "| Top target | Family | Priority score |",
        "| --- | --- | ---: |",
    ]
    for _, row in targets.iterrows():
        lines.append(f"| {row['target']} | {row['family']} | {float(row['priority_score']):.3f} |")
    lines.extend(
        [
            "",
            "## 8. Main Findings So Far",
            "",
            "- EMT and stromal signals often overlap, so stromal correction is essential.",
            "- Partial EMT and CAF/TAM/hypoxic niche signals dominate many first spatial runs.",
            "- Peritoneal metastatic PDAC in GSE274557 shows a higher EMT-niche fraction than liver metastasis in the current scoring summary.",
            "- Real scRNA reference deconvolution is now available for the PDAC pilot and suggests different tumor/stromal/immune mixtures across primary, liver, and peritoneal metastatic samples.",
            "- AXL/TAM family members rank strongly because they combine EMT/metastasis relevance, druggability, compound availability, and literature support.",
            "",
            "## 9. What Is Still External",
            "",
            "The code side is ready, but some scientific gates cannot be faked:",
            "",
            "- HEST/UNI/CONCH downloads require accepted HuggingFace terms and token-based access.",
            "- HTAN assay downloads require selected file IDs and Synapse/Gen3/HTAN credentials.",
            "- Pathology validation requires real expert review of the generated queue.",
            "",
            "## 10. How a Student Can Start",
            "",
            "1. Read `docs/methods/04_how_to_read_emt_scores.md`.",
            "2. Run toy data tests with `python -m pytest`.",
            "3. Inspect `data/processed/tcga_xena_v1/cancer_type_summary.tsv`.",
            "4. Inspect `data/processed/target_ranker_real_evidence_v1/target_ranking.tsv`.",
            "5. Inspect spatial outputs in `data/processed/spatial_emt_niche_gnn_comparison/`.",
            "6. Use this report to explain the biological logic before going into code.",
            "",
            "## 11. Glossary",
            "",
            "| Term | Meaning |",
            "| --- | --- |",
            "| EMT | A plasticity program where epithelial cancer cells gain mesenchymal-like traits. |",
            "| Partial EMT | A mixed state with both epithelial and mesenchymal features. |",
            "| CAF | Cancer-associated fibroblast, a stromal cell type that can mimic or support EMT programs. |",
            "| TAM | Tumor-associated macrophage. |",
            "| Deconvolution | Estimating which cell types contribute to a bulk or spatial transcriptomic signal. |",
            "| Graph neural network | A model that learns from nodes and their relationships, useful for spatial neighborhoods. |",
            "| Weak label | A useful but imperfect label derived from rules or proxy scores rather than direct expert annotation. |",
        ]
    )
    STUDENT_REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def make_interview_guide(paths: dict[str, str]) -> None:
    targets = read(TARGET_RANKING).sort_values("priority_score", ascending=False).head(5)
    lines = [
        "# Project Interview Guide: Concepts, Methods, Tools, Findings",
        "",
        "## 1. One-Minute Project Pitch",
        "",
        "I built a public-data AI pipeline for studying EMT, metastasis, and therapeutic target susceptibility. The project has three connected parts: an EMT-state atlas across TCGA, a metastasis target ranker integrating druggability and dependency evidence, and a spatial EMT niche graph pipeline that models tumor-stroma-immune neighborhoods in spatial transcriptomics. The key idea is to distinguish true malignant EMT from stromal contamination and then use that context to propose testable target hypotheses.",
        "",
        "## 2. High-Level Diagram",
        "",
        f"![Project architecture]({paths['architecture']})",
        "",
        "## 3. Concept Questions",
        "",
        "### What is EMT and why is it important in cancer?",
        "EMT is a biological plasticity program where epithelial cells gain mesenchymal-like traits such as motility, invasion, stress tolerance, and therapy resistance. In cancer, EMT-like states are linked to metastasis and treatment escape, but EMT is not always a simple binary switch.",
        "",
        "### Why did you focus on partial EMT?",
        "Many tumors show hybrid states rather than fully epithelial or fully mesenchymal states. Partial EMT can preserve proliferation and cell-cell adhesion while gaining invasive capacity, so it may be especially relevant for metastatic niches.",
        "",
        "### Why is stromal correction important?",
        "Spatial and bulk samples can contain CAFs, fibroblasts, immune cells, and tumor cells together. Mesenchymal genes may come from stromal cells rather than cancer cells. Without stromal correction, a model might incorrectly call CAF-rich tissue malignant EMT.",
        "",
        "## 4. Methodology Questions",
        "",
        "### What are the main pipelines?",
        "1. EMT-state-atlas scores TCGA/Xena samples for EMT, partial EMT, stromal risk, immune context, hypoxia, and related signatures.",
        "2. Metastasis-target-ranker combines evidence such as EMT specificity, metastasis association, dependency, druggability, compound availability, safety risk, and literature support.",
        "3. Spatial-EMT-niche-GNN scores Visium/GEO cohorts, builds spatial graphs, trains interpretable graph-aware baselines, and prepares deconvolution/pathologist review.",
        "",
        "### How did you build spatial graphs?",
        "Nodes are spatial spots or inferred compartments. Edges include k-nearest spatial neighbors, physical radius neighbors, ligand-receptor edges, hypoxia gradients, ECM gradients, and histology-similarity edges when H&E features are available.",
        "",
        "### What is the model trying to predict?",
        "The first model predicts weak EMT-niche labels derived from EMT, partial EMT, CAF/TAM, hypoxia, ECM, and stromal-risk scores. This is intentionally hypothesis-generating; final validation needs expert pathology and stronger labels.",
        "",
        "### How did you handle deconvolution?",
        "The project includes marker-proxy deconvolution, NNLS reference deconvolution, and prepared inputs for Tangram, cell2location, and RCTD/spacexr. A real GSE154778 PDAC scRNA-derived reference is already built.",
        "",
        "## 5. Technical Questions",
        "",
        "### Which languages and tools are used?",
        "Python, pandas, numpy, scipy, matplotlib, h5py/AnnData, scanpy, PyTorch CPU, Tangram, cell2location, R 4.6 with spacexr/RCTD, HuggingFace Hub, Synapse, Gen3, and HTAN CLI.",
        "",
        "### Why use simple interpretable baselines before deep learning?",
        "Because biology and data quality are the hard part. Interpretable scoring and graph baselines reveal whether labels are plausible before using complex GNNs that might hide confounding.",
        "",
        "### What makes the project reproducible?",
        "Large public datasets stay local under `data/raw/`; GitHub stores scripts, manifests, documentation, small outputs, test data, and reports. Every blocker now has a status manifest or script.",
        "",
        "## 6. Findings You Can Mention",
        "",
        "- TCGA cancer types with high mean EMT signals include sarcoma, GBM, melanoma, and others in the current Xena summary.",
        "- Spatial cohorts repeatedly show that EMT-niche labels require stromal interpretation.",
        "- GSE274557 metastatic PDAC was scaled to all 55 non-PDX samples, with patient-batched graph summaries across 13 patients.",
        "- Peritoneal metastatic PDAC shows higher EMT-niche fraction than liver metastasis in the current scoring summary.",
        "- The top target hypotheses include:",
        "",
        "| Target | Family | Why it is interesting |",
        "| --- | --- | --- |",
    ]
    for _, row in targets.iterrows():
        lines.append(f"| {row['target']} | {row['family']} | Multi-evidence priority score {float(row['priority_score']):.3f}. |")
    lines.extend(
        [
            "",
            "## 7. Advantages Of The Approach",
            "",
            "- Uses public data, so others can reproduce or challenge it.",
            "- Separates EMT from stromal contamination instead of ignoring confounding.",
            "- Combines bulk, single-cell reference, spatial transcriptomics, target evidence, and pathology review planning.",
            "- Produces interpretable evidence cards and review queues rather than only black-box predictions.",
            "",
            "## 8. Limitations To State Honestly",
            "",
            "- Current labels are weak labels, not final pathologist-validated labels.",
            "- Visium spots are mixtures of multiple cells.",
            "- Some resources are gated by licenses or credentials.",
            "- Target rankings are research hypotheses, not clinical recommendations.",
            "- Full cell2location/Tangram/RCTD publication runs need careful cell-level scRNA references and compute.",
            "",
            "## 9. Likely Interview Questions And Answers",
            "",
            "### Q: What is the novelty?",
            "A: The novelty is the integrated, contamination-aware workflow: EMT-state scoring, metastasis target ranking, spatial niche graph modeling, deconvolution, and pathology review are connected into one reproducible public-data framework.",
            "",
            "### Q: Why graph modeling?",
            "A: Metastasis and EMT are niche-dependent. A spot's biology depends not only on its own expression but also on neighboring CAFs, TAMs, hypoxia, ECM, and ligand-receptor interactions.",
            "",
            "### Q: Why not directly claim a biomarker?",
            "A: Because the current labels are weak and public datasets vary in quality. The scientifically responsible output is a ranked set of hypotheses and validation-ready workflows.",
            "",
            "### Q: How would you validate experimentally?",
            "A: First use pathologist review and deconvolution; then validate targets in EMT-high and EMT-low cell models using CRISPR or drug perturbation; finally test spatial localization with multiplex imaging or spatial transcriptomics.",
            "",
            "### Q: What would you improve next?",
            "A: Add expert pathology labels, run full cell-level deconvolution, add HTAN validation, run foundation pathology embeddings, and build stronger leave-cohort-out GNN validation.",
            "",
            "## 10. Visuals To Explain During Interview",
            "",
            f"![Completion]({paths['completion']})",
            "",
            f"![Spatial scale]({paths['cohorts']})",
            "",
            f"![Target ranking]({paths['targets']})",
            "",
            f"![EMT cartoon]({paths['cartoon']})",
        ]
    )
    INTERVIEW_GUIDE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    paths = {
        "architecture": project_architecture_chart(),
        "completion": completion_chart(),
        "cohorts": cohort_scale_chart(),
        "targets": target_ranker_chart(),
        "tcga": tcga_emt_chart(),
        "cartoon": emt_cartoon(),
    }
    make_student_report(paths)
    make_interview_guide(paths)
    print(f"Wrote {STUDENT_REPORT}")
    print(f"Wrote {INTERVIEW_GUIDE}")
    print(f"Wrote assets to {ASSET_DIR}")


if __name__ == "__main__":
    main()
