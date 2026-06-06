from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys

import pandas as pd


PYTHON_MODULES = {
    "cell2location": "publication-grade probabilistic deconvolution",
    "tangram": "cell-to-space mapping and projection",
    "anndata": "shared h5ad IO for spatial/scRNA workflows",
    "scanpy": "single-cell preprocessing",
    "torch": "deep learning backend for tangram/cell2location",
}
DEFAULT_ENV_PYTHON = Path(".venv-deconv/Scripts/python.exe")
DEFAULT_RSCRIPT = Path("C:/Program Files/R/R-4.6.0/bin/Rscript.exe")


def run_command(args: list[str], timeout: int = 60, env: dict[str, str] | None = None) -> tuple[bool, str]:
    try:
        result = subprocess.run(args, check=False, capture_output=True, text=True, timeout=timeout, env=env)
    except subprocess.TimeoutExpired:
        return False, f"timeout_after_{timeout}s"
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}"
    output = (result.stdout + "\n" + result.stderr).strip()
    return result.returncode == 0, output[:500]


def module_available(name: str, python_exe: Path | str = sys.executable, timeout: int = 60) -> tuple[bool, str]:
    code = (
        "import importlib, json; "
        f"m={name!r}; "
        "mod=importlib.import_module(m); "
        "print(json.dumps({'version': getattr(mod, '__version__', '')}))"
    )
    return run_command([str(python_exe), "-c", code], timeout=timeout)


def r_package_available(package: str) -> tuple[bool, str]:
    rscript = DEFAULT_RSCRIPT if DEFAULT_RSCRIPT.exists() else shutil.which("Rscript")
    if not rscript:
        return False, "Rscript not found"
    code = (
        ".libPaths(c(file.path(getwd(), '.r-lib'), .libPaths())); "
        f"library({package}); "
        f"cat('{package}', as.character(packageVersion('{package}')), '\\n')"
    )
    return run_command([str(rscript), "-e", code], timeout=120)


def main() -> None:
    rows = []
    env_python = DEFAULT_ENV_PYTHON if DEFAULT_ENV_PYTHON.exists() else Path(sys.executable)
    for name, use in PYTHON_MODULES.items():
        available, evidence = module_available(name, env_python, timeout=180 if name == "cell2location" else 60)
        rows.append(
            {
                "tool": name,
                "runtime": "python",
                "runtime_path": str(env_python),
                "available": available,
                "best_use": use,
                "evidence": evidence,
                "next_action": (
                    "Ready for pipeline integration."
                    if available
                    else "Installed package may be missing or import may hang; keep NNLS/Tangram fallback active and debug in a Linux/GPU environment if needed."
                ),
            }
        )
    spacexr_ready, spacexr_evidence = r_package_available("spacexr")
    rows.append(
        {
            "tool": "RCTD/spacexr",
            "runtime": "R",
            "runtime_path": str(DEFAULT_RSCRIPT if DEFAULT_RSCRIPT.exists() else shutil.which("Rscript") or ""),
            "available": spacexr_ready,
            "best_use": "robust cell-type mixture deconvolution",
            "evidence": spacexr_evidence,
            "next_action": "Ready for an RCTD adapter using the real GSE154778 reference." if spacexr_ready else "Install R and Bioconductor spacexr in .r-lib.",
        }
    )
    out = Path("data/processed/spatial_emt_niche_gnn_blockers/deconvolution_tool_readiness.tsv")
    out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out, sep="\t", index=False)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
