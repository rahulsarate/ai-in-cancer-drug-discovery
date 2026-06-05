from __future__ import annotations

import argparse
import io
from pathlib import Path
from urllib.request import Request, urlopen

import pandas as pd

from metastasis_target_ranker.ranking import starter_targets


ROOT = Path(__file__).resolve().parents[1]
DEPMAP_FILES_URL = "https://depmap.org/portal/api/download/files"


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Fetch DepMap PortalCompounds and extract PRISM target-level hits.")
    p.add_argument("--release", default="DepMap Public 26Q1")
    p.add_argument("--raw-out", default="data/raw/prism/PortalCompounds.csv")
    p.add_argument("--out", default="data/raw/prism/prism_target_hits.tsv")
    return p


def depmap_files() -> pd.DataFrame:
    request = Request(DEPMAP_FILES_URL, headers={"Accept": "text/csv", "User-Agent": "Mozilla/5.0 EMT-Metastasis-AI/0.1"})
    with urlopen(request, timeout=120) as response:
        return pd.read_csv(io.StringIO(response.read().decode("utf-8", errors="replace")))


def download(url: str, out: Path) -> None:
    request = Request(url, headers={"User-Agent": "Mozilla/5.0 EMT-Metastasis-AI/0.1"})
    with urlopen(request, timeout=120) as response:
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "wb") as handle:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                handle.write(chunk)


def split_targets(value: str) -> list[str]:
    if pd.isna(value):
        return []
    text = str(value).replace(",", ";").replace("|", ";")
    return [part.strip().upper() for part in text.split(";") if part.strip()]


def main() -> None:
    args = parser().parse_args()
    files = depmap_files()
    hit = files[(files["release"].eq(args.release)) & (files["filename"].eq("PortalCompounds.csv"))]
    if hit.empty:
        hit = files[files["filename"].eq("PortalCompounds.csv")].sort_values("release_date", ascending=False).head(1)
    if hit.empty:
        raise RuntimeError("Could not find PortalCompounds.csv in DepMap file list.")

    raw = ROOT / args.raw_out
    if not raw.exists():
        download(hit.iloc[0]["url"], raw)

    compounds = pd.read_csv(raw)
    target_set = set(starter_targets()["target"].astype(str).str.upper())
    rows = []
    for _, row in compounds.iterrows():
        for target in split_targets(row.get("GeneSymbolOfTargets")):
            if target in target_set:
                rows.append(
                    {
                        "target": target,
                        "compound_name": row.get("CompoundName"),
                        "screen_metric": "portal_compound_target_annotation",
                        "effect_size": "",
                        "source_url": "https://depmap.org/repurposing/",
                        "notes": row.get("TargetOrMechanism", ""),
                    }
                )
    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).drop_duplicates().to_csv(out, sep="\t", index=False)
    print(f"Wrote {out} ({len(rows)} target-compound rows)")


if __name__ == "__main__":
    main()

