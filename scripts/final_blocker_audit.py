from __future__ import annotations

from pathlib import Path

import pandas as pd


OUT = Path("data/processed/spatial_emt_niche_gnn_project_status")


def exists(path: str) -> bool:
    return Path(path).exists()


def main() -> None:
    rows = [
        {
            "blocker": "HEST gated download",
            "category": "credential_legal_gate",
            "internal_resolution": "HF access checker and safe downloader implemented",
            "required_external_action": "Accept HEST terms and set HF_TOKEN",
            "evidence_path": "data/processed/spatial_emt_niche_gnn_histology/hf_gated_resource_download_status.tsv",
            "internal_status": "complete" if exists("scripts/download_hf_gated_resources.py") else "missing",
            "can_be_closed_without_external_action": False,
        },
        {
            "blocker": "UNI/CONCH foundation weights",
            "category": "credential_license_gate",
            "internal_resolution": "Foundation access check and safe model-card downloader implemented",
            "required_external_action": "Accept model terms and set HF_TOKEN; keep weights local",
            "evidence_path": "data/processed/spatial_emt_niche_gnn_histology/foundation_model_access_status.tsv",
            "internal_status": "complete" if exists("scripts/check_foundation_model_access.py") else "missing",
            "can_be_closed_without_external_action": False,
        },
        {
            "blocker": "HTAN selected assay download",
            "category": "credential_file_selection_gate",
            "internal_resolution": "HTAN CLI/Synapse/Gen3 checks, selected-file template, and downloader implemented",
            "required_external_action": "Export selected HTAN file IDs and configure portal/Synapse/Gen3 credentials",
            "evidence_path": "data/processed/spatial_emt_niche_gnn_htan/htan_selected_file_download_status.tsv",
            "internal_status": "complete" if exists("scripts/download_htan_selected_files.py") else "missing",
            "can_be_closed_without_external_action": False,
        },
        {
            "blocker": "Pathologist expert scoring",
            "category": "human_expert_gate",
            "internal_resolution": "Queue, batches, SOP, reviewer roles, sourcing plan, and recruitment email implemented",
            "required_external_action": "Verified pathologist or translational pathology reviewer scores the queue",
            "evidence_path": "data/processed/spatial_emt_niche_gnn_pathology_review/pathologist_review_batches.tsv",
            "internal_status": "complete" if exists("data/processed/spatial_emt_niche_gnn_pathology_review/pathologist_review_batches.tsv") else "missing",
            "can_be_closed_without_external_action": False,
        },
        {
            "blocker": "Advanced deconvolution adapters",
            "category": "engineering_gate",
            "internal_resolution": "Tangram/cell2location/RCTD input prep implemented with real GSE154778 reference",
            "required_external_action": "None for adapter readiness; full publication-scale model training remains optional/heavy",
            "evidence_path": "data/processed/spatial_emt_niche_gnn_geo_met_pdac_gse274557/advanced_deconvolution/advanced_deconvolution_input_manifest.tsv",
            "internal_status": "complete" if exists("data/processed/spatial_emt_niche_gnn_geo_met_pdac_gse274557/advanced_deconvolution/advanced_deconvolution_input_manifest.tsv") else "pending_run",
            "can_be_closed_without_external_action": True,
        },
    ]
    audit = pd.DataFrame(rows)
    internal_complete = audit["internal_status"].eq("complete").mean() * 100
    externally_closeable = audit["can_be_closed_without_external_action"].mean() * 100
    OUT.mkdir(parents=True, exist_ok=True)
    audit.to_csv(OUT / "final_blocker_audit.tsv", sep="\t", index=False)
    pd.DataFrame(
        [
            {
                "metric": "internal_blocker_resolution_percent",
                "value": round(internal_complete, 1),
                "interpretation": "Engineering/reproducibility readiness for all known blockers.",
            },
            {
                "metric": "blockers_closeable_without_credentials_or_human_percent",
                "value": round(externally_closeable, 1),
                "interpretation": "Some blockers require legal credentials or human expert work by design.",
            },
        ]
    ).to_csv(OUT / "final_blocker_audit_summary.tsv", sep="\t", index=False)
    print(f"Wrote {OUT / 'final_blocker_audit.tsv'}")


if __name__ == "__main__":
    main()
