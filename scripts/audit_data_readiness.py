from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Audit local public-data readiness from the manifest.")
    p.add_argument("--manifest", default="configs/public_data_manifest.json")
    p.add_argument("--out", default="data/processed/data_readiness.tsv")
    return p


def main() -> None:
    args = parser().parse_args()
    manifest = json.loads((ROOT / args.manifest).read_text(encoding="utf-8"))
    rows = []
    for group, entries in manifest.items():
        for entry in entries:
            local = ROOT / entry["local_path"]
            rows.append(
                {
                    "group": group,
                    "id": entry["id"],
                    "dataset_name": entry["dataset_name"],
                    "local_path": entry["local_path"],
                    "exists": local.exists(),
                    "size_mb": round(local.stat().st_size / (1024 * 1024), 2) if local.exists() else 0,
                    "has_direct_url": bool(entry.get("url")),
                    "source_page": entry.get("source_page", ""),
                }
            )

    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out, sep="\t", index=False)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()

