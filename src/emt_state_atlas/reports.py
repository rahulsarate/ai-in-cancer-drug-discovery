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


def write_atlas_report(
    scores: pd.DataFrame,
    summary: pd.DataFrame,
    survival: pd.DataFrame | None,
    plots: list[Path],
    out_path: str | Path,
) -> Path:
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# EMT State Atlas Report",
        "",
        "This report summarizes EMT, stromal, immune, CAF/TAM, hypoxia, and ferroptosis-window signals.",
        "",
        "Interpret all results as research hypotheses. Bulk EMT scores can be inflated by stromal/fibroblast signal.",
        "",
        "## Dataset Overview",
        "",
        f"- Samples scored: {len(scores)}",
        f"- Cancer types: {scores['cancer_type'].nunique() if 'cancer_type' in scores.columns else 'unknown'}",
        f"- EMT-high samples: {int(scores['emt_high'].sum()) if 'emt_high' in scores.columns else 'not computed'}",
        f"- Stromal-inflated EMT candidates: {int(scores['stromal_inflated_emt_candidate'].sum()) if 'stromal_inflated_emt_candidate' in scores.columns else 'not computed'}",
        "",
        "## Top Cancer Types by Mean EMT Score",
        "",
    ]

    top_cols = [col for col in ["cancer_type", "emt_score_mean", "partial_emt_score_mean", "stromal_fibroblast_mean", "caf_tam_niche_mean"] if col in summary.columns]
    if top_cols:
        lines.append(table_to_markdown(summary[top_cols].head(10)))
    else:
        lines.append("No cancer-type summary columns were available.")

    lines.extend(["", "## Survival Associations", ""])
    if survival is not None and not survival.empty:
        lines.append(table_to_markdown(survival.head(20)))
    else:
        lines.append("Survival associations were not generated or did not have enough complete events.")

    lines.extend(["", "## Plots", ""])
    if plots:
        for path in plots:
            lines.append(f"- {path.name}")
    else:
        lines.append("No plots were written because plotting dependencies were unavailable or required columns were missing.")

    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out
