from __future__ import annotations

import math
from pathlib import Path

import pandas as pd

from .families import TARGET_FAMILIES


DEFAULT_WEIGHTS = {
    "emt_state_specificity": 0.20,
    "metastatic_association": 0.18,
    "druggability": 0.16,
    "crispr_dependency": 0.16,
    "compound_availability": 0.12,
    "normal_tissue_safety": 0.10,
    "literature_support": 0.08,
}


def minmax(series: pd.Series) -> pd.Series:
    series = pd.to_numeric(series, errors="coerce")
    lo = series.min(skipna=True)
    hi = series.max(skipna=True)
    if pd.isna(lo) or pd.isna(hi) or math.isclose(float(lo), float(hi)):
        return pd.Series(0.5, index=series.index)
    return (series - lo) / (hi - lo)


def starter_targets() -> pd.DataFrame:
    rows = []
    for family, genes in TARGET_FAMILIES.items():
        for gene in genes:
            rows.append({"target": gene, "family": family})
    return pd.DataFrame(rows).drop_duplicates("target")


def load_optional_table(path: str | Path | None, key: str = "target") -> pd.DataFrame | None:
    if not path:
        return None
    path = Path(path)
    table = pd.read_csv(path, sep="\t" if path.suffix.lower() != ".csv" else ",")
    table[key] = table[key].astype(str).str.upper()
    return table


def merge_evidence(base: pd.DataFrame, tables: list[pd.DataFrame | None]) -> pd.DataFrame:
    merged = base.copy()
    merged["target"] = merged["target"].astype(str).str.upper()
    for table in tables:
        if table is None:
            continue
        merged = merged.merge(table, on="target", how="left")
    return merged


def fill_evidence_defaults(frame: pd.DataFrame) -> pd.DataFrame:
    defaults = {
        "emt_state_specificity": 0.5,
        "metastatic_association": 0.5,
        "druggability": 0.5,
        "crispr_dependency": 0.5,
        "compound_availability": 0.5,
        "normal_tissue_safety": 0.5,
        "literature_support": 0.5,
    }
    for col, default in defaults.items():
        if col not in frame.columns:
            frame[col] = default
        frame[col] = pd.to_numeric(frame[col], errors="coerce").fillna(default)
    return frame


def rank_targets(frame: pd.DataFrame, weights: dict[str, float] | None = None) -> pd.DataFrame:
    weights = weights or DEFAULT_WEIGHTS
    ranked = frame.copy()
    evidence_present = pd.DataFrame(index=ranked.index)
    for col in weights:
        evidence_present[col] = col in ranked.columns and ranked[col].notna()
    ranked["evidence_completeness"] = evidence_present.mean(axis=1)
    ranked["missing_evidence_count"] = len(weights) - evidence_present.sum(axis=1)
    ranked = fill_evidence_defaults(ranked)

    normalized_cols = []
    for col in weights:
        norm_col = f"{col}_norm"
        ranked[norm_col] = minmax(ranked[col])
        normalized_cols.append(norm_col)

    ranked["priority_score"] = 0.0
    for col, weight in weights.items():
        ranked["priority_score"] += ranked[f"{col}_norm"] * weight

    ranked = ranked.sort_values(["priority_score", "evidence_completeness"], ascending=False)
    return ranked.reset_index(drop=True)
