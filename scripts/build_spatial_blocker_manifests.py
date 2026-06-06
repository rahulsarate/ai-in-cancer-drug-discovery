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
        "solution": "Use marker-proxy plus PDAC marker-reference NNLS now; later run cell2location/Tangram/RCTD with real matched scRNA.",
        "status": "nnls_marker_reference_run",
        "source": "OpenProblems spatial decomposition benchmark; Spotless benchmark",
        "next_action": "Replace marker reference with public or matched PDAC scRNA cell-type signatures.",
    },
    {
        "blocker": "HTAN validation",
        "solution": "Use HTAN portal manifests and level-2 spatial transcriptomics auxiliary/RNA-seq files.",
        "status": "htan_wustl_pdac_target_manifest_ready",
        "source": "https://humantumoratlas.org/standard/spatial_transcriptomics/slide-seqlevel2",
        "next_action": "Download HTAN WUSTL PDAC matrix/spatial metadata files from the portal and adapt to standard tables.",
    },
    {
        "blocker": "Metastasis/progression cohorts",
        "solution": "Run brain-metastasis plus a matched GSE274557 Pt-1 primary/liver/peritoneal metastatic PDAC pilot.",
        "status": "matched_site_pilot_implemented",
        "source": "GEO GSE274557, GSE179572",
        "next_action": "Scale GSE274557 from Pt-1 to all non-PDX patients when storage/runtime budget allows.",
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
        "pipeline_status": "matched_pt1_primary_liver_peritoneal_pilot_implemented",
        "pipeline_output": "data/processed/spatial_emt_niche_gnn_geo_met_pdac_gse274557",
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
        "pipeline_status": "downloaded_standardized_scored_graph_trained",
        "pipeline_output": "data/processed/spatial_emt_niche_gnn_geo_brain_met",
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
        "- Deconvolution: marker-proxy and PDAC marker-reference NNLS are implemented; cell2location/RCTD/Tangram need matched scRNA references.",
        "- HTAN: WUSTL PDAC target manifest is selected; portal file download remains next.",
        "- Metastasis/progression: GSE179572 brain metastasis and GSE274557 Pt-1 matched primary/liver/peritoneal PDAC now run end-to-end.",
        "",
        "## Immediate Next Runs",
        "",
        "1. Run H&E tile features across all local 10x cohorts.",
        "2. Replace marker-reference NNLS with matched/public PDAC scRNA signatures.",
        "3. Scale GSE274557 from Pt-1 to the full non-PDX sample set.",
    ]
    (out / "blocker_solution_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
