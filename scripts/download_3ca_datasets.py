from __future__ import annotations

import argparse
import tarfile
from pathlib import Path
from urllib.parse import unquote, urlparse
from urllib.request import Request, urlopen

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Download and extract selected public 3CA datasets from the dataset manifest.")
    p.add_argument("--manifest", default="data/processed/pan_cancer_emt_state_atlas/annotated_single_cell/3ca_dataset_manifest.tsv")
    p.add_argument("--raw-dir", default="data/raw/scrna/3ca")
    p.add_argument("--dataset", action="append", help="3CA dataset_name from the manifest. Repeatable.")
    p.add_argument("--max-cells", type=int, help="Optional maximum cell count for automatic selection.")
    p.add_argument("--limit", type=int, help="Optional maximum number of selected datasets.")
    return p


def filename_from_url(url: str, fallback: str) -> str:
    name = Path(unquote(urlparse(url).path)).name
    return name or fallback


def download(url: str, out_path: Path) -> None:
    if out_path.exists() and out_path.stat().st_size > 0:
        return
    request = Request(url, headers={"User-Agent": "Mozilla/5.0 EMT-State-Atlas/0.1"})
    with urlopen(request, timeout=300) as response:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("wb") as handle:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                handle.write(chunk)


def extract_tarball(path: Path, out_dir: Path) -> None:
    if out_dir.exists() and any(out_dir.iterdir()):
        return
    out_dir.mkdir(parents=True, exist_ok=True)
    with tarfile.open(path, "r:*") as tar:
        tar.extractall(out_dir)


def select_rows(manifest: pd.DataFrame, datasets: list[str] | None, max_cells: int | None, limit: int | None) -> pd.DataFrame:
    ready = manifest[manifest["download_status"].eq("ready")].copy()
    ready["cells"] = pd.to_numeric(ready["cells"], errors="coerce")
    if datasets:
        return ready[ready["dataset_name"].isin(datasets)].copy()
    if max_cells is not None:
        ready = ready[ready["cells"].le(max_cells)]
    ready = ready.sort_values(["cancer_group", "cells"])
    if limit:
        ready = ready.head(limit)
    return ready


def main() -> None:
    args = parser().parse_args()
    manifest = pd.read_csv(ROOT / args.manifest, sep="\t")
    rows = select_rows(manifest, args.dataset, args.max_cells, args.limit)
    raw_dir = ROOT / args.raw_dir
    records = []
    for _, row in rows.iterrows():
        dataset_name = row["dataset_name"]
        data_name = filename_from_url(row["data_url"], f"Data_{dataset_name}.tar.gz")
        meta_name = filename_from_url(row["metadata_url"], f"Meta-data_{dataset_name}.tar.gz")
        data_path = raw_dir / data_name
        meta_path = raw_dir / meta_name
        print(f"Downloading {dataset_name} data -> {data_path}")
        download(row["data_url"], data_path)
        print(f"Downloading {dataset_name} metadata -> {meta_path}")
        download(row["metadata_url"], meta_path)
        data_extract = raw_dir / data_name.replace(".tar.gz", "")
        meta_extract = raw_dir / meta_name.replace(".tar.gz", "")
        if data_path.suffixes[-2:] == [".tar", ".gz"]:
            extract_tarball(data_path, data_extract)
        if meta_path.suffixes[-2:] == [".tar", ".gz"]:
            extract_tarball(meta_path, meta_extract)
        records.append(
            {
                "dataset_name": dataset_name,
                "cancer_group": row["cancer_group"],
                "data_archive": str(data_path.relative_to(ROOT)),
                "metadata_archive": str(meta_path.relative_to(ROOT)),
                "data_dir": str(data_extract.relative_to(ROOT)),
                "metadata_dir": str(meta_extract.relative_to(ROOT)),
                "cells": row["cells"],
            }
        )
    out = raw_dir / "downloaded_3ca_datasets.tsv"
    pd.DataFrame(records).to_csv(out, sep="\t", index=False)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
