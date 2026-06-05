from __future__ import annotations

from pathlib import Path

import pandas as pd


def read_table(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    suffixes = [suffix.lower() for suffix in path.suffixes]
    if ".csv" in suffixes:
        return pd.read_csv(path)
    return pd.read_csv(path, sep="\t")


def read_expression(path: str | Path) -> pd.DataFrame:
    """Read an expression matrix with gene symbols in either index or columns."""
    frame = read_table(path)
    first_col = frame.columns[0]
    if first_col.lower() in {"gene", "genes", "symbol", "hugo_symbol", "gene_symbol", "sample", "sample_id"}:
        frame = frame.set_index(first_col)
    return frame


def orient_expression(expr: pd.DataFrame, known_genes: set[str]) -> pd.DataFrame:
    """Return samples x genes matrix."""
    index_hits = sum(str(idx).upper() in known_genes for idx in expr.index)
    column_hits = sum(str(col).upper() in known_genes for col in expr.columns)

    if index_hits > column_hits:
        expr = expr.T

    expr.columns = [str(col).upper() for col in expr.columns]
    expr.index = [str(idx) for idx in expr.index]
    return expr.apply(pd.to_numeric, errors="coerce")


def read_metadata(path: str | Path | None) -> pd.DataFrame | None:
    if path is None:
        return None
    metadata = read_table(path)
    if "sample_id" not in metadata.columns:
        metadata = metadata.rename(columns={metadata.columns[0]: "sample_id"})
    metadata["sample_id"] = metadata["sample_id"].astype(str)
    return metadata
