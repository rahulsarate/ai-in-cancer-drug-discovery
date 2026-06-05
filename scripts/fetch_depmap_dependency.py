from __future__ import annotations

import argparse
import csv
import io
from pathlib import Path
from urllib.request import Request, urlopen

import pandas as pd

from metastasis_target_ranker.ranking import starter_targets


ROOT = Path(__file__).resolve().parents[1]
DEPMAP_FILES_URL = "https://depmap.org/portal/api/download/files"


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Fetch DepMap release files and extract target-family dependency columns.")
    p.add_argument("--release", help="Release name, e.g. 'DepMap Public 26Q1'. Defaults to latest listed release.")
    p.add_argument("--out-dir", default="data/raw/depmap")
    p.add_argument("--extract-out", default="data/raw/depmap/target_family_CRISPRGeneEffect.csv")
    p.add_argument("--max-mb", type=float, default=700)
    return p


def read_file_manifest() -> pd.DataFrame:
    request = Request(DEPMAP_FILES_URL, headers={"Accept": "text/csv", "User-Agent": "Mozilla/5.0 EMT-Metastasis-AI/0.1"})
    with urlopen(request, timeout=120) as response:
        text = response.read().decode("utf-8", errors="replace")
    return pd.read_csv(io.StringIO(text))


def latest_release(files: pd.DataFrame) -> str:
    releases = files[["release", "release_date"]].drop_duplicates().sort_values("release_date", ascending=False)
    return str(releases.iloc[0]["release"])


def download_file(url: str, out: Path, max_mb: float) -> None:
    request = Request(url, headers={"User-Agent": "Mozilla/5.0 EMT-Metastasis-AI/0.1"})
    with urlopen(request, timeout=120) as response:
        length = response.headers.get("Content-Length")
        if length and int(length) / (1024 * 1024) > max_mb:
            raise RuntimeError(f"Remote file is {int(length) / (1024 * 1024):.1f} MB, above --max-mb {max_mb}.")
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "wb") as handle:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                handle.write(chunk)


def column_gene(column: str) -> str:
    return str(column).split(" (")[0].split("|")[0].upper()


def extract_target_columns(source: Path, out: Path) -> int:
    targets = set(starter_targets()["target"].astype(str).str.upper())
    with open(source, "r", encoding="utf-8", errors="replace", newline="") as src:
        reader = csv.reader(src)
        header = next(reader)
        keep_indices = [0]
        for idx, col in enumerate(header[1:], start=1):
            if column_gene(col) in targets:
                keep_indices.append(idx)
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8", newline="") as dst:
            writer = csv.writer(dst)
            writer.writerow([header[idx] for idx in keep_indices])
            row_count = 0
            for row in reader:
                writer.writerow([row[idx] if idx < len(row) else "" for idx in keep_indices])
                row_count += 1
    return row_count


def main() -> None:
    args = parser().parse_args()
    files = read_file_manifest()
    release = args.release or latest_release(files)
    selected = files[files["release"].eq(release)]
    out_dir = ROOT / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    wanted = {}
    for filename in ["CRISPRGeneEffect.csv", "Model.csv"]:
        hit = selected[selected["filename"].eq(filename)]
        if hit.empty:
            print(f"Missing {filename} in {release}")
            continue
        wanted[filename] = hit.iloc[0]["url"]

    for filename, url in wanted.items():
        local = out_dir / filename
        if local.exists():
            print(f"Already exists: {local}")
        else:
            print(f"Downloading {filename} from {release}")
            download_file(url, local, args.max_mb)
            print(f"Wrote {local}")

    source = out_dir / "CRISPRGeneEffect.csv"
    if source.exists():
        rows = extract_target_columns(source, ROOT / args.extract_out)
        print(f"Wrote {ROOT / args.extract_out} ({rows} models)")


if __name__ == "__main__":
    main()

