from __future__ import annotations

from pathlib import Path

import pandas as pd


MODELS = [
    {
        "model": "HEST-1k / HEST model ecosystem",
        "input": "H&E tile plus spatial transcriptomics context",
        "strength": "Designed around ST plus histology benchmarking.",
        "access_status": "HEST dataset access gated in this environment; request HuggingFace access first.",
        "source_url": "https://huggingface.co/datasets/MahmoodLab/hest",
    },
    {
        "model": "UNI",
        "input": "H&E tiles",
        "strength": "General-purpose pathology foundation embeddings.",
        "access_status": "Requires configured model weights/license before automated extraction.",
        "source_url": "https://github.com/mahmoodlab/UNI",
    },
    {
        "model": "CONCH",
        "input": "H&E tiles and text-aligned pathology representation",
        "strength": "Useful when text-guided pathology concepts are needed.",
        "access_status": "Requires configured model weights/license before automated extraction.",
        "source_url": "https://github.com/mahmoodlab/CONCH",
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
