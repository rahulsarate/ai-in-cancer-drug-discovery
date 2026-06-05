from __future__ import annotations

import argparse
import gzip
from pathlib import Path

from emt_state_atlas.aliases import expand_gene_filter, read_aliases
from emt_state_atlas.signatures import SIGNATURES


ROOT = Path(__file__).resolve().parents[1]


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Extract signature rows from a large Xena gene x sample matrix.")
    p.add_argument("--expression", required=True)
    p.add_argument("--gene-aliases", default="data/raw/gene_aliases/signature_gene_aliases.tsv")
    p.add_argument("--out", default="data/processed/tcga_xena_v1/signature_expression.tsv")
    return p


def open_text(path: Path):
    if path.suffix.lower() == ".gz":
        return gzip.open(path, "rt", encoding="utf-8", errors="replace")
    return open(path, "r", encoding="utf-8", errors="replace")


def main() -> None:
    args = parser().parse_args()
    expression = ROOT / args.expression
    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)

    known_genes = {gene.upper() for genes in SIGNATURES.values() for gene in genes}
    aliases = read_aliases(ROOT / args.gene_aliases)
    wanted = expand_gene_filter(known_genes, aliases)

    kept = 0
    with open_text(expression) as src, open(out, "w", encoding="utf-8", newline="") as dst:
        header = src.readline()
        dst.write(header)
        for line in src:
            row_id = line.split("\t", 1)[0].split("|")[0].upper()
            if row_id in wanted:
                dst.write(line)
                kept += 1
    print(f"Wrote {out} with {kept} signature/alias rows")


if __name__ == "__main__":
    main()

