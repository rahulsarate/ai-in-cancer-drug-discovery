import fs from "node:fs/promises";
import path from "node:path";

import { Presentation, PresentationFile } from "@oai/artifact-tool";

const ROOT = "C:/Users/HP/OneDrive/Documents/AI in Cancer Drug Discovery";
const OUTPUT_DIR = path.join(ROOT, "deliverables", "emt_vista_presentation_pack");
const FINAL_PPTX = path.join(OUTPUT_DIR, "EMT_ViSTA_Project_Interpretation_Presentation.pptx");
const RENDER_DIR = path.join(OUTPUT_DIR, "qa_slides");

const ASSETS = {
  lung: path.join(ROOT, "data/processed/emt_virtual_spatial_staining_v1/resnet50/maps/CytAssist_FFPE_Human_Lung_Squamous_Cell_Carcinoma_he_overlay.png"),
  crc: path.join(ROOT, "data/processed/emt_virtual_spatial_staining_v1/resnet50/maps/Visium_FFPE_Human_Intestinal_Cancer_he_overlay.png"),
  lungMaps: path.join(ROOT, "data/processed/emt_virtual_spatial_staining_v1/resnet50/maps/CytAssist_FFPE_Human_Lung_Squamous_Cell_Carcinoma_virtual_stains.png"),
  crcMaps: path.join(ROOT, "data/processed/emt_virtual_spatial_staining_v1/resnet50/maps/Visium_FFPE_Human_Intestinal_Cancer_virtual_stains.png"),
};

const C = {
  canvas: "#FFFFFF",
  ink: "#111111",
  muted: "#5F6670",
  panel: "#EDEDED",
  rule: "#B8BCC4",
  accent: "#6DCBF4",
  accentStrong: "#3D8DFF",
  teal: "#2A9D8F",
  coral: "#E76F51",
  red: "#C23B4A",
  paleBlue: "#EAF5FB",
  paleCoral: "#FBECE8",
};

const FONT = "Arial";
const presentation = Presentation.create({ slideSize: { width: 1280, height: 720 } });

function box(slide, { left, top, width, height, fill = "none", line = "none", radius = 0, name }) {
  return slide.shapes.add({
    geometry: radius ? "roundRect" : "rect",
    name,
    position: { left, top, width, height },
    fill,
    line: line === "none" ? { style: "solid", fill: "none", width: 0 } : { style: "solid", fill: line, width: 1 },
    ...(radius ? { borderRadius: radius } : {}),
  });
}

function textBox(slide, text, { left, top, width, height, size = 24, color = C.ink, bold = false, align = "left", valign = "top", fill = "none", line = "none", radius = 0, name, autoFit = "shrinkText" }) {
  const shape = box(slide, { left, top, width, height, fill, line, radius, name });
  shape.text = text;
  shape.text.style = {
    typeface: FONT,
    fontSize: size,
    color,
    bold,
    alignment: align,
    verticalAlignment: valign,
    autoFit,
    insets: { top: 10, right: 12, bottom: 8, left: 12 },
  };
  return shape;
}

function title(slide, value, number) {
  textBox(slide, value, { left: 42, top: 30, width: 1130, height: 72, size: 48, bold: true, autoFit: "shrinkText" });
  textBox(slide, String(number).padStart(2, "0"), { left: 1180, top: 650, width: 58, height: 28, size: 18, color: C.muted, align: "right", valign: "bottom" });
}

function addNotes(slide, talkTrack, sources = []) {
  const block = [talkTrack, "", "[Sources]", ...sources.map((source) => `- ${source}`)].join("\n");
  slide.speakerNotes.textFrame.setText(block);
  slide.speakerNotes.setVisible(true);
}

async function addImage(slide, filePath, position, alt, fit = "cover") {
  const blob = new Uint8Array(await fs.readFile(filePath));
  return slide.images.add({ blob, contentType: "image/png", alt, fit, position });
}

function bullets(items) {
  return items.map((item) => `• ${item}`).join("\n");
}

function metric(slide, x, value, label, color = C.accentStrong) {
  textBox(slide, value, { left: x, top: 330, width: 340, height: 115, size: 64, bold: true, color, fill: C.panel, valign: "bottom" });
  textBox(slide, label, { left: x, top: 445, width: 340, height: 108, size: 24, fill: C.panel });
}

// 1. Cover
{
  const slide = presentation.slides.add();
  slide.background.fill = C.canvas;
  await addImage(slide, ASSETS.lung, { left: 710, top: 0, width: 570, height: 720 }, "Lung squamous H&E with virtual-stain overlays", "cover");
  box(slide, { left: 0, top: 0, width: 710, height: 720, fill: C.canvas });
  textBox(slide, "EMT-ViSTA", { left: 52, top: 90, width: 600, height: 90, size: 76, bold: true, autoFit: "none" });
  textBox(slide, "Virtual spatial staining of epithelial-mesenchymal plasticity from routine H&E", { left: 52, top: 205, width: 575, height: 170, size: 36, bold: true });
  textBox(slide, "A risk-aware, uncertainty-aware research pipeline", { left: 52, top: 430, width: 560, height: 70, size: 24, color: C.accentStrong, bold: true });
  textBox(slide, "Real public spatial data • Lung and colorectal holdouts • Honest negative baselines", { left: 52, top: 545, width: 580, height: 82, size: 22, color: C.muted });
  addNotes(slide, "Open with the project promise, then immediately frame it as a research and assay-triage system rather than a diagnostic product.", [
    "Local project output: data/processed/emt_virtual_spatial_staining_v1/resnet50/maps/CytAssist_FFPE_Human_Lung_Squamous_Cell_Carcinoma_he_overlay.png",
    "Dong A, Blanpain C. Nature Reviews Cancer (2026). https://www.nature.com/articles/s41568-025-00873-0",
  ]);
}

// 2. Problem
{
  const slide = presentation.slides.add();
  title(slide, "The molecular question is spatial, but the routine slide is not", 2);
  textBox(slide, "Routine H&E", { left: 55, top: 165, width: 500, height: 58, size: 30, bold: true });
  textBox(slide, bullets(["Ubiquitous in pathology", "Shows architecture and morphology", "Cheap enough for large cohorts", "Does not directly measure RNA programs"]), { left: 55, top: 238, width: 500, height: 300, size: 25, fill: C.panel });
  textBox(slide, "Spatial transcriptomics", { left: 725, top: 165, width: 500, height: 58, size: 30, bold: true });
  textBox(slide, bullets(["Measures spatial molecular programs", "Resolves CAF, TAM and hypoxia niches", "Costly and not routine", "Provides supervision for virtual staining"]), { left: 725, top: 238, width: 500, height: 300, size: 25, fill: C.paleBlue });
  box(slide, { left: 607, top: 245, width: 66, height: 66, fill: C.accentStrong, radius: 33 });
  textBox(slide, "?", { left: 607, top: 242, width: 66, height: 66, size: 40, color: "#FFFFFF", bold: true, align: "center", valign: "middle" });
  textBox(slide, "Can morphology nominate where these programs are active?", { left: 335, top: 585, width: 610, height: 54, size: 28, bold: true, align: "center" });
  addNotes(slide, "Explain the translation gap: H&E is routine, while spatial RNA is informative but expensive. The model tries to transfer supervised molecular information to routine morphology.", [
    "HEST-1k. NeurIPS Datasets and Benchmarks (2024). https://proceedings.neurips.cc/paper_files/paper/2024/file/60a899cc31f763be0bde781a75e04458-Paper-Datasets_and_Benchmarks_Track.pdf",
    "STPath. npj Digital Medicine (2025). https://www.nature.com/articles/s41746-025-02020-3",
  ]);
}

// 3. Questions and hypothesis
{
  const slide = presentation.slides.add();
  title(slide, "The hypothesis is useful only if it survives contamination controls", 3);
  textBox(slide, "Central hypothesis", { left: 55, top: 145, width: 350, height: 55, size: 28, bold: true, color: C.accentStrong });
  textBox(slide, "Multi-scale H&E morphology contains enough signal to predict spatial epithelial-mesenchymal plasticity and its microenvironment, provided stromal admixture and uncertainty are modeled explicitly.", { left: 55, top: 205, width: 1170, height: 135, size: 30, bold: true, fill: C.paleBlue });
  const qs = [
    ["Q1", "Can H&E predict epithelial, mesenchymal and partial-EMT programs?"],
    ["Q2", "Can it separate malignant plasticity from CAF-rich spot mixing?"],
    ["Q3", "Do local tissue neighborhoods improve prediction?"],
    ["Q4", "Does uncertainty identify predictions that should be rejected?"],
  ];
  qs.forEach(([q, value], index) => {
    const x = index % 2 === 0 ? 55 : 660;
    const y = index < 2 ? 390 : 520;
    textBox(slide, q, { left: x, top: y, width: 70, height: 64, size: 26, bold: true, color: "#FFFFFF", fill: C.accentStrong, align: "center", valign: "middle" });
    textBox(slide, value, { left: x + 85, top: y, width: 480, height: 78, size: 22, bold: true });
  });
  addNotes(slide, "State the hypothesis as a falsifiable proposition. The distinctive part is not H&E-to-score regression alone; it is separating malignant plasticity from stromal admixture and refusing uncertain predictions.", [
    "Local protocol: docs/emt_virtual_spatial_staining/detailed_project_plan.md",
    "Thompson EW et al. Nature Reviews Clinical Oncology (2025). https://www.nature.com/articles/s41571-025-01058-2",
  ]);
}

// 4. Contamination
{
  const slide = presentation.slides.add();
  title(slide, "Stromal signal can mimic tumour EMT", 4);
  await addImage(slide, ASSETS.crc, { left: 42, top: 130, width: 610, height: 500 }, "Colorectal H&E with prediction overlays", "contain");
  textBox(slide, "The confounder", { left: 700, top: 150, width: 480, height: 54, size: 30, bold: true, color: C.red });
  textBox(slide, "A Visium spot can mix malignant epithelial cells with fibroblasts, macrophages and ECM. That mixture can mimic partial EMT without proving tumour-cell plasticity.", { left: 700, top: 215, width: 490, height: 155, size: 25 });
  textBox(slide, "EMT-ViSTA response", { left: 700, top: 410, width: 480, height: 54, size: 30, bold: true, color: C.teal });
  textBox(slide, bullets(["Require epithelial + mesenchymal co-activity", "Predict stromal inflation separately", "Gate candidate partial EMT by malignant evidence", "Abstain when confidence is inadequate"]), { left: 700, top: 470, width: 490, height: 170, size: 22, fill: C.panel });
  addNotes(slide, "This is the core biological safety slide. Describe spot mixing and why an EMT score must be interpreted alongside epithelial evidence, CAF signals and stromal risk.", [
    "Local output: data/processed/emt_virtual_spatial_staining_v1/resnet50/maps/Visium_FFPE_Human_Intestinal_Cancer_he_overlay.png",
    "Dong A, Blanpain C. Nature Reviews Cancer (2026). https://www.nature.com/articles/s41568-025-00873-0",
  ]);
}

// 5. Data design
{
  const slide = presentation.slides.add();
  title(slide, "Five public cohorts created a real cross-cancer technical test", 5);
  textBox(slide, "Dataset-level separation prevents neighboring spots from leaking across train and test.", { left: 55, top: 135, width: 1160, height: 70, size: 27, color: C.muted });
  metric(slide, 55, "5", "aligned public cancer datasets", C.accentStrong);
  metric(slide, 470, "16,862", "molecularly scored spatial spots", C.teal);
  metric(slide, 885, "6,518", "held-out lung + colorectal spots", C.coral);
  textBox(slide, "TRAIN  Breast + prostate", { left: 55, top: 585, width: 355, height: 58, size: 22, bold: true, fill: C.paleBlue });
  textBox(slide, "VALIDATE  Ovarian", { left: 470, top: 585, width: 340, height: 58, size: 22, bold: true, fill: C.panel });
  textBox(slide, "TEST  Lung squamous + colorectal", { left: 870, top: 585, width: 355, height: 58, size: 22, bold: true, fill: C.paleCoral });
  addNotes(slide, "Clarify that these are dataset-level technical holdouts, not independent multi-patient clinical cohorts. The split is still stronger than random spot splitting because it avoids local leakage.", [
    "Local manifest: data/processed/emt_virtual_spatial_staining_v1/training_pair_manifest.json",
    "Local report: docs/emt_virtual_spatial_staining/implementation_report.md",
  ]);
}

// 6. Workflow
{
  const slide = presentation.slides.add();
  title(slide, "Molecular supervision becomes uncertainty-aware maps", 6);
  const steps = [
    ["1", "Pair H&E + spatial RNA"], ["2", "Score EMT + TME"], ["3", "Extract center + context"],
    ["4", "Add spatial neighbors"], ["5", "Fit multitask ensemble"], ["6", "Gate, abstain, export"],
  ];
  steps.forEach(([num, label], index) => {
    const x = 42 + index * 204;
    if (index < steps.length - 1) box(slide, { left: x + 158, top: 342, width: 74, height: 5, fill: C.rule });
  });
  steps.forEach(([num, label], index) => {
    const x = 42 + index * 204;
    box(slide, { left: x, top: 260, width: 160, height: 170, fill: index % 2 ? C.paleBlue : C.panel, line: C.rule });
    textBox(slide, num, { left: x + 48, top: 278, width: 64, height: 64, size: 34, bold: true, color: "#FFFFFF", fill: C.accentStrong, align: "center", valign: "middle", radius: 32 });
    textBox(slide, label, { left: x + 10, top: 355, width: 140, height: 64, size: 20, bold: true, align: "center", valign: "middle" });
  });
  textBox(slide, "Every stage produces inspectable TSV, JSON, image or GeoJSON outputs.", { left: 260, top: 520, width: 760, height: 65, size: 27, bold: true, align: "center" });
  addNotes(slide, "Walk left to right. Emphasize that the workflow is reproducible and modular: labels, embeddings, model, evaluation and exports can be run independently.", [
    "Local pipeline: scripts/run_emt_vista_pipeline.py",
    "Local package: src/emt_virtual_spatial_staining/",
  ]);
}

// 7. Method importance
{
  const slide = presentation.slides.add();
  title(slide, "Each method targets a specific failure mode", 7);
  const columns = [
    ["Biological validity", "Malignant-gated partial EMT\nSeparate CAF/TAM/ECM outputs\nStromal false-positive test", C.teal],
    ["Generalization", "Dataset-level holdouts\nCenter + context scales\nHandcrafted and ImageNet controls", C.accentStrong],
    ["Trustworthiness", "Bootstrap uncertainty\nCalibration and selective risk\nExplicit abstention", C.coral],
  ];
  columns.forEach(([head, body, color], index) => {
    const x = 42 + index * 412;
    box(slide, { left: x, top: 175, width: 370, height: 390, fill: C.panel });
    box(slide, { left: x, top: 175, width: 370, height: 12, fill: color });
    textBox(slide, head, { left: x + 20, top: 215, width: 330, height: 60, size: 28, bold: true });
    textBox(slide, body, { left: x + 20, top: 310, width: 330, height: 210, size: 24 });
  });
  textBox(slide, "The method is designed to fail visibly before it can overclaim.", { left: 200, top: 600, width: 880, height: 55, size: 30, bold: true, color: C.red, align: "center" });
  addNotes(slide, "Connect each method to a risk: stromal mixing, domain shift and false confidence. This is a useful interview slide because it explains why the methodology matters, not just what tools were used.", [
    "Local methods: docs/emt_virtual_spatial_staining/research_article_draft.md",
    "Towards robust foundation models for digital pathology. Nature Communications (2026). https://www.nature.com/articles/s41467-026-73923-2",
  ]);
}

// 8. Model
{
  const slide = presentation.slides.add();
  title(slide, "The v1 model stays interpretable before going deep", 8);
  const nodes = [
    [70, 205, 235, 100, "Center tile\n224 × 224"],
    [70, 385, 235, 100, "Context tile\n448 × 448"],
    [390, 295, 250, 120, "Image representation\nHandcrafted / ResNet / Phikon"],
    [720, 295, 225, 120, "Spatial neighbor\nmean features"],
    [1010, 250, 220, 210, "Bootstrap PCA + ridge\n\nMean = prediction\nSpread = uncertainty"],
  ];
  const connectors = [[305,255,390,335],[305,435,390,375],[640,355,720,355],[945,355,1010,355]];
  connectors.forEach(([x1,y1,x2,y2])=>box(slide,{left:x1,top:y1,width:x2-x1,height:5,fill:C.rule}));
  nodes.forEach(([x,y,w,h,label], index)=>textBox(slide,label,{left:x,top:y,width:w,height:h,size:index===4?23:24,bold:true,align:"center",valign:"middle",fill:index===4?C.paleBlue:C.panel,line:C.rule}));
  textBox(slide, "Why not start with a giant neural network? A transparent baseline reveals leakage, stain bias and weak labels before model complexity hides them.", { left: 170, top: 550, width: 940, height: 84, size: 25, bold: true, align: "center" });
  addNotes(slide, "Explain PCA plus ridge as an engineering baseline, not the final architecture. It tests whether the data contain a transferable signal before moving to GNNs or multimodal Transformers.", [
    "Local implementation: src/emt_virtual_spatial_staining/modeling.py",
    "Phikon-v2. https://arxiv.org/abs/2409.09173",
    "Bioptimus H-Optimus. https://www.bioptimus.com/h-optimus",
  ]);
}

// 9. Outputs
{
  const slide = presentation.slides.add();
  title(slide, "The output is a reviewable hypothesis map, not a hidden score", 9);
  await addImage(slide, ASSETS.lungMaps, { left: 42, top: 130, width: 720, height: 510 }, "Lung virtual stain coordinate maps", "contain");
  textBox(slide, "Each spot carries", { left: 810, top: 150, width: 390, height: 50, size: 29, bold: true });
  textBox(slide, bullets(["Eight program predictions", "Prediction uncertainty", "Malignant partial-EMT gate", "Stromal-inflation risk", "Abstain / review status", "GeoJSON hotspot export"]), { left: 810, top: 225, width: 390, height: 300, size: 24, fill: C.panel });
  textBox(slide, "Interpret together: signal + contamination + uncertainty + morphology", { left: 800, top: 560, width: 410, height: 78, size: 24, bold: true, color: C.accentStrong, align: "center" });
  addNotes(slide, "Describe the outputs as spatial review tools. A high partial-EMT probability means morphology resembles training regions under the label definition; it does not prove gene expression.", [
    "Local output: data/processed/emt_virtual_spatial_staining_v1/resnet50/maps/CytAssist_FFPE_Human_Lung_Squamous_Cell_Carcinoma_virtual_stains.png",
    "Local interpretation rule: docs/emt_virtual_spatial_staining/README.md",
  ]);
}

// 10. Benchmark chart
{
  const slide = presentation.slides.add();
  title(slide, "Held-out data rejected both image controls", 10);
  slide.charts.add("bar", {
    position: { left: 55, top: 165, width: 690, height: 430 },
    categories: ["Handcrafted", "ResNet50"],
    series: [{ name: "Median held-out Spearman", values: [0.014, -0.086], valuesFormatCode: "0.000", fill: C.accentStrong }],
    hasLegend: false,
    dataLabels: { showValue: true, position: "outEnd" },
    chartFill: C.canvas,
    chartLine: { style: "solid", width: 0, fill: C.canvas },
    plotAreaFill: { type: "none" },
    xAxis: { visible: true, deleted: false, textStyle: { typeface: FONT, fontSize: "18px", color: C.ink } },
    yAxis: { visible: true, deleted: false, numberFormatCode: "0.0", min: -0.1, max: 0.4, majorUnit: 0.1, majorGridlines: { style: "solid", width: 1, fill: C.panel }, textStyle: { typeface: FONT, fontSize: "15px", color: C.ink } },
    barOptions: { direction: "column", grouping: "clustered", gapWidth: 120 },
  });
  box(slide, { left: 100, top: 205, width: 590, height: 4, fill: C.red });
  textBox(slide, "Predefined gate = 0.35", { left: 470, top: 175, width: 230, height: 32, size: 18, color: C.red, bold: true, align: "right" });
  textBox(slide, "Result", { left: 810, top: 175, width: 390, height: 48, size: 29, bold: true });
  textBox(slide, "Neither representation generalized adequately to held-out lung and colorectal spots.", { left: 810, top: 235, width: 390, height: 120, size: 27, bold: true, fill: C.paleCoral });
  textBox(slide, "Useful signal", { left: 810, top: 405, width: 390, height: 48, size: 27, bold: true, color: C.teal });
  textBox(slide, "The handcrafted epithelial program reached 0.310, below the 0.35 gate. Pure-stroma false-positive control passed.", { left: 810, top: 460, width: 390, height: 130, size: 23 });
  addNotes(slide, "Pause here. The correct finding is that the controls failed. This protects the project from turning attractive maps into unsupported molecular claims.", [
    "Local benchmark: docs/emt_virtual_spatial_staining/backend_benchmark_summary.tsv",
    "Local gates: data/processed/emt_virtual_spatial_staining_v1/resnet50/emt_vista_go_no_go.tsv",
  ]);
}

// 11. Interpretation
{
  const slide = presentation.slides.add();
  title(slide, "A failed performance gate is a scientific result, not a software failure", 11);
  textBox(slide, "What the run establishes", { left: 55, top: 150, width: 535, height: 58, size: 30, bold: true, color: C.teal });
  textBox(slide, bullets(["End-to-end paired-data pipeline works", "Lung and CRC stay outside model fitting", "Uncertainty and safety metrics are reported", "Maps align correctly with H&E", "Weak baselines are honestly rejected"]), { left: 55, top: 220, width: 535, height: 310, size: 24, fill: C.panel });
  textBox(slide, "What the run does not establish", { left: 690, top: 150, width: 535, height: 58, size: 30, bold: true, color: C.red });
  textBox(slide, bullets(["H&E directly measures EMT", "Hotspots are true invasive fronts", "Performance transfers across patients", "The method is clinically actionable", "A negative baseline disproves the concept"]), { left: 690, top: 220, width: 535, height: 310, size: 24, fill: C.paleCoral });
  textBox(slide, "Conclusion: the framework is ready for a stronger experiment; the biomarker is not ready for use.", { left: 155, top: 585, width: 970, height: 65, size: 29, bold: true, align: "center" });
  addNotes(slide, "Use this slide to demonstrate research maturity. Separate engineering completion from biological validation and clinical readiness.", [
    "Local implementation report: docs/emt_virtual_spatial_staining/implementation_report.md",
    "Local research article draft: docs/emt_virtual_spatial_staining/research_article_draft.md",
  ]);
}

// 12. Cancer examples
{
  const slide = presentation.slides.add();
  title(slide, "Lung and colorectal slides expose different morphology domains", 12);
  await addImage(slide, ASSETS.lung, { left: 42, top: 135, width: 580, height: 470 }, "Lung squamous H&E overlay", "contain");
  await addImage(slide, ASSETS.crc, { left: 658, top: 135, width: 580, height: 470 }, "Colorectal H&E overlay", "contain");
  textBox(slide, "Lung squamous", { left: 42, top: 610, width: 580, height: 45, size: 24, bold: true, align: "center" });
  textBox(slide, "Colorectal / intestinal", { left: 658, top: 610, width: 580, height: 45, size: 24, bold: true, align: "center" });
  addNotes(slide, "Point out domain differences in tissue architecture and stain distribution. Cross-cancer holdout performance is intentionally hard and may require cancer-specific heads or larger heterogeneous training cohorts.", [
    "Local lung output: data/processed/emt_virtual_spatial_staining_v1/resnet50/maps/CytAssist_FFPE_Human_Lung_Squamous_Cell_Carcinoma_he_overlay.png",
    "Local colorectal output: data/processed/emt_virtual_spatial_staining_v1/resnet50/maps/Visium_FFPE_Human_Intestinal_Cancer_he_overlay.png",
  ]);
}

// 13. Pros and cons
{
  const slide = presentation.slides.add();
  title(slide, "The project is strong as a research platform and limited as a biomarker", 13);
  textBox(slide, "Advantages", { left: 55, top: 145, width: 540, height: 60, size: 31, bold: true, color: C.teal });
  textBox(slide, bullets(["Uses routine H&E and public paired data", "Targets biologically coherent programs", "Explicitly models stromal contamination", "Produces uncertainty and abstention", "Reproducible modular GitHub workflow", "Negative results remain visible"]), { left: 55, top: 220, width: 540, height: 350, size: 24, fill: C.panel });
  textBox(slide, "Limitations", { left: 685, top: 145, width: 540, height: 60, size: 31, bold: true, color: C.red });
  textBox(slide, bullets(["Small number of slides and patients", "Spatial spots remain mixed compartments", "CPU benchmarks sample spots", "Foundation model not benchmarked at scale", "No blinded pathologist labels", "No external institution or prospective endpoint"]), { left: 685, top: 220, width: 540, height: 350, size: 24, fill: C.paleCoral });
  addNotes(slide, "Present the trade-off clearly. The advantages justify continued research; the limitations define the next experiments and prevent clinical overclaiming.", ["Local student report: docs/emt_virtual_spatial_staining/student_project_report.md"]);
}

// 14. Highlights
{
  const slide = presentation.slides.add();
  title(slide, "Four design choices make EMT-ViSTA more than expression regression", 14);
  const points = [
    ["01", "Risk-aware partial EMT", "Joint epithelial/mesenchymal evidence plus a separate stromal-risk output."],
    ["02", "Spatial morphology", "Center, context and neighborhood representations model tissue organization."],
    ["03", "Selective prediction", "Calibration, ensemble spread and abstention define when the model should remain silent."],
    ["04", "Predefined falsification", "Release gates are fixed before interpretation, so a visually attractive map cannot override failed evidence."],
  ];
  points.forEach(([num, head, body], index) => {
    const x = index % 2 === 0 ? 55 : 660;
    const y = index < 2 ? 165 : 405;
    textBox(slide, num, { left: x, top: y, width: 90, height: 90, size: 38, bold: true, color: "#FFFFFF", fill: C.accentStrong, align: "center", valign: "middle" });
    textBox(slide, head, { left: x + 110, top: y, width: 450, height: 55, size: 27, bold: true });
    textBox(slide, body, { left: x + 110, top: y + 62, width: 450, height: 115, size: 22, color: C.muted });
  });
  addNotes(slide, "These are the project highlights to use in an interview. They communicate novelty without claiming state-of-the-art predictive accuracy.", ["Local interview guide: docs/emt_virtual_spatial_staining/interview_and_viva_guide.md"]);
}

// 15. Roadmap
{
  const slide = presentation.slides.add();
  title(slide, "The next study must move from slides to patients", 15);
  const milestones = [
    ["Now", "Full-scale Phikon / H-Optimus", "Run all spots on CUDA; compare under the same frozen gates."],
    ["Next", "Compartment-resolved labels", "Matched scRNA deconvolution plus two-pathologist region annotations."],
    ["Then", "Patient-level validation", "Leave-patient-out lung and CRC cohorts with confidence intervals."],
    ["Decisive", "External institution", "Untouched scanner, center and technology; prospective assay-triage endpoint."],
  ];
  box(slide, { left: 120, top: 350, width: 1040, height: 5, fill: C.rule });
  milestones.forEach(([phase, head, body], index) => {
    const x = 70 + index * 302;
    box(slide, { left: x + 105, top: 326, width: 52, height: 52, fill: C.accentStrong, radius: 26 });
    textBox(slide, phase, { left: x, top: 180, width: 260, height: 48, size: 22, color: C.accentStrong, bold: true, align: "center" });
    textBox(slide, head, { left: x, top: 235, width: 260, height: 72, size: 25, bold: true, align: "center" });
    textBox(slide, body, { left: x, top: 405, width: 260, height: 155, size: 21, align: "center", fill: C.panel });
  });
  textBox(slide, "Success means passing frozen external-validation gates, not reaching 100% software completion.", { left: 175, top: 610, width: 930, height: 52, size: 26, bold: true, color: C.red, align: "center" });
  addNotes(slide, "This is the execution roadmap. Emphasize patient-level units, pathology annotation and external centers as the real validation unlocks.", [
    "HEST-1k repository. https://github.com/mahmoodlab/hest",
    "Local project plan: docs/emt_virtual_spatial_staining/detailed_project_plan.md",
  ]);
}

// 16. Pitch and close
{
  const slide = presentation.slides.add();
  title(slide, "Interview pitch: a trustworthy virtual stain abstains", 16);
  textBox(slide, "30-second pitch", { left: 55, top: 145, width: 310, height: 50, size: 29, bold: true, color: C.accentStrong });
  textBox(slide, "I built EMT-ViSTA, a multimodal pipeline that learns spatial EMT and tumour-microenvironment programs from routine H&E using paired spatial transcriptomics. Its novelty is contamination-aware partial-EMT prediction with uncertainty and abstention. The first lung and colorectal holdouts rejected simple image baselines, which gave us an honest roadmap toward pathology-foundation, patient-level and pathologist-validated studies.", { left: 55, top: 215, width: 720, height: 315, size: 28, bold: true, fill: C.paleBlue });
  textBox(slide, "Remember", { left: 835, top: 170, width: 340, height: 50, size: 29, bold: true });
  textBox(slide, bullets(["Problem before tools", "Why each control matters", "Results without spin", "Limits define next experiments", "Maps nominate; assays validate"]), { left: 835, top: 245, width: 360, height: 250, size: 24, fill: C.panel });
  textBox(slide, "The strongest answer is not ‘the model worked.’ It is ‘the study design prevented us from claiming that it did.’", { left: 180, top: 580, width: 920, height: 70, size: 27, bold: true, color: C.red, align: "center" });
  addNotes(slide, "Close by resolving the opening tension. The project is valuable because it creates a rigorous bridge from routine pathology to spatial hypotheses while preserving the right to abstain.", [
    "Local interview guide: docs/emt_virtual_spatial_staining/interview_and_viva_guide.md",
    "Local implementation report: docs/emt_virtual_spatial_staining/implementation_report.md",
  ]);
}

await fs.mkdir(OUTPUT_DIR, { recursive: true });
await fs.mkdir(RENDER_DIR, { recursive: true });

for (let i = 0; i < presentation.slides.items.length; i += 1) {
  const slide = presentation.slides.items[i];
  const png = await presentation.export({ slide, format: "png", scale: 1 });
  await fs.writeFile(path.join(RENDER_DIR, `slide-${i + 1}.png`), new Uint8Array(await png.arrayBuffer()));
  const layout = await slide.export({ format: "layout" });
  await fs.writeFile(path.join(RENDER_DIR, `slide-${i + 1}.json`), JSON.stringify(layout, null, 2));
}

const montage = await presentation.export({ format: "png", montage: true, scale: 0.35 });
await fs.writeFile(path.join(OUTPUT_DIR, "EMT_ViSTA_Presentation_Montage.png"), new Uint8Array(await montage.arrayBuffer()));

const pptx = await PresentationFile.exportPptx(presentation);
await pptx.save(FINAL_PPTX);
console.log(`Created ${FINAL_PPTX}`);
