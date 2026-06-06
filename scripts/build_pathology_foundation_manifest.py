from __future__ import annotations

from pathlib import Path

import pandas as pd


MODELS = [
    {
        "model": "HEST-1k / HEST model ecosystem",
        "input": "H&E tile plus spatial transcriptomics context",
        "strength": "Designed around ST plus histology benchmarking.",
        "access_status": "Check with scripts/check_foundation_model_access.py; authenticate with HF_TOKEN before scale download.",
        "source_url": "https://huggingface.co/datasets/MahmoodLab/hest",
    },
    {
        "model": "UNI2-h / UNI",
        "input": "H&E tiles",
        "strength": "General-purpose pathology foundation embeddings for histology-similarity edges.",
        "access_status": "Gated HuggingFace model; requires accepted terms and institutional/academic access.",
        "source_url": "https://huggingface.co/MahmoodLab/UNI2-h",
    },
    {
        "model": "CONCH",
        "input": "H&E tiles and text-aligned pathology representation",
        "strength": "Useful when text-guided pathology concepts are needed.",
        "access_status": "Gated HuggingFace model; requires accepted terms/contact sharing before weight download.",
        "source_url": "https://huggingface.co/MahmoodLab/CONCH",
    },
    {
        "model": "CTransPath / HIPT-style encoders",
        "input": "H&E tiles",
        "strength": "Practical baseline family for tile embeddings.",
        "access_status": "Optional local weights required.",
        "source_url": "https://github.com/Xiyue-Wang/TransPath",
    },
]


def main() -> None:
    out = Path("data/processed/spatial_emt_niche_gnn_histology/pathology_foundation_model_manifest.tsv")
    out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(MODELS).to_csv(out, sep="\t", index=False)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
