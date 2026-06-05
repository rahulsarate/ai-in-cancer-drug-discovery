from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Create a structured review pack for top ranked targets.")
    p.add_argument("--ranking", required=True)
    p.add_argument("--out", default="data/processed/target_review/top_target_review.tsv")
    p.add_argument("--top-n", type=int, default=20)
    return p


def category(score: float, missing: int) -> str:
    if missing >= 4:
        return "exploratory_missing_evidence"
    if score >= 0.70:
        return "immediate_review"
    if score >= 0.55:
        return "secondary_review"
    return "watchlist"


def main() -> None:
    args = parser().parse_args()
    ranking = pd.read_csv(ROOT / args.ranking, sep="\t").head(args.top_n)
    rows = []
    for _, row in ranking.iterrows():
        score = float(row.get("priority_score", 0))
        missing = int(row.get("missing_evidence_count", 0))
        rows.append(
            {
                "target": row["target"],
                "priority_score": round(score, 3),
                "family": row.get("family", ""),
                "review_category": category(score, missing),
                "decision": "requires_expert_review",
                "key_supporting_evidence": (
                    f"EMT={row.get('emt_state_specificity', '')}; "
                    f"druggability={row.get('druggability', '')}; "
                    f"compound={row.get('compound_availability', '')}; "
                    f"literature={row.get('literature_support', '')}"
                ),
                "key_concerns": f"Missing evidence categories: {missing}",
                "next_experiment": "Confirm malignant-cell expression, safety, and perturbation evidence before wet-lab prioritization.",
                "notes": "Computational triage only; not a clinical recommendation.",
            }
        )
    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out, sep="\t", index=False)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()

