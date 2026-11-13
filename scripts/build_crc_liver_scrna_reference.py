from __future__ import annotations

import argparse

from crc_liver_invasion_front.reference import build_study_matched_reference


def main() -> None:
    parser = argparse.ArgumentParser(description="Build study-matched GSE225857 scRNA pseudobulk references.")
    parser.add_argument("--extract-dir", default="data/raw/spatial/geo/GSE225857/extract")
    parser.add_argument("--out-dir", default="data/processed/crc_liver_invasion_front_v1/reference")
    args = parser.parse_args()
    reference, audit = build_study_matched_reference(args.extract_dir, args.out_dir)
    print(f"Built {len(reference)} study-matched reference compartments from {int(audit['cells'].sum()):,} cells.")


if __name__ == "__main__":
    main()
