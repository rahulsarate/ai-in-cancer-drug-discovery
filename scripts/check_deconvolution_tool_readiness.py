from __future__ import annotations

from pathlib import Path
import shutil

import pandas as pd


PYTHON_MODULES = {
    "cell2location": "publication-grade probabilistic deconvolution",
    "tangram": "cell-to-space mapping and projection",
    "anndata": "shared h5ad IO for spatial/scRNA workflows",
    "scanpy": "single-cell preprocessing",
    "torch": "deep learning backend for tangram/cell2location",
}


def module_available(name: str) -> bool:
    try:
        __import__(name)
        return True
    except Exception:
        return False


def main() -> None:
    rows = []
    for name, use in PYTHON_MODULES.items():
        rows.append(
            {
                "tool": name,
                "runtime": "python",
                "available": module_available(name),
                "best_use": use,
                "next_action": "Install in a dedicated Python <=3.11 environment with GPU optional." if not module_available(name) else "Ready.",
            }
        )
    rows.append(
        {
            "tool": "RCTD/spacexr",
            "runtime": "R",
            "available": shutil.which("Rscript") is not None,
            "best_use": "robust cell-type mixture deconvolution",
            "next_action": "Install R, Bioconductor dependencies, and spacexr/RCTD." if shutil.which("Rscript") is None else "Ready to install spacexr.",
        }
    )
    out = Path("data/processed/spatial_emt_niche_gnn_blockers/deconvolution_tool_readiness.tsv")
    out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out, sep="\t", index=False)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
