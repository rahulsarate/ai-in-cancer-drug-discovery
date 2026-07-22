from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from .cards import safe_slug
from .reports import table_to_markdown


EVIDENCE_COLUMNS = [
    "emt_state_specificity",
    "metastatic_association",
    "druggability",
    "crispr_dependency",
    "compound_availability",
    "normal_tissue_safety",
    "literature_support",
    "evidence_completeness",
]


FAMILY_CONTEXT = {
    "AXL_TAM": {
        "states": ["immune_inflamed_emt", "stromal_dominant", "mesenchymal"],
        "rationale": "AXL/TAM-family biology is most relevant when EMT co-occurs with TAM, stromal, or inflammatory context.",
        "assays": ["AXL/GAS6 IHC or RNA validation", "macrophage co-culture invasion assay", "EMT-high organoid drug combination"],
    },
    "FAK_SRC_integrin": {
        "states": ["stromal_dominant", "mesenchymal", "hybrid_e_m"],
        "rationale": "Integrin/FAK/SRC programs fit ECM remodeling, adhesion, invasion, and tumor-stroma interaction hypotheses.",
        "assays": ["matrix invasion assay", "collagen-rich organoid assay", "pFAK/pSRC pathology panel"],
    },
    "TGF_beta_SMAD": {
        "states": ["hybrid_e_m", "stromal_dominant", "mesenchymal"],
        "rationale": "TGF-beta/SMAD signaling is a canonical EMT and CAF-crosstalk axis, especially in hybrid and stromal-rich settings.",
        "assays": ["TGF-beta stimulation/reversal assay", "SMAD phospho-marker validation", "CAF conditioned-media experiment"],
    },
    "hypoxia_metabolism": {
        "states": ["hypoxic_emt", "mesenchymal"],
        "rationale": "Hypoxia and metabolic stress can reinforce EMT, invasion, angiogenesis, and therapy tolerance.",
        "assays": ["hypoxia chamber EMT assay", "CA9/SLC2A1 marker validation", "drug response under low oxygen"],
    },
    "ferroptosis": {
        "states": ["mesenchymal", "hypoxic_emt"],
        "rationale": "Mesenchymal-like and therapy-tolerant states can expose lipid-peroxidation and iron-handling vulnerabilities.",
        "assays": ["ferroptosis rescue assay", "lipid ROS assay", "GPX4/SLC7A11/ACSL4 marker panel"],
    },
    "CAF_TAM_crosstalk": {
        "states": ["immune_inflamed_emt", "stromal_dominant"],
        "rationale": "CAF/TAM crosstalk is most plausible when EMT is embedded in immune and stromal neighborhoods.",
        "assays": ["CAF/TAM multiplex IHC", "cytokine perturbation assay", "spatial co-localization validation"],
    },
    "YAP_TAZ_TEAD": {
        "states": ["hybrid_e_m", "mesenchymal", "stromal_dominant"],
        "rationale": "YAP/TAZ/TEAD signaling links mechanics, ECM stiffness, plasticity, and EMT-like survival states.",
        "assays": ["YAP nuclear localization", "matrix stiffness assay", "TEAD reporter or perturbation experiment"],
    },
}


DEFAULT_CONTEXT = {
    "states": ["hybrid_e_m", "mesenchymal"],
    "rationale": "Prioritize in EMT-high or hybrid-EMT contexts, then validate with tumor-intrinsic and stromal controls.",
    "assays": ["state-specific expression validation", "invasion assay", "drug response assay"],
}


STATE_FRACTION_COLUMNS = {
    "hybrid_e_m": "hybrid_fraction",
    "mesenchymal": "mesenchymal_like_fraction",
    "hypoxic_emt": "mesenchymal_like_fraction",
    "stromal_dominant": "stromal_dominant_fraction",
    "immune_inflamed_emt": "mesenchymal_like_fraction",
}


def _fmt(value: Any) -> str:
    if pd.isna(value):
        return "not available"
    if isinstance(value, float):
        return f"{value:.3g}"
    return str(value)


def _evidence_strength(value: float) -> str:
    if value >= 0.75:
        return "strong"
    if value >= 0.55:
        return "moderate"
    if value >= 0.35:
        return "limited"
    return "weak"


def _top_cancers_for_states(state_summary: pd.DataFrame | None, states: list[str], top_n: int = 5) -> pd.DataFrame:
    if state_summary is None or state_summary.empty:
        return pd.DataFrame()
    summary = state_summary.copy()
    if "cancer_type" not in summary.columns:
        return pd.DataFrame()

    count_cols = [f"{state}_count" for state in states if f"{state}_count" in summary.columns]
    if count_cols:
        summary["matched_state_count"] = summary[count_cols].sum(axis=1)
        summary["matched_state_fraction"] = summary["matched_state_count"] / summary["sample_count"].replace(0, pd.NA)
    elif "mesenchymal_like_fraction" in summary.columns:
        summary["matched_state_fraction"] = summary["mesenchymal_like_fraction"]
        summary["matched_state_count"] = pd.NA
    else:
        return pd.DataFrame()

    cols = [
        col
        for col in [
            "cancer_type",
            "sample_count",
            "matched_state_fraction",
            "matched_state_count",
            "mesenchymal_like_fraction",
            "hybrid_fraction",
            "stromal_dominant_fraction",
        ]
        if col in summary.columns
    ]
    return summary.sort_values("matched_state_fraction", ascending=False)[cols].head(top_n).reset_index(drop=True)


def target_therapy_card_markdown(row: pd.Series, state_summary: pd.DataFrame | None = None) -> str:
    target = row.get("target", "unknown")
    family = str(row.get("family", "unknown"))
    context = FAMILY_CONTEXT.get(family, DEFAULT_CONTEXT)
    top_cancers = _top_cancers_for_states(state_summary, context["states"])

    evidence_rows = []
    for col in EVIDENCE_COLUMNS:
        if col in row.index:
            value = float(row.get(col, 0.0) or 0.0)
            evidence_rows.append({"evidence": col, "score": value, "strength": _evidence_strength(value)})

    lines = [
        f"# EMT Therapeutic Evidence Card: {target}",
        "",
        f"- Target family: {_fmt(family)}",
        f"- Priority score: {_fmt(row.get('priority_score'))}",
        f"- EMT contexts: {', '.join(context['states'])}",
        "",
        "## Rationale",
        "",
        context["rationale"],
        "",
        "## Evidence Scores",
        "",
        table_to_markdown(pd.DataFrame(evidence_rows)),
        "",
        "## Best-Matching Atlas Contexts",
        "",
        table_to_markdown(top_cancers) if not top_cancers.empty else "No matched cancer-type state summary was available.",
        "",
        "## Suggested Validation Assays",
        "",
    ]
    lines.extend([f"- {assay}" for assay in context["assays"]])
    lines.extend(
        [
            "",
            "## Use Boundary",
            "",
            "This is a target-prioritization hypothesis. It is not a clinical treatment recommendation and needs orthogonal validation.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_therapy_evidence_cards(
    ranking: pd.DataFrame,
    state_summary: pd.DataFrame | None,
    out_dir: str | Path,
    top_n: int = 20,
) -> list[Path]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    ranked = ranking.sort_values("priority_score", ascending=False) if "priority_score" in ranking.columns else ranking
    paths: list[Path] = []
    for _, row in ranked.head(top_n).iterrows():
        target = safe_slug(row.get("target", f"target_{_}"))
        path = out / f"{target}_emt_therapy_card.md"
        path.write_text(target_therapy_card_markdown(row, state_summary), encoding="utf-8")
        paths.append(path)
    return paths


def write_therapy_report(
    ranking: pd.DataFrame,
    state_summary: pd.DataFrame | None,
    out_path: str | Path,
    top_n: int = 20,
) -> Path:
    ranked = ranking.sort_values("priority_score", ascending=False) if "priority_score" in ranking.columns else ranking.copy()
    top = ranked.head(top_n).copy()
    if "family" in top.columns:
        family_summary = (
            top.groupby("family", dropna=False)
            .agg(target_count=("target", "count"), mean_priority_score=("priority_score", "mean"))
            .sort_values("mean_priority_score", ascending=False)
            .reset_index()
        )
    else:
        family_summary = pd.DataFrame()

    cols = [
        col
        for col in [
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
        if col in top.columns
    ]

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Pan-Cancer EMT Therapeutic Evidence Report",
        "",
        "Targets are linked to EMT atlas contexts as research hypotheses for validation.",
        "",
        "## Top Targets",
        "",
        table_to_markdown(top[cols]) if cols else "No target ranking columns were available.",
        "",
        "## Target Families",
        "",
        table_to_markdown(family_summary) if not family_summary.empty else "No target-family summary was available.",
        "",
        "## Atlas Context Notes",
        "",
        "Prioritize targets in cancer types where the matching EMT state is frequent and the confidence/stromal warning profile fits the biological question.",
    ]
    if state_summary is not None and not state_summary.empty:
        context_cols = [
            col
            for col in [
                "cancer_type",
                "sample_count",
                "mesenchymal_like_fraction",
                "hybrid_fraction",
                "stromal_dominant_fraction",
                "high_confidence_fraction",
            ]
            if col in state_summary.columns
        ]
        lines.extend(["", "## Highest EMT-Context Cancer Types", "", table_to_markdown(state_summary[context_cols].head(12))])
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


def disease_group_target_recommendations(
    ranking: pd.DataFrame,
    group_summary: pd.DataFrame,
    top_n_per_group: int = 12,
) -> pd.DataFrame:
    if ranking.empty or group_summary.empty or "cancer_group" not in group_summary.columns:
        return pd.DataFrame()
    ranked = ranking.copy()
    if "priority_score" not in ranked.columns:
        ranked["priority_score"] = 0.0

    rows = []
    for _, group_row in group_summary.iterrows():
        group = group_row.get("cancer_group")
        for _, target_row in ranked.iterrows():
            family = str(target_row.get("family", "unknown"))
            context = FAMILY_CONTEXT.get(family, DEFAULT_CONTEXT)
            state_values = []
            for state in context["states"]:
                col = STATE_FRACTION_COLUMNS.get(state)
                if col and col in group_row.index and pd.notna(group_row[col]):
                    state_values.append(float(group_row[col]))
            state_context_score = max(state_values) if state_values else 0.0
            confidence = float(group_row.get("high_confidence_fraction", 0.0) or 0.0)
            stromal = float(group_row.get("stromal_dominant_fraction", 0.0) or 0.0)
            disease_priority = float(target_row.get("priority_score", 0.0) or 0.0) * (
                0.55 + 0.30 * state_context_score + 0.10 * confidence + 0.05 * stromal
            )
            rows.append(
                {
                    "cancer_group": group,
                    "target": target_row.get("target"),
                    "family": family,
                    "disease_priority_score": disease_priority,
                    "pan_cancer_priority_score": target_row.get("priority_score"),
                    "matched_state_context_score": state_context_score,
                    "high_confidence_fraction": confidence,
                    "stromal_dominant_fraction": stromal,
                    "recommended_context": ", ".join(context["states"]),
                    "rationale": context["rationale"],
                    "validation_assays": "; ".join(context["assays"]),
                }
            )
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    return (
        out.sort_values(["cancer_group", "disease_priority_score"], ascending=[True, False])
        .groupby("cancer_group", as_index=False, group_keys=False)
        .head(top_n_per_group)
        .reset_index(drop=True)
    )


def write_disease_group_target_report(recommendations: pd.DataFrame, out_path: str | Path) -> Path:
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# EMT Target Recommendations by Disease Group",
        "",
        "Targets are ranked by combining pan-cancer evidence with the disease group's EMT-state context.",
        "",
    ]
    if recommendations.empty:
        lines.append("No disease-group target recommendations were generated.")
    else:
        for group, part in recommendations.groupby("cancer_group", dropna=False):
            display_cols = [
                col
                for col in [
                    "target",
                    "family",
                    "disease_priority_score",
                    "pan_cancer_priority_score",
                    "matched_state_context_score",
                    "recommended_context",
                    "validation_assays",
                ]
                if col in part.columns
            ]
            lines.extend([f"## {group}", "", table_to_markdown(part[display_cols].head(12)), ""])
    lines.extend(
        [
            "## Use Boundary",
            "",
            "These are research prioritization cards. Disease-specific assays and independent data must precede any clinical claim.",
        ]
    )
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out
