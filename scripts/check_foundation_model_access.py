from __future__ import annotations

import os
from pathlib import Path

import pandas as pd


OUT = Path("data/processed/spatial_emt_niche_gnn_histology")
RESOURCES = [
    {
        "resource": "HEST-1k dataset",
        "hub_type": "dataset",
        "repo_id": "MahmoodLab/hest",
        "why_needed": "Multimodal histology plus spatial transcriptomics scale-up.",
        "license_or_gate": "HuggingFace dataset access/terms may be required.",
        "priority": "high",
    },
    {
        "resource": "H-Optimus-0",
        "hub_type": "model",
        "repo_id": "bioptimus/H-optimus-0",
        "why_needed": "Primary BioOptimus-aligned H&E foundation embedding backend.",
        "license_or_gate": "Apache-2.0 model; gated contact-sharing acceptance is required for file access.",
        "priority": "high",
    },
    {
        "resource": "Phikon-v2",
        "hub_type": "model",
        "repo_id": "owkin/phikon-v2",
        "why_needed": "Ungated pathology-foundation fallback for executable H&E embeddings.",
        "license_or_gate": "Custom non-commercial model license; review before redistribution or commercial use.",
        "priority": "high",
    },
    {
        "resource": "UNI2-h",
        "hub_type": "model",
        "repo_id": "MahmoodLab/UNI2-h",
        "why_needed": "High-capacity H&E tile embeddings for morphology-similarity edges.",
        "license_or_gate": "Gated; requires accepted terms and institutional email for academic/non-commercial use.",
        "priority": "high",
    },
    {
        "resource": "UNI",
        "hub_type": "model",
        "repo_id": "MahmoodLab/UNI",
        "why_needed": "Earlier UNI pathology foundation baseline.",
        "license_or_gate": "Gated; requires accepted HuggingFace terms.",
        "priority": "medium",
    },
    {
        "resource": "CONCH",
        "hub_type": "model",
        "repo_id": "MahmoodLab/CONCH",
        "why_needed": "Vision-language pathology embeddings and text-guided morphology concepts.",
        "license_or_gate": "Gated; requires accepted terms/contact sharing; CC-BY-NC-ND-4.0.",
        "priority": "high",
    },
]


def access_status(repo_id: str, hub_type: str, token: str | None) -> dict[str, object]:
    try:
        from huggingface_hub import HfApi
        from huggingface_hub.errors import GatedRepoError, RepositoryNotFoundError
    except Exception as exc:
        return {
            "accessible": False,
            "status": "huggingface_hub_missing",
            "evidence": f"{type(exc).__name__}: {exc}",
        }
    api = HfApi(token=token)
    try:
        if hub_type == "dataset":
            info = api.dataset_info(repo_id)
        else:
            info = api.model_info(repo_id)
        gated = getattr(info, "gated", None)
        return {
            "accessible": True,
            "status": "accessible" if not gated else f"metadata_accessible_gated_{gated}",
            "evidence": f"sha={getattr(info, 'sha', '')}; gated={gated}",
        }
    except GatedRepoError as exc:
        return {"accessible": False, "status": "gated_auth_required", "evidence": str(exc)[:500]}
    except RepositoryNotFoundError as exc:
        return {"accessible": False, "status": "not_found_or_private", "evidence": str(exc)[:500]}
    except Exception as exc:
        text = str(exc)
        status = "auth_required_or_network_error" if "401" in text or "403" in text else "check_failed"
        return {"accessible": False, "status": status, "evidence": f"{type(exc).__name__}: {text[:500]}"}


def main() -> None:
    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_HUB_TOKEN")
    rows = []
    for resource in RESOURCES:
        status = access_status(resource["repo_id"], resource["hub_type"], token)
        rows.append(
            {
                **resource,
                **status,
                "hf_token_configured": bool(token),
                "next_action": (
                    "Accept the HuggingFace terms with an institutional account, set HF_TOKEN, and rerun before downloading gated files."
                    if str(status["status"]).startswith("metadata_accessible_gated") and not token
                    else (
                        "Use optional foundation embedding adapter after confirming license/terms."
                        if status["accessible"]
                        else "Accept the HuggingFace terms with an institutional account, set HF_TOKEN, and rerun this check."
                    )
                ),
            }
        )
    OUT.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT / "foundation_model_access_status.tsv", sep="\t", index=False)
    print(f"Wrote {OUT / 'foundation_model_access_status.tsv'}")


if __name__ == "__main__":
    main()
