from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]


def download(url: str, local: Path) -> None:
    request = Request(url, headers={"User-Agent": "Mozilla/5.0 EMT-Metastasis-AI/0.1"})
    with urlopen(request, timeout=120) as response, open(local, "wb") as handle:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            handle.write(chunk)


def remote_size_mb(url: str) -> float | None:
    request = Request(url, method="HEAD", headers={"User-Agent": "Mozilla/5.0 EMT-Metastasis-AI/0.1"})
    try:
        with urlopen(request, timeout=30) as response:
            length = response.headers.get("Content-Length")
            return round(int(length) / (1024 * 1024), 2) if length else None
    except (HTTPError, URLError, TimeoutError, ValueError):
        return None


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="List or download public data manifest entries.")
    p.add_argument("--manifest", default="configs/public_data_manifest.json")
    p.add_argument("--group", choices=["tcga_xena", "target_ranker"])
    p.add_argument("--id", action="append", dest="ids", help="Download/list only a specific manifest id. Can be repeated.")
    p.add_argument("--download", action="store_true", help="Download entries that include a direct URL.")
    p.add_argument("--max-mb", type=float, help="Skip downloads larger than this size when Content-Length is available.")
    return p


def main() -> None:
    args = parser().parse_args()
    manifest_path = ROOT / args.manifest
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    groups = [args.group] if args.group else manifest.keys()

    for group in groups:
        print(f"\n[{group}]")
        for entry in manifest[group]:
            if args.ids and entry["id"] not in args.ids:
                continue
            local = ROOT / entry["local_path"]
            local.parent.mkdir(parents=True, exist_ok=True)
            print(f"- {entry['id']}: {entry['dataset_name']}")
            print(f"  source: {entry['source_page']}")
            print(f"  local:  {local}")
            if args.download:
                url = entry.get("url")
                if not url:
                    print("  download: skipped; manifest documents source page but no stable direct URL")
                    continue
                size = remote_size_mb(url)
                if size is not None:
                    print(f"  remote size: {size} MB")
                if args.max_mb is not None and size is not None and size > args.max_mb:
                    print(f"  download: skipped; larger than --max-mb {args.max_mb}")
                    continue
                print(f"  download: {url}")
                try:
                    download(url, local)
                except (HTTPError, URLError, TimeoutError) as exc:
                    print(f"  download: failed: {exc}")


if __name__ == "__main__":
    main()
