from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
import yaml

from emt_virtual_spatial_staining.data import combine_cohorts, deterministic_group_split, write_training_pairs


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Build patient-safe EMT-ViSTA H&E/spatial training pairs.")
    p.add_argument("--config", default="configs/emt_virtual_spatial_staining.yml")
    p.add_argument("--out-dir")
    return p


def main() -> None:
    args = parser().parse_args()
    config = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    out_dir = Path(args.out_dir or config["output_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)
    frame = combine_cohorts(config["cohorts"])
    test_ids = {str(value) for value in config.get("test_dataset_ids", [])}
    frame["split"] = deterministic_group_split(frame, group_col="dataset_id", test_groups=test_ids)
    validation_ids = {str(value) for value in config.get("validation_dataset_ids", [])}
    if test_ids & validation_ids:
        raise ValueError("A dataset cannot be both a test and validation cohort")
    frame.loc[frame["dataset_id"].astype(str).isin(validation_ids), "split"] = "validation"
    frame.loc[
        ~frame["dataset_id"].astype(str).isin(test_ids | validation_ids),
        "split",
    ] = "train"
    pairs_path = write_training_pairs(frame, out_dir / "virtual_stain_training_pairs.tsv")

    summary = (
        frame.groupby(["dataset_id", "cancer_type", "split", "label_tier"], dropna=False)
        .agg(spots=("spot_uid", "count"), mean_label_confidence=("label_confidence", "mean"))
        .reset_index()
    )
    summary.to_csv(out_dir / "training_pair_summary.tsv", sep="\t", index=False)
    manifest = {
        "project": config.get("project", "EMT-ViSTA"),
        "pairs": str(pairs_path),
        "spots": len(frame),
        "datasets": int(frame["dataset_id"].nunique()),
        "split_counts": frame["split"].value_counts().to_dict(),
        "test_dataset_ids": sorted(test_ids),
        "validation_dataset_ids": sorted(validation_ids),
        "warning": "10x public examples are technical validation datasets, not clinical validation cohorts.",
    }
    (out_dir / "training_pair_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
