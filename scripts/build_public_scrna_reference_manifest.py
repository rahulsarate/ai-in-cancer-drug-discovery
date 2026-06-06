from __future__ import annotations

from pathlib import Path

import pandas as pd


REFERENCES = [
    {
        "accession": "GSE154778",
        "disease": "PDAC primary and metastatic lesions",
        "modality": "10x scRNA-seq",
        "best_use": "Matched primary/metastatic PDAC reference for malignant, CAF, macrophage, T-cell compartments.",
        "source_url": "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE154778",
        "priority": "high",
        "status": "downloaded_marker_assigned_reference_v1_built",
    },
    {
        "accession": "GSE155698",
        "disease": "PDAC and non-cancer pancreas",
        "modality": "10x scRNA-seq",
        "best_use": "Large PDAC/non-cancer reference; useful for ductal/tumor epithelial and normal pancreas controls.",
        "source_url": "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE155698",
        "priority": "high",
        "status": "candidate_for_real_reference_download",
    },
    {
        "accession": "GSE205013",
        "disease": "PDAC chemotherapy-treated and untreated tumor microenvironment",
        "modality": "single-cell RNA-seq",
        "best_use": "Treatment-context reference for CAF, TAM, T-cell, and malignant compartments.",
        "source_url": "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE205013",
        "priority": "medium",
        "status": "candidate_for_real_reference_download",
    },
    {
        "accession": "HTAN WUSTL snRNA/scRNA",
        "disease": "Untreated and chemo-resistant pancreatic cancer",
        "modality": "single-nucleus/single-cell RNA-seq",
        "best_use": "Best matched reference for HTAN WUSTL spatial PDAC if downloaded through HTAN/Synapse.",
        "source_url": "https://data.humantumoratlas.org/",
        "priority": "high",
        "status": "portal_download_required",
    },
]


def main() -> None:
    out = Path("data/processed/spatial_emt_niche_gnn_references/public_pdac_scrna_reference_manifest.tsv")
    out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(REFERENCES).to_csv(out, sep="\t", index=False)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
