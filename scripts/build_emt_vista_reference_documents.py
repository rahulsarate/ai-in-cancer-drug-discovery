from __future__ import annotations

from datetime import date
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(r"C:\Users\HP\OneDrive\Documents\AI in Cancer Drug Discovery")
OUT = ROOT / "deliverables" / "emt_vista_presentation_pack"
DOCX_PATH = OUT / "EMT_ViSTA_Complete_Project_Reference.docx"
PDF_PATH = OUT / "EMT_ViSTA_Interview_Questions_and_Answers.pdf"
ASSETS = ROOT / "docs" / "emt_virtual_spatial_staining" / "assets"
LUNG = ROOT / "data" / "processed" / "emt_virtual_spatial_staining_v1" / "resnet50" / "maps" / "CytAssist_FFPE_Human_Lung_Squamous_Cell_Carcinoma_he_overlay.png"
CRC = ROOT / "data" / "processed" / "emt_virtual_spatial_staining_v1" / "resnet50" / "maps" / "Visium_FFPE_Human_Intestinal_Cancer_he_overlay.png"

BLUE = RGBColor(46, 116, 181)
DARK_BLUE = RGBColor(31, 77, 120)
INK = RGBColor(20, 27, 34)
MUTED = RGBColor(92, 101, 111)
TEAL = RGBColor(42, 157, 143)
RED = RGBColor(155, 28, 28)
LIGHT_BLUE = "EAF5FB"
LIGHT_GRAY = "F4F6F9"
LIGHT_RED = "FBECE8"


def set_repeat_table_header(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    repeat = OxmlElement("w:tblHeader")
    repeat.set(qn("w:val"), "true")
    tr_pr.append(repeat)


def set_cell_fill(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_cell_margins(cell, top=80, start=120, bottom=80, end=120) -> None:
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for margin, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tc_mar.find(qn(f"w:{margin}"))
        if node is None:
            node = OxmlElement(f"w:{margin}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def set_cell_width(cell, width_dxa: int) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_w = tc_pr.find(qn("w:tcW"))
    if tc_w is None:
        tc_w = OxmlElement("w:tcW")
        tc_pr.append(tc_w)
    tc_w.set(qn("w:w"), str(width_dxa))
    tc_w.set(qn("w:type"), "dxa")


def set_table_geometry(table, widths_dxa: list[int], indent_dxa: int = 120) -> None:
    table.autofit = False
    table.alignment = WD_TABLE_ALIGNMENT.LEFT
    tbl_pr = table._tbl.tblPr
    tbl_w = tbl_pr.find(qn("w:tblW"))
    if tbl_w is None:
        tbl_w = OxmlElement("w:tblW")
        tbl_pr.append(tbl_w)
    tbl_w.set(qn("w:w"), str(sum(widths_dxa)))
    tbl_w.set(qn("w:type"), "dxa")
    tbl_ind = tbl_pr.find(qn("w:tblInd"))
    if tbl_ind is None:
        tbl_ind = OxmlElement("w:tblInd")
        tbl_pr.append(tbl_ind)
    tbl_ind.set(qn("w:w"), str(indent_dxa))
    tbl_ind.set(qn("w:type"), "dxa")

    grid = table._tbl.tblGrid
    for child in list(grid):
        grid.remove(child)
    for width in widths_dxa:
        grid_col = OxmlElement("w:gridCol")
        grid_col.set(qn("w:w"), str(width))
        grid.append(grid_col)
    for row in table.rows:
        for index, cell in enumerate(row.cells):
            set_cell_width(cell, widths_dxa[index])
            set_cell_margins(cell)
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER


def set_run_font(run, size=None, color=INK, bold=None, italic=None) -> None:
    run.font.name = "Calibri"
    run._element.get_or_add_rPr().rFonts.set(qn("w:ascii"), "Calibri")
    run._element.get_or_add_rPr().rFonts.set(qn("w:hAnsi"), "Calibri")
    if size is not None:
        run.font.size = Pt(size)
    run.font.color.rgb = color
    if bold is not None:
        run.bold = bold
    if italic is not None:
        run.italic = italic


def add_paragraph(doc, text: str, *, bold=False, color=INK, align=None, style=None, after=8, before=0, keep=False):
    paragraph = doc.add_paragraph(style=style)
    paragraph.paragraph_format.space_before = Pt(before)
    paragraph.paragraph_format.space_after = Pt(after)
    paragraph.paragraph_format.line_spacing = 1.333
    paragraph.paragraph_format.keep_with_next = keep
    if align is not None:
        paragraph.alignment = align
    run = paragraph.add_run(text)
    set_run_font(run, color=color, bold=bold)
    return paragraph


def add_bullets(doc, items: list[str]) -> None:
    for item in items:
        paragraph = doc.add_paragraph(style="List Bullet")
        paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
        paragraph.paragraph_format.left_indent = Inches(0.375)
        paragraph.paragraph_format.first_line_indent = Inches(-0.194)
        paragraph.paragraph_format.space_after = Pt(4)
        paragraph.paragraph_format.line_spacing = 1.208
        run = paragraph.add_run(item)
        set_run_font(run)


def add_numbered(doc, items: list[str]) -> None:
    for item in items:
        paragraph = doc.add_paragraph(style="List Number")
        paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
        paragraph.paragraph_format.left_indent = Inches(0.375)
        paragraph.paragraph_format.first_line_indent = Inches(-0.194)
        paragraph.paragraph_format.space_after = Pt(4)
        paragraph.paragraph_format.line_spacing = 1.208
        run = paragraph.add_run(item)
        set_run_font(run)


def add_heading(doc, text: str, level: int = 1):
    paragraph = doc.add_heading(text, level=level)
    paragraph.paragraph_format.keep_with_next = True
    return paragraph


def add_callout(doc, title: str, body: str, fill=LIGHT_BLUE, color=DARK_BLUE) -> None:
    table = doc.add_table(rows=1, cols=1)
    set_table_geometry(table, [9360])
    cell = table.cell(0, 0)
    set_cell_fill(cell, fill)
    p = cell.paragraphs[0]
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run(title)
    set_run_font(r, size=12, color=color, bold=True)
    p2 = cell.add_paragraph()
    p2.paragraph_format.space_after = Pt(2)
    p2.paragraph_format.line_spacing = 1.25
    r2 = p2.add_run(body)
    set_run_font(r2, color=INK)
    doc.add_paragraph().paragraph_format.space_after = Pt(1)


def add_table(doc, headers: list[str], rows: list[list[str]], widths_dxa: list[int]) -> None:
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    header = table.rows[0]
    set_repeat_table_header(header)
    for index, value in enumerate(headers):
        cell = header.cells[index]
        set_cell_fill(cell, LIGHT_GRAY)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        run = p.add_run(value)
        set_run_font(run, size=9.5, color=DARK_BLUE, bold=True)
    for row in rows:
        cells = table.add_row().cells
        for index, value in enumerate(row):
            p = cells[index].paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.0
            run = p.add_run(str(value))
            set_run_font(run, size=9)
    set_table_geometry(table, widths_dxa)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def configure_document(doc: Document) -> None:
    section = doc.sections[0]
    section.page_width = Inches(8.5)
    section.page_height = Inches(11)
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)
    section.header_distance = Inches(0.492)
    section.footer_distance = Inches(0.492)

    normal = doc.styles["Normal"]
    normal.font.name = "Calibri"
    normal._element.rPr.rFonts.set(qn("w:ascii"), "Calibri")
    normal._element.rPr.rFonts.set(qn("w:hAnsi"), "Calibri")
    normal.font.size = Pt(11)
    normal.font.color.rgb = INK
    normal.paragraph_format.space_after = Pt(8)
    normal.paragraph_format.line_spacing = 1.333
    normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    for style_name, size, color, before, after in (
        ("Heading 1", 16, BLUE, 18, 10),
        ("Heading 2", 13, BLUE, 12, 6),
        ("Heading 3", 12, DARK_BLUE, 8, 4),
    ):
        style = doc.styles[style_name]
        style.font.name = "Calibri"
        style._element.rPr.rFonts.set(qn("w:ascii"), "Calibri")
        style._element.rPr.rFonts.set(qn("w:hAnsi"), "Calibri")
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = color
        style.paragraph_format.space_before = Pt(before)
        style.paragraph_format.space_after = Pt(after)
        style.paragraph_format.keep_with_next = True

    header = section.header
    hp = header.paragraphs[0]
    hp.alignment = WD_ALIGN_PARAGRAPH.LEFT
    hr = hp.add_run("EMT-ViSTA • Complete Project Reference")
    set_run_font(hr, size=9, color=MUTED, bold=True)
    footer = section.footer
    fp = footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = fp.add_run("Research and interview reference  •  ")
    set_run_font(run, size=9, color=MUTED)
    field = OxmlElement("w:fldSimple")
    field.set(qn("w:instr"), "PAGE")
    fp._p.append(field)


def build_docx() -> None:
    doc = Document()
    configure_document(doc)

    # Editorial cover
    for _ in range(4):
        add_paragraph(doc, "", after=12)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(12)
    r = p.add_run("EMT-ViSTA")
    set_run_font(r, size=30, color=DARK_BLUE, bold=True)
    p2 = doc.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p2.paragraph_format.space_after = Pt(18)
    r2 = p2.add_run("Virtual Spatial Staining of Epithelial-Mesenchymal Plasticity From Routine H&E")
    set_run_font(r2, size=18, color=INK, bold=True)
    p3 = doc.add_paragraph()
    p3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p3.paragraph_format.space_after = Pt(32)
    r3 = p3.add_run("Complete project report • methodology reference • interpretation guide • interview preparation")
    set_run_font(r3, size=12, color=MUTED, italic=True)
    add_callout(
        doc,
        "Project position",
        "An operational research pipeline with real public-data benchmarks and explicit safety gates. Current maps are hypotheses for assay triage and validation, not clinical molecular measurements.",
    )
    add_paragraph(doc, f"Prepared {date.today().strftime('%d %B %Y')}", align=WD_ALIGN_PARAGRAPH.CENTER, color=MUTED, after=2)
    add_paragraph(doc, "Repository: AI in Cancer Drug Discovery", align=WD_ALIGN_PARAGRAPH.CENTER, color=MUTED)
    doc.add_page_break()

    add_heading(doc, "How to use this document", 1)
    add_paragraph(doc, "This document has three uses: understanding the research design, presenting the project to scientists and clinicians, and preparing concise but technically sound interview answers.")
    add_numbered(doc, [
        "Read Sections 1–5 to understand the biological problem, hypothesis, questions and data.",
        "Use Sections 6–9 to explain the methodology, technical implementation and findings.",
        "Use Sections 10–14 for interpretation, limitations, pitch, interview framing and future work.",
    ])
    add_heading(doc, "Contents", 2)
    add_table(doc, ["Section", "Purpose"], [
        ["1. Executive summary", "The project in one page"],
        ["2. Scientific background", "Why epithelial-mesenchymal plasticity matters"],
        ["3. Hypothesis and questions", "Falsifiable aims and expected outcomes"],
        ["4. Data and literature", "Public databases, datasets and scientific grounding"],
        ["5. Methodology", "End-to-end workflow and why each choice matters"],
        ["6. Technical implementation", "Tools, models, outputs and reproducibility"],
        ["7. Results", "Actual held-out lung and colorectal benchmark"],
        ["8. Interpretation", "Valid and invalid conclusions"],
        ["9. Pros, cons and novelty", "Strengths, limitations and differentiators"],
        ["10. Project pitch", "30-second, 2-minute and 5-minute versions"],
        ["11. Interview reference", "High-yield answers and technical talking points"],
        ["12. Future study", "Publication and validation roadmap"],
    ], [2100, 7260])

    add_heading(doc, "1. Executive summary", 1)
    add_paragraph(doc, "EMT-ViSTA is a multimodal computational pathology project that tests whether routine H&E morphology can predict spatial epithelial, mesenchymal, partial-EMT, CAF, TAM, hypoxia, ECM-remodeling and stromal-contamination programs learned from paired spatial transcriptomics. The project is designed around a central safety problem: a mesenchymal-looking spatial spot can reflect malignant plasticity, fibroblast-rich stroma or simple spot mixing.")
    add_callout(doc, "Central contribution", "EMT-ViSTA predicts the candidate molecular program, a stromal-inflation risk and predictive uncertainty together. It can abstain when the evidence is not adequate.")
    add_paragraph(doc, "Five public aligned 10x cancer datasets supplied 16,862 scored spots. Breast and prostate were assigned to training, ovarian to validation, and lung squamous plus colorectal/intestinal cancer to held-out technical testing. Handcrafted and ImageNet ResNet50 baselines did not pass the predefined molecular-performance gates. Both passed the pure-stroma false-positive criterion. The negative benchmark is a useful scientific result because it demonstrates that software completion is not equivalent to biomarker validation.")
    if (ASSETS / "workflow_overview.png").exists():
        doc.add_picture(str(ASSETS / "workflow_overview.png"), width=Inches(6.4))
        add_paragraph(doc, "Figure 1. Executed EMT-ViSTA workflow.", color=MUTED, align=WD_ALIGN_PARAGRAPH.CENTER, after=10)

    add_heading(doc, "2. Scientific background and project importance", 1)
    add_heading(doc, "2.1 Epithelial-mesenchymal plasticity", 2)
    add_paragraph(doc, "Cancer EMT is increasingly understood as epithelial-mesenchymal plasticity rather than a binary conversion. Tumour cells can occupy partial or hybrid states, transition over time and interact with fibroblasts, macrophages, hypoxia and ECM. These states are associated with invasion, metastatic dissemination and treatment adaptation, but identifying them in human tissue remains difficult.")
    add_heading(doc, "2.2 Why spatial context matters", 2)
    add_paragraph(doc, "Bulk RNA averages malignant and stromal compartments. Single-cell RNA provides cell-level resolution but often loses intact tissue architecture. Spatial transcriptomics connects molecular programs to tissue regions, while H&E provides routine morphology. Paired H&E-spatial data therefore create a supervised setting for testing whether morphology can nominate molecularly interesting regions.")
    add_heading(doc, "2.3 Why the project matters", 2)
    add_bullets(doc, [
        "Spatial transcriptomics is informative but costly and not routine for every specimen.",
        "H&E is available at clinical scale and can support retrospective cohorts.",
        "Reliable virtual maps could prioritize laser-capture, spatial assays, pathology review and pharmacodynamic studies.",
        "Explicit abstention and contamination flags can prevent attractive but unreliable maps from becoming clinical claims.",
    ])

    add_heading(doc, "3. Hypothesis, research questions and aims", 1)
    add_callout(doc, "Central hypothesis", "Multi-scale H&E morphology contains transferable information about spatial epithelial-mesenchymal plasticity and its tumour microenvironment, but meaningful prediction requires explicit modeling of stromal admixture, domain shift and uncertainty.")
    add_heading(doc, "3.1 Primary research questions", 2)
    add_numbered(doc, [
        "Can routine H&E predict epithelial, mesenchymal and partial-EMT program scores learned from spatial transcriptomics?",
        "Can the model distinguish candidate malignant partial EMT from CAF-rich or stromal-inflated expression?",
        "Do local tissue-neighborhood representations improve prediction beyond image-only features?",
        "Does model uncertainty identify regions where abstention reduces prediction error?",
        "Do learned representations generalize to held-out lung squamous and colorectal datasets?",
        "Can the resulting maps support hypothesis generation without being confused with measured RNA or clinical diagnosis?",
    ])
    add_heading(doc, "3.2 Specific aims", 2)
    add_table(doc, ["Aim", "Execution", "Success criterion"], [
        ["Aim 1: Labels", "Construct EMT/TME scores and contamination-aware partial-EMT targets.", "Biological definitions are explicit and versioned."],
        ["Aim 2: Morphology", "Compare handcrafted, generic and pathology-foundation representations.", "Learned features beat transparent controls on held-out data."],
        ["Aim 3: Spatial context", "Add nearest-neighbor image representations.", "Spatial refinement improves patient-safe evaluation."],
        ["Aim 4: Safety", "Calibrate, quantify uncertainty and abstain.", "Selective prediction lowers error and stroma FPR stays below 0.15."],
        ["Aim 5: Translation", "Export H&E overlays and hotspots.", "Outputs remain reviewable and traceable to confidence fields."],
    ], [1100, 4780, 3480])

    add_heading(doc, "4. Data sources and literature grounding", 1)
    add_heading(doc, "4.1 Databases and datasets", 2)
    add_table(doc, ["Resource", "Role", "Used in v1", "Notes"], [
        ["10x Genomics public Visium", "Aligned H&E, coordinates and gene counts", "Yes", "Breast, prostate, ovarian, lung squamous and intestinal/CRC."],
        ["Local spatial EMT pipeline", "Molecular program scores and metadata", "Yes", "Provides EMT, CAF, TAM, hypoxia, ECM and stromal features."],
        ["Hugging Face: owkin/phikon-v2", "Pathology foundation embeddings", "Adapter + smoke run", "Ungated operational backend; full benchmark needs CUDA scale."],
        ["Hugging Face: Bioptimus H-Optimus-0", "Large pathology foundation model", "Adapter ready", "Model host requires user-specific access workflow and token."],
        ["HEST-1k", "Large paired histology-spatial scale-up", "Planned validation", "1,229 profiles and multimodal benchmarking framework."],
        ["HTAN / GEO spatial cohorts", "Multi-patient external validation", "Planned", "Needed for institution and patient-level generalization."],
        ["CELLxGENE / GEO scRNA-seq", "Compartment-resolved reference", "Planned", "Needed for malignant versus stromal deconvolution."],
    ], [1500, 2550, 1500, 3810])
    add_heading(doc, "4.2 Key literature", 2)
    add_table(doc, ["Reference", "Contribution to the project"], [
        ["Dong & Blanpain, Nature Reviews Cancer, 2026", "Defines EMT tumour states, partial states and therapeutic interpretation."],
        ["Thompson et al., Nature Reviews Clinical Oncology, 2025", "Clinical framing of epithelial-mesenchymal plasticity, metastasis and treatment resistance."],
        ["Jaume et al., HEST-1k, NeurIPS 2024", "Large-scale paired histology-spatial dataset and benchmark design."],
        ["Filiot et al., Phikon-v2, 2024", "Public pathology foundation-model representation for biomarker prediction."],
        ["STPath, npj Digital Medicine, 2025", "Large-scale generative H&E-to-spatial expression modeling and cross-platform considerations."],
        ["Towards robust foundation models for digital pathology, Nature Communications, 2026", "Shows medical-center confounding and the importance of out-of-domain evaluation."],
    ], [4000, 5360])
    add_paragraph(doc, "Links and full citations appear in Section 14.", color=MUTED)

    add_heading(doc, "5. Methodology and why each step matters", 1)
    methodology_rows = [
        ["1. Pairing and QC", "Match H&E coordinates to molecular spots and retain tissue/QC metadata.", "Prevents image-label misalignment and makes missing data visible."],
        ["2. Program scoring", "Compute epithelial, mesenchymal, partial-EMT, CAF, TAM-SPP1, hypoxia, ECM and stromal-risk targets.", "Program scores are more stable and interpretable than thousands of individual genes."],
        ["3. Malignant gating", "Require joint epithelial/mesenchymal activity and penalize high stromal risk.", "Reduces the chance of calling fibroblast-rich spots tumour EMT."],
        ["4. Multi-scale tiles", "Extract 224-pixel center and 448-pixel context regions.", "Captures local cells plus glands, desmoplasia, necrosis, vessels and invasive architecture."],
        ["5. Representations", "Compare handcrafted, ResNet50, Phikon-v2 and H-Optimus adapters.", "Separates simple stain/texture signal from learned pathology-specific representations."],
        ["6. Spatial context", "Append mean k-nearest-neighbor image features.", "Models tissue neighborhoods without an opaque full GNN in the first benchmark."],
        ["7. Multitask ensemble", "Bootstrap PCA plus ridge models predict eight programs together.", "Provides a transparent baseline and ensemble spread for uncertainty."],
        ["8. Calibration", "Measure partial-EMT AUPRC, calibration and stroma false positives.", "A virtual stain must be both accurate and honest about probability."],
        ["9. Abstention", "Reject high-uncertainty or high-risk predictions.", "Tests whether silence improves safety and error."],
        ["10. Export", "Create TSV, JSON, PNG overlays and GeoJSON hotspots.", "Enables review, downstream tooling and reproducibility."],
    ]
    add_table(doc, ["Step", "What was done", "Why it is important"], methodology_rows, [1700, 4200, 3460])

    add_heading(doc, "5.1 Label definitions", 2)
    add_bullets(doc, [
        "Epithelial score: epithelial identity and cell-cell adhesion program.",
        "Mesenchymal score: motility, matrix interaction and mesenchymal program.",
        "Partial-EMT score: co-activity of epithelial and mesenchymal programs rather than an average along one axis.",
        "Stromal contamination risk: likelihood that mesenchymal expression is explained by fibroblast/ECM-rich admixture.",
        "Malignant-gated partial-EMT probability: partial-EMT evidence retained only when epithelial evidence is adequate and stromal risk is controlled.",
    ])
    add_heading(doc, "5.2 Predefined go/no-go criteria", 2)
    add_table(doc, ["Criterion", "Threshold", "Purpose"], [
        ["Median test Spearman", ">= 0.35", "Overall held-out molecular ranking accuracy."],
        ["Programs above 0.35", ">= 4", "Prevents one easy target from hiding broad failure."],
        ["Partial-EMT AUPRC above prevalence", ">= 0.15", "Measures discrimination beyond class prevalence."],
        ["Pure-stroma false-positive rate", "< 0.15", "Safety against stromal mimicry."],
        ["Partial-EMT calibration error", "< 0.10", "Probability reliability."],
        ["Abstention error improvement", ">= 0.15", "Confirms uncertainty is useful rather than decorative."],
    ], [3900, 1800, 3660])

    add_heading(doc, "6. Technical implementation and tools", 1)
    add_table(doc, ["Tool", "Project role", "Advantage", "Limitation"], [
        ["Python 3.10", "Reproducible runtime", "Stable scientific ecosystem", "Separate environment required from system Python 3.14"],
        ["pandas / NumPy", "Tables and numerical processing", "Transparent, inspectable transformations", "Memory-bound at very large scale"],
        ["scikit-learn", "PCA, ridge, neighbors, metrics", "Strong interpretable baselines", "No end-to-end image learning"],
        ["PyTorch / torchvision", "ResNet and tensor inference", "Standard accelerated ecosystem", "CUDA needed for scale"],
        ["Transformers", "Phikon-v2 adapter", "Public pathology-specific features", "Large model and license considerations"],
        ["timm", "H-Optimus adapter", "Broad ViT model support", "Weights require host access workflow"],
        ["Matplotlib / seaborn", "Scientific plots and maps", "Reproducible static figures", "Not a clinical WSI viewer"],
        ["GeoJSON", "Hotspot exchange", "Interoperable spatial output", "Coordinates require slide metadata"],
        ["pytest", "Regression and safety testing", "28 passing tests prevent silent breakage", "Cannot establish biological validity"],
    ], [1500, 2100, 2860, 2900])
    add_heading(doc, "6.1 Repository deliverables", 2)
    add_bullets(doc, [
        "Numbered scripts 09–16 for pairing, embeddings, baselines, multitask training, evaluation, inference, maps and paper figures.",
        "A reusable emt_virtual_spatial_staining Python package.",
        "A five-cohort YAML configuration and end-to-end orchestrator.",
        "Machine-readable predictions, metrics, safety tables, manifests and model metadata.",
        "Student report, interview guide, manuscript draft and implementation report.",
    ])

    add_heading(doc, "7. Results from the real-data run", 1)
    add_table(doc, ["Representation", "Held-out spots", "Median Spearman", "Best program", "Best Spearman", "Gates passed"], [
        ["Handcrafted multi-scale", "1,024", "0.014", "Epithelial", "0.310", "2/7"],
        ["ResNet50 ImageNet", "256", "-0.086", "Partial-EMT score", "-0.032", "2/7"],
    ], [2050, 1300, 1500, 1800, 1350, 1360])
    add_paragraph(doc, "The handcrafted model did not meet the median 0.35 gate, although epithelial score reached 0.310. ResNet50 did not improve transfer. Partial-EMT discrimination, calibration and abstention-improvement gates failed. Both controls passed the pure-stroma false-positive threshold.")
    if (ASSETS / "backend_comparison.png").exists():
        doc.add_picture(str(ASSETS / "backend_comparison.png"), width=Inches(6.2))
        add_paragraph(doc, "Figure 2. Median held-out performance versus the predefined gate.", color=MUTED, align=WD_ALIGN_PARAGRAPH.CENTER)
    add_callout(doc, "Primary finding", "The engineering pipeline is operational, but simple morphology and generic ImageNet features do not provide reliable cross-cancer molecular virtual stains in this sampled benchmark.", fill=LIGHT_RED, color=RED)
    if LUNG.exists():
        doc.add_picture(str(LUNG), width=Inches(6.25))
        add_paragraph(doc, "Figure 3. Held-out lung squamous H&E overlay. Spatial alignment is correct; molecular accuracy gates remain failed.", color=MUTED, align=WD_ALIGN_PARAGRAPH.CENTER)

    add_heading(doc, "8. Interpretation: what the findings mean", 1)
    add_heading(doc, "8.1 Valid conclusions", 2)
    add_bullets(doc, [
        "The complete paired-data, modeling, uncertainty, evaluation and export workflow runs on real public slides.",
        "Dataset-level holdouts expose substantial cross-cancer domain shift.",
        "Handcrafted features retain more epithelial ranking signal than the sampled ResNet50 control but still fail the release gate.",
        "The stromal false-positive control behaves conservatively in the first run.",
        "A pathology-specific representation and better ground truth are justified as the next experiment.",
    ])
    add_heading(doc, "8.2 Invalid conclusions", 2)
    add_bullets(doc, [
        "H&E has not been shown to directly measure EMT or spatial RNA.",
        "Predicted hotspots have not been established as invasive fronts or metastatic niches.",
        "The lung and colorectal slides are technical holdouts, not multi-patient clinical validation.",
        "The negative controls do not prove that pathology foundation models will succeed.",
        "No treatment or patient decision should be based on these outputs.",
    ])
    add_callout(doc, "Interpretation rule", "A high virtual partial-EMT probability means that morphology resembles molecularly scored training regions under this label definition. It must be reviewed together with stromal risk, uncertainty, tissue region and orthogonal molecular or pathology evidence.")

    add_heading(doc, "9. Advantages, disadvantages and novelty", 1)
    add_table(doc, ["Advantages", "Disadvantages / risks"], [[
        "Routine H&E input; public reproducible data; program-level biological targets; explicit contamination risk; uncertainty and abstention; interpretable controls; reviewable maps and GeoJSON; honest negative results.",
        "Few slides/patients; mixed spatial spots; bounded CPU samples; foundation model not yet benchmarked at full scale; no blinded pathologist regions; no untouched institution; no prospective endpoint; domain and stain shift.",
    ]], [4680, 4680])
    add_heading(doc, "9.1 Novel contributions", 2)
    add_bullets(doc, [
        "Risk-aware partial EMT rather than unqualified H&E-to-expression regression.",
        "Joint prediction of molecular program, contamination risk and uncertainty.",
        "Multi-scale morphology plus spatial-neighbor refinement.",
        "Predefined biological and calibration gates that can reject attractive outputs.",
        "Lung and colorectal transfer experiments embedded in a pan-cancer pipeline.",
    ])

    add_heading(doc, "10. Project pitch", 1)
    add_heading(doc, "10.1 Thirty-second pitch", 2)
    add_callout(doc, "Pitch", "I built EMT-ViSTA, a multimodal pipeline that learns spatial EMT and tumour-microenvironment programs from routine H&E using paired spatial transcriptomics. Its novelty is contamination-aware partial-EMT prediction with uncertainty and abstention. The first lung and colorectal holdouts rejected simple image baselines, giving an honest roadmap toward pathology-foundation, patient-level and pathologist-validated studies.")
    add_heading(doc, "10.2 Two-minute pitch", 2)
    add_paragraph(doc, "Spatial EMT and its CAF, macrophage, hypoxia and ECM context matter for metastasis and therapy resistance, but spatial transcriptomics is too expensive for routine use. EMT-ViSTA asks whether routine H&E can nominate these spatial programs. I paired five public cancer H&E-spatial datasets, built program-level labels, and introduced a malignant partial-EMT gate so fibroblast-rich spots are not automatically called tumour EMT. The model combines center and context image representations with spatial-neighbor features, predicts eight targets through a bootstrap ensemble, and exports uncertainty, abstention and H&E overlays.")
    add_paragraph(doc, "The first held-out lung and colorectal experiment produced a negative but important finding. Handcrafted and generic ResNet50 features did not meet predefined molecular-performance or calibration gates, while the pure-stroma false-positive gate passed. That means the software is operational but the biomarker is not validated. The next decisive experiment is full-scale pathology-foundation extraction followed by leave-patient-out validation, scRNA-based compartment labels and blinded pathologist annotations.")
    add_heading(doc, "10.3 Five-minute presentation structure", 2)
    add_numbered(doc, [
        "Problem: spatial EMT matters, but routine H&E does not directly measure it.",
        "Hypothesis: morphology contains transferable signal if contamination and uncertainty are modeled.",
        "Method: paired public data, risk-aware labels, multi-scale representations, spatial ensemble and safety gates.",
        "Finding: simple controls fail held-out molecular criteria; stroma safety passes.",
        "Interpretation: framework ready, biomarker not ready.",
        "Next study: pathology foundation models, patient-level cohorts, pathologist/scRNA ground truth and external centers.",
    ])

    add_heading(doc, "11. Interview reference", 1)
    add_heading(doc, "11.1 High-yield answers", 2)
    add_table(doc, ["Question", "Best concise answer"], [
        ["What is the project?", "A contamination-aware H&E-to-spatial-program research pipeline for EMT and the tumour microenvironment."],
        ["What is the novelty?", "It predicts partial EMT, stromal risk and uncertainty together and can abstain."],
        ["Why program scores?", "They reduce spatial-RNA dropout and match the biological question better than thousands of single genes."],
        ["Why dataset-level splits?", "Random spot splits leak slide-specific stain and local tissue information."],
        ["Why PCA plus ridge?", "It is a transparent regularized baseline that reveals domain shift before larger models hide it."],
        ["What was the result?", "The first handcrafted and ResNet controls failed held-out molecular gates; pure-stroma safety passed."],
        ["Was the project successful?", "The platform succeeded and the baselines were correctly falsified; biological validation remains incomplete."],
        ["What is next?", "Full pathology-foundation runs, patient-level cohorts, scRNA deconvolution, pathologist regions and external validation."],
    ], [3350, 6010])
    add_heading(doc, "11.2 Technical talking points", 2)
    add_bullets(doc, [
        "Unit of validation: patient and institution, not individual neighboring spots.",
        "Primary continuous metric: held-out Spearman correlation; partial EMT also needs AUPRC and calibration.",
        "Uncertainty: spread across bootstrap ensemble predictions.",
        "Selective risk: error after abstaining on the most uncertain spots.",
        "Safety metric: false-positive partial EMT in molecularly defined pure-stroma regions.",
        "Failure analysis: domain shift, weak labels, spot mixing, small cohort size and non-pathology ImageNet features.",
    ])
    add_paragraph(doc, "The companion PDF contains the full interview and viva question bank.", color=MUTED)

    add_heading(doc, "12. Future execution and publication roadmap", 1)
    add_table(doc, ["Phase", "Execution", "Evidence produced", "Estimated effort"], [
        ["Foundation scale-up", "Full Phikon-v2 and H-Optimus extraction on CUDA.", "Fair representation benchmark under frozen gates.", "1–2 weeks"],
        ["Ground-truth refinement", "Matched scRNA deconvolution and two-pathologist annotations.", "Malignant/stromal compartment labels and agreement.", "3–6 weeks"],
        ["Patient-level validation", "Multi-patient lung and CRC leave-one-patient-out analysis.", "Confidence intervals and disease-specific models.", "4–8 weeks"],
        ["External center", "Untouched institution, scanner and platform.", "Out-of-domain generalization and failure cases.", "6–12 weeks"],
        ["Prospective utility", "Assay-triage endpoint and region-selection study.", "Clinical workflow utility, not just correlation.", "3–9 months"],
    ], [1500, 3300, 3000, 1560])
    add_heading(doc, "12.1 Publication decision rule", 2)
    add_paragraph(doc, "The manuscript should be submitted as a positive molecular virtual-stain study only if frozen patient-level external gates pass. Otherwise, the appropriate article is a rigorous framework and negative-benchmark report focused on contamination controls, domain shift and reproducible failure analysis.")
    if (ASSETS / "readiness_dimensions.png").exists():
        doc.add_picture(str(ASSETS / "readiness_dimensions.png"), width=Inches(6.2))
        add_paragraph(doc, "Figure 4. Engineering completion and scientific validation are reported separately.", color=MUTED, align=WD_ALIGN_PARAGRAPH.CENTER)

    add_heading(doc, "13. Conclusion", 1)
    add_paragraph(doc, "EMT-ViSTA is a completed executable research MVP and an incomplete biological biomarker. Its strongest contribution is the combination of spatial EMT hypotheses with contamination risk, uncertainty, abstention and predefined falsification. The project provides a credible platform for pathology-foundation and patient-level studies while demonstrating the scientific value of refusing unsupported claims.")
    add_callout(doc, "Final message", "A trustworthy virtual stain must know when not to stain.")

    add_heading(doc, "14. References and project resources", 1)
    references = [
        "Dong A, Blanpain C. Identification, functional insights and therapeutic targeting of EMT tumour states. Nature Reviews Cancer. 2026. https://www.nature.com/articles/s41568-025-00873-0",
        "Thompson EW et al. EMT and cancer: what clinicians should know. Nature Reviews Clinical Oncology. 2025. https://www.nature.com/articles/s41571-025-01058-2",
        "Jaume G et al. HEST-1k: A Dataset for Spatial Transcriptomics and Histology Image Analysis. NeurIPS Datasets and Benchmarks. 2024. https://proceedings.neurips.cc/paper_files/paper/2024/file/60a899cc31f763be0bde781a75e04458-Paper-Datasets_and_Benchmarks_Track.pdf",
        "Filiot A et al. Phikon-v2, a large and public feature extractor for biomarker prediction. 2024. https://arxiv.org/abs/2409.09173",
        "STPath: a generative foundation model for integrating spatial transcriptomics and whole-slide images. npj Digital Medicine. 2025. https://www.nature.com/articles/s41746-025-02020-3",
        "Towards robust foundation models for digital pathology. Nature Communications. 2026. https://www.nature.com/articles/s41467-026-73923-2",
        "Bioptimus H-Optimus model family. https://www.bioptimus.com/h-optimus",
        "HEST official repository. https://github.com/mahmoodlab/hest",
        "Project protocol: docs/emt_virtual_spatial_staining/detailed_project_plan.md",
        "Project implementation report: docs/emt_virtual_spatial_staining/implementation_report.md",
        "Project article draft: docs/emt_virtual_spatial_staining/research_article_draft.md",
    ]
    add_bullets(doc, references)

    OUT.mkdir(parents=True, exist_ok=True)
    doc.save(DOCX_PATH)


QA_SECTIONS = {
    "Concept and biological rationale": [
        ("What problem does EMT-ViSTA solve?", "It tests whether routine H&E can nominate spatial EMT and tumour-microenvironment programs that would otherwise require spatial transcriptomics.", "Spatial RNA is molecularly informative but expensive. H&E is routine and scalable. The project creates a supervised bridge while preserving uncertainty and contamination warnings.", "Why is this nomination rather than diagnosis?"),
        ("What is the central hypothesis?", "Multi-scale morphology contains transferable information about epithelial-mesenchymal plasticity if stromal mixing and uncertainty are modeled explicitly.", "The hypothesis is falsifiable through held-out dataset performance, stroma false-positive tests, calibration and selective-risk criteria.", "What result would make you reject the hypothesis?"),
        ("Why use the term epithelial-mesenchymal plasticity?", "Because cancer cells occupy dynamic partial states rather than following only a complete binary EMT.", "Plasticity includes movement among epithelial, hybrid and mesenchymal states. It better matches recent human tumour literature and avoids treating EMT as a one-way switch.", "How does plasticity change label design?"),
        ("What is partial EMT?", "A state in which epithelial and mesenchymal programs are simultaneously active.", "It is not simply a midpoint on one score. EMT-ViSTA requires co-activity of both programs and then applies malignant and stromal-risk gates.", "Why can a midpoint score be misleading?"),
        ("Why is stromal contamination a major issue?", "Fibroblasts and ECM can produce mesenchymal expression in a mixed spatial spot without malignant-cell EMT.", "Visium spots contain multiple cells. Without an epithelial requirement and stromal-risk output, fibroblast-rich regions can become false partial-EMT hotspots.", "How would single-cell references help?"),
        ("What are the main research questions?", "Can H&E predict EMT/TME programs, separate malignant plasticity from stroma, benefit from spatial context and identify when to abstain?", "The questions cover biological validity, model value, generalization and safety rather than correlation alone.", "Which question is most clinically important?"),
    ],
    "Data and methodology": [
        ("Which data were used?", "Five public aligned 10x Visium cancer datasets: breast, prostate, ovarian, lung squamous and intestinal/colorectal.", "Together they supplied 16,862 scored spots. Breast and prostate trained the model, ovarian validated it, and lung plus colorectal were held out.", "Why are these technical rather than clinical cohorts?"),
        ("Why use public 10x datasets first?", "They provide standardized counts, coordinates and aligned H&E for a fast reproducible MVP.", "Their standard format reduces ingestion risk and allows the scientific question to be tested before scaling to heterogeneous portals.", "What bias can product datasets introduce?"),
        ("How did you avoid data leakage?", "Splits were defined at dataset/sample level, never by random neighboring spots.", "Random spot splitting leaks stain, tissue architecture and spatial autocorrelation from one slide into both train and test sets.", "What is the correct future validation unit?"),
        ("Why predict programs instead of individual genes?", "Programs are more stable under spatial-RNA sparsity and more interpretable biologically.", "They reduce dimensionality and match EMT/TME questions. The trade-off is signature dependence, so signatures must be versioned and sensitivity-tested.", "When would gene-level prediction be useful?"),
        ("How was partial EMT labeled?", "By joint epithelial and mesenchymal activity, then reduced when stromal risk was high or epithelial evidence was weak.", "The model also records confidence tiers so weak or contaminated spots do not receive the same supervision as high-confidence spots.", "Is this still a weak label?"),
        ("Why use center and context tiles?", "The center captures local morphology; the context captures glands, desmoplasia, immune aggregates, vessels and necrosis.", "Combining scales represents the spot and its tissue niche. This is especially relevant for invasive fronts and CAF/hypoxia neighborhoods.", "How would you choose tile size on a new scanner?"),
        ("Which image representations were tested?", "Handcrafted features, ImageNet ResNet50 and operational adapters for Phikon-v2 and H-Optimus-0.", "Handcrafted and ResNet form transparent controls. Phikon-v2 is pathology-specific and was smoke-tested; full foundation benchmarking requires CUDA-scale extraction.", "Why is ResNet50 not a pathology foundation model?"),
        ("What model architecture was used?", "A bootstrap multitask ensemble of PCA plus ridge models using image and spatial-neighbor features.", "It is a regularized, interpretable baseline. PCA is fit on training data, ridge predicts eight targets, and ensemble spread estimates uncertainty.", "What model would you test next?"),
        ("Why not start with a graph neural network or Transformer?", "A simpler baseline reveals leakage, weak labels and domain shift before complexity hides them.", "A complex model is justified only after it beats stain, texture, ImageNet and pathology-foundation controls on patient-level holdouts.", "When would a heterogeneous GNN become useful?"),
        ("How was spatial information added?", "Each spot received the mean image representation of its nearest spatial neighbors.", "This gives a transparent neighborhood baseline and tests whether local tissue organization helps beyond the center tile.", "What information is lost by averaging neighbors?"),
        ("How was uncertainty estimated?", "By the prediction spread across bootstrapped ensemble members.", "The ensemble mean is the prediction and its standard deviation is an epistemic uncertainty proxy. Selective-risk analysis checks whether rejecting uncertain spots lowers error.", "What uncertainty is not captured?"),
        ("What is abstention?", "The model refuses to issue a confident virtual stain when uncertainty or contamination risk is excessive.", "Abstention converts uncertainty into an operational decision and is evaluated by whether error improves after uncertain cases are removed.", "Why is abstention important in biomedicine?"),
        ("Which metrics were used?", "Spearman, Pearson, MAE and R-squared for continuous programs; AUPRC, calibration and stroma false-positive rate for partial EMT.", "The metric bundle covers ranking, absolute error, discrimination, probability reliability and biological safety.", "Why is no single metric sufficient?"),
        ("Why prioritize Spearman correlation?", "It evaluates whether spots are ranked correctly even if score scales differ across cohorts.", "Program scores are relative and can shift in scale. Spearman is robust to monotonic transformations, while Pearson and MAE provide complementary information.", "What limitation does Spearman have?"),
        ("What does AUPRC above prevalence mean?", "It measures how much partial-EMT discrimination improves beyond the positive-class baseline.", "AUPRC is informative under class imbalance. Subtracting prevalence prevents an apparently reasonable raw score from hiding weak performance.", "Why not report AUROC only?"),
    ],
    "Results and interpretation": [
        ("What were the main results?", "Handcrafted features reached median held-out Spearman 0.014; ResNet50 reached -0.086. Neither met the 0.35 gate.", "The best handcrafted result was epithelial score at 0.310. Partial-EMT discrimination, calibration and abstention-improvement criteria failed. Pure-stroma FPR passed.", "Which result was most encouraging?"),
        ("Did the project fail?", "The engineering platform succeeded; the first two biological baselines were correctly falsified.", "A rigorous project is successful when it distinguishes an operational pipeline from an unsupported biomarker claim. The negative result guides the next model and data experiments.", "How would you present a negative result to a sponsor?"),
        ("What does passing the stroma false-positive gate mean?", "The model rarely labeled molecularly defined pure-stroma regions as partial EMT under the selected threshold.", "This supports the gating design, but it does not rescue poor overall molecular accuracy or prove malignant specificity.", "Could a conservative model pass by predicting no positives?"),
        ("Why might ResNet50 perform worse than handcrafted features?", "ImageNet features are not pathology-specific and the sampled experiment is vulnerable to stain and domain shift.", "Handcrafted color and tissue-density features can preserve coarse morphology directly. Generic learned features may encode natural-image abstractions or dataset identity rather than transferable biology.", "How would you test this explanation?"),
        ("What can be concluded from the maps?", "They are reviewable model hypotheses aligned to H&E, not measured molecular maps.", "A high score means morphological similarity to labeled training regions. It must be interpreted with contamination risk, uncertainty and orthogonal evidence.", "What annotation would make the maps more credible?"),
        ("What cannot be concluded?", "The project does not show that H&E directly measures EMT, predicts metastasis or supports patient treatment decisions.", "The holdouts are not multi-patient external cohorts, and there are no blinded pathologist regions or prospective outcomes.", "What claim would be acceptable today?"),
        ("Why are negative results valuable here?", "They prevent visually compelling overlays from being mistaken for molecular validation.", "The failed gates identify domain shift and weak-label risk early, before expensive clinical or mechanistic claims are built on unreliable predictions.", "How do predefined gates reduce bias?"),
    ],
    "Limitations, novelty and next steps": [
        ("What are the main limitations?", "Few slides and patients, mixed spatial spots, sampled CPU runs, no full foundation benchmark, no blinded pathologist labels and no external institution.", "Each limitation maps to a specific next experiment rather than a vague need for more data.", "Which limitation should be solved first?"),
        ("What is the project novelty?", "Risk-aware partial EMT, separate stromal-risk prediction, spatial morphology, uncertainty, abstention and predefined biological safety gates.", "The novelty is the integrated safety-oriented design, not merely H&E-to-expression regression.", "How is this different from STPath?"),
        ("What are the advantages?", "Routine input, public reproducible data, interpretable programs, modular outputs and explicit failure handling.", "The pipeline can support assay triage and method development while keeping large data local and code reproducible.", "Which advantage matters most for GitHub adoption?"),
        ("What are the disadvantages?", "The task is weakly supervised, domain-sensitive and computationally expensive at foundation-model scale.", "The model can learn stain, scanner or cohort identity. Clinical translation requires patient-level and center-level evidence.", "How would domain-adversarial learning help?"),
        ("What is the next decisive experiment?", "Run full Phikon-v2/H-Optimus features on CUDA and evaluate multi-patient lung and CRC cohorts under the frozen gates.", "This should be combined with matched scRNA deconvolution and two-pathologist region annotation.", "Why freeze the gates before the next run?"),
        ("How would scRNA-seq improve the project?", "It would provide cell-type references to separate malignant, fibroblast, macrophage and endothelial contributions in mixed spots.", "Cell2location, RCTD or related methods can generate compartment proportions and cleaner malignant partial-EMT supervision.", "What happens if the reference is disease-mismatched?"),
        ("How would pathologists contribute?", "They would annotate tumour-rich, stroma-rich, invasive-edge, necrotic/hypoxic, immune-rich and vessel-rich regions.", "Two blinded reviewers enable agreement estimates and region-level validation independent of molecular signatures.", "How would you handle disagreement?"),
        ("When is the project publication ready?", "After full foundation-model comparison, patient-level confidence intervals, pathologist/scRNA ground truth and untouched external-center evaluation.", "If gates remain failed, the valid paper is a framework and negative benchmark rather than a positive biomarker paper.", "What would be the primary endpoint?"),
        ("Can this be used clinically now?", "No. It is a research and assay-triage system, not a diagnostic or treatment-selection tool.", "Clinical use would require intended-use definition, independent validation, prospective utility, quality management and regulatory assessment.", "What is a realistic near-term use?"),
        ("How could it support cancer drug discovery?", "It could nominate spatial EMT/TME niches for profiling, target validation and pharmacodynamic sampling.", "Maps can prioritize regions for laser capture, spatial assays or drug-response comparison. They rank regions for investigation rather than therapies for patients.", "Which drug-discovery experiment would you run first?"),
        ("How would you answer ‘what did you personally learn’?", "I learned that reproducible multimodal engineering and biological validation are separate achievements.", "The project reinforced the value of patient-safe splits, explicit contamination models, negative controls and communicating uncertainty before complexity.", "What engineering challenge was hardest?"),
        ("Give the 30-second project pitch.", "I built EMT-ViSTA, a contamination-aware H&E-to-spatial-program pipeline for EMT and the tumour microenvironment.", "It combines paired spatial transcriptomics, multi-scale morphology, spatial context, uncertainty and abstention. The first lung and CRC holdouts rejected simple baselines, defining a rigorous path toward pathology-foundation and patient-level validation.", "What single sentence should the interviewer remember?"),
    ],
}


def build_pdf() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleCustom", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=28, leading=32, textColor=colors.HexColor("#1F4D78"), alignment=TA_CENTER, spaceAfter=18)
    subtitle_style = ParagraphStyle("SubtitleCustom", parent=styles["Normal"], fontName="Helvetica", fontSize=13, leading=18, textColor=colors.HexColor("#5C656F"), alignment=TA_CENTER, spaceAfter=18)
    section_style = ParagraphStyle("Section", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=18, leading=22, textColor=colors.HexColor("#2E74B5"), spaceBefore=8, spaceAfter=10)
    question_style = ParagraphStyle("Question", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=12.5, leading=16, textColor=colors.white, spaceAfter=0)
    label_style = ParagraphStyle("Label", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=9.5, leading=12, textColor=colors.HexColor("#1F4D78"), spaceAfter=2)
    answer_style = ParagraphStyle("Answer", parent=styles["Normal"], fontName="Helvetica", fontSize=9.5, leading=13, textColor=colors.HexColor("#141B22"), spaceAfter=6)
    small_style = ParagraphStyle("Small", parent=styles["Normal"], fontName="Helvetica-Oblique", fontSize=8.5, leading=11, textColor=colors.HexColor("#5C656F"), spaceAfter=8)
    pitch_style = ParagraphStyle("Pitch", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=12, leading=17, textColor=colors.HexColor("#1F4D78"), alignment=TA_LEFT)

    def page(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#68717B"))
        canvas.drawString(0.75 * inch, 0.47 * inch, "EMT-ViSTA • Interview and Viva Questions")
        canvas.drawRightString(7.75 * inch, 0.47 * inch, f"Page {doc.page}")
        canvas.setStrokeColor(colors.HexColor("#D6DADF"))
        canvas.line(0.75 * inch, 0.62 * inch, 7.75 * inch, 0.62 * inch)
        canvas.restoreState()

    pdf = SimpleDocTemplate(str(PDF_PATH), pagesize=letter, rightMargin=0.72 * inch, leftMargin=0.72 * inch, topMargin=0.72 * inch, bottomMargin=0.8 * inch, title="EMT-ViSTA Interview Questions and Answers", author="EMT-ViSTA Project")
    story = [Spacer(1, 0.8 * inch), Paragraph("EMT-ViSTA", title_style), Paragraph("Interview and Viva Questions & Answers", title_style), Paragraph("Concept • methodology • tools • findings • interpretation • limitations • next studies", subtitle_style), HRFlowable(width="85%", thickness=2, color=colors.HexColor("#6DCBF4"), spaceBefore=8, spaceAfter=24), Paragraph("Thirty-second answer", section_style), Table([[Paragraph("EMT-ViSTA is a multimodal research pipeline that learns spatial EMT and tumour-microenvironment programs from routine H&E using paired spatial transcriptomics. Its novelty is contamination-aware partial-EMT prediction with uncertainty and abstention. The first held-out lung and colorectal benchmarks rejected simple image baselines, proving the value of predefined safety gates and defining the next patient-level pathology-foundation study.", pitch_style)]], colWidths=[6.6 * inch], style=TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EAF5FB")), ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#6DCBF4")), ("LEFTPADDING", (0, 0), (-1, -1), 14), ("RIGHTPADDING", (0, 0), (-1, -1), 14), ("TOPPADDING", (0, 0), (-1, -1), 14), ("BOTTOMPADDING", (0, 0), (-1, -1), 14)])), Spacer(1, 18), Paragraph("How to practice", section_style), Paragraph("Answer each question in one sentence first. Add the deep answer only when asked. End with the follow-up question as a self-test.", answer_style), PageBreak()]

    question_number = 1
    for section_index, (section, questions) in enumerate(QA_SECTIONS.items()):
        story.append(Paragraph(section, section_style))
        story.append(Paragraph(f"{len(questions)} questions", small_style))
        for question, short_answer, deep_answer, follow_up in questions:
            q_table = Table([[Paragraph(f"Q{question_number}. {question}", question_style)]], colWidths=[6.8 * inch])
            q_table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#2E74B5")), ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10), ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7)]))
            story.extend([q_table, Spacer(1, 5), Paragraph("SHORT ANSWER", label_style), Paragraph(short_answer, answer_style), Paragraph("DEEP ANSWER", label_style), Paragraph(deep_answer, answer_style), Paragraph(f"Self-test: {follow_up}", small_style), Spacer(1, 6)])
            question_number += 1
        if section_index < len(QA_SECTIONS) - 1:
            story.append(Spacer(1, 12))

    story.extend([PageBreak(), Paragraph("Last-minute interview checklist", section_style), Paragraph("• Define the problem before naming tools.<br/>• Explain why stromal contamination changes the target.<br/>• State the dataset split and held-out cancers.<br/>• Report the negative result without softening it.<br/>• Separate engineering completion from biological and clinical validation.<br/>• End with the next decisive experiment.", answer_style), Spacer(1, 18), Paragraph("One sentence to remember", section_style), Table([[Paragraph("A trustworthy virtual stain must know when not to stain.", pitch_style)]], colWidths=[6.6 * inch], style=TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FBECE8")), ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#C23B4A")), ("LEFTPADDING", (0, 0), (-1, -1), 14), ("RIGHTPADDING", (0, 0), (-1, -1), 14), ("TOPPADDING", (0, 0), (-1, -1), 14), ("BOTTOMPADDING", (0, 0), (-1, -1), 14)]))])
    pdf.build(story, onFirstPage=page, onLaterPages=page)


if __name__ == "__main__":
    build_docx()
    build_pdf()
    print(f"Created {DOCX_PATH}")
    print(f"Created {PDF_PATH}")
