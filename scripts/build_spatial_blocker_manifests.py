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
        "solution": "Use 10x H&E tile features plus morphology embedding baseline; later add configured foundation model weights.",
        "status": "morphology_embedding_baseline_implemented",
        "source": "local 10x spatial directories",
        "next_action": "Configure UNI/CONCH/HEST-compatible model weights and compare embeddings to the current baseline.",
    },
    {
        "blocker": "Real deconvolution",
        "solution": "Use marker-proxy plus PDAC marker-reference NNLS now; public scRNA reference candidates are selected.",
        "status": "public_scrna_reference_manifest_ready",
        "source": "GSE154778, GSE155698, GSE205013, HTAN WUSTL",
        "next_action": "Download processed scRNA matrices/cell metadata and build real cell_type x gene references.",
    },
    {
        "blocker": "HTAN validation",
        "solution": "Use HTAN portal manifests and level-2 spatial transcriptomics auxiliary/RNA-seq files.",
        "status": "htan_wustl_pdac_target_manifest_ready",
        "source": "https://humantumoratlas.org/standard/spatial_transcriptomics/slide-seqlevel2",
        "next_action": "Install/configure Synapse or use the HTAN portal Download selected files workflow for HTAN WUSTL PDAC.",
    },
    {
        "blocker": "Metastasis/progression cohorts",
        "solution": "Run brain-metastasis plus GSE274557 Pt-1 graph pilot; full GSE274557 non-PDX data are downloaded, standardized, and scored.",
        "status": "full_non_pdx_standardized_and_scored",
        "source": "GEO GSE274557, GSE179572",
        "next_action": "Run full GSE274557 graph workflow by patient batches to avoid monolithic edge-table failures.",
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
        "pipeline_status": "all_55_non_pdx_downloaded_standardized_scored; pt1_graph_pilot_implemented",
        "pipeline_output": "data/processed/spatial_emt_niche_gnn_geo_met_pdac_gse274557_fullprep",
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
        "- H&E/pathology: tile features, histology-similarity edges, and morphology embedding baseline are implemented; foundation model weights remain optional.",
        "- Deconvolution: marker-proxy and PDAC marker-reference NNLS are implemented; public scRNA references are prioritized for upgrade.",
        "- HTAN: WUSTL PDAC target manifest is selected; Synapse/portal assay download remains next.",
        "- Metastasis/progression: GSE179572 brain metastasis and GSE274557 full non-PDX scoring are complete; Pt-1 graph pilot is complete.",
        "",
        "## Immediate Next Runs",
        "",
        "1. Run H&E tile features across all local 10x cohorts.",
        "2. Build real scRNA-derived references from GSE154778/GSE155698/GSE205013.",
        "3. Run full GSE274557 graph workflow in patient batches.",
    ]
    (out / "blocker_solution_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
