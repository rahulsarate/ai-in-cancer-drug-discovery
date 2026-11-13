from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "docs" / "tnbc_digital_twin_emt_plasticity" / "novelty_positioning"
ASSET_DIR = OUT_DIR / "assets"


CAPABILITIES = [
    "TNBC NAC",
    "EMT/EMP states",
    "Persister biology",
    "Longitudinal shift",
    "Single-cell layer",
    "Label curation",
    "Platform-aware validation",
    "Clinician report rules",
]


ROWS = [
    {
        "resource": "pCR/RCB outcome literature",
        "type": "clinical endpoint",
        "TNBC NAC": 2,
        "EMT/EMP states": 0,
        "Persister biology": 0,
        "Longitudinal shift": 0,
        "Single-cell layer": 0,
        "Label curation": 1,
        "Platform-aware validation": 0,
        "Clinician report rules": 1,
        "similarity": "Defines why pCR/residual disease matters.",
        "difference": "Does not model dynamic EMT or persister state transitions.",
    },
    {
        "resource": "EMP/EMT plasticity reviews",
        "type": "biology review",
        "TNBC NAC": 1,
        "EMT/EMP states": 2,
        "Persister biology": 1,
        "Longitudinal shift": 0,
        "Single-cell layer": 1,
        "Label curation": 0,
        "Platform-aware validation": 0,
        "Clinician report rules": 0,
        "similarity": "Frames EMT as a continuum linked to resistance.",
        "difference": "Usually conceptual, not an executable TNBC NAC digital-twin pipeline.",
    },
    {
        "resource": "Drug-tolerant persister reviews",
        "type": "biology review",
        "TNBC NAC": 0,
        "EMT/EMP states": 1,
        "Persister biology": 2,
        "Longitudinal shift": 0,
        "Single-cell layer": 1,
        "Label curation": 0,
        "Platform-aware validation": 0,
        "Clinician report rules": 0,
        "similarity": "Highlights reversible survivor states and relapse reservoirs.",
        "difference": "Not TNBC NAC-specific and usually not linked to response-model validation.",
    },
    {
        "resource": "MRI-based TNBC NAC digital twins",
        "type": "imaging/mechanistic DT",
        "TNBC NAC": 2,
        "EMT/EMP states": 0,
        "Persister biology": 0,
        "Longitudinal shift": 2,
        "Single-cell layer": 0,
        "Label curation": 0,
        "Platform-aware validation": 1,
        "Clinician report rules": 1,
        "similarity": "Builds patient-specific NAC response twins in TNBC.",
        "difference": "Primarily imaging/tumor-growth centered rather than transcriptomic EMT/persister state biology.",
    },
    {
        "resource": "QSP / virtual-patient IO twins",
        "type": "mechanistic systems model",
        "TNBC NAC": 1,
        "EMT/EMP states": 0,
        "Persister biology": 0,
        "Longitudinal shift": 1,
        "Single-cell layer": 0,
        "Label curation": 0,
        "Platform-aware validation": 1,
        "Clinician report rules": 1,
        "similarity": "Uses mechanistic simulation and virtual patients for oncology decisions.",
        "difference": "Usually immune/QSP-focused, not EMT/persister digital-state reporting in TNBC NAC.",
    },
    {
        "resource": "Oncology DT scoping reviews",
        "type": "field review",
        "TNBC NAC": 0,
        "EMT/EMP states": 0,
        "Persister biology": 0,
        "Longitudinal shift": 1,
        "Single-cell layer": 0,
        "Label curation": 0,
        "Platform-aware validation": 1,
        "Clinician report rules": 2,
        "similarity": "Identifies validation, governance, and credibility requirements.",
        "difference": "Broad review layer, not a disease-specific executable pipeline.",
    },
    {
        "resource": "This TNBC EMT digital twin",
        "type": "research prototype",
        "TNBC NAC": 2,
        "EMT/EMP states": 2,
        "Persister biology": 2,
        "Longitudinal shift": 2,
        "Single-cell layer": 2,
        "Label curation": 2,
        "Platform-aware validation": 2,
        "Clinician report rules": 2,
        "similarity": "Uses accepted response endpoints, public cohorts, state modeling, and external validation principles.",
        "difference": "Combines EMT/persister state dynamics, curated labels, cross-platform validation, and single-cell ambiguity governance in one TNBC NAC workflow.",
    },
]


SOURCES = [
    {
        "name": "CTNeoBC pCR pooled analysis",
        "url": "https://pubmed.ncbi.nlm.nih.gov/24529560/",
        "role": "pCR endpoint context.",
    },
    {
        "name": "Residual cancer burden long-term outcomes",
        "url": "https://pubmed.ncbi.nlm.nih.gov/34902335/",
        "role": "Residual disease prognostic context.",
    },
    {
        "name": "KEYNOTE-522 overall survival",
        "url": "https://pubmed.ncbi.nlm.nih.gov/39282906/",
        "role": "Modern TNBC NAC/chemo-immunotherapy context.",
    },
    {
        "name": "MRI-based TNBC NAC digital twins",
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC11976917/",
        "role": "Closest TNBC NAC digital twin comparator.",
    },
    {
        "name": "From virtual patients to digital twins in immuno-oncology",
        "url": "https://www.nature.com/articles/s41746-024-01188-4",
        "role": "Mechanistic/QSP digital twin comparator.",
    },
    {
        "name": "Advancing precision oncology with digital and virtual twins",
        "url": "https://www.mdpi.com/2072-6694/16/22/3817",
        "role": "Scoping review and credibility context.",
    },
    {
        "name": "Update on epithelial-mesenchymal plasticity in cancer progression",
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC10872224/",
        "role": "EMP biology context.",
    },
    {
        "name": "Drug-tolerant persister cells in cancer",
        "url": "https://www.nature.com/articles/s41467-025-66376-6",
        "role": "Persister biology and translation gaps.",
    },
]


def make_dirs() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ASSET_DIR.mkdir(parents=True, exist_ok=True)


def build_matrix() -> pd.DataFrame:
    return pd.DataFrame(ROWS)


def plot_heatmap(df: pd.DataFrame) -> None:
    values = df[CAPABILITIES].to_numpy(dtype=float)
    fig, ax = plt.subplots(figsize=(13, 7))
    im = ax.imshow(values, cmap="YlGnBu", vmin=0, vmax=2)
    ax.set_xticks(range(len(CAPABILITIES)), CAPABILITIES, rotation=35, ha="right", fontsize=10)
    ax.set_yticks(range(len(df)), df["resource"], fontsize=10)
    for i in range(values.shape[0]):
        for j in range(values.shape[1]):
            label = ["-", "partial", "strong"][int(values[i, j])]
            color = "white" if values[i, j] > 1.2 else "#102a43"
            ax.text(j, i, label, ha="center", va="center", fontsize=8, color=color)
    ax.set_title("Novelty Matrix: Where This Project Extends the Current Landscape", fontsize=16, weight="bold", pad=16)
    cbar = fig.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_ticks([0, 1, 2])
    cbar.set_ticklabels(["absent", "partial", "strong"])
    fig.tight_layout()
    fig.savefig(ASSET_DIR / "novelty_matrix_heatmap.png", dpi=220)
    plt.close(fig)


def plot_positioning(df: pd.DataFrame) -> None:
    coords = {
        "pCR/RCB outcome literature": (0.8, 2.0),
        "EMP/EMT plasticity reviews": (3.0, 1.4),
        "Drug-tolerant persister reviews": (3.2, 1.3),
        "MRI-based TNBC NAC digital twins": (3.7, 3.8),
        "QSP / virtual-patient IO twins": (4.1, 3.4),
        "Oncology DT scoping reviews": (1.8, 3.0),
        "This TNBC EMT digital twin": (4.6, 4.2),
    }
    colors = {
        "This TNBC EMT digital twin": "#d62828",
        "MRI-based TNBC NAC digital twins": "#247ba0",
        "QSP / virtual-patient IO twins": "#247ba0",
        "Oncology DT scoping reviews": "#6a4c93",
        "pCR/RCB outcome literature": "#5c677d",
        "EMP/EMT plasticity reviews": "#2a9d8f",
        "Drug-tolerant persister reviews": "#2a9d8f",
    }
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.axhspan(3.2, 5, color="#edf6f9", zorder=0)
    ax.axvspan(3.2, 5, color="#fff4e6", zorder=0)
    for resource, (x, y) in coords.items():
        ax.scatter(x, y, s=190 if resource.startswith("This") else 105, color=colors[resource], edgecolor="white", linewidth=1.5)
        ax.text(x + 0.06, y + 0.06, resource.replace(" digital twins", " DTs"), fontsize=9, color="#1f2937")
    ax.set_xlim(0, 5.2)
    ax.set_ylim(0, 5.2)
    ax.set_xlabel("Dynamic state biology / mechanism focus", fontsize=12)
    ax.set_ylabel("Validation and translational packaging", fontsize=12)
    ax.set_title("Positioning Map: Novelty Is Integration, Not a Single Isolated Ingredient", fontsize=15, weight="bold")
    ax.grid(True, color="#d9e2ec", linewidth=0.8)
    fig.tight_layout()
    fig.savefig(ASSET_DIR / "novelty_positioning_map.png", dpi=220)
    plt.close(fig)


def plot_evidence_stack() -> None:
    layers = [
        ("Clinical endpoint", 1.0, "pCR/RD, RCB, response-label audit"),
        ("Bulk transcriptomics", 1.3, "EMT, TME, resistance, persister signatures"),
        ("Longitudinal dynamics", 1.6, "GSE43816 pre/post-NAC transition priors"),
        ("Single-cell persister layer", 1.45, "GSE164715 species-filtered targeted annotations"),
        ("Validation governance", 1.25, "GSE163882 external, platform diagnostics, label curation"),
        ("Clinician-style reporting", 1.05, "uncertainty, percentiles, research-only boundaries"),
    ]
    fig, ax = plt.subplots(figsize=(12, 6.5))
    y = 0
    colors = ["#264653", "#2a9d8f", "#e9c46a", "#f4a261", "#e76f51", "#6a4c93"]
    for idx, (name, width, note) in enumerate(layers):
        left = (1.8 - width) / 2
        ax.barh(y, width, left=left, height=0.62, color=colors[idx], alpha=0.92)
        ax.text(left + width / 2, y, name, color="white", weight="bold", fontsize=12, ha="center", va="center")
        ax.text(1.95, y, note, color="#1f2937", fontsize=10, va="center")
        y += 1
    ax.set_xlim(0, 4.4)
    ax.set_ylim(-0.7, len(layers) - 0.25)
    ax.invert_yaxis()
    ax.axis("off")
    ax.set_title("Evidence Stack: The Project Converts Disconnected Resources Into a Governed Digital-Twin Workflow", fontsize=15, weight="bold", pad=12)
    fig.tight_layout()
    fig.savefig(ASSET_DIR / "evidence_stack.png", dpi=220)
    plt.close(fig)


def plot_state_diagram() -> None:
    fig, ax = plt.subplots(figsize=(10, 6.2))
    ax.axis("off")
    states = {
        "E\nEpithelial\nchemo-sensitive": (0.16, 0.58, "#2a9d8f"),
        "H\nHybrid\nplastic": (0.43, 0.70, "#e9c46a"),
        "M\nMesenchymal\nresistant": (0.70, 0.58, "#e76f51"),
        "P\nPersister\nstress tolerant": (0.44, 0.30, "#6a4c93"),
    }
    for label, (x, y, color) in states.items():
        circle = plt.Circle((x, y), 0.115, color=color, ec="white", lw=2)
        ax.add_patch(circle)
        ax.text(x, y, label, ha="center", va="center", color="white", fontsize=11, weight="bold")
    arrows = [
        ((0.25, 0.61), (0.33, 0.67), "plasticity"),
        ((0.53, 0.68), (0.61, 0.62), "EMT shift"),
        ((0.66, 0.50), (0.52, 0.36), "therapy pressure"),
        ((0.36, 0.36), (0.21, 0.51), "reversion"),
        ((0.44, 0.59), (0.44, 0.42), "drug tolerance"),
    ]
    for start, end, text in arrows:
        ax.annotate("", xy=end, xytext=start, arrowprops=dict(arrowstyle="->", lw=2, color="#1f2937"))
        mx, my = (start[0] + end[0]) / 2, (start[1] + end[1]) / 2
        ax.text(mx, my + 0.035, text, fontsize=9, ha="center", color="#1f2937")
    ax.text(0.5, 0.94, "Four-State EMT Plasticity Digital Twin", ha="center", fontsize=18, weight="bold", color="#111827")
    ax.text(0.5, 0.08, "Novelty: state fractions + transition priors + persister/niche layers + uncertainty-aware reporting", ha="center", fontsize=11, color="#374151")
    fig.tight_layout()
    fig.savefig(ASSET_DIR / "four_state_digital_twin_diagram.png", dpi=220)
    plt.close(fig)


def write_report(df: pd.DataFrame) -> None:
    rows = []
    for row in ROWS:
        rows.append(
            {
                "Comparator": row["resource"],
                "Similar to this project": row["similarity"],
                "Different from this project": row["difference"],
            }
        )
    comp = pd.DataFrame(rows)
    novelty_points = [
        "It is TNBC NAC-specific but biologically state-centered, not only endpoint-centered.",
        "It treats EMT as a dynamic epithelial-hybrid-mesenchymal-persister state space.",
        "It separates tumor-cell persister, stress-tolerance, and niche-persister layers.",
        "It calibrates transition priors from paired pre/post-NAC TNBC samples.",
        "It audits and curates response labels instead of assuming public metadata are clean.",
        "It separates same-platform, cross-platform, raw, percentile, z-score, and quantile-calibrated validation.",
        "It integrates a species-filtered single-cell persister layer but explicitly preserves ambiguous compartments.",
        "It defines clinician-style reporting rules that forbid treatment recommendations and emphasize uncertainty.",
    ]
    lines = [
        "# Novelty and Literature Positioning Report",
        "",
        "## Bottom Line",
        "",
        "The project is novel primarily by integration and governance. Individual ingredients exist in the literature: TNBC NAC response endpoints, EMT plasticity biology, drug-tolerant persister biology, imaging-based breast cancer digital twins, QSP/virtual-patient oncology twins, and digital-twin credibility reviews. What is less common is a TNBC NAC workflow that combines EMT-state dynamics, persister biology, longitudinal transition priors, single-cell persister/niche review, response-label curation, platform-aware external validation, and clinician-style reporting boundaries in one reproducible package.",
        "",
        "## Novel Contributions",
        "",
        *[f"{i + 1}. {point}" for i, point in enumerate(novelty_points)],
        "",
        "## Similar Reports and How This Project Differs",
        "",
        comp.to_markdown(index=False),
        "",
        "## Capability Matrix",
        "",
        df[["resource", *CAPABILITIES]].to_markdown(index=False),
        "",
        "## Interpretation",
        "",
        "The closest comparator is MRI-based TNBC NAC digital-twin work, because it also creates patient-specific neoadjuvant treatment twins in TNBC. The key difference is biological resolution: the MRI twin is stronger for growth and treatment-response simulation, while this project is stronger for transcriptomic EMT/persister state interpretation and research-report governance.",
        "",
        "EMP and DTP reviews motivate the biological premise but do not provide an executable TNBC NAC validation pipeline. Oncology digital-twin reviews define credibility needs but are not disease-specific implementations. QSP/virtual-patient immuno-oncology work provides mechanistic simulation philosophy but does not focus on TNBC NAC EMT/persister state transitions.",
        "",
        "## Charts Generated",
        "",
        "- `assets/novelty_matrix_heatmap.png`",
        "- `assets/novelty_positioning_map.png`",
        "- `assets/evidence_stack.png`",
        "- `assets/four_state_digital_twin_diagram.png`",
        "",
        "## Sources Used",
        "",
        *[f"- [{source['name']}]({source['url']}): {source['role']}" for source in SOURCES],
    ]
    (OUT_DIR / "novelty_and_positioning_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    make_dirs()
    df = build_matrix()
    df.to_csv(OUT_DIR / "novelty_comparison_matrix.tsv", sep="\t", index=False)
    pd.DataFrame(SOURCES).to_csv(OUT_DIR / "novelty_sources.tsv", sep="\t", index=False)
    plot_heatmap(df)
    plot_positioning(df)
    plot_evidence_stack()
    plot_state_diagram()
    write_report(df)
    print(f"wrote novelty assets to {OUT_DIR}")


if __name__ == "__main__":
    main()
