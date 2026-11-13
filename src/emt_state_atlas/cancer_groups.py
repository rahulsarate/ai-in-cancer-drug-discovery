from __future__ import annotations

import pandas as pd


CANCER_TYPE_TO_GROUP = {
    "HNSC": "Head and Neck Cancer",
    "BRCA": "Breast Cancer",
    "COAD": "Colon / Intestine Cancer",
    "READ": "Colon / Intestine Cancer",
    "PAAD": "Pancreatic Cancer",
    "GBM": "Brain Tumors",
    "LGG": "Brain Tumors",
    "PRAD": "Prostate Cancer",
    "OV": "Ovarian Cancer",
    "SKCM": "Skin Cancer",
    "UVM": "Skin Cancer",
    "LUAD": "Lung Cancer",
    "LUSC": "Lung Cancer",
    "ESCA": "Oesophageal Cancer",
    "LAML": "Blood Tumors",
    "DLBC": "Blood Tumors",
}


REQUESTED_CANCER_GROUPS = [
    "Head and Neck Cancer",
    "Breast Cancer",
    "Colon / Intestine Cancer",
    "Pancreatic Cancer",
    "Brain Tumors",
    "Prostate Cancer",
    "Ovarian Cancer",
    "Skin Cancer",
    "Lung Cancer",
    "Oesophageal Cancer",
    "Blood Tumors",
]


GROUP_NOTES = {
    "Head and Neck Cancer": "TCGA HNSC; includes head and neck squamous cell carcinoma.",
    "Breast Cancer": "TCGA BRCA.",
    "Colon / Intestine Cancer": "TCGA COAD and READ; small-intestine tumors need external cohorts beyond TCGA PanCan.",
    "Pancreatic Cancer": "TCGA PAAD.",
    "Brain Tumors": "TCGA GBM and LGG.",
    "Prostate Cancer": "TCGA PRAD.",
    "Ovarian Cancer": "TCGA OV.",
    "Skin Cancer": "TCGA SKCM and UVM.",
    "Lung Cancer": "TCGA LUAD and LUSC.",
    "Oesophageal Cancer": "TCGA ESCA.",
    "Blood Tumors": "TCGA LAML and DLBC; additional hematologic cohorts can be added later.",
}


def cancer_group_for_code(code: object) -> str:
    text = str(code).strip().upper() if pd.notna(code) else "UNKNOWN"
    return CANCER_TYPE_TO_GROUP.get(text, "Other / Not Requested")


def add_cancer_groups(frame: pd.DataFrame, cancer_type_col: str = "cancer_type") -> pd.DataFrame:
    out = frame.copy()
    if cancer_type_col not in out.columns:
        out[cancer_type_col] = "unknown"
    out["cancer_group"] = out[cancer_type_col].map(cancer_group_for_code)
    out["cancer_group_note"] = out["cancer_group"].map(GROUP_NOTES).fillna("Cohort is present but outside the requested disease-focus set.")
    return out


def requested_group_table() -> pd.DataFrame:
    rows = []
    for group in REQUESTED_CANCER_GROUPS:
        codes = [code for code, mapped in CANCER_TYPE_TO_GROUP.items() if mapped == group]
        rows.append({"cancer_group": group, "tcga_codes": ", ".join(codes), "note": GROUP_NOTES[group]})
    return pd.DataFrame(rows)
