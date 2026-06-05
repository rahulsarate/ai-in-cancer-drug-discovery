from __future__ import annotations

import numpy as np
import pandas as pd

from .signatures import SIGNATURES


def _zscore_by_gene(expr: pd.DataFrame) -> pd.DataFrame:
    values = expr.replace([np.inf, -np.inf], np.nan)
    values = values.fillna(values.median(numeric_only=True))
    centered = values - values.mean(axis=0)
    scale = values.std(axis=0, ddof=0).replace(0, np.nan)
    return centered.divide(scale, axis=1).fillna(0.0)


def score_signature(zexpr: pd.DataFrame, genes: list[str], aliases: dict[str, list[str]] | None = None) -> pd.Series:
    aliases = aliases or {}
    expanded = []
    for gene in genes:
        expanded.append(gene)
        expanded.extend(aliases.get(gene, []))
    present = [gene for gene in expanded if gene in zexpr.columns]
    if not present:
        return pd.Series(np.nan, index=zexpr.index)
    return zexpr[present].mean(axis=1)


def score_expression(
    expr: pd.DataFrame,
    signatures: dict[str, list[str]] | None = None,
    aliases: dict[str, list[str]] | None = None,
) -> pd.DataFrame:
    """Score samples for EMT, TME, and vulnerability programs.

    Parameters
    ----------
    expr:
        Samples x genes matrix with gene symbols as columns.
    signatures:
        Optional replacement signature dictionary.
    """
    signatures = signatures or SIGNATURES
    zexpr = _zscore_by_gene(expr)

    scores = pd.DataFrame(index=expr.index)
    for name, genes in signatures.items():
        scores[name] = score_signature(zexpr, [gene.upper() for gene in genes], aliases=aliases)

    scores["emt_score"] = scores["mesenchymal"] - scores["epithelial"]
    scores["partial_emt_score"] = np.minimum(scores["epithelial"], scores["mesenchymal"])
    scores["partial_emt_balance"] = -np.abs(scores["epithelial"] - scores["mesenchymal"])
    scores["stromal_contamination_risk"] = scores["stromal_fibroblast"].rank(pct=True)
    scores["immune_context"] = scores["immune_total"]
    scores["caf_tam_niche"] = scores[["caf", "tam_spp1"]].mean(axis=1)
    scores["ferroptosis_window"] = scores["ferroptosis_sensitivity"] - scores["ferroptosis_resistance"]
    scores.insert(0, "sample_id", scores.index.astype(str))
    return scores.reset_index(drop=True)


def merge_scores_with_metadata(scores: pd.DataFrame, metadata: pd.DataFrame | None) -> pd.DataFrame:
    if metadata is None:
        return scores
    return scores.merge(metadata, on="sample_id", how="left")
