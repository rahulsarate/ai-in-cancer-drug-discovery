from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from emt_state_atlas.io import read_table
from emt_state_atlas.metadata import harmonize_metadata
from metastasis_target_ranker.evidence import build_evidence_tables, read_table as read_optional_table
from metastasis_target_ranker.ranking import merge_evidence, rank_targets, starter_targets
from metastasis_target_ranker.reports import write_target_cards, write_target_summary


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Build target-ranker evidence tables and reports.")
    p.add_argument("--expression")
    p.add_argument("--emt-scores")
    p.add_argument("--metadata")
    p.add_argument("--depmap-gene-effect")
    p.add_argument("--open-targets")
    p.add_argument("--chembl")
    p.add_argument("--dgidb")
    p.add_argument("--prism")
    p.add_argument("--lincs")
    p.add_argument("--out-dir", default="data/processed/target_ranker_v1")
    p.add_argument("--top-n", type=int, default=20)
    return p


def main() -> None:
    args = parser().parse_args()
    out = Path(args.out_dir)
    evidence_dir = out / "evidence_tables"
    cards_dir = out / "target_cards"
    evidence_dir.mkdir(parents=True, exist_ok=True)

    expression = read_table(args.expression) if args.expression else None
    scores = read_table(args.emt_scores) if args.emt_scores else None
    metadata = harmonize_metadata(read_table(args.metadata)) if args.metadata else None
    base = starter_targets()

    tables = build_evidence_tables(
        base=base,
        expression=expression,
        scores=scores,
        metadata=metadata,
        depmap_gene_effect=read_optional_table(args.depmap_gene_effect),
        open_targets=read_optional_table(args.open_targets),
        chembl=read_optional_table(args.chembl),
        dgidb=read_optional_table(args.dgidb),
        prism=read_optional_table(args.prism),
        lincs=read_optional_table(args.lincs),
    )

    input_audit = pd.DataFrame(
        [
            {"source": "expression", "path": args.expression, "available": bool(args.expression)},
            {"source": "emt_scores", "path": args.emt_scores, "available": bool(args.emt_scores)},
            {"source": "metadata", "path": args.metadata, "available": bool(args.metadata)},
            {"source": "depmap_gene_effect", "path": args.depmap_gene_effect, "available": bool(args.depmap_gene_effect)},
            {"source": "open_targets", "path": args.open_targets, "available": bool(args.open_targets)},
            {"source": "chembl", "path": args.chembl, "available": bool(args.chembl)},
            {"source": "dgidb", "path": args.dgidb, "available": bool(args.dgidb)},
            {"source": "prism", "path": args.prism, "available": bool(args.prism)},
            {"source": "lincs", "path": args.lincs, "available": bool(args.lincs)},
        ]
    )
    input_audit.to_csv(out / "input_availability.tsv", sep="\t", index=False)

    table_list = []
    for name, table in tables.items():
        path = evidence_dir / f"{name}.tsv"
        table.to_csv(path, sep="\t", index=False)
        table_list.append(table)

    ranked = rank_targets(merge_evidence(base, table_list))
    out.mkdir(parents=True, exist_ok=True)
    ranked.to_csv(out / "target_ranking.tsv", sep="\t", index=False)
    write_target_summary(ranked, out / "target_ranking_report.md", top_n=args.top_n)
    write_target_cards(ranked, cards_dir, top_n=args.top_n)


if __name__ == "__main__":
    main()
