import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const OUT = path.join(ROOT, "deliverables", "crc_liver_invasion_front_presentation_pack");
const QA = path.join(ROOT, "tmp", "crc_liver_presentation_qa");
const FIG = path.join(ROOT, "data", "processed", "crc_liver_invasion_front_v1", "figures");

const C = {
  ink: "#111820",
  muted: "#5F6B73",
  line: "#CBD2D8",
  panel: "#F2F4F5",
  green: "#3E7650",
  greenPale: "#E8F1EB",
  rust: "#A7543B",
  rustPale: "#F7EBE6",
  purple: "#725494",
  blue: "#2B6F97",
  white: "#FFFFFF",
};

async function writeBlob(filePath, blob) {
  await fs.writeFile(filePath, new Uint8Array(await blob.arrayBuffer()));
}

async function imageBytes(filePath) {
  const bytes = await fs.readFile(filePath);
  return bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
}

function box(slide, x, y, w, h, fill, line = fill, radius = false) {
  return slide.shapes.add({
    geometry: radius ? "roundRect" : "rect",
    position: { left: x, top: y, width: w, height: h },
    fill,
    line: { style: "solid", fill: line, width: line === fill ? 0 : 1 },
    ...(radius ? { borderRadius: "rounded-md" } : {}),
  });
}

function textBox(slide, text, x, y, w, h, size = 24, color = C.ink, bold = false, align = "left") {
  const shape = slide.shapes.add({
    geometry: "textbox",
    position: { left: x, top: y, width: w, height: h },
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  shape.text = text;
  shape.text.style = {
    fontSize: size,
    typeface: "Arial",
    color,
    bold,
    alignment: align,
    verticalAlignment: "middle",
    autoFit: "shrinkText",
    wrap: "square",
    insets: { top: 0, right: 0, bottom: 0, left: 0 },
  };
  return shape;
}

function title(slide, claim, index) {
  textBox(slide, claim, 42, 28, 1120, 76, 38, C.ink, true);
  box(slide, 42, 112, 1196, 2, C.line);
  textBox(slide, String(index).padStart(2, "0"), 1180, 664, 58, 20, 13, C.muted, false, "right");
}

function notes(slide, body, sources = []) {
  const lines = [body, "", "[Sources]", ...sources.map((s) => `- ${s}`), "[/Sources]"];
  slide.speakerNotes.textFrame.setText(lines.join("\n"));
  slide.speakerNotes.setVisible(true);
}

async function addImage(slide, filename, x, y, w, h, alt, fit = "contain") {
  slide.images.add({
    blob: await imageBytes(path.join(FIG, filename)),
    contentType: "image/png",
    alt,
    fit,
    position: { left: x, top: y, width: w, height: h },
  });
}

function bulletList(slide, items, x, y, w, startIndex = 0, accent = C.green, step = 74, itemHeight = 66) {
  let top = y;
  items.forEach((item, i) => {
    box(slide, x, top + 7, 9, 9, accent);
    textBox(slide, item, x + 24, top, w - 24, itemHeight, 22, C.ink, false);
    top += step;
  });
}

async function main() {
  await fs.mkdir(OUT, { recursive: true });
  await fs.mkdir(QA, { recursive: true });
  const p = Presentation.create({ slideSize: { width: 1280, height: 720 } });

  // 1 - cover, adapted from Codex Grid slide 01.
  {
    const s = p.slides.add();
    s.background.fill = C.white;
    textBox(s, "SPATIAL ONCOLOGY | EXECUTED PUBLIC-DATA PROJECT", 42, 38, 720, 32, 15, C.green, true);
    textBox(s, "CRC Liver-Metastasis\nInvasion-Front Model", 42, 160, 1000, 210, 62, C.ink, true);
    textBox(s, "A compartment-aware heterogeneous graph of tumour-host contact, partial EMT and metastatic niche programs", 42, 425, 940, 90, 28, C.muted);
    box(s, 42, 592, 1196, 3, C.green);
    textBox(s, "GSE225857 | 22,260 Visium spots | leave-section-out validation | research use only", 42, 618, 1050, 32, 17, C.ink, true);
    notes(s, "Open by framing the model as an auditable hypothesis generator, not a clinical biomarker. The scientific object is the tumour-liver interface, not the whole slide.", [
      "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE225857",
      "https://doi.org/10.1126/sciadv.adf5464",
    ]);
  }

  // 2 - question and hypotheses.
  {
    const s = p.slides.add();
    title(s, "The interface may encode two different invasion ecosystems", 2);
    textBox(s, "CENTRAL QUESTION", 42, 143, 220, 28, 15, C.green, true);
    textBox(s, "Which malignant and host-cell programs distinguish the inferred tumour front from the malignant core?", 42, 180, 1120, 86, 34, C.ink, true);
    box(s, 42, 308, 570, 260, C.greenPale);
    textBox(s, "Host-contact front", 70, 338, 500, 42, 28, C.green, true);
    bulletList(s, ["Damaged hepatocyte context", "Macrophage and ECM-contact messages", "Direct tumour-liver adjacency"], 72, 398, 500, 0, C.green, 56, 48);
    box(s, 644, 308, 594, 260, C.rustPale);
    textBox(s, "Metabolically stressed core", 674, 338, 520, 42, 28, C.rust, true);
    bulletList(s, ["Partial EMT and hypoxia", "Glycolytic programs", "Fibroblast and ECM-rich neighborhoods"], 676, 398, 520, 0, C.rust, 56, 48);
    textBox(s, "Hypothesis: typed spatial context will transfer between liver sections better than unstructured spot features.", 42, 610, 1120, 44, 22, C.ink, true);
    notes(s, "Explain that the two ecosystems are competing, testable interpretations. The pipeline does not assume that pEMT must peak at the visible boundary.", [
      "https://pmc.ncbi.nlm.nih.gov/articles/PMC5680474/",
      "https://pmc.ncbi.nlm.nih.gov/articles/PMC7217855/",
    ]);
  }

  // 3 - evidence stack, adapted from Codex Grid slide 19.
  {
    const s = p.slides.add();
    title(s, "Public data support discovery, reference construction and audit", 3);
    textBox(s, "The model uses only openly documented assets and reports missing labels instead of inventing them.", 42, 132, 1130, 46, 22, C.muted);
    const items = [
      ["22,260", "Visium spots", "4 primary CRC + 2 liver metastasis sections", C.greenPale],
      ["56,072", "single cells", "Matched malignant, fibroblast, myeloid and endothelial pseudobulk reference", C.panel],
      ["48", "GeoMx AOIs", "Downloaded as orthogonal evidence; site labels remain unresolved", C.rustPale],
    ];
    items.forEach((it, i) => {
      const x = 42 + i * 400;
      box(s, x, 225, 370, 320, it[3]);
      textBox(s, it[0], x + 28, 260, 314, 78, 54, C.ink, true);
      textBox(s, it[1], x + 28, 348, 314, 38, 23, C.green, true);
      textBox(s, it[2], x + 28, 406, 314, 104, 20, C.ink);
    });
    textBox(s, "Important: hepatocytes were absent from the processed scRNA clusters and were not imputed into the matched reference.", 42, 590, 1150, 44, 20, C.rust, true);
    notes(s, "Use this slide to demonstrate evidence discipline. The GeoMx table was retained but not assigned primary/metastasis labels because its public count file lacks a machine-readable annotation table.", [
      "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE225857",
      "https://doi.org/10.5281/zenodo.7520789",
      "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE224235",
    ]);
  }

  // 4 - workflow image.
  {
    const s = p.slides.add();
    title(s, "Compartment identity is preserved end to end", 4);
    await addImage(s, "workflow_overview.png", 60, 135, 1160, 500, "Workflow from public spatial data through scoring, interface construction, typed graph modeling and validation");
    notes(s, "Walk left to right. Emphasize section-wise normalization, CRC-lineage gating, signed graph distance, relation-specific messages, held-out-section testing, and a pathology review queue.", [
      "Repository pipeline: scripts/run_crc_liver_invasion_front.py",
      "https://doi.org/10.1126/sciadv.adf5464",
    ]);
  }

  // 5 - interface definition.
  {
    const s = p.slides.add();
    title(s, "A signed 300 micrometre coordinate makes the boundary testable", 5);
    const xs = [88, 330, 572, 814, 1056];
    const labels = ["Tumour core", "Tumour front", "Boundary", "Liver front", "Liver parenchyma"];
    const fills = [C.rustPale, "#F2D8CE", C.ink, C.greenPale, "#D3E5D8"];
    xs.forEach((x, i) => {
      box(s, x, 270, 164, 128, fills[i]);
      textBox(s, labels[i], x + 12, 290, 140, 82, 21, i === 2 ? C.white : C.ink, true, "center");
      if (i < xs.length - 1) textBox(s, "→", x + 176, 309, 48, 40, 30, C.muted, true, "center");
    });
    textBox(s, "-3 hops", 330, 428, 164, 30, 18, C.rust, true, "center");
    textBox(s, "0", 572, 428, 164, 30, 18, C.ink, true, "center");
    textBox(s, "+3 hops", 814, 428, 164, 30, 18, C.green, true, "center");
    bulletList(s, ["Boundary seeds require high-confidence malignant-hepatocyte contact.", "Primary CRC sections are explicitly marked not applicable.", "pEMT requires epithelial, mesenchymal and CRC-lineage support; fibroblast-high mixtures are flagged."], 84, 500, 1110, 0, C.green);
    notes(s, "Three graph hops approximate 300 micrometres. This mirrors recent pathologist-reviewed CRLM spatial work but remains a sensitivity-tested approximation.", [
      "https://www.nature.com/articles/s41416-026-03567-y",
      "https://pmc.ncbi.nlm.nih.gov/articles/PMC5680474/",
    ]);
  }

  // 6 - spatial maps.
  {
    const s = p.slides.add();
    title(s, "Both liver sections yield coherent but weak-label interfaces", 6);
    await addImage(s, "interface_maps.png", 42, 125, 860, 520, "Spatial compartment and signed distance maps for liver metastasis sections L1 and L2");
    textBox(s, "L1", 950, 152, 120, 42, 28, C.green, true);
    textBox(s, "303 boundary pairs\n1,562 interface spots\n861 tumour-front spots", 950, 206, 250, 125, 22, C.ink);
    textBox(s, "L2", 950, 378, 120, 42, 28, C.green, true);
    textBox(s, "452 boundary pairs\n2,597 interface spots\n1,130 tumour-front spots", 950, 432, 250, 125, 22, C.ink);
    textBox(s, "Both: mixed or uncertain HGP proxy", 950, 595, 260, 32, 18, C.rust, true);
    notes(s, "Do not call these pathologist-confirmed invasive fronts. They are reproducible marker-plus-spatial candidates intended to organize human review and downstream experiments.", [
      "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE225857",
      "https://pmc.ncbi.nlm.nih.gov/articles/PMC6611753/",
    ]);
  }

  // 7 - graph.
  {
    const s = p.slides.add();
    title(s, "Typed edges retain the biological meaning of neighbourhoods", 7);
    await addImage(s, "heterograph_interface_excerpt.png", 42, 130, 1196, 510, "Heterogeneous tumour-liver interface graph excerpt and relation counts");
    notes(s, "Physical neighbours, compartment contacts, gradient directions and ligand-receptor opportunities are distinct edge types. Ligand-receptor edges require positive expression above the within-section 80th percentile and are interface-local.", [
      "Repository module: src/crc_liver_invasion_front/graph.py",
      "https://doi.org/10.1126/sciadv.adf5464",
    ]);
  }

  // 8 - gradients.
  {
    const s = p.slides.add();
    title(s, "The inferred front is host-contact rich, not uniformly pEMT high", 8);
    await addImage(s, "interface_gradient_profiles.png", 42, 125, 820, 520, "Program profiles across signed tumour-to-liver distance bands");
    textBox(s, "+0.060", 918, 160, 260, 62, 46, C.green, true);
    textBox(s, "damaged-hepatocyte\nfront minus core", 918, 228, 260, 68, 20, C.ink);
    box(s, 918, 320, 276, 2, C.line);
    textBox(s, "-0.117", 918, 350, 260, 62, 46, C.rust, true);
    textBox(s, "ECM remodelling\nfront minus core", 918, 418, 260, 68, 20, C.ink);
    textBox(s, "pEMT, glycolysis and hypoxia also trend toward the inferred malignant core.", 918, 520, 270, 105, 20, C.muted, true);
    notes(s, "This is the most interesting negative result. A simplistic invasive-ring story is not supported. Alternatives include a host-contact front around a stressed core, section-specific architecture, and residual spot mixing.", [
      "Generated table: data/processed/crc_liver_invasion_front_v1/front_vs_core_statistics.tsv",
      "https://www.nature.com/articles/s41416-026-03567-y",
    ]);
  }

  // 9 - validation metrics.
  {
    const s = p.slides.add();
    title(s, "Held-out sections recover transferable weak-label structure", 9);
    textBox(s, "0.908", 54, 174, 280, 82, 58, C.green, true);
    textBox(s, "ROC AUC", 54, 262, 280, 34, 21, C.ink, true);
    textBox(s, "0.857", 354, 174, 280, 82, 58, C.blue, true);
    textBox(s, "Average precision", 354, 262, 280, 34, 21, C.ink, true);
    textBox(s, "0.831", 654, 174, 280, 82, 58, C.purple, true);
    textBox(s, "Balanced accuracy", 654, 262, 280, 34, 21, C.ink, true);
    textBox(s, "0.020", 954, 174, 280, 82, 58, C.rust, true);
    textBox(s, "Permutation P", 954, 262, 280, 34, 21, C.ink, true);
    await addImage(s, "interface_model_interpretation.png", 42, 330, 760, 310, "Coefficient and ablation interpretation for the typed message-passing model");
    bulletList(s, ["2 held-out liver sections", "3,439 malignant spots", "1,290 tumour-front spots", "48 local and relation-aware features", "50 within-section permutations"], 850, 340, 350, 0, C.purple);
    notes(s, "AUC measures recovery of an inferred spatial label across two sections. Boundary-defining cross-interface messages are excluded from model features to reduce label leakage.", [
      "Generated metrics: data/processed/crc_liver_invasion_front_v1/model_metrics.json",
      "Repository module: src/crc_liver_invasion_front/modeling.py",
    ]);
  }

  // 10 - interpretation.
  {
    const s = p.slides.add();
    title(s, "The model prioritizes a host-injury axis for experimental follow-up", 10);
    box(s, 42, 150, 580, 440, C.greenPale);
    textBox(s, "FRONT-ASSOCIATED", 72, 182, 500, 30, 16, C.green, true);
    textBox(s, "+0.809", 72, 235, 180, 60, 44, C.green, true);
    textBox(s, "Neighbour damaged-hepatocyte program", 260, 242, 320, 48, 22, C.ink, true);
    textBox(s, "+0.457", 72, 325, 180, 60, 44, C.green, true);
    textBox(s, "Neighbour MRC1/CCL18-like macrophage program", 260, 325, 320, 68, 22, C.ink, true);
    textBox(s, "+0.446", 72, 425, 180, 60, 44, C.green, true);
    textBox(s, "Contact-neighbour ECM program", 260, 432, 320, 48, 22, C.ink, true);
    box(s, 650, 150, 588, 440, C.rustPale);
    textBox(s, "CORE-ASSOCIATED", 680, 182, 500, 30, 16, C.rust, true);
    textBox(s, "-0.832", 680, 235, 180, 60, 44, C.rust, true);
    textBox(s, "Neighbour hypoxia program", 868, 242, 320, 48, 22, C.ink, true);
    textBox(s, "-0.745", 680, 325, 180, 60, 44, C.rust, true);
    textBox(s, "Neighbour partial-EMT program", 868, 332, 320, 48, 22, C.ink, true);
    textBox(s, "-0.641", 680, 425, 180, 60, 44, C.rust, true);
    textBox(s, "Neighbour glycolysis program", 868, 432, 320, 48, 22, C.ink, true);
    textBox(s, "Predictive coefficients generate mechanisms to test; they are not causal effects or drug recommendations.", 42, 620, 1180, 40, 21, C.ink, true);
    notes(s, "Frame the result as a ranked experimental agenda: hepatocyte injury and macrophage contact at the front versus pEMT, hypoxia and glycolysis in the core.", [
      "Generated table: data/processed/crc_liver_invasion_front_v1/model_feature_importance.tsv",
      "https://www.nature.com/articles/s41416-026-03567-y",
    ]);
  }

  // 11 - strengths and limits.
  {
    const s = p.slides.add();
    title(s, "Interpretability is the main strength; label quality is the main constraint", 11);
    textBox(s, "Advantages", 42, 150, 540, 42, 28, C.green, true);
    bulletList(s, ["Separates malignant pEMT from stromal mesenchymal RNA", "Preserves spatial direction and edge semantics", "Uses held-out sections, permutation and ablation", "Reports unavailable metadata and reference compartments"], 48, 215, 540, 0, C.green);
    textBox(s, "Limitations", 650, 150, 540, 42, 28, C.rust, true);
    bulletList(s, ["Only two liver-metastasis sections", "Weak interfaces and HGP proxies", "Visium spots mix several cell types", "Co-expression edges do not prove signalling", "No survival, treatment-response or causal endpoint"], 656, 215, 540, 0, C.rust);
    textBox(s, "Best use: auditable hypothesis generation and pathologist-guided experiment design.", 42, 632, 1120, 36, 23, C.ink, true);
    notes(s, "This slide is important in an interview. State the limitation before being asked, then explain how each next experiment addresses a specific uncertainty.", [
      "https://pmc.ncbi.nlm.nih.gov/articles/PMC6611753/",
      "Repository report: docs/crc_liver_invasion_front/executed_project_report.md",
    ]);
  }

  // 12 - action-oriented close.
  {
    const s = p.slides.add();
    title(s, "Next: convert weak spatial labels into validated mechanism", 12);
    const steps = [
      ["1", "Pathology", "Trace tumour-liver boundaries and score consensus HGP percentages"],
      ["2", "Protein", "Validate EPCAM/KRT20, VIM/LAMC2, MRC1/CCL18, FAP/POSTN, CD31 and CA9/GLUT1"],
      ["3", "Perturb", "Test CCL18-PITPNM3, SPP1-CD44/ITGAV, TGF-beta and CXCL12-CXCR4 axes"],
      ["4", "Generalize", "Repeat in independent CRLM cohorts with patient-level endpoints"],
    ];
    steps.forEach((st, i) => {
      const y = 152 + i * 112;
      textBox(s, st[0], 48, y, 62, 62, 38, i < 2 ? C.green : C.purple, true, "center");
      box(s, 126, y + 30, 100, 2, C.line);
      textBox(s, st[1], 250, y, 180, 58, 26, C.ink, true);
      textBox(s, st[2], 448, y, 760, 64, 21, C.muted);
    });
    textBox(s, "Pitch: a reproducible map of where malignant plasticity meets liver biology, built to tell us what to validate next.", 42, 620, 1160, 45, 24, C.ink, true);
    notes(s, "Close with the decision enabled by the project: it identifies what regions, cell states and interaction axes deserve pathology review and perturbation, while keeping unsupported clinical claims out of scope.", [
      "https://pmc.ncbi.nlm.nih.gov/articles/PMC5680474/",
      "https://www.nature.com/articles/s41416-026-03567-y",
      "Repository workflow: scripts/run_crc_liver_invasion_front.py",
    ]);
  }

  for (const [i, s] of p.slides.items.entries()) {
    const stem = `slide-${String(i + 1).padStart(2, "0")}`;
    await writeBlob(path.join(QA, `${stem}.png`), await p.export({ slide: s, format: "png", scale: 1 }));
    await fs.writeFile(path.join(QA, `${stem}.layout.json`), await (await s.export({ format: "layout" })).text());
  }
  await writeBlob(path.join(QA, "deck-montage.webp"), await p.export({ format: "webp", montage: true, scale: 1 }));
  const pptx = await PresentationFile.exportPptx(p);
  await pptx.save(path.join(OUT, "CRC_Liver_Invasion_Front_Interpretation_Presentation.pptx"));
}

main().catch((err) => {
  console.error(err);
  process.exitCode = 1;
});
