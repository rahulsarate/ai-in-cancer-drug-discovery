from __future__ import annotations

from pathlib import Path

import pandas as pd


BLOCKERS = [
    {
        "blocker": "HEST-1k scale ingestion",
        "solution": "Use authenticated HuggingFace/Hest library manifest; select cancer subsets first.",
        "status": "access_required",
        "source": "https://huggingface.co/datasets/MahmoodLab/hest",
        "next_action": "Request/confirm HF access, then cache HEST_v1_1_0.csv and subset cancer samples.",
    },
    {
        "blocker": "H&E/pathology features",
        "solution": "Use 10x tissue_hires_image + spot coordinates for basic tile features; later add foundation embeddings.",
        "status": "basic_solution_implemented",
        "source": "local 10x spatial directories",
        "next_action": "Run extract_he_tile_features.py for each cohort; add QuPath/pathologist regions when available.",
    },
    {
        "blocker": "Real deconvolution",
        "solution": "Use marker-proxy now; add NNLS reference deconvolution; later run cell2location/Tangram/RCTD.",
        "status": "fallback_implemented",
        "source": "OpenProblems spatial decomposition benchmark; Spotless benchmark",
        "next_action": "Build matched scRNA reference matrices per cancer type.",
    },
    {
        "blocker": "HTAN validation",
        "solution": "Use HTAN portal manifests and level-2 spatial transcriptomics auxiliary/RNA-seq files.",
        "status": "manifest_ready",
        "source": "https://humantumoratlas.org/standard/spatial_transcriptomics/slide-seqlevel2",
        "next_action": "Select one HTAN cancer atlas and download exported matrix + metadata.",
    },
    {
        "blocker": "Metastasis/progression cohorts",
        "solution": "Prioritize public GEO Visium metastatic/progression cohorts before broad scraping.",
        "status": "candidate_manifest_ready",
        "source": "GEO GSE274557, GSE179572",
        "next_action": "Download small candidate first; add metadata flags for primary/metastasis/progression.",
    },
]

METASTASIS_COHORTS = [
    {
        "accession": "GSE274557",
        "title": "Spatial mapping of transcriptomic and lineage plasticity in metastatic pancreatic cancer",
        "organism": "Homo sapiens",
        "platform": "10x Visium",
        "disease": "metastatic pancreatic cancer",
        "samples": "55 samples; primary, liver, lung, peritoneal metastases",
        "source_url": "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE274557",
        "priority": "high",
    },
    {
        "accession": "GSE179572",
        "title": "Spatial transcriptomics of six surgically-resected human brain metastasis samples",
        "organism": "Homo sapiens",
        "platform": "10x Visium",
        "disease": "brain metastasis",
        "samples": "six brain metastasis samples",
        "source_url": "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE179572",
        "priority": "medium",
    },
]

DECONV_TOOLS = [
    {"tool": "marker_proxy", "implemented": True, "needs_reference": False, "best_use": "first-pass risk control"},
    {"tool": "NNLS reference", "implemented": True, "needs_reference": True, "best_use": "fast matched scRNA baseline"},
    {"tool": "cell2location", "implemented": False, "needs_reference": True, "best_use": "publication-grade probabilistic deconvolution"},
    {"tool": "RCTD", "implemented": False, "needs_reference": True, "best_use": "robust spot mixture estimates"},
    {"tool": "Tangram", "implemented": False, "needs_reference": True, "best_use": "cell mapping and spatial gene projection"},
    {"tool": "stereoscope", "implemented": False, "needs_reference": True, "best_use": "probabilistic reference mapping"},
]


def main() -> None:
    out = Path("data/processed/spatial_emt_niche_gnn_blockers")
    out.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(BLOCKERS).to_csv(out / "blocker_solution_manifest.tsv", sep="\t", index=False)
    pd.DataFrame(METASTASIS_COHORTS).to_csv(out / "metastasis_progression_candidates.tsv", sep="\t", index=False)
    pd.DataFrame(DECONV_TOOLS).to_csv(out / "deconvolution_tool_plan.tsv", sep="\t", index=False)
    write_report(out)
    print(f"Wrote blocker manifests to {out}")


def write_report(out: Path) -> None:
    lines = [
        "# Spatial EMT Blocker Solution Report",
        "",
        "## Best Solutions",
        "",
        "- HEST-1k: gated HuggingFace access check plus selected cancer subset ingestion before full-scale download.",
        "- H&E/pathology: basic tile features are implemented now; foundation embeddings come later.",
        "- Deconvolution: marker-proxy and NNLS reference fallback are implemented; cell2location/RCTD/Tangram need matched scRNA references.",
        "- HTAN: use portal manifests first, then select a single cancer atlas for validation.",
        "- Metastasis/progression: start with GSE274557 metastatic PDAC and GSE179572 brain metastasis.",
        "",
        "## Immediate Next Runs",
        "",
        "1. Run H&E tile features across all local 10x cohorts.",
        "2. Build a cancer-specific scRNA reference matrix for one cohort and run NNLS.",
        "3. Select one metastatic GEO cohort and add a primary/metastasis metadata flag.",
    ]
    (out / "blocker_solution_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
