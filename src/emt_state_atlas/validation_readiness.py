from __future__ import annotations

from pathlib import Path

import pandas as pd

from .reports import table_to_markdown


VALIDATION_COHORTS = [
    {
        "validation_layer": "annotated_single_cell",
        "candidate_source": "TISCH2 selected dataset export",
        "status": "ready_for_import_after_portal_export",
        "needed_fields": "expression matrix; cell_id; cell_type; malignant_status or CNV call; cancer type",
        "purpose": "separate malignant EMT from CAF/TAM EMT mimicry",
    },
    {
        "validation_layer": "annotated_single_cell",
        "candidate_source": "3CA cancer category dataset",
        "status": "ready_for_import_after_dataset_download",
        "needed_fields": "AnnData or expression matrix; obs metadata; malignant/cell-type labels",
        "purpose": "curated malignant-cell validation across cancer categories",
    },
    {
        "validation_layer": "spatial_pathology",
        "candidate_source": "HTAN selected Level 3/4 spatial or single-cell files",
        "status": "requires_selected_files_and_credentials",
        "needed_fields": "spatial expression; spot/cell metadata; sample/cancer annotation; optional pathology regions",
        "purpose": "matched human tumor atlas validation",
    },
    {
        "validation_layer": "clinical",
        "candidate_source": "external survival cohort with treatment annotation",
        "status": "not_yet_imported",
        "needed_fields": "sample expression/signature scores; OS/PFS time/event; stage; grade; treatment; cancer group",
        "purpose": "independent validation of Cox and event-rate screens",
    },
    {
        "validation_layer": "pathology",
        "candidate_source": "expert region review form",
        "status": "queue_ready_labels_pending",
        "needed_fields": "cohort/run; region_id; invasive_edge; CAF score; TAM score; hypoxia/necrosis; tumor-intrinsic EMT label",
        "purpose": "convert spatial hypotheses into reviewed region labels",
    },
]


def validation_readiness_table() -> pd.DataFrame:
    return pd.DataFrame(VALIDATION_COHORTS)


def write_validation_readiness_report(frame: pd.DataFrame, out_path: str | Path) -> Path:
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# EMT Atlas Validation Cohort Readiness",
        "",
        "This table tracks the remaining external validation inputs needed to move from internal research screens to stronger independent evidence.",
        "",
        table_to_markdown(frame),
    ]
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out
