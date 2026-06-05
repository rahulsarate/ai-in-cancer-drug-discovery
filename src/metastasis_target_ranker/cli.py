from __future__ import annotations

import argparse
from pathlib import Path

from .ranking import load_optional_table, merge_evidence, rank_targets, starter_targets
from .reports import write_target_cards, write_target_summary


def load_config(path: str) -> dict:
    try:
        import yaml
    except ImportError:
        if Path(path).name == "target_ranker.yml":
            return {}
        raise RuntimeError("Install PyYAML to use a custom target-ranker config.")

    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Rank EMT/metastasis target candidates.")
    parser.add_argument("--config", default="configs/target_ranker.yml")
    parser.add_argument("--out", required=True)
    parser.add_argument("--cards-dir", help="Optional directory for Markdown evidence cards.")
    parser.add_argument("--report-out", help="Optional Markdown target summary report.")
    parser.add_argument("--top-n", type=int, default=20)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    config = load_config(args.config)

    base_path = config.get("base_targets")
    base = load_optional_table(base_path) if base_path else starter_targets()
    tables = [load_optional_table(path) for path in config.get("evidence_tables", {}).values()]
    ranked = rank_targets(merge_evidence(base, tables), weights=config.get("weights"))

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    ranked.to_csv(out, sep="\t", index=False)

    if args.cards_dir:
        write_target_cards(ranked, args.cards_dir, top_n=args.top_n)
    if args.report_out:
        write_target_summary(ranked, args.report_out, top_n=args.top_n)


if __name__ == "__main__":
    main()
