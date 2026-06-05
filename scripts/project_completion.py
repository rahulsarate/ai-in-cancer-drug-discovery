from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
STATUS_CREDIT = {
    "done": 1.0,
    "partial": 0.5,
    "blocked_external_data": 0.0,
    "not_started": 0.0,
}


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Calculate completion percentages for project modules.")
    p.add_argument("--criteria", default="configs/completion_criteria.json")
    p.add_argument("--out-dir", default="data/processed/project_status")
    return p


def percent(items: list[dict]) -> float:
    total = sum(float(item["weight"]) for item in items)
    earned = sum(float(item["weight"]) * STATUS_CREDIT[item["status"]] for item in items)
    return round(100 * earned / total, 1) if total else 0.0


def main() -> None:
    args = parser().parse_args()
    criteria = json.loads((ROOT / args.criteria).read_text(encoding="utf-8"))
    out_dir = ROOT / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    summary = []
    for project, items in criteria.items():
        project_percent = percent(items)
        summary.append({"project": project, "completion_percent": project_percent})
        for item in items:
            rows.append({"project": project, **item})

    detail = pd.DataFrame(rows)
    summary_frame = pd.DataFrame(summary)
    detail.to_csv(out_dir / "completion_detail.tsv", sep="\t", index=False)
    summary_frame.to_csv(out_dir / "completion_summary.tsv", sep="\t", index=False)

    lines = ["# Project Completion Status", ""]
    for row in summary:
        lines.append(f"- {row['project']}: {row['completion_percent']}%")
    lines.extend(["", "## Remaining Work", ""])
    for row in rows:
        if row["status"] != "done":
            lines.append(f"- {row['project']} / {row['id']}: {row['label']} ({row['status']})")
    (out_dir / "completion_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(summary_frame.to_string(index=False))


if __name__ == "__main__":
    main()
