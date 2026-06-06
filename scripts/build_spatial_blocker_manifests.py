from __future__ import annotations

from pathlib import Path

import pandas as pd


BLOCKERS = [
    {
        "blocker": "HEST-1k scale ingestion",
        "solution": "Use scripts/check_foundation_model_access.py to verify HuggingFace access; select cancer subsets before full image download.",
        "status": "hf_access_check_implemented_auth_required",
        "source": "https://huggingface.co/datasets/MahmoodLab/hest",
        "next_action": "Accept HEST/HuggingFace terms with an institutional account, set HF_TOKEN, then cache HEST metadata and cancer subsets.",
    },
    {
        "blocker": "H&E/pathology features",
        "solution": "Use 10x H&E tile features, morphology baseline embeddings, and foundation access checks for UNI2/UNI/CONCH.",
        "status": "baseline_ready_foundation_access_check_implemented",
        "source": "local 10x spatial directories",
        "next_action": "After HF terms are accepted, run optional foundation embedding adapters and compare to the current baseline.",
    },
    {
        "blocker": "Real deconvolution",
        "solution": "Use marker-proxy, real GSE154778 NNLS, Tangram/Scanpy/PyTorch/cell2location Python env, and Bioconductor spacexr/RCTD R env.",
        "status": "advanced_environment_installed_cell2location_tangram_rctd_ready",
        "source": "GSE154778, GSE155698, GSE205013, HTAN WUSTL",
        "next_action": "Implement Tangram, RCTD, and cell2location adapters using the real GSE154778 reference; prefer GPU/WSL for long cell2location model training.",
    },
    {
        "blocker": "HTAN validation",
        "solution": "Use HTAN portal manifests plus scripts/check_htan_access.py; Synapse client is installed, Gen3 remains credential/profile dependent.",
        "status": "client_check_implemented_synapse_credentials_required",
        "source": "https://humantumoratlas.org/standard/spatial_transcriptomics/slide-seqlevel2",
        "next_action": "Log in to Synapse or configure Gen3 credentials, select open-access WUSTL PDAC files in the HTAN portal, and download selected assay files.",
    },
    {
        "blocker": "Pathologist expert review",
        "solution": "Generate an AI-prioritized review queue with explicit human scoring fields and literature-grounded region classes.",
        "status": "review_queue_ready_human_annotation_required",
        "source": "data/processed/spatial_emt_niche_gnn_pathology_review/pathologist_review_queue.tsv",
        "next_action": "A pathologist/translational scientist scores the queue; use expert_action and 0-3 morphology scores for validation.",
    },
    {
        "blocker": "Metastasis/progression cohorts",
        "solution": "Run brain-metastasis, GSE274557 Pt-1 pilot, and full GSE274557 patient-batched graph/model summaries.",
        "status": "full_patient_batched_graph_complete",
        "source": "GEO GSE274557, GSE179572",
        "next_action": "Use patient-batched outputs for leave-patient/site validation and manuscript figures.",
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
        "pipeline_status": "all_55_non_pdx_downloaded_standardized_scored_patient_batched_graph_complete",
        "pipeline_output": "data/processed/spatial_emt_niche_gnn_geo_met_pdac_gse274557_patient_batches",
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
        "- HEST-1k: HuggingFace access check is implemented; full ingestion waits for accepted access terms and HF_TOKEN.",
        "- H&E/pathology: tile features, histology-similarity edges, morphology embedding baseline, and foundation access checks are implemented.",
        "- Deconvolution: marker-proxy, PDAC marker-reference NNLS, real GSE154778 NNLS, Tangram environment, and RCTD/spacexr environment are implemented.",
        "- HTAN: WUSTL PDAC target manifest and Synapse/Gen3 access checks are implemented; assay download waits for logged-in file selection.",
        "- Pathologist review: expert scoring queue is generated; interpretation still requires human annotation.",
        "- Metastasis/progression: GSE179572 brain metastasis and full GSE274557 patient-batched graph/model summaries are complete.",
        "",
        "## Immediate Next Runs",
        "",
        "1. Run H&E tile features across all local 10x cohorts.",
        "2. Build Tangram and RCTD adapters around the existing GSE154778 reference.",
        "3. Expand real scRNA references with GSE155698/GSE205013.",
    ]
    (out / "blocker_solution_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
