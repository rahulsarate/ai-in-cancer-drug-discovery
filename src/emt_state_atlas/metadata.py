from __future__ import annotations

import re

import pandas as pd


SAMPLE_ALIASES = ["sample_id", "sample", "Sample", "ID", "id", "submitter_id"]
CANCER_TYPE_ALIASES = [
    "cancer_type",
    "cancer type abbreviation",
    "cohort",
    "project",
    "project_id",
    "primary_disease",
    "_primary_disease",
    "disease",
    "study",
]
TIME_ALIASES = ["time", "OS.time", "OS_days", "days_to_death", "days_to_last_follow_up", "DSS.time", "PFI.time"]
EVENT_ALIASES = ["event", "OS", "vital_status", "DSS", "PFI"]
METASTASIS_ALIASES = ["metastatic", "sample_type", "sample_type.samples", "tumor_stage", "pathologic_stage"]


def tcga_patient_barcode(sample_id: str) -> str:
    text = str(sample_id)
    match = re.match(r"^(TCGA-[A-Z0-9]{2}-[A-Z0-9]{4})", text, flags=re.IGNORECASE)
    return match.group(1).upper() if match else text.upper()


def find_column(frame: pd.DataFrame, aliases: list[str]) -> str | None:
    lower = {str(col).lower(): col for col in frame.columns}
    for alias in aliases:
        if alias.lower() in lower:
            return lower[alias.lower()]
    return None


def harmonize_metadata(metadata: pd.DataFrame) -> pd.DataFrame:
    """Normalize common TCGA/Xena metadata columns for downstream analyses."""
    frame = metadata.copy()

    sample_col = find_column(frame, SAMPLE_ALIASES) or frame.columns[0]
    frame = frame.rename(columns={sample_col: "sample_id"})
    frame["sample_id"] = frame["sample_id"].astype(str)
    frame["patient_id"] = frame["sample_id"].map(tcga_patient_barcode)

    cancer_col = find_column(frame, CANCER_TYPE_ALIASES)
    if cancer_col and cancer_col != "cancer_type":
        frame = frame.rename(columns={cancer_col: "cancer_type"})
    if "cancer_type" not in frame.columns:
        frame["cancer_type"] = "unknown"

    time_col = find_column(frame, TIME_ALIASES)
    if time_col and time_col != "time":
        frame = frame.rename(columns={time_col: "time"})
    if "time" in frame.columns:
        frame["time"] = pd.to_numeric(frame["time"], errors="coerce")

    event_col = find_column(frame, EVENT_ALIASES)
    if event_col and event_col != "event":
        frame = frame.rename(columns={event_col: "event"})
    if "event" in frame.columns:
        frame["event"] = normalize_event(frame["event"])

    metastasis_col = find_column(frame, METASTASIS_ALIASES)
    if metastasis_col:
        frame["metastasis_label"] = frame[metastasis_col].astype(str)
        frame["is_metastatic"] = frame["metastasis_label"].str.contains(
            "metast|stage iv|stage 4|distant", case=False, na=False
        )

    return frame


def normalize_event(series: pd.Series) -> pd.Series:
    if pd.api.types.is_numeric_dtype(series):
        return pd.to_numeric(series, errors="coerce")
    text = series.astype(str).str.lower()
    return text.isin(["1", "true", "dead", "deceased", "event", "yes", "progressed"]).astype(int)


def attach_patient_metadata(scores: pd.DataFrame, metadata: pd.DataFrame | None) -> pd.DataFrame:
    if metadata is None:
        return scores
    meta = harmonize_metadata(metadata)
    frame = scores.copy()
    frame["patient_id"] = frame["sample_id"].map(tcga_patient_barcode)

    direct = frame.merge(meta, on="sample_id", how="left", suffixes=("", "_meta"))
    if "cancer_type" not in direct.columns:
        direct["cancer_type"] = pd.NA

    patient_meta = meta.drop(columns=["sample_id"], errors="ignore").drop_duplicates("patient_id")
    fallback = frame[["sample_id", "patient_id"]].merge(patient_meta, on="patient_id", how="left", suffixes=("", "_patient"))
    fallback = fallback.set_index("sample_id")
    direct = direct.set_index("sample_id", drop=False)

    for col in fallback.columns:
        if col == "patient_id":
            continue
        if col not in direct.columns:
            direct[col] = pd.NA
        direct[col] = direct[col].combine_first(fallback[col])
    direct = direct.reset_index(drop=True)
    return direct
