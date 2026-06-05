from __future__ import annotations

from pathlib import Path

import pandas as pd


def read_aliases(path: str | Path | None) -> dict[str, list[str]]:
    if not path:
        return {}
    path = Path(path)
    if not path.exists():
        return {}
    table = pd.read_csv(path, sep="\t" if path.suffix.lower() != ".csv" else ",")
    if "symbol" not in table.columns or "alias" not in table.columns:
        return {}
    aliases: dict[str, list[str]] = {}
    for _, row in table.dropna(subset=["symbol", "alias"]).iterrows():
        symbol = str(row["symbol"]).upper()
        alias = str(row["alias"]).split(".")[0].upper()
        aliases.setdefault(symbol, []).append(alias)
    return aliases


def expand_gene_filter(genes: set[str], aliases: dict[str, list[str]]) -> set[str]:
    expanded = {gene.upper() for gene in genes}
    for gene in list(expanded):
        expanded.update(alias.upper() for alias in aliases.get(gene, []))
    return expanded
