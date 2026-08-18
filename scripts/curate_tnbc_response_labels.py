from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
VALID_RESPONSES = {"pcr_or_good_response", "residual_or_poor_response"}


def text(value: object) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()


def curate_row(row: pd.Series) -> dict[str, object]:
    tnbc = bool(row.get("tnbc_confirmed_or_likely", False))
    standard = text(row.get("standard_response"))
    pcr_rd = text(row.get("pathologic_response_pcr_rd")).upper()
    rcb = text(row.get("pathologic_response_rcb_class")).upper()
    flag = text(row.get("audit_flag"))

    composite = ""
    strict = ""
    decision = "exclude"
    reason = []
    needs_manual = False

    if not tnbc:
        reason.append("not_tnbc_confirmed_or_likely")
    elif standard not in VALID_RESPONSES:
        reason.append("missing_or_unknown_response_label")
    else:
        composite = standard
        decision = "lock_original_composite_label"
        reason.append("tnbc_likely_with_valid_original_label")

    if tnbc and standard in VALID_RESPONSES and "RD" in pcr_rd:
        strict = "residual_or_poor_response"
        if standard == "pcr_or_good_response":
            composite = "residual_or_poor_response"
            decision = "recode_to_residual_for_locked_composite"
            reason.append("pathologic_response_field_reports_residual_disease")
            if "RCB-0/I" in rcb:
                reason.append("original_good_response_bucket_probably_reflected_rcb_0_i_not_strict_pcr")
            elif rcb:
                reason.append(f"rcb_class_{rcb.lower()}_supports_residual_or_poor_response")
            else:
                reason.append("rcb_class_missing_but_rd_field_supports_residual")
        else:
            reason.append("strict_endpoint_residual_disease")
    elif tnbc and standard in VALID_RESPONSES and "PCR" in pcr_rd:
        strict = "pcr_or_good_response"
        reason.append("strict_endpoint_explicit_pcr")
    elif tnbc and standard == "residual_or_poor_response":
        strict = "residual_or_poor_response"
        reason.append("strict_endpoint_inferred_from_original_residual_label")
    elif tnbc and standard == "pcr_or_good_response":
        strict = ""
        reason.append("strict_pcr_not_explicit_in_available_audit_fields")

    if "residual_text_but_pcr_label" in flag:
        needs_manual = True
        reason.append("audit_conflict_was_resolved_by_pathologic_rd_field")
    if "missing_standard_response" in flag:
        needs_manual = True

    locked = bool(tnbc and composite in VALID_RESPONSES)
    return {
        "locked_for_curated_composite_model": locked,
        "locked_composite_response": composite if locked else "",
        "locked_strict_pcr_response": strict,
        "curation_decision": decision,
        "manual_review_recommended": needs_manual,
        "curation_reason": ";".join(dict.fromkeys(reason)),
    }


def write_report(curated: pd.DataFrame, out_path: Path) -> None:
    summary = (
        curated.groupby(["dataset_id", "locked_composite_response", "curation_decision"], dropna=False)
        .size()
        .reset_index(name="samples")
        .sort_values(["dataset_id", "locked_composite_response", "curation_decision"])
    )
    review = (
        curated[curated["manual_review_recommended"]]
        .groupby(["dataset_id", "curation_decision", "curation_reason"], dropna=False)
        .size()
        .reset_index(name="samples")
    )
    strict = (
        curated.groupby(["dataset_id", "locked_strict_pcr_response"], dropna=False)
        .size()
        .reset_index(name="samples")
        .sort_values(["dataset_id", "locked_strict_pcr_response"])
    )
    lines = [
        "# TNBC Response-Label Curation Sign-Off",
        "",
        "## Curation Decision",
        "",
        "The original response model used a broad `pcr_or_good_response` versus `residual_or_poor_response` endpoint. During audit, several `GSE25055` and `GSE25065` rows had `pathologic_response_pcr_rd = RD` while the model label was `pcr_or_good_response`. For a locked modeling table, those rows are conservatively recoded to `residual_or_poor_response` because the available pathology field states residual disease.",
        "",
        "Rows with unknown labels remain excluded. Non-TNBC-likely rows remain excluded from TNBC modeling. The curation table preserves a strict pCR/RD field separately from the curated composite model field so downstream reports do not overstate pCR specificity.",
        "",
        "## Locked Composite Label Summary",
        "",
        summary.to_markdown(index=False),
        "",
        "## Strict pCR/RD Availability",
        "",
        strict.to_markdown(index=False),
        "",
        "## Manual-Review Rows Resolved or Excluded",
        "",
        review.to_markdown(index=False) if not review.empty else "No manual-review rows detected.",
        "",
        "## Sign-Off Rules",
        "",
        "- Use `locked_composite_response` for the curated response-model sensitivity analysis.",
        "- Use `locked_strict_pcr_response` only when explicitly discussing strict pCR/RD evidence.",
        "- Do not call RCB-0/I rows strict pCR unless an explicit pCR field is present.",
        "- Unknown `GSE18864` labels remain excluded from response modeling.",
        "- This is a computational curation sign-off; final publication should still cite the source cohort metadata definitions.",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Curate TNBC NAC response labels after audit conflicts.")
    p.add_argument("--audit-table", default="data/processed/tnbc_digital_twin/response_label_audit/tnbc_response_label_audit_table.tsv")
    p.add_argument("--model-table", default="data/processed/tnbc_digital_twin/tnbc_nac_emt_digital_twin_tnbc_response_model_table.tsv")
    p.add_argument("--out-dir", default="data/processed/tnbc_digital_twin/response_label_curation")
    p.add_argument("--docs-dir", default="docs/tnbc_digital_twin_emt_plasticity")
    return p


def main() -> None:
    args = parser().parse_args()
    out_dir = ROOT / args.out_dir
    docs_dir = ROOT / args.docs_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    docs_dir.mkdir(parents=True, exist_ok=True)

    audit = pd.read_csv(ROOT / args.audit_table, sep="\t")
    curated_fields = audit.apply(curate_row, axis=1, result_type="expand")
    curated = pd.concat([audit, curated_fields], axis=1)
    curated.to_csv(out_dir / "tnbc_response_label_curation_table.tsv", sep="\t", index=False)

    model = pd.read_csv(ROOT / args.model_table, sep="\t")
    keep_cols = [
        "dataset_id",
        "sample_id",
        "locked_for_curated_composite_model",
        "locked_composite_response",
        "locked_strict_pcr_response",
        "curation_decision",
        "manual_review_recommended",
        "curation_reason",
    ]
    locked = model.merge(curated[keep_cols], on=["dataset_id", "sample_id"], how="left")
    locked = locked[locked["locked_for_curated_composite_model"] == True].copy()  # noqa: E712
    locked["original_standard_response"] = locked["standard_response"]
    locked["standard_response"] = locked["locked_composite_response"]
    locked.to_csv(out_dir / "tnbc_curated_response_model_table.tsv", sep="\t", index=False)

    report = out_dir / "tnbc_response_label_curation_signoff_report.md"
    write_report(curated, report)
    write_report(curated, docs_dir / "response_label_curation_signoff.md")
    print(f"wrote {report}")
    print(f"wrote {out_dir / 'tnbc_curated_response_model_table.tsv'}")


if __name__ == "__main__":
    main()
