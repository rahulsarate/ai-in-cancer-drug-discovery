from __future__ import annotations

from pathlib import Path

import pandas as pd


def read_table(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    suffixes = [suffix.lower() for suffix in path.suffixes]
    if ".csv" in suffixes:
        return pd.read_csv(path)
    return pd.read_csv(path, sep="\t")


def read_expression(path: str | Path, gene_filter: set[str] | None = None) -> pd.DataFrame:
    """Read an expression matrix with gene symbols in either index or columns.

    When ``gene_filter`` is provided and the file is gene x sample, large Xena
    matrices are streamed in chunks so only required genes are loaded.
    """
    if gene_filter:
        frame = read_filtered_expression(path, gene_filter)
    else:
        frame = read_table(path)
    first_col = frame.columns[0]
    if first_col.lower() in {"gene", "genes", "symbol", "hugo_symbol", "gene_symbol", "cellname", "sample", "sample_id"}:
        frame = frame.set_index(first_col)
    return frame


def read_filtered_expression(path: str | Path, gene_filter: set[str]) -> pd.DataFrame:
    path = Path(path)
    suffixes = [suffix.lower() for suffix in path.suffixes]
    sep = "," if ".csv" in suffixes else "\t"
    gene_filter = {gene.upper() for gene in gene_filter}

    header = pd.read_csv(path, sep=sep, nrows=0)
    first_col = header.columns[0]
    header_gene_hits = sum(str(col).split("|")[0].upper() in gene_filter for col in header.columns[1:])
    if first_col.lower() in {"sample", "sample_id"} and header_gene_hits > 0:
        return pd.read_csv(path, sep=sep)
    if first_col.lower() not in {"gene", "genes", "symbol", "hugo_symbol", "gene_symbol"}:
        return pd.read_csv(path, sep=sep)

    chunks = []
    for chunk in pd.read_csv(path, sep=sep, chunksize=1000):
        genes = chunk[first_col].astype(str).str.split("|").str[0].str.upper()
        filtered = chunk[genes.isin(gene_filter)]
        if not filtered.empty:
            filtered = filtered.copy()
            filtered[first_col] = filtered[first_col].astype(str).str.split("|").str[0].str.upper()
            chunks.append(filtered)
    if not chunks:
        return pd.DataFrame(columns=header.columns)
    return pd.concat(chunks, ignore_index=True)


def orient_expression(expr: pd.DataFrame, known_genes: set[str]) -> pd.DataFrame:
    """Return samples x genes matrix."""
    index_hits = sum(str(idx).upper() in known_genes for idx in expr.index)
    column_hits = sum(str(col).upper() in known_genes for col in expr.columns)

    if index_hits > column_hits:
        expr = expr.T

    expr.columns = [str(col).split("|")[0].upper() for col in expr.columns]
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
