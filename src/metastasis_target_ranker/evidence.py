from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from .ranking import starter_targets


CURATED_FAMILY_PRIORS = {
    "AXL_TAM": {"druggability": 0.85, "literature_support": 0.90, "compound_availability": 0.80},
    "TGF_beta_SMAD": {"druggability": 0.75, "literature_support": 0.95, "compound_availability": 0.75},
    "YAP_TAZ_TEAD": {"druggability": 0.65, "literature_support": 0.75, "compound_availability": 0.55},
    "FAK_SRC_integrin": {"druggability": 0.90, "literature_support": 0.80, "compound_availability": 0.85},
    "ferroptosis": {"druggability": 0.55, "literature_support": 0.75, "compound_availability": 0.60},
    "CAF_TAM_crosstalk": {"druggability": 0.75, "literature_support": 0.75, "compound_availability": 0.70},
    "hypoxia_metabolism": {"druggability": 0.70, "literature_support": 0.70, "compound_availability": 0.65},
    "PRC2_KMT2D": {"druggability": 0.65, "literature_support": 0.65, "compound_availability": 0.55},
    "RNA_P_body": {"druggability": 0.30, "literature_support": 0.45, "compound_availability": 0.25},
}


def read_table(path: str | Path | None) -> pd.DataFrame | None:
    if not path:
        return None
    path = Path(path)
    if not path.exists():
        return None
    suffixes = [suffix.lower() for suffix in path.suffixes]
    sep = "," if ".csv" in suffixes else "\t"
    return pd.read_csv(path, sep=sep)


def gene_columns(frame: pd.DataFrame, target_genes: set[str]) -> dict[str, str]:
    mapping = {}
    for col in frame.columns:
        gene = str(col).split(" (")[0].split("|")[0].upper()
        if gene in target_genes:
            mapping[gene] = col
    return mapping


def minmax(values: pd.Series) -> pd.Series:
    values = pd.to_numeric(values, errors="coerce")
    lo = values.min(skipna=True)
    hi = values.max(skipna=True)
    if pd.isna(lo) or pd.isna(hi) or np.isclose(lo, hi):
        return pd.Series(0.5, index=values.index)
    return (values - lo) / (hi - lo)


def curated_prior_table(base: pd.DataFrame | None = None) -> pd.DataFrame:
    base = starter_targets() if base is None else base.copy()
    rows = []
    for _, row in base.iterrows():
        priors = CURATED_FAMILY_PRIORS.get(row["family"], {})
        rows.append(
            {
                "target": row["target"],
                "druggability": priors.get("druggability", 0.5),
                "compound_availability": priors.get("compound_availability", 0.5),
                "literature_support": priors.get("literature_support", 0.5),
            }
        )
    return pd.DataFrame(rows)


def emt_specificity_from_scores(expression: pd.DataFrame | None, scores: pd.DataFrame | None, base: pd.DataFrame) -> pd.DataFrame:
    if expression is None or scores is None or "sample_id" not in scores.columns:
        return pd.DataFrame({"target": base["target"], "emt_state_specificity": pd.NA})

    expr = expression.copy()
    if expr.columns[0].lower() in {"sample_id", "sample"}:
        expr = expr.set_index(expr.columns[0])
    expr.columns = [str(col).upper() for col in expr.columns]
    score_frame = scores.set_index("sample_id")
    shared = expr.index.intersection(score_frame.index)
    if len(shared) < 4 or "emt_score" not in score_frame.columns:
        return pd.DataFrame({"target": base["target"], "emt_state_specificity": pd.NA})

    high = score_frame.loc[shared, "emt_score"] >= score_frame.loc[shared, "emt_score"].quantile(0.75)
    low = score_frame.loc[shared, "emt_score"] <= score_frame.loc[shared, "emt_score"].quantile(0.25)
    rows = []
    for target in base["target"].astype(str).str.upper():
        if target not in expr.columns or high.sum() == 0 or low.sum() == 0:
            score = 0.5
        else:
            diff = expr.loc[shared[high], target].mean() - expr.loc[shared[low], target].mean()
            score = float(diff)
        rows.append({"target": target, "emt_state_specificity": score})
    table = pd.DataFrame(rows)
    table["emt_state_specificity"] = minmax(table["emt_state_specificity"]).fillna(0.5)
    return table


def metastasis_association_from_metadata(expression: pd.DataFrame | None, metadata: pd.DataFrame | None, base: pd.DataFrame) -> pd.DataFrame:
    if expression is None or metadata is None or "is_metastatic" not in metadata.columns:
        return pd.DataFrame({"target": base["target"], "metastatic_association": pd.NA})

    expr = expression.copy()
    if expr.columns[0].lower() in {"sample_id", "sample"}:
        expr = expr.set_index(expr.columns[0])
    expr.columns = [str(col).upper() for col in expr.columns]
    meta = metadata.set_index("sample_id")
    shared = expr.index.intersection(meta.index)
    if len(shared) < 4:
        return pd.DataFrame({"target": base["target"], "metastatic_association": pd.NA})

    metastatic = meta.loc[shared, "is_metastatic"].astype(bool)
    rows = []
    for target in base["target"].astype(str).str.upper():
        if target not in expr.columns or metastatic.sum() == 0 or (~metastatic).sum() == 0:
            score = 0.5
        else:
            score = expr.loc[shared[metastatic], target].mean() - expr.loc[shared[~metastatic], target].mean()
        rows.append({"target": target, "metastatic_association": score})
    table = pd.DataFrame(rows)
    table["metastatic_association"] = minmax(table["metastatic_association"]).fillna(0.5)
    return table


def crispr_dependency_from_depmap(depmap_gene_effect: pd.DataFrame | None, base: pd.DataFrame) -> pd.DataFrame:
    if depmap_gene_effect is None:
        return pd.DataFrame({"target": base["target"], "crispr_dependency": pd.NA, "normal_tissue_safety": pd.NA})

    targets = set(base["target"].astype(str).str.upper())
    mapping = gene_columns(depmap_gene_effect, targets)
    rows = []
    for target in targets:
        col = mapping.get(target)
        if not col:
            rows.append({"target": target, "crispr_dependency": pd.NA, "normal_tissue_safety": pd.NA})
            continue
        values = pd.to_numeric(depmap_gene_effect[col], errors="coerce")
        dependency = -values.quantile(0.10)
        pan_essential_penalty = max(0.0, -values.median())
        rows.append(
            {
                "target": target,
                "crispr_dependency": dependency,
                "normal_tissue_safety": 1.0 - pan_essential_penalty,
            }
        )
    table = pd.DataFrame(rows)
    table["crispr_dependency"] = minmax(table["crispr_dependency"]).fillna(0.5)
    table["normal_tissue_safety"] = minmax(table["normal_tissue_safety"]).fillna(0.5)
    return table


def count_evidence(table: pd.DataFrame | None, base: pd.DataFrame, value_col: str, target_col: str = "target") -> pd.DataFrame:
    if table is None or target_col not in table.columns:
        return pd.DataFrame({"target": base["target"], value_col: pd.NA})
    counts = table.assign(target=table[target_col].astype(str).str.upper()).groupby("target").size()
    out = pd.DataFrame({"target": base["target"].astype(str).str.upper()})
    out[value_col] = out["target"].map(counts).fillna(0)
    out[value_col] = minmax(out[value_col]).fillna(0.5)
    return out


def build_evidence_tables(
    base: pd.DataFrame | None = None,
    expression: pd.DataFrame | None = None,
    scores: pd.DataFrame | None = None,
    metadata: pd.DataFrame | None = None,
    depmap_gene_effect: pd.DataFrame | None = None,
    open_targets: pd.DataFrame | None = None,
    chembl: pd.DataFrame | None = None,
    dgidb: pd.DataFrame | None = None,
    prism: pd.DataFrame | None = None,
    lincs: pd.DataFrame | None = None,
) -> dict[str, pd.DataFrame]:
    base = starter_targets() if base is None else base.copy()
    priors = curated_prior_table(base)
    chembl_compounds = count_evidence(chembl, base, "chembl_compound_count")
    dgidb_interactions = count_evidence(dgidb, base, "dgidb_interaction_count")
    open_target_hits = count_evidence(open_targets, base, "open_targets_hit_count")
    prism_hits = count_evidence(prism, base, "prism_hit_count")
    lincs_hits = count_evidence(lincs, base, "lincs_hit_count")

    availability = priors[["target", "compound_availability"]].merge(chembl_compounds, on="target").merge(
        dgidb_interactions, on="target"
    ).merge(prism_hits, on="target").merge(lincs_hits, on="target")
    availability["compound_availability"] = availability[
        ["compound_availability", "chembl_compound_count", "dgidb_interaction_count", "prism_hit_count", "lincs_hit_count"]
    ].mean(axis=1)

    druggability = priors[["target", "druggability"]].merge(open_target_hits, on="target").merge(chembl_compounds, on="target")
    druggability["druggability"] = druggability[["druggability", "open_targets_hit_count", "chembl_compound_count"]].mean(axis=1)

    literature = priors[["target", "literature_support"]].merge(open_target_hits, on="target").merge(lincs_hits, on="target")
    literature["literature_support"] = literature[["literature_support", "open_targets_hit_count", "lincs_hit_count"]].mean(axis=1)

    dependency = crispr_dependency_from_depmap(depmap_gene_effect, base)

    return {
        "emt_state_specificity": emt_specificity_from_scores(expression, scores, base),
        "metastatic_association": metastasis_association_from_metadata(expression, metadata, base),
        "crispr_dependency": dependency[["target", "crispr_dependency"]],
        "normal_tissue_safety": dependency[["target", "normal_tissue_safety"]],
        "druggability": druggability[["target", "druggability"]],
        "compound_availability": availability[["target", "compound_availability"]],
        "literature_support": literature[["target", "literature_support"]],
    }
