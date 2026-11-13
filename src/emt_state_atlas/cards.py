from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pandas as pd

from .cancer_groups import add_cancer_groups, requested_group_table
from .consensus import add_consensus_states, consensus_cancer_type_summary
from .reports import table_to_markdown


DISPLAY_SCORE_COLUMNS = [
    "emt_score",
    "partial_emt_score",
    "epithelial",
    "mesenchymal",
    "stromal_contamination_risk",
    "immune_context",
    "caf_tam_niche",
    "hypoxia",
    "ferroptosis_window",
]


def safe_slug(value: Any) -> str:
    text = str(value) if pd.notna(value) else "unknown"
    text = re.sub(r"[^A-Za-z0-9._-]+", "_", text).strip("_")
    return text[:120] or "unknown"


def _fmt(value: Any) -> str:
    if pd.isna(value):
        return "not available"
    if isinstance(value, float):
        return f"{value:.3g}"
    return str(value)


def _row_dict(row: pd.Series) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in row.items():
        if pd.isna(value):
            out[key] = None
        elif hasattr(value, "item"):
            out[key] = value.item()
        else:
            out[key] = value
    return out


def sample_card_markdown(row: pd.Series) -> str:
    sample_id = row.get("sample_id", "unknown")
    cancer_type = row.get("cancer_type", "unknown")
    cancer_group = row.get("cancer_group", "Other / Not Requested")
    state = row.get("consensus_emt_state", "uncertain")
    confidence = row.get("confidence_label", "low")
    explanation = row.get("state_explanation", "")

    lines = [
        f"# EMT State Card: {sample_id}",
        "",
        f"- Cancer type: {_fmt(cancer_type)}",
        f"- Cancer group: {_fmt(cancer_group)}",
        f"- Consensus EMT state: {_fmt(state)}",
        f"- Confidence: {_fmt(confidence)}",
        f"- Confidence reason: {_fmt(row.get('confidence_reason'))}",
        f"- Stromal warning: {_fmt(row.get('stromal_warning'))}",
        "",
        "## Interpretation",
        "",
        explanation or "No interpretation was available.",
        "",
        "## Key Scores",
        "",
    ]

    score_rows = [
        {"score": col, "value": row.get(col)}
        for col in DISPLAY_SCORE_COLUMNS
        if col in row.index
    ]
    lines.append(table_to_markdown(pd.DataFrame(score_rows)))
    lines.extend(
        [
            "",
            "## Research Use",
            "",
            "This card is a research summary, not a treatment recommendation. Validate tumor-intrinsic EMT with single-cell, spatial, pathology, or orthogonal assays before clinical interpretation.",
        ]
    )
    return "\n".join(lines) + "\n"


def cancer_type_card_markdown(row: pd.Series, cancer_type_col: str = "cancer_type") -> str:
    cancer_type = row.get(cancer_type_col, "unknown")
    lines = [
        f"# EMT Cancer-Type Card: {cancer_type}",
        "",
        f"- Samples: {_fmt(row.get('sample_count'))}",
        f"- Mean EMT score: {_fmt(row.get('emt_score_mean'))}",
        f"- Mesenchymal-like fraction: {_fmt(row.get('mesenchymal_like_fraction'))}",
        f"- Hybrid EMT fraction: {_fmt(row.get('hybrid_fraction'))}",
        f"- Stromal-dominant fraction: {_fmt(row.get('stromal_dominant_fraction'))}",
        f"- High-confidence fraction: {_fmt(row.get('high_confidence_fraction'))}",
        "",
        "## State Counts",
        "",
    ]
    state_rows = [
        {"state": col.removesuffix("_count"), "count": row.get(col)}
        for col in row.index
        if str(col).endswith("_count") and col != "sample_count"
    ]
    lines.append(table_to_markdown(pd.DataFrame(state_rows)))
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "Use this cancer-type card to identify cohorts where EMT biology may be common enough for deeper single-cell, spatial, survival, or therapeutic analysis.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_state_cards(
    scores: pd.DataFrame,
    out_dir: str | Path,
    max_sample_cards: int | None = 50,
    cancer_type_col: str = "cancer_type",
) -> dict[str, Path]:
    out = Path(out_dir)
    sample_md = out / "sample_md"
    sample_json = out / "sample_json"
    cancer_md = out / "cancer_type_md"
    for directory in [sample_md, sample_json, cancer_md]:
        directory.mkdir(parents=True, exist_ok=True)

    data = add_cancer_groups(scores, cancer_type_col=cancer_type_col)
    if "consensus_emt_state" not in data.columns:
        data = add_consensus_states(data, cancer_type_col=cancer_type_col)

    ordered = data.sort_values(
        [col for col in ["confidence_label", "emt_score"] if col in data.columns],
        ascending=[True, False][: len([col for col in ["confidence_label", "emt_score"] if col in data.columns])],
    )
    if max_sample_cards is not None:
        ordered = ordered.head(max_sample_cards)

    for _, row in ordered.iterrows():
        sample_id = row.get("sample_id", f"sample_{_}")
        slug = safe_slug(sample_id)
        (sample_md / f"{slug}.md").write_text(sample_card_markdown(row), encoding="utf-8")
        (sample_json / f"{slug}.json").write_text(json.dumps(_row_dict(row), indent=2, sort_keys=True), encoding="utf-8")

    cancer_summary = consensus_cancer_type_summary(data, cancer_type_col=cancer_type_col)
    group_summary = consensus_cancer_type_summary(data, cancer_type_col="cancer_group")
    for _, row in cancer_summary.iterrows():
        slug = safe_slug(row.get(cancer_type_col, "unknown"))
        (cancer_md / f"{slug}.md").write_text(cancer_type_card_markdown(row, cancer_type_col), encoding="utf-8")

    group_md = out / "cancer_group_md"
    group_md.mkdir(parents=True, exist_ok=True)
    for _, row in group_summary.iterrows():
        slug = safe_slug(row.get("cancer_group", "unknown"))
        (group_md / f"{slug}.md").write_text(cancer_type_card_markdown(row, "cancer_group"), encoding="utf-8")

    summary_path = out / "cancer_type_state_summary.tsv"
    group_summary_path = out / "cancer_group_state_summary.tsv"
    requested_groups_path = out / "requested_cancer_groups.tsv"
    scored_path = out / "emt_scores_with_consensus.tsv"
    cancer_summary.to_csv(summary_path, sep="\t", index=False)
    group_summary.to_csv(group_summary_path, sep="\t", index=False)
    requested_group_table().to_csv(requested_groups_path, sep="\t", index=False)
    data.to_csv(scored_path, sep="\t", index=False)
    return {
        "scores": scored_path,
        "cancer_type_summary": summary_path,
        "cancer_group_summary": group_summary_path,
        "requested_cancer_groups": requested_groups_path,
        "sample_md_dir": sample_md,
        "sample_json_dir": sample_json,
        "cancer_type_md_dir": cancer_md,
        "cancer_group_md_dir": group_md,
    }


def write_card_report(
    scores: pd.DataFrame,
    out_path: str | Path,
    cancer_type_col: str = "cancer_type",
) -> Path:
    data = add_cancer_groups(scores, cancer_type_col=cancer_type_col)
    if "consensus_emt_state" not in data.columns:
        data = add_consensus_states(data, cancer_type_col=cancer_type_col)
    cancer_summary = consensus_cancer_type_summary(data, cancer_type_col=cancer_type_col)
    group_summary = consensus_cancer_type_summary(data, cancer_type_col="cancer_group")

    state_counts = data["consensus_emt_state"].value_counts().rename_axis("state").reset_index(name="count")
    confidence_counts = data["confidence_label"].value_counts().rename_axis("confidence").reset_index(name="count")
    top_cols = [
        col
        for col in [
            cancer_type_col,
            "sample_count",
            "emt_score_mean",
            "mesenchymal_like_fraction",
            "hybrid_fraction",
            "stromal_dominant_fraction",
            "high_confidence_fraction",
        ]
        if col in cancer_summary.columns
    ]

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Pan-Cancer EMT State Atlas Card Report",
        "",
        "This report adds consensus EMT state labels, confidence fields, and user-facing card summaries to the scored atlas.",
        "",
        "Interpret all results as research hypotheses. Bulk EMT calls require stromal, single-cell, spatial, or pathology validation before clinical use.",
        "",
        "## Overview",
        "",
        f"- Samples: {len(data)}",
        f"- Cancer types: {data[cancer_type_col].nunique() if cancer_type_col in data.columns else 'unknown'}",
        f"- High-confidence samples: {int(data['confidence_label'].eq('high').sum()) if 'confidence_label' in data.columns else 0}",
        f"- Stromal-warning samples: {int(data['stromal_warning'].sum()) if 'stromal_warning' in data.columns else 0}",
        "",
        "## State Distribution",
        "",
        table_to_markdown(state_counts),
        "",
        "## Confidence Distribution",
        "",
        table_to_markdown(confidence_counts),
        "",
        "## Top Cancer Types",
        "",
        table_to_markdown(cancer_summary[top_cols].head(15)) if top_cols else "No cancer-type summary available.",
        "",
        "## Requested Cancer Groups",
        "",
        table_to_markdown(requested_group_table()),
        "",
        "## Requested Group EMT Summary",
        "",
        table_to_markdown(
            group_summary[
                [
                    col
                    for col in [
                        "cancer_group",
                        "sample_count",
                        "emt_score_mean",
                        "mesenchymal_like_fraction",
                        "hybrid_fraction",
                        "stromal_dominant_fraction",
                        "high_confidence_fraction",
                    ]
                    if col in group_summary.columns
                ]
            ].head(20)
        ),
        "",
        "## Next Validation Steps",
        "",
        "- Validate high EMT states in malignant single cells.",
        "- Review stromal-dominant calls with CAF/fibroblast and pathology markers.",
        "- Prioritize high-confidence hybrid or mesenchymal-like groups for target and drug evidence cards.",
    ]
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out
