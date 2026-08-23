from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "deliverables" / "crc_liver_invasion_front_presentation_pack"
DOCX_PATH = OUT / "CRC_Liver_Invasion_Front_Complete_Project_Reference.docx"
PDF_PATH = OUT / "CRC_Liver_Invasion_Front_Interview_QA.pdf"
FIGURES = ROOT / "data" / "processed" / "crc_liver_invasion_front_v1" / "figures"

INK = RGBColor(23, 33, 43)
GREEN = RGBColor(62, 118, 80)
BLUE = RGBColor(43, 111, 151)
MUTED = RGBColor(95, 107, 115)
LIGHT = "F2F4F5"
GREEN_LIGHT = "E8F1EB"
RUST_LIGHT = "F7EBE6"


def set_repeat_table_header(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)


def prevent_row_split(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    tr_pr.append(OxmlElement("w:cantSplit"))


def set_cell_fill(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_cell_width(cell, width_dxa: int) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_w = tc_pr.find(qn("w:tcW"))
    if tc_w is None:
        tc_w = OxmlElement("w:tcW")
        tc_pr.append(tc_w)
    tc_w.set(qn("w:w"), str(width_dxa))
    tc_w.set(qn("w:type"), "dxa")


def set_table_geometry(table, widths: list[int]) -> None:
    table.autofit = False
    tbl_pr = table._tbl.tblPr
    tbl_w = tbl_pr.find(qn("w:tblW"))
    if tbl_w is None:
        tbl_w = OxmlElement("w:tblW")
        tbl_pr.append(tbl_w)
    tbl_w.set(qn("w:w"), str(sum(widths)))
    tbl_w.set(qn("w:type"), "dxa")
    tbl_ind = OxmlElement("w:tblInd")
    tbl_ind.set(qn("w:w"), "120")
    tbl_ind.set(qn("w:type"), "dxa")
    tbl_pr.append(tbl_ind)
    grid = table._tbl.tblGrid
    for child in list(grid):
        grid.remove(child)
    for width in widths:
        col = OxmlElement("w:gridCol")
        col.set(qn("w:w"), str(width))
        grid.append(col)
    for row in table.rows:
        for cell, width in zip(row.cells, widths):
            set_cell_width(cell, width)


def add_bullet(doc: Document, text: str) -> None:
    p = doc.add_paragraph(style="List Bullet")
    p.add_run(text)


def new_numbering_id(doc: Document) -> int:
    numbering = doc.part.numbering_part.element
    style_num_id = int(doc.styles["List Number"]._element.pPr.numPr.numId.val)
    source_num = next(n for n in numbering.findall(qn("w:num")) if int(n.get(qn("w:numId"))) == style_num_id)
    abstract_id = source_num.find(qn("w:abstractNumId")).get(qn("w:val"))
    existing = [int(n.get(qn("w:numId"))) for n in numbering.findall(qn("w:num"))]
    new_id = max(existing, default=0) + 1
    num = OxmlElement("w:num")
    num.set(qn("w:numId"), str(new_id))
    abstract = OxmlElement("w:abstractNumId")
    abstract.set(qn("w:val"), abstract_id)
    num.append(abstract)
    override = OxmlElement("w:lvlOverride")
    override.set(qn("w:ilvl"), "0")
    start = OxmlElement("w:startOverride")
    start.set(qn("w:val"), "1")
    override.append(start)
    num.append(override)
    numbering.append(num)
    return new_id


def add_number(doc: Document, text: str, num_id: int) -> None:
    p = doc.add_paragraph(style="List Number")
    num_pr = p._p.get_or_add_pPr().get_or_add_numPr()
    num_pr.get_or_add_ilvl().val = 0
    num_pr.get_or_add_numId().val = num_id
    p.add_run(text)


def add_callout(doc: Document, heading: str, body: str, fill: str = GREEN_LIGHT) -> None:
    table = doc.add_table(rows=1, cols=1)
    prevent_row_split(table.rows[0])
    set_table_geometry(table, [9360])
    cell = table.cell(0, 0)
    set_cell_fill(cell, fill)
    p = cell.paragraphs[0]
    r = p.add_run(heading + ". ")
    r.bold = True
    r.font.color.rgb = GREEN if fill == GREEN_LIGHT else INK
    p.add_run(body)
    doc.add_paragraph().paragraph_format.space_after = Pt(0)


def add_table(doc: Document, headers: list[str], rows: list[list[str]], widths: list[int]) -> None:
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    for i, header in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = header
        set_cell_fill(cell, LIGHT)
        for run in cell.paragraphs[0].runs:
            run.bold = True
            run.font.color.rgb = INK
    set_repeat_table_header(table.rows[0])
    for row in rows:
        cells = table.add_row().cells
        for i, value in enumerate(row):
            cells[i].text = str(value)
    set_table_geometry(table, widths)
    doc.add_paragraph().paragraph_format.space_after = Pt(0)


def style_doc(doc: Document) -> None:
    section = doc.sections[0]
    section.page_width = Inches(8.5)
    section.page_height = Inches(11)
    section.top_margin = Inches(0.82)
    section.bottom_margin = Inches(0.78)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)
    styles = doc.styles
    normal = styles["Normal"]
    normal.font.name = "Arial"
    normal.font.size = Pt(10.5)
    normal.font.color.rgb = INK
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.18
    for name, size, color, before, after in [
        ("Title", 28, INK, 0, 10),
        ("Subtitle", 13, MUTED, 0, 18),
        ("Heading 1", 17, GREEN, 16, 8),
        ("Heading 2", 13, BLUE, 12, 6),
        ("Heading 3", 11.5, INK, 9, 4),
    ]:
        style = styles[name]
        style.font.name = "Arial"
        style.font.size = Pt(size)
        style.font.color.rgb = color
        style.font.bold = name != "Subtitle"
        style.paragraph_format.space_before = Pt(before)
        style.paragraph_format.space_after = Pt(after)
    for name in ["List Bullet", "List Number"]:
        styles[name].font.name = "Arial"
        styles[name].font.size = Pt(10.5)
        styles[name].paragraph_format.space_after = Pt(4)
        styles[name].paragraph_format.line_spacing = 1.18
    header = section.header.paragraphs[0]
    header.text = "CRC Liver-Metastasis Invasion-Front Model | Research Reference"
    header.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    for run in header.runs:
        run.font.name = "Arial"
        run.font.size = Pt(8)
        run.font.color.rgb = MUTED
    footer = section.footer.paragraphs[0]
    footer.text = "Research use only | Generated from the executed public-data pipeline"
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in footer.runs:
        run.font.name = "Arial"
        run.font.size = Pt(8)
        run.font.color.rgb = MUTED


def build_docx() -> None:
    doc = Document()
    style_doc(doc)
    p = doc.add_paragraph(style="Title")
    p.add_run("CRC Liver-Metastasis\nInvasion-Front Model")
    doc.add_paragraph("Complete project reference for research students, presentations and interviews", style="Subtitle")
    p = doc.add_paragraph()
    p.add_run("Executed release: ").bold = True
    p.add_run("GSE225857 public spatial transcriptomics and matched single-cell reference")
    p = doc.add_paragraph()
    p.add_run("Scope: ").bold = True
    p.add_run("Hypothesis generation only. Not a diagnostic, prognostic or treatment-selection system.")
    add_callout(doc, "One-sentence thesis", "The tumour-liver interface can be represented as a signed, compartment-aware heterogeneous graph that separates host-contact biology from malignant partial-EMT and metabolic programs.")
    if (FIGURES / "workflow_overview.png").exists():
        doc.add_picture(str(FIGURES / "workflow_overview.png"), width=Inches(6.3))
        cap = doc.add_paragraph("Figure 1. Executed workflow from public data to an auditable interface model.")
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cap.runs[0].italic = True
        cap.runs[0].font.size = Pt(9)

    doc.add_page_break()
    doc.add_heading("1. Executive Summary", level=1)
    doc.add_paragraph(
        "Colorectal cancer liver metastases grow through biologically distinct tumour-host interfaces. Whole-slide or untyped spot analysis can blur malignant epithelial plasticity with fibroblast, macrophage and liver-derived RNA. This project builds a reproducible spatial workflow that identifies candidate tumour-liver boundaries, scores biologically defined compartments, constructs typed graph relations, and tests whether relation-aware features transfer between two public liver-metastasis sections."
    )
    add_table(doc, ["Executed asset", "Scale", "Role"], [
        ["GSE225857 Visium", "6 sections; 22,260 spots", "Discovery, interface construction and cross-section validation"],
        ["GSE225857 scRNA-seq", "56,072 cells in four recovered reference groups", "Study-matched pseudobulk reference and cell-state audit"],
        ["Zenodo 7520789 GeoMx", "48 AOIs from four patients", "Orthogonal evidence asset; AOI site labels unresolved"],
    ], [2200, 2100, 5060])
    add_callout(doc, "Executed result", "The leakage-controlled typed message-passing baseline achieved ROC AUC 0.908, average precision 0.857, balanced accuracy 0.831 and within-section permutation P=0.0196. These values show transfer between two sections, not clinical generalization.")

    doc.add_heading("2. Hypothesis and Research Questions", level=1)
    doc.add_heading("Central hypothesis", level=2)
    doc.add_paragraph("Partial-EMT CRC cells occupy spatially distinct hepatocyte-contact or fibroblast-rich interface ecosystems, with separable macrophage, endothelial, ECM, glycolytic and hypoxic gradients.")
    doc.add_heading("Primary questions", level=2)
    for q in [
        "Can malignant partial EMT be separated from fibroblast-driven stromal mesenchymal signal in mixed Visium spots?",
        "Which programs rise or fall across a signed tumour-core, tumour-front, boundary and liver-front coordinate?",
        "Do physical, contact, ligand-receptor and gradient edges provide transferable information between liver sections?",
        "Are inferred interfaces compatible with desmoplastic, replacement or mixed histological growth-pattern hypotheses?",
        "Which cell-interaction axes deserve pathologist review, protein validation and perturbation?",
    ]:
        add_bullet(doc, q)
    doc.add_heading("Falsifiable expectations", level=2)
    add_bullet(doc, "A uniform invasive-ring hypothesis predicts higher pEMT, glycolysis and hypoxia at the tumour front.")
    add_bullet(doc, "A host-contact hypothesis predicts hepatocyte injury and macrophage/contact signals at the boundary.")
    add_bullet(doc, "A desmoplastic-like hypothesis predicts a fibroblast/ECM barrier; a replacement-like hypothesis predicts direct tumour-hepatocyte contact and vessel co-option.")

    doc.add_heading("3. Why the Methodology Matters", level=1)
    add_table(doc, ["Design choice", "Why it matters", "Failure prevented"], [
        ["CRC-lineage-gated pEMT", "Requires epithelial, mesenchymal and malignant-lineage evidence", "Calling fibroblast-rich spots malignant EMT"],
        ["Signed graph distance", "Preserves direction from malignant core into adjacent liver", "Whole-slide averaging that erases the interface"],
        ["Heterogeneous graph", "Keeps physical, contact, LR and gradient relations distinct", "Treating all neighbours as biologically equivalent"],
        ["Leave-section-out validation", "Holds out complete tissue sections", "Spot leakage between train and test sets"],
        ["Section-aware permutation", "Compares performance with a label-shuffled null", "Mistaking spatial autocorrelation for robust signal"],
        ["Ablation", "Removes feature groups to test reliance", "Opaque importance claims"],
    ], [2050, 3760, 3550])

    doc.add_heading("4. Data and Literature Grounding", level=1)
    doc.add_heading("Public databases", level=2)
    for item in [
        "NCBI GEO GSE225857: four primary CRC and two liver-metastasis 10x Visium FFPE sections plus processed single-cell tables.",
        "Zenodo 7520789 / GEO GSE224235: open GeoMx CTA count table containing 48 AOIs from matched primary and liver-metastatic tissue.",
        "PRJEB71493: three human CRLM Visium experiments retained as a future processed-matrix validation target because raw reads are approximately 63 GB.",
    ]:
        add_bullet(doc, item)
    doc.add_heading("Key literature", level=2)
    add_table(doc, ["Source", "Contribution to design"], [
        ["Science Advances, DOI 10.1126/sciadv.adf5464", "Public multi-omic CRC/CRLM discovery cohort and matched cell-state context"],
        ["International HGP consensus, PMCID PMC5680474", "Definitions of desmoplastic, replacement and pushing tumour-liver growth patterns"],
        ["Diagnostic reproducibility, PMCID PMC6611753", "Need for standardized pathologist scoring and interobserver review"],
        ["Immune and vascular HGP context, PMCID PMC7217855", "Biological interpretation of stromal, immune and vessel-co-option niches"],
        ["British Journal of Cancer 2026, s41416-026-03567-y", "Pathologist-reviewed 300 micrometre fronts and damaged-hepatocyte markers"],
    ], [3400, 5960])

    doc.add_heading("5. End-to-End Methodology", level=1)
    steps = [
        ("Ingest and harmonize", "Load processed Visium counts, coordinates, images and section metadata; retain raw files locally and version small manifests."),
        ("Quality control and normalization", "Filter to under-tissue spots, library-size normalize to 10,000, log transform, and score programs as within-section percentile ranks."),
        ("Score cell states and niches", "Score malignant CRC, epithelial, mesenchymal, pEMT, hepatocyte, damaged hepatocyte, MRC1/CCL18-like macrophage, activated fibroblast, endothelial, ECM, glycolysis and hypoxia programs."),
        ("Control stromal inflation", "Require CRC-lineage support for malignant pEMT; flag mesenchymal-high, malignant-low, fibroblast-high spots."),
        ("Infer the interface", "Build six-neighbour spatial graphs; use high-confidence malignant-hepatocyte contacts as boundary seeds; assign signed three-hop distance bands."),
        ("Construct typed relations", "Create spatial, compartment-contact, tumour-liver contact, ECM/glycolysis gradient and positive high-expression ligand-receptor edges."),
        ("Create relation-aware features", "Aggregate neighbouring programs separately by edge family; exclude boundary-defining cross-interface messages from predictive features."),
        ("Validate", "Fit a standardized class-balanced L2 logistic baseline; leave out each liver section; run 50 within-section permutations and biological feature-group ablations."),
        ("Interpret and queue review", "Generate spatial maps, gradient plots, coefficients, edge summaries and a pathologist scoring template."),
    ]
    methods_num_id = new_numbering_id(doc)
    for heading, body in steps:
        p = doc.add_paragraph(style="List Number")
        num_pr = p._p.get_or_add_pPr().get_or_add_numPr()
        num_pr.get_or_add_ilvl().val = 0
        num_pr.get_or_add_numId().val = methods_num_id
        r = p.add_run(heading + ": ")
        r.bold = True
        p.add_run(body)

    doc.add_heading("6. Technical Implementation", level=1)
    add_table(doc, ["Layer", "Tools", "Advantage"], [
        ["Data engineering", "Python, pandas, NumPy, SciPy", "Transparent matrix handling and reproducible tabular outputs"],
        ["Spatial graph", "Array-coordinate kNN/contact logic", "Efficient graph construction without requiring a heavy graph runtime"],
        ["Statistics", "Mann-Whitney, rank-biserial effect, Benjamini-Hochberg FDR", "Reports direction, magnitude and multiplicity-adjusted evidence"],
        ["Model", "scikit-learn logistic regression", "Interpretable relation-aware baseline appropriate for two sections"],
        ["Visualization", "Matplotlib and Streamlit", "Publication-style figures plus an explorable research workbench"],
        ["Testing", "pytest smoke and unit tests", "Protects scoring, graph-merging and ranking behavior"],
    ], [1900, 2900, 4560])
    add_callout(doc, "Why not a deep GNN in v1", "With only two liver-metastasis sections, a deep relational model would add capacity without enough independent biological units. The current model performs typed message passing but keeps the final classifier interpretable and auditable.", RUST_LIGHT)

    doc.add_heading("7. Executed Results", level=1)
    add_table(doc, ["Metric", "Value", "Correct interpretation"], [
        ["Liver sections", "2", "Independent tissue sections used in leave-section-out validation"],
        ["Malignant spots", "3,439", "Spot-level observations, not patients"],
        ["Tumour-front spots", "1,290", "Weak labels within the malignant compartment"],
        ["ROC AUC", "0.908", "Transfer of inferred labels between two sections"],
        ["Average precision", "0.857", "Positive-class ranking under class imbalance"],
        ["Balanced accuracy", "0.831", "Mean sensitivity across both classes"],
        ["Permutation P", "0.0196", "Observed AUC exceeded 50 section-wise shuffled-label runs"],
    ], [2300, 1500, 5560])
    doc.add_heading("Spatial findings", level=2)
    add_bullet(doc, "Damaged-hepatocyte score was higher at the inferred tumour front than malignant core: delta +0.0604, rank-biserial effect +0.133.")
    add_bullet(doc, "ECM remodelling was lower at the inferred front: delta -0.117, effect -0.229.")
    add_bullet(doc, "Partial EMT, glycolysis, hypoxia and activated-fibroblast programs were also more prominent in malignant core regions.")
    add_bullet(doc, "Both liver sections were assigned mixed or uncertain HGP proxies; the workflow did not force a desmoplastic or replacement label.")
    doc.add_heading("Predictive feature directions", level=2)
    add_table(doc, ["Feature", "Coefficient", "Direction"], [
        ["Spatial-neighbour damaged hepatocyte", "+0.809", "Tumour front"],
        ["Spatial-neighbour MRC1/CCL18-like macrophage", "+0.457", "Tumour front"],
        ["Contact-neighbour ECM", "+0.446", "Tumour front"],
        ["Spatial-neighbour hypoxia", "-0.832", "Tumour core"],
        ["Spatial-neighbour ECM", "-0.794", "Tumour core"],
        ["Spatial-neighbour partial EMT", "-0.745", "Tumour core"],
        ["Spatial-neighbour glycolysis", "-0.641", "Tumour core"],
    ], [5200, 1500, 2660])
    add_callout(doc, "Interpretation", "The first public-data run supports a host-contact front surrounding a more pEMT, hypoxic, glycolytic and ECM-rich malignant core. This is a testable architecture, not a proven mechanism.")

    doc.add_heading("8. Novelty and Project Highlights", level=1)
    for item in [
        "Interface-first analysis rather than whole-slide averaging.",
        "Explicit separation of malignant pEMT and stromal-inflated EMT.",
        "Heterogeneous node states for malignant, hepatocyte, macrophage, fibroblast, endothelial and other compartments.",
        "Directional ECM and glycolysis gradient edges plus named ligand-receptor edge families.",
        "Leakage-aware leave-section-out validation, within-section permutation and feature-group ablation.",
        "Honest representation of missing hepatocyte references and unresolved GeoMx labels.",
        "A user-facing workbench that exposes both supported and unsupported claims.",
    ]:
        add_bullet(doc, item)

    doc.add_heading("9. Pros, Cons and Risk Controls", level=1)
    add_table(doc, ["Dimension", "Advantage", "Risk / control"], [
        ["Biology", "Cell-state and niche programs are interpretable", "Signature dependence; validate with multiplex protein and pathology"],
        ["Spatial design", "Signed distance focuses on the operative boundary", "Boundary is weak-label; require H&E tracing"],
        ["Model", "Low-capacity and auditable", "May miss nonlinear effects; upgrade only after more cohorts"],
        ["Data", "Open and reproducible", "Two liver sections; add independent CRLM cohorts"],
        ["Interactions", "Typed LR hypotheses are experimentally actionable", "Co-expression is not signalling; require perturbation"],
        ["Clinical translation", "Produces candidate biomarkers and regions", "No outcome endpoint; prohibit clinical interpretation"],
    ], [1550, 3650, 4160])

    doc.add_heading("10. Supported and Unsupported Claims", level=1)
    doc.add_heading("Supported", level=2)
    for item in [
        "Public sections contain coherent malignant, hepatocyte and niche programs that permit an auditable candidate interface.",
        "A relation-aware linear baseline transfers inferred front/core labels between the two public liver sections.",
        "The result prioritizes measurable hepatocyte-injury, macrophage, fibroblast, endothelial, ECM, pEMT, hypoxia and glycolysis hypotheses.",
    ]:
        add_bullet(doc, item)
    doc.add_heading("Not supported", level=2)
    for item in [
        "Patient survival, recurrence or treatment-response prediction.",
        "Pathologist-confirmed histological growth patterns.",
        "Causal ligand-receptor signalling or validated therapeutic targets.",
        "Population-level generalization from two liver sections.",
        "Any diagnosis or treatment recommendation.",
    ]:
        add_bullet(doc, item)

    doc.add_heading("11. Experimental and Publication Roadmap", level=1)
    roadmap_num_id = new_numbering_id(doc)
    add_number(doc, "Have two pathologists trace tumour-liver boundaries and score desmoplastic, replacement and pushing percentages using consensus criteria.", roadmap_num_id)
    add_number(doc, "Validate signed bands with multiplex IF/IHC for EPCAM or KRT20, VIM/LAMC2, MRC1/CCL18, FAP/POSTN, CD31 and CA9/GLUT1.", roadmap_num_id)
    add_number(doc, "Benchmark marker proxies against cell2location, RCTD or Tangram using a liver-inclusive scRNA reference.", roadmap_num_id)
    add_number(doc, "Perturb CCL18-PITPNM3, SPP1-CD44/ITGAV, TGF-beta-TGFBR2 and CXCL12-CXCR4 in CRLM organoid-liver or precision-cut liver models.", roadmap_num_id)
    add_number(doc, "Validate patient-level effect directions in PRJEB71493 or the 26-sample ISS CRLM cohort.", roadmap_num_id)
    add_number(doc, "Only after external validation, compare the interpretable baseline with a relational GNN and histology foundation embeddings.", roadmap_num_id)

    doc.add_page_break()
    doc.add_heading("12. Project Pitch", level=1)
    add_callout(doc, "Thirty-second pitch", "I built a compartment-aware spatial graph model of the colorectal cancer-liver metastasis interface. It separates malignant partial EMT from stromal mesenchymal signal, assigns a signed 300 micrometre boundary, and preserves hepatocyte, macrophage, fibroblast, endothelial, ECM, metabolic and ligand-receptor context as typed relations. The held-out-section baseline reached ROC AUC 0.908 with permutation P=0.0196, but I present it as a weak-label research result because the independent unit count is two sections and HGP labels need pathologist review.")
    doc.add_heading("Why this project is interview-worthy", level=2)
    add_bullet(doc, "It demonstrates biological problem formulation, public-data engineering, spatial statistics, graph design, validation and scientific communication.")
    add_bullet(doc, "It contains a valuable negative result and explains why that result changed the next experiment.")
    add_bullet(doc, "It shows restraint: a simple model was chosen because the biological sample size did not justify a deep GNN.")
    add_bullet(doc, "It links technical controls directly to scientific failure modes such as stromal contamination and spatial leakage.")

    doc.add_heading("13. Interview Reference", level=1)
    add_table(doc, ["Question cue", "Answer anchor"], [
        ["Why a heterogeneous graph?", "Different edge families encode different biological mechanisms and can be ablated separately."],
        ["How did you handle stromal contamination?", "CRC-lineage-gated pEMT plus explicit stromal-inflation flags."],
        ["Why not a deep GNN?", "Only two independent liver sections; interpretability and variance control were higher priorities."],
        ["What surprised you?", "pEMT, hypoxia and glycolysis were core-associated rather than uniformly front-enriched."],
        ["What does AUC 0.908 prove?", "Technical transfer of weak labels between sections, not clinical validity."],
        ["What would you do next?", "Pathology, multiplex protein, liver-inclusive deconvolution, perturbation and independent cohorts."],
    ], [3000, 6360])

    doc.add_heading("14. Reproducibility and Outputs", level=1)
    doc.add_paragraph("Run: python scripts/run_crc_liver_invasion_front.py")
    for item in [
        "Core package: src/crc_liver_invasion_front/",
        "Research workbench: apps/crc_liver_invasion_front_app.py",
        "Processed outputs: data/processed/crc_liver_invasion_front_v1/",
        "Documentation: docs/crc_liver_invasion_front/",
        "Tests: tests/test_crc_liver_invasion_front.py",
    ]:
        add_bullet(doc, item)
    doc.add_paragraph("Large public files remain under data/raw/ and are excluded from Git. Derived tables, figures, metrics and reports are reproducible from the documented workflow.")

    doc.add_heading("15. References", level=1)
    refs = [
        "NCBI GEO. GSE225857. https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE225857",
        "Science Advances. DOI 10.1126/sciadv.adf5464. https://doi.org/10.1126/sciadv.adf5464",
        "International consensus guidelines for CRLM histopathological growth patterns. PMCID PMC5680474. https://pmc.ncbi.nlm.nih.gov/articles/PMC5680474/",
        "Diagnostic reproducibility of CRLM growth patterns. PMCID PMC6611753. https://pmc.ncbi.nlm.nih.gov/articles/PMC6611753/",
        "Immune and vascular context of CRLM growth patterns. PMCID PMC7217855. https://pmc.ncbi.nlm.nih.gov/articles/PMC7217855/",
        "British Journal of Cancer 2026 spatial CRLM study. https://www.nature.com/articles/s41416-026-03567-y",
        "Zenodo 7520789. https://doi.org/10.5281/zenodo.7520789",
        "NCBI GEO. GSE224235. https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE224235",
        "NCBI BioProject. PRJEB71493. https://www.ncbi.nlm.nih.gov/bioproject/PRJEB71493/",
    ]
    references_num_id = new_numbering_id(doc)
    for ref in refs:
        add_number(doc, ref, references_num_id)
    OUT.mkdir(parents=True, exist_ok=True)
    doc.save(DOCX_PATH)


def page_number(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(HexColor("#5F6B73"))
    canvas.drawString(0.72 * inch, 0.46 * inch, "CRC Liver Invasion Front | Interview and Viva Guide")
    canvas.drawRightString(7.78 * inch, 0.46 * inch, f"Page {doc.page}")
    canvas.restoreState()


def build_pdf() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    title = ParagraphStyle("TitleX", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=25, leading=29, textColor=HexColor("#17212B"), spaceAfter=12, alignment=TA_LEFT)
    subtitle = ParagraphStyle("SubtitleX", parent=styles["Normal"], fontName="Helvetica", fontSize=12, leading=17, textColor=HexColor("#5F6B73"), spaceAfter=18)
    h1 = ParagraphStyle("H1X", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=17, leading=21, textColor=HexColor("#3E7650"), spaceBefore=8, spaceAfter=8)
    qstyle = ParagraphStyle("QX", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=12.5, leading=16, textColor=HexColor("#17212B"), spaceBefore=10, spaceAfter=4)
    body = ParagraphStyle("BodyX", parent=styles["BodyText"], fontName="Helvetica", fontSize=10, leading=14, textColor=HexColor("#17212B"), spaceAfter=7)
    answer = ParagraphStyle("AnswerX", parent=body, leftIndent=12, borderColor=HexColor("#CBD2D8"), borderWidth=0.8, borderPadding=7, backColor=HexColor("#F2F4F5"), spaceAfter=10)
    small = ParagraphStyle("SmallX", parent=body, fontSize=8.5, leading=11, textColor=HexColor("#5F6B73"))

    questions = [
        ("What problem does the project solve?", "It models the tumour-liver interface directly. Standard spot-level or whole-slide analysis can merge malignant epithelial plasticity with fibroblast, macrophage and hepatocyte RNA. The workflow preserves compartments and spatial direction so candidate invasion mechanisms can be compared."),
        ("What is the central hypothesis?", "Partial-EMT CRC cells occupy distinct hepatocyte-contact or fibroblast-rich ecosystems, with separable macrophage, endothelial, ECM, glycolytic and hypoxic gradients. Typed spatial context should transfer between liver sections better than unstructured spot features."),
        ("Why focus on the invasion front?", "Histopathological growth patterns are defined at the tumour-liver boundary. Desmoplastic growth has a fibrotic rim; replacement growth brings cancer cells into contact with liver plates and may use vessel co-option. Whole-slide averages can erase this biology."),
        ("Which public data were used?", "GSE225857 supplied four primary CRC and two liver-metastasis Visium FFPE sections, totaling 22,260 spots, plus processed single-cell tables. Zenodo 7520789 supplied an open 48-AOI GeoMx count table used as an orthogonal evidence asset."),
        ("How was the single-cell reference built?", "Author-annotated processed cells were harmonized and aggregated into pseudobulk malignant CRC, activated fibroblast, macrophage/myeloid and endothelial profiles. The recovered groups contained 56,072 cells. Hepatocytes were absent and were reported as unavailable rather than fabricated."),
        ("How were EMT and partial EMT scored?", "Counts were normalized within section. Curated epithelial, mesenchymal and CRC-lineage programs were converted to within-section percentile scores. Partial EMT requires concurrent epithelial, mesenchymal and malignant-lineage support."),
        ("How did you prevent stromal contamination from becoming malignant EMT?", "Mesenchymal-high, malignant-low and fibroblast-high spots receive a stromal-inflation warning. Only CRC-lineage-supported spots can enter the malignant partial-EMT compartment or the front/core model."),
        ("How was the tumour-liver interface defined?", "A six-neighbour spatial graph was built from Visium array coordinates. High-confidence malignant-hepatocyte contacts seeded the boundary. Breadth-first graph distance then assigned tumour-front and liver-front spots for three hops, approximately 300 micrometres."),
        ("Why approximately 300 micrometres?", "Three Visium centre-to-centre graph steps are roughly 300 micrometres and mirror the tumour- and liver-front width used in recent pathologist-reviewed CRLM spatial work. It remains an approximation that should be sensitivity-tested."),
        ("What makes the graph heterogeneous?", "Nodes carry cell-compartment labels. Edges distinguish physical proximity, compartment contact, direct tumour-hepatocyte contact, ligand-receptor co-expression, and directional ECM or glycolysis gradients. Different relations are aggregated separately."),
        ("Which ligand-receptor axes are represented?", "The hypothesis set includes CCL18-PITPNM3, SPP1-CD44/ITGAV, TGF-beta-TGFBR2, CXCL12-CXCR4, HGF-MET, VEGFA-KDR, ANGPT2-TEK, COL1A1-ITGA2 and GAS6-AXL. These edges indicate co-expression opportunities, not functional signalling."),
        ("Is the method a GNN?", "V1 performs typed message passing but uses standardized logistic regression as the final classifier. This is a graph-informed baseline rather than a deep relational GNN. With only two independent liver sections, the simpler model is easier to audit and less prone to overfitting."),
        ("How was train-test leakage controlled?", "Whole liver sections, not random spots, were held out. Boundary-defining cross-interface messages were excluded from predictive features. Labels were permuted within section for the null comparison."),
        ("What was the model performance?", "Across leave-one-liver-section-out predictions, ROC AUC was 0.908, average precision 0.857 and balanced accuracy 0.831. The empirical P value from 50 within-section permutations was 0.0196; null mean AUC was 0.495."),
        ("Why does AUC 0.908 not prove clinical value?", "The endpoint is an inferred weak spatial label, only two sections are independent biological units, and thousands of spots are not thousands of patients. The metric demonstrates technical transfer between these sections, not prognosis, treatment response or population generalization."),
        ("What was the most important positive result?", "Damaged-hepatocyte context was higher at the inferred front, and neighbouring damaged-hepatocyte and MRC1/CCL18-like macrophage programs were among the strongest front-associated model features. This prioritizes a host-injury and myeloid-contact hypothesis."),
        ("What was the most important negative result?", "Partial EMT, glycolysis and hypoxia were not uniformly higher at the inferred tumour front. They were more prominent in malignant core regions. That rejects a simplistic invasive-ring story and changes the validation plan."),
        ("How do you interpret the front-versus-core architecture?", "The current data are consistent with a host-contact front surrounding a metabolically stressed, pEMT-rich core. Competing explanations include section-specific growth architecture, Visium spot mixing and imperfect weak labels. Pathology and protein validation are needed to distinguish them."),
        ("What do desmoplastic and replacement growth patterns mean here?", "Desmoplastic growth implies a fibroblast/ECM-rich rim separating tumour and liver. Replacement growth implies direct malignant-hepatocyte contact and possible vessel co-option. Both sections remained mixed or uncertain proxies because H&E was not scored by pathologists."),
        ("What are the project’s main methodological advantages?", "It is compartment-aware, spatially directional, relation-specific, low-capacity, leakage-controlled and reproducible. It reports missing evidence instead of silently imputing it and exposes unsupported claims in the UI."),
        ("What are the most serious limitations?", "Two liver-metastasis sections, weak boundary and HGP labels, spot-level cell mixing, incomplete liver-inclusive single-cell reference, co-expression rather than functional signalling, and no patient outcome endpoint."),
        ("What would you validate first?", "First obtain consensus pathologist boundary/HGP scores. Then perform multiplex IF or IHC across signed bands for malignant, pEMT, macrophage, fibroblast, endothelial, hypoxia/glycolysis and damaged-hepatocyte markers."),
        ("Which perturbations are most informative?", "Test macrophage-contact and stromal axes such as CCL18-PITPNM3, SPP1-CD44/ITGAV, TGF-beta-TGFBR2 and CXCL12-CXCR4 in CRC liver organoids, co-cultures or precision-cut liver models. Perturbations should be spatially read out, not only measured in bulk."),
        ("How would you upgrade the model?", "Add pathologist labels, a liver-inclusive scRNA reference, cell2location or RCTD benchmarking, more independent CRLM cohorts and patient-level endpoints. Only then compare the linear baseline with a relational GNN and H&E foundation embeddings."),
        ("How is the project reproducible?", "The repository contains a single pipeline command, modules for scoring/interface/graph/model/reporting, tests, manifests, small derived outputs, figures and a Streamlit workbench. Large public files remain local under data/raw and are excluded from Git."),
        ("What did you personally demonstrate through this project?", "The project shows end-to-end reasoning: translating pathology into computable labels, designing biological graph relations, controlling contamination and leakage, validating at the correct section level, interpreting a surprising negative result and communicating uncertainty."),
        ("Give the 30-second pitch.", "I built a compartment-aware spatial graph model of the CRC liver-metastasis interface. It separates malignant partial EMT from stromal signal, assigns a signed 300 micrometre boundary, and encodes host-cell, ECM, metabolic and ligand-receptor context as typed relations. The held-out-section baseline reached AUC 0.908, but I treat it as a weak-label hypothesis generator because only two liver sections and no pathologist HGP labels are available."),
    ]

    story = [
        Paragraph("CRC Liver-Metastasis Invasion-Front Model", title),
        Paragraph("Interview and Viva Questions with Model Answers", subtitle),
        Table([[Paragraph("QUICK FACTS", qstyle), Paragraph("22,260 Visium spots | 6 sections | 2 liver sections | ROC AUC 0.908 | permutation P 0.0196", body)]], colWidths=[1.35 * inch, 5.85 * inch], style=TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), HexColor("#E8F1EB")),
            ("BOX", (0, 0), (-1, -1), 0.6, HexColor("#CBD2D8")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ])),
        Spacer(1, 14),
        Paragraph("How to use this guide", h1),
        Paragraph("Answer in three layers: first state the design decision, then give the executed evidence, then name the limitation or next validation. The model answers below are intentionally concise enough for interviews but technically precise enough for a viva.", body),
        PageBreak(),
    ]
    sections = [
        (0, 5, "Concept and data"),
        (5, 13, "Methodology and technical design"),
        (13, 20, "Results and interpretation"),
        (20, 27, "Limitations, next steps and interview pitch"),
    ]
    for start, end, heading in sections:
        story.append(Paragraph(heading, h1))
        for idx in range(start, end):
            question, response = questions[idx]
            story.append(KeepTogether([
                Paragraph(f"Question {idx + 1}. {question}", qstyle),
                Paragraph(response, answer),
            ]))
        if end < len(questions):
            story.append(PageBreak())
    story.extend([
        PageBreak(),
        Paragraph("Rapid-fire numbers", h1),
        Table([
            ["Item", "Value"],
            ["Visium sections", "6: four primary CRC and two liver metastases"],
            ["Spots", "22,260 total; 3,439 malignant model spots"],
            ["Tumour-front spots", "1,290"],
            ["Features", "48 local and relation-aware features"],
            ["ROC AUC", "0.908"],
            ["Average precision", "0.857"],
            ["Balanced accuracy", "0.831"],
            ["Permutation test", "50 shuffles; P=0.0196; null AUC 0.495"],
            ["Matched scRNA reference", "56,072 recovered cells across four groups"],
        ], colWidths=[2.2 * inch, 5.0 * inch], repeatRows=1, style=TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), HexColor("#17212B")),
            ("TEXTCOLOR", (0, 0), (-1, 0), HexColor("#FFFFFF")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.4, HexColor("#CBD2D8")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [HexColor("#FFFFFF"), HexColor("#F2F4F5")]),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 7),
            ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ])),
        Spacer(1, 16),
        Paragraph("Safe closing line", h1),
        Paragraph("The strongest outcome is not a treatment claim; it is a clear, testable map of which tumour-host regions, cell states and interaction axes deserve pathology review and perturbation next.", answer),
        Spacer(1, 16),
        Paragraph("Core sources", h1),
        Paragraph("GSE225857: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE225857<br/>Science Advances: https://doi.org/10.1126/sciadv.adf5464<br/>HGP consensus: https://pmc.ncbi.nlm.nih.gov/articles/PMC5680474/<br/>Diagnostic reproducibility: https://pmc.ncbi.nlm.nih.gov/articles/PMC6611753/<br/>CRLM spatial fronts: https://www.nature.com/articles/s41416-026-03567-y<br/>Zenodo GeoMx: https://doi.org/10.5281/zenodo.7520789", small),
    ])
    doc = SimpleDocTemplate(str(PDF_PATH), pagesize=letter, leftMargin=0.65 * inch, rightMargin=0.65 * inch, topMargin=0.68 * inch, bottomMargin=0.68 * inch, title="CRC Liver Invasion Front Interview Q&A", author="CRC Liver Invasion Front Project")
    doc.build(story, onFirstPage=page_number, onLaterPages=page_number)


if __name__ == "__main__":
    build_docx()
    build_pdf()
