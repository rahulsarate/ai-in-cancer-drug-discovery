from __future__ import annotations

import argparse
import os
from pathlib import Path

import pandas as pd


RESOURCES = [
    {
        "resource": "HEST metadata",
        "repo_id": "MahmoodLab/hest",
        "repo_type": "dataset",
        "filename": "HEST_v1_1_0.csv",
        "local_subdir": "data/raw/hest",
        "safe_to_attempt": True,
    },
    {
        "resource": "UNI2-h model card",
        "repo_id": "MahmoodLab/UNI2-h",
        "repo_type": "model",
        "filename": "README.md",
        "local_subdir": "data/raw/pathology_foundation/UNI2-h",
        "safe_to_attempt": True,
    },
    {
        "resource": "UNI model card",
        "repo_id": "MahmoodLab/UNI",
        "repo_type": "model",
        "filename": "README.md",
        "local_subdir": "data/raw/pathology_foundation/UNI",
        "safe_to_attempt": True,
    },
    {
        "resource": "CONCH model card",
        "repo_id": "MahmoodLab/CONCH",
        "repo_type": "model",
        "filename": "README.md",
        "local_subdir": "data/raw/pathology_foundation/CONCH",
        "safe_to_attempt": True,
    },
]


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Download safe gated-resource files when HF_TOKEN and accepted terms are available.")
    p.add_argument("--out-dir", default="data/processed/spatial_emt_niche_gnn_histology")
    p.add_argument("--attempt-download", action="store_true", help="Attempt safe metadata/model-card downloads.")
    return p


def try_download(row: dict[str, object], token: str | None, attempt: bool) -> dict[str, object]:
    status = dict(row)
    status["hf_token_configured"] = bool(token)
    status["download_attempted"] = False
    status["downloaded"] = False
    status["local_path"] = ""
    status["error"] = ""
    if not attempt:
        status["next_action"] = "Set HF_TOKEN and rerun with --attempt-download after accepting gated terms."
        return status
    if not token:
        status["error"] = "HF_TOKEN not configured"
        status["next_action"] = "Accept terms, set HF_TOKEN, and rerun."
        return status
    try:
        from huggingface_hub import hf_hub_download
    except Exception as exc:
        status["error"] = f"huggingface_hub import failed: {exc}"
        status["next_action"] = "Install huggingface_hub in .venv-deconv."
        return status
    status["download_attempted"] = True
    try:
        local_dir = Path(str(row["local_subdir"]))
        local_dir.mkdir(parents=True, exist_ok=True)
        path = hf_hub_download(
            repo_id=str(row["repo_id"]),
            repo_type=str(row["repo_type"]),
            filename=str(row["filename"]),
            token=token,
            local_dir=local_dir,
            local_dir_use_symlinks=False,
        )
        status["downloaded"] = True
        status["local_path"] = path
        status["next_action"] = "Use this file as the first safe access proof; keep large gated weights/images out of Git."
    except Exception as exc:
        status["error"] = f"{type(exc).__name__}: {str(exc)[:400]}"
        status["next_action"] = "Confirm terms are accepted for this repo and rerun."
    return status


def main() -> None:
    args = parser().parse_args()
    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_HUB_TOKEN")
    rows = [try_download(row, token, args.attempt_download) for row in RESOURCES]
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out / "hf_gated_resource_download_status.tsv", sep="\t", index=False)
    print(f"Wrote {out / 'hf_gated_resource_download_status.tsv'}")


if __name__ == "__main__":
    main()
