from __future__ import annotations

from pathlib import Path

import pandas as pd


def table_to_markdown(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "No rows available."
    text = frame.copy()
    for col in text.columns:
        if pd.api.types.is_numeric_dtype(text[col]):
            text[col] = text[col].map(lambda value: f"{value:.3g}" if pd.notna(value) else "")
        else:
            text[col] = text[col].fillna("").astype(str)
    header = "| " + " | ".join(text.columns) + " |"
    sep = "| " + " | ".join(["---"] * len(text.columns)) + " |"
    rows = ["| " + " | ".join(map(str, row)) + " |" for row in text.to_numpy()]
    return "\n".join([header, sep, *rows])


def evidence_strength(score: float) -> str:
    if score >= 0.75:
        return "strong"
    if score >= 0.55:
        return "moderate"
    if score >= 0.35:
        return "limited"
    return "weak"


def write_target_cards(ranked: pd.DataFrame, out_dir: str | Path, top_n: int = 20) -> list[Path]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths = []
    evidence_cols = [
        "emt_state_specificity",
        "metastatic_association",
        "druggability",
        "crispr_dependency",
        "compound_availability",
        "normal_tissue_safety",
        "literature_support",
    ]

    for _, row in ranked.head(top_n).iterrows():
        target = str(row["target"])
        path = out / f"{target}_evidence_card.md"
        lines = [
            f"# {target} Evidence Card",
            "",
            f"- Family: {row.get('family', 'unknown')}",
            f"- Priority score: {row.get('priority_score', 0):.3f}",
            f"- Evidence completeness: {row.get('evidence_completeness', 0):.2f}",
            "",
            "## Evidence Scores",
            "",
        ]
        for col in evidence_cols:
            value = float(row.get(col, 0.5))
            lines.append(f"- {col}: {value:.3f} ({evidence_strength(value)})")
        lines.extend(
            [
                "",
                "## Interpretation",
                "",
                "This card is a research-prioritization summary, not a clinical recommendation. Review raw evidence sources and normal-tissue safety before experimental use.",
                "",
            ]
        )
        path.write_text("\n".join(lines), encoding="utf-8")
        paths.append(path)
    return paths


def write_target_summary(ranked: pd.DataFrame, out_path: str | Path, top_n: int = 20) -> Path:
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    cols = [
        "target",
        "family",
        "priority_score",
        "emt_state_specificity",
        "metastatic_association",
        "druggability",
        "crispr_dependency",
        "compound_availability",
        "normal_tissue_safety",
        "literature_support",
    ]
    cols = [col for col in cols if col in ranked.columns]
    lines = [
        "# Metastasis Target Ranking Report",
        "",
        "Targets are ranked as research hypotheses using EMT specificity, metastasis association, druggability, dependency, compound availability, safety, and literature support.",
        "",
        table_to_markdown(ranked[cols].head(top_n)),
        "",
    ]
    out.write_text("\n".join(lines), encoding="utf-8")
    return out
