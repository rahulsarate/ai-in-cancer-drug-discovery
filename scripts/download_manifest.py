from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.request import urlretrieve


ROOT = Path(__file__).resolve().parents[1]


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="List or download public data manifest entries.")
    p.add_argument("--manifest", default="configs/public_data_manifest.json")
    p.add_argument("--group", choices=["tcga_xena", "target_ranker"])
    p.add_argument("--download", action="store_true", help="Download entries that include a direct URL.")
    return p


def main() -> None:
    args = parser().parse_args()
    manifest_path = ROOT / args.manifest
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    groups = [args.group] if args.group else manifest.keys()

    for group in groups:
        print(f"\n[{group}]")
        for entry in manifest[group]:
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
                print(f"  download: {url}")
                urlretrieve(url, local)


if __name__ == "__main__":
    main()

