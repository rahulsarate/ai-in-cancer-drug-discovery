import fs from "node:fs/promises";
import path from "node:path";
import os from "node:os";
import { Presentation, PresentationFile } from "file:///C:/Users/HP/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs";

const ROOT = process.cwd();
const DOCS = path.join(ROOT, "docs", "tnbc_digital_twin_emt_plasticity");
const NOVELTY = path.join(DOCS, "novelty_positioning");
const ASSETS = path.join(NOVELTY, "assets");
const OUT = path.join(NOVELTY, "tnbc_emt_digital_twin_novelty_deck.pptx");
const SCRATCH = path.join(os.tmpdir(), "codex-presentations", "tnbc-novelty-positioning");
const PREVIEW = path.join(SCRATCH, "preview");
const LAYOUT = path.join(SCRATCH, "layout");

const slideW = 1280;
const slideH = 720;
const page = { left: 64, top: 48, width: 1152, height: 624 };

const colors = {
  ink: "#14213D",
  body: "#334155",
  muted: "#64748B",
  bg: "#F8FAFC",
  panel: "#FFFFFF",
  teal: "#2A9D8F",
  gold: "#E9C46A",
  coral: "#E76F51",
  purple: "#6A4C93",
  red: "#D62828",
  blue: "#247BA0",
  line: "#CBD5E1",
};

async function writeBlob(filePath, blob) {
  await fs.writeFile(filePath, new Uint8Array(await blob.arrayBuffer()));
}

function addText(slide, text, position, style = {}) {
  const box = slide.shapes.add({
    geometry: "textbox",
    position,
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  box.text = text;
  box.text.style = {
    fontSize: style.fontSize ?? 20,
    bold: style.bold ?? false,
    color: style.color ?? colors.body,
  };
  return box;
}

function addTitle(slide, title, subtitle = "") {
  addText(slide, "TNBC EMT DIGITAL TWIN", { left: page.left, top: 34, width: 360, height: 24 }, {
    fontSize: 12,
    bold: true,
    color: colors.teal,
  });
  addText(slide, title, { left: page.left, top: 66, width: 850, height: 70 }, {
    fontSize: 34,
    bold: true,
    color: colors.ink,
  });
  if (subtitle) {
    addText(slide, subtitle, { left: page.left, top: 124, width: 900, height: 44 }, {
      fontSize: 18,
      color: colors.muted,
    });
  }
}

function addFooter(slide, text = "Research prototype: not clinical decision support") {
  slide.shapes.add({
    geometry: "line",
    position: { left: page.left, top: 678, width: page.width, height: 0 },
    line: { style: "solid", fill: colors.line, width: 1 },
  });
  addText(slide, text, { left: page.left, top: 686, width: page.width, height: 18 }, {
    fontSize: 10,
    color: colors.muted,
  });
}

function addCard(slide, title, body, x, y, w, h, accent = colors.teal) {
  slide.shapes.add({
    geometry: "roundRect",
    position: { left: x, top: y, width: w, height: h },
    fill: colors.panel,
    line: { style: "solid", fill: colors.line, width: 1 },
    borderRadius: 12,
  });
  slide.shapes.add({
    geometry: "rect",
    position: { left: x, top: y, width: 8, height: h },
    fill: accent,
    line: { style: "solid", fill: accent, width: 0 },
  });
  addText(slide, title, { left: x + 22, top: y + 16, width: w - 36, height: 28 }, {
    fontSize: 18,
    bold: true,
    color: colors.ink,
  });
  addText(slide, body, { left: x + 22, top: y + 52, width: w - 36, height: h - 60 }, {
    fontSize: 14,
    color: colors.body,
  });
}

async function addImage(slide, fileName, position, alt) {
  const blob = await fs.readFile(path.join(ASSETS, fileName));
  slide.images.add({
    blob,
    contentType: "image/png",
    alt,
    fit: "contain",
    position,
  });
}

function addBullets(slide, bullets, x, y, w, fontSize = 18, gap = 42) {
  bullets.forEach((bullet, idx) => {
    const top = y + idx * gap;
    slide.shapes.add({
      geometry: "ellipse",
      position: { left: x, top: top + 8, width: 10, height: 10 },
      fill: idx % 2 === 0 ? colors.teal : colors.coral,
      line: { style: "solid", fill: "none", width: 0 },
    });
    addText(slide, bullet, { left: x + 22, top, width: w - 22, height: gap }, {
      fontSize,
      color: colors.body,
    });
  });
}

async function buildDeck() {
  await fs.mkdir(path.dirname(OUT), { recursive: true });
  await fs.mkdir(PREVIEW, { recursive: true });
  await fs.mkdir(LAYOUT, { recursive: true });

  const deck = Presentation.create({ slideSize: { width: slideW, height: slideH } });

  // 1 Cover
  {
    const slide = deck.slides.add();
    slide.background.fill = colors.bg;
    slide.shapes.add({ geometry: "rect", position: { left: 0, top: 0, width: 26, height: slideH }, fill: colors.teal, line: { style: "solid", fill: colors.teal, width: 0 } });
    addText(slide, "NOVELTY POSITIONING", { left: 78, top: 72, width: 440, height: 28 }, { fontSize: 14, bold: true, color: colors.teal });
    addText(slide, "Digital Twin of EMT Plasticity Under Therapy", { left: 78, top: 130, width: 720, height: 116 }, { fontSize: 48, bold: true, color: colors.ink });
    addText(slide, "How this TNBC NAC project differs from current literature, digital-twin reports, and EMT/persister resources", { left: 82, top: 270, width: 660, height: 74 }, { fontSize: 22, color: colors.body });
    await addImage(slide, "four_state_digital_twin_diagram.png", { left: 770, top: 100, width: 430, height: 360 }, "Four-state EMT plasticity digital twin diagram");
    addCard(slide, "Thesis", "Novelty is not one isolated algorithm. It is the integration of dynamic EMT/persister state biology, curated public TNBC NAC labels, cross-platform validation, and clinician-safe reporting.", 82, 470, 1030, 120, colors.red);
    addFooter(slide, "Novelty package built from locked project outputs and verified comparator literature");
  }

  // 2 Landscape
  {
    const slide = deck.slides.add();
    slide.background.fill = colors.bg;
    addTitle(slide, "Current Landscape: Many Pieces, Few Integrated Workflows", "The literature covers endpoints, biology, imaging twins, and governance, but usually in separate silos.");
    addCard(slide, "Clinical endpoint literature", "pCR, residual disease, and RCB explain why response matters, but not how surviving cells adapt.", 74, 200, 260, 130, colors.blue);
    addCard(slide, "EMP and persister biology", "Reviews define EMT plasticity and drug-tolerant persister concepts, often without a TNBC NAC validation workflow.", 360, 200, 280, 130, colors.teal);
    addCard(slide, "MRI-based TNBC twins", "Closest comparator: strong for imaging-calibrated tumor-growth response, less focused on transcriptomic EMT/persister states.", 666, 200, 280, 130, colors.gold);
    addCard(slide, "Oncology DT/QSP reviews", "Useful credibility and simulation frameworks, but broad and rarely label-curated TNBC NAC state pipelines.", 972, 200, 234, 130, colors.purple);
    addText(slide, "Gap: A governed transcriptomic state twin that explains therapy-induced EMT/persister biology under TNBC NAC.", { left: 96, top: 420, width: 980, height: 64 }, { fontSize: 30, bold: true, color: colors.ink });
    addFooter(slide, "Comparators: pCR/RCB literature; EMP/DTP reviews; MRI-based TNBC NAC DTs; QSP/IO and oncology DT reviews");
  }

  // 3 Heatmap
  {
    const slide = deck.slides.add();
    slide.background.fill = colors.bg;
    addTitle(slide, "Novelty Matrix", "This project’s distinctiveness is the complete row: state biology, validation, and governance together.");
    await addImage(slide, "novelty_matrix_heatmap.png", { left: 70, top: 160, width: 1120, height: 470 }, "Novelty matrix heatmap");
    addFooter(slide, "Scale: absent, partial, strong coverage. Matrix is qualitative positioning, not a claim of superiority.");
  }

  // 4 Positioning Map
  {
    const slide = deck.slides.add();
    slide.background.fill = colors.bg;
    addTitle(slide, "Where the Project Sits", "Closest to TNBC digital-twin work, but shifted toward transcriptomic state biology and report governance.");
    await addImage(slide, "novelty_positioning_map.png", { left: 98, top: 154, width: 760, height: 500 }, "Novelty positioning map");
    addCard(slide, "Interpretation", "MRI-based TNBC twins are the closest cousin. This project complements them by explaining molecular state trajectories: E, H, M, P, persister/niche programs, label uncertainty, and platform shift.", 885, 210, 290, 260, colors.red);
    addFooter(slide);
  }

  // 5 Evidence stack
  {
    const slide = deck.slides.add();
    slide.background.fill = colors.bg;
    addTitle(slide, "Evidence Stack", "The project converts disconnected public resources into a governed digital-twin workflow.");
    await addImage(slide, "evidence_stack.png", { left: 62, top: 158, width: 1110, height: 430 }, "Evidence stack chart");
    addFooter(slide, "Stack layers: endpoint curation, bulk signatures, longitudinal dynamics, scRNA persister layer, validation governance, clinician-style reporting");
  }

  // 6 Similar vs different
  {
    const slide = deck.slides.add();
    slide.background.fill = colors.bg;
    addTitle(slide, "Similar, But Not the Same", "The project reuses trusted ideas but recombines them around a different scientific question.");
    addCard(slide, "MRI-based TNBC NAC digital twins", "Similar: patient-specific NAC twins.\nDifferent: this project is transcriptomic EMT/persister-state centered, not imaging growth centered.", 78, 184, 520, 118, colors.gold);
    addCard(slide, "EMP / DTP reviews", "Similar: same biology of plasticity and survival.\nDifferent: this project operationalizes biology in scored TNBC NAC cohorts.", 650, 184, 520, 118, colors.teal);
    addCard(slide, "QSP / IO virtual patients", "Similar: mechanistic simulation philosophy.\nDifferent: this project uses public TNBC NAC transcriptomics, label curation, and report governance.", 78, 340, 520, 132, colors.purple);
    addCard(slide, "pCR / RCB literature", "Similar: same endpoint motivation.\nDifferent: this project models survival-state mechanisms, not endpoint alone.", 650, 340, 520, 132, colors.blue);
    addText(slide, "Novelty claim: complementary to current work, not a replacement for it.", { left: 166, top: 546, width: 930, height: 44 }, { fontSize: 28, bold: true, color: colors.red });
    addFooter(slide);
  }

  // 7 Eight novelty claims
  {
    const slide = deck.slides.add();
    slide.background.fill = colors.bg;
    addTitle(slide, "Eight Novel Contributions", "These are the defensible novelty claims for a report, viva, proposal, or manuscript introduction.");
    addBullets(slide, [
      "TNBC NAC-specific but state-centered, not only endpoint-centered.",
      "EMT modeled as dynamic E/H/M/P state space.",
      "Persister separated into tumor-cell, stress-tolerance, and niche layers.",
      "Transition priors calibrated from paired pre/post-NAC TNBC samples.",
      "Public response labels audited and curated before sensitivity modeling.",
      "Same-platform and cross-platform validation kept separate.",
      "Single-cell ambiguity preserved instead of overconfident cell labels.",
      "Clinician-style reporting forbids treatment recommendations and foregrounds uncertainty.",
    ], 92, 178, 1050, 17, 48);
    addFooter(slide);
  }

  // 8 Clinical value
  {
    const slide = deck.slides.add();
    slide.background.fill = colors.bg;
    addTitle(slide, "Why Clinicians Should Care", "The project is not a prescriber; it is a research-grade explanation layer for residual-risk biology.");
    addCard(slide, "Molecular review prompt", "Shows whether residual-risk biology appears hypoxic, AXL/TAM-high, YAP/TAZ-high, stromal-supported, immune-contextual, or persister-enriched.", 86, 190, 330, 180, colors.teal);
    addCard(slide, "Uncertainty first", "Reports cohort percentiles, bootstrap bands, platform shifts, and label caveats before interpretation.", 470, 190, 330, 180, colors.gold);
    addCard(slide, "Post-NAC research triage", "Helps prioritize specimens for deeper profiling, spatial assays, single-cell work, or trial hypothesis generation.", 854, 190, 330, 180, colors.coral);
    addText(slide, "Clinical boundary: no treatment recommendation, no individual survival claim, no clinical deployment without prospective validation.", { left: 116, top: 470, width: 980, height: 80 }, { fontSize: 26, bold: true, color: colors.red });
    addFooter(slide);
  }

  // 9 Research value
  {
    const slide = deck.slides.add();
    slide.background.fill = colors.bg;
    addTitle(slide, "Why Researchers Should Care", "It creates a reusable scaffold for asking better residual-disease questions.");
    addBullets(slide, [
      "Benchmark EMT, TME, resistance, and persister signatures across public TNBC NAC cohorts.",
      "Test how endpoint definitions change model behavior.",
      "Compare raw, percentile, z-score, and quantile cross-platform calibration.",
      "Connect bulk response models with longitudinal therapy shifts and single-cell persister biology.",
      "Use ambiguity as data: unresolved compartments become follow-up targets, not hidden errors.",
    ], 90, 190, 760, 21, 62);
    slide.charts.add("bar", {
      position: { left: 860, top: 210, width: 300, height: 280 },
      categories: ["EMT", "TME", "Twin", "Combined"],
      title: "GSE163882 AUROC x100",
      titleTextStyle: { fontSize: 12 },
      series: [{ name: "GSE163882 AUROC x100", values: [43.4, 64.3, 58.4, 64.9], fill: colors.teal }],
      hasLegend: false,
      dataLabels: { showValue: true, position: "outEnd" },
      yAxis: { minimumScale: 0, maximumScale: 100, majorGridlines: { style: "solid", fill: colors.line, width: 1 } },
    });
    addText(slide, "External validation: combined state + TME features outperform EMT-only.", { left: 850, top: 500, width: 330, height: 52 }, { fontSize: 16, color: colors.body });
    addFooter(slide);
  }

  // 10 Creative roadmap
  {
    const slide = deck.slides.add();
    slide.background.fill = colors.bg;
    addTitle(slide, "Creative Roadmap", "The next-generation version becomes a multimodal residual-disease twin.");
    const x0 = 88;
    const y0 = 220;
    const gap = 168;
    const items = [
      ["Time-lapse", "early on-treatment velocity"],
      ["Spatial", "niche distance and immune exclusion"],
      ["Perturbation", "AXL/TAM, TGF-beta, hypoxia, ferroptosis"],
      ["Explant", "organoid/PDX calibration"],
      ["Trial enrichment", "residual-disease subgroups"],
      ["Uncertainty UI", "confidence before claims"],
    ];
    items.forEach((it, i) => {
      const x = x0 + (i % 3) * 370;
      const y = y0 + Math.floor(i / 3) * gap;
      addCard(slide, it[0], it[1], x, y, 300, 110, [colors.teal, colors.gold, colors.coral, colors.purple, colors.blue, colors.red][i]);
    });
    addFooter(slide, "Roadmap is prospective: all clinical use requires locked assays and prospective validation");
  }

  // 11 Takeaway
  {
    const slide = deck.slides.add();
    slide.background.fill = colors.bg;
    addTitle(slide, "Takeaway", "Novelty is a governed bridge from endpoint prediction to state-aware residual biology.");
    addText(slide, "Similar to current work:", { left: 88, top: 195, width: 420, height: 34 }, { fontSize: 24, bold: true, color: colors.ink });
    addBullets(slide, [
      "Uses accepted pCR/RD/RCB clinical logic.",
      "Builds on EMT plasticity and persister biology.",
      "Shares digital-twin goals of simulation, validation, and decision support.",
    ], 98, 245, 500, 18, 54);
    addText(slide, "Different from current work:", { left: 670, top: 195, width: 420, height: 34 }, { fontSize: 24, bold: true, color: colors.ink });
    addBullets(slide, [
      "Centers transcriptomic E/H/M/P state dynamics in TNBC NAC.",
      "Includes label curation, platform-aware validation, and scRNA ambiguity review.",
      "Outputs clinician-style research reports with hard safety boundaries.",
    ], 680, 245, 500, 18, 54);
    addCard(slide, "Final claim", "A computationally complete research prototype for EMT/persister-state interpretation, not a clinically deployed treatment-selection model.", 180, 530, 920, 84, colors.red);
    addFooter(slide, "Main deck sources are listed in the novelty positioning report.");
  }

  for (const [index, slide] of deck.slides.items.entries()) {
    const stem = `slide-${String(index + 1).padStart(2, "0")}`;
    const png = await deck.export({ slide, format: "png", scale: 1 });
    await writeBlob(path.join(PREVIEW, `${stem}.png`), png);
    const layout = await slide.export({ format: "layout" });
    await fs.writeFile(path.join(LAYOUT, `${stem}.layout.json`), await layout.text());
  }
  const montage = await deck.export({ format: "webp", montage: true, scale: 1 });
  await writeBlob(path.join(PREVIEW, "deck_montage.webp"), montage);
  const pptx = await PresentationFile.exportPptx(deck);
  await pptx.save(OUT);
  console.log(`wrote ${OUT}`);
  console.log(`preview ${PREVIEW}`);
}

buildDeck().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
