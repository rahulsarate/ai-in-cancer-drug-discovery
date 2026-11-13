from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
AUDIT_DATASETS = ["GSE18864", "GSE25055", "GSE25065", "GSE45898", "GSE163882"]
EVIDENCE_COLUMNS = [
    "response_to_nac",
    "miller_payne_response",
    "pathologic_response_pcr_rd",
    "pathologic_response_rcb_class",
    "clinical_response",
    "sample_title",
    "sample_description",
    "tnbc_confirmed_or_likely",
    "standard_response",
]


def confidence(row: pd.Series) -> str:
    response = str(row.get("standard_response", "unknown"))
    if response not in {"pcr_or_good_response", "residual_or_poor_response"}:
        return "unlabeled"
    if str(row.get("response_to_nac", "")).strip() in {"pCR", "RD"}:
        return "high"
    if str(row.get("pathologic_response_pcr_rd", "")).strip():
        return "high"
    if str(row.get("miller_payne_response", "")).strip():
        return "medium"
    if str(row.get("clinical_response", "")).strip():
        return "medium"
    return "low"


def flag(row: pd.Series) -> str:
    notes = []
    response = str(row.get("standard_response", "unknown"))
    if response == "unknown":
        notes.append("missing_standard_response")
    if str(row.get("tnbc_confirmed_or_likely", "")).lower() != "true":
        notes.append("not_tnbc_likely")
    raw_terms = " ".join(str(row.get(col, "")) for col in EVIDENCE_COLUMNS).lower()
    if "pcr" in raw_terms and "residual_or_poor_response" == response:
        notes.append("pcr_text_but_residual_label")
    if ("rd" in raw_terms or "residual" in raw_terms) and "pcr_or_good_response" == response:
        notes.append("residual_text_but_pcr_label")
    return ";".join(notes) if notes else "ok"


def build_audit(metadata: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    cols = ["dataset_id", "sample_id"] + [col for col in EVIDENCE_COLUMNS if col in metadata.columns]
    audit = metadata[metadata["dataset_id"].isin(AUDIT_DATASETS)][cols].copy()
    audit["response_label_confidence"] = audit.apply(confidence, axis=1)
    audit["audit_flag"] = audit.apply(flag, axis=1)
    summary = (
        audit.groupby(["dataset_id", "standard_response", "tnbc_confirmed_or_likely", "response_label_confidence", "audit_flag"], dropna=False)
        .size()
        .reset_index(name="samples")
        .sort_values(["dataset_id", "standard_response", "audit_flag"])
    )
    return audit, summary


def write_report(summary: pd.DataFrame, out_path: Path) -> None:
    lines = [
        "# TNBC NAC Response Label Audit",
        "",
        "## Purpose",
        "",
        "Create a reproducible audit table for response labels used in TNBC NAC modeling. This is not a substitute for manual curation, but it identifies evidence columns, confidence levels, and rows needing review.",
        "",
        "## Summary",
        "",
        summary.to_markdown(index=False),
        "",
        "## Manual Curation Rules",
        "",
        "- Keep `pCR` or RCB-0/I as `pcr_or_good_response`.",
        "- Keep residual disease, non-pCR, RCB-II/III, poor/minor/no response as `residual_or_poor_response`.",
        "- Miller-Payne grade 4-5 is currently treated as good response; grade 1-3 as poor response.",
        "- Any row with an audit flag other than `ok` should be manually checked before manuscript claims.",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Audit response labels for TNBC NAC digital-twin modeling cohorts.")
    p.add_argument("--metadata", default="data/processed/tnbc_digital_twin/tnbc_nac_geo_sample_metadata.tsv")
    p.add_argument("--out-dir", default="data/processed/tnbc_digital_twin/response_label_audit")
    return p


def main() -> None:
    args = parser().parse_args()
    out_dir = ROOT / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    metadata = pd.read_csv(ROOT / args.metadata, sep="\t", dtype=str)
    audit, summary = build_audit(metadata)
    audit.to_csv(out_dir / "tnbc_response_label_audit_table.tsv", sep="\t", index=False)
    summary.to_csv(out_dir / "tnbc_response_label_audit_summary.tsv", sep="\t", index=False)
    write_report(summary, out_dir / "tnbc_response_label_audit_report.md")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
