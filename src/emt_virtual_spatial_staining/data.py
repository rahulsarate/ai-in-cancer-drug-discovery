from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd

from .labels import add_virtual_stain_labels


IDENTITY_COLUMNS = [
    "spot_id",
    "sample_id",
    "section_id",
    "cohort",
    "cancer_type",
    "disease",
    "x",
    "y",
    "pixel_x",
    "pixel_y",
]


def load_scored_cohort(
    scores_path: str | Path,
    spatial_dir: str | Path,
    dataset_id: str | None = None,
) -> pd.DataFrame:
    scores_path = Path(scores_path)
    frame = pd.read_csv(scores_path, sep="\t", low_memory=False)
    frame["spot_id"] = frame["spot_id"].astype(str)
    frame["scores_path"] = str(scores_path.resolve())
    frame["spatial_dir"] = str(Path(spatial_dir).resolve())
    frame["dataset_id"] = dataset_id or scores_path.parent.name
    if "sample_id" not in frame.columns:
        frame["sample_id"] = frame["dataset_id"]
    return add_virtual_stain_labels(frame)


def combine_cohorts(entries: list[dict[str, str]]) -> pd.DataFrame:
    frames = [
        load_scored_cohort(entry["scores"], entry["spatial_dir"], entry.get("dataset_id"))
        for entry in entries
    ]
    if not frames:
        raise ValueError("At least one cohort entry is required")
    combined = pd.concat(frames, ignore_index=True, sort=False)
    combined["spot_uid"] = combined["dataset_id"].astype(str) + "::" + combined["spot_id"].astype(str)
    if combined["spot_uid"].duplicated().any():
        raise ValueError("Duplicate spot_uid values found after cohort merge")
    return combined


def deterministic_group_split(
    frame: pd.DataFrame,
    group_col: str = "sample_id",
    test_groups: set[str] | None = None,
    validation_fraction: float = 0.2,
    test_fraction: float = 0.2,
) -> pd.Series:
    groups = frame[group_col].fillna("unknown").astype(str)
    unique = sorted(groups.unique())
    test_groups = {str(value) for value in (test_groups or set())}
    explicit_test = bool(test_groups)

    mapping: dict[str, str] = {}
    for group in unique:
        if group in test_groups:
            mapping[group] = "test"
            continue
        digest = hashlib.sha256(group.encode("utf-8")).hexdigest()
        value = int(digest[:8], 16) / 0xFFFFFFFF
        if not explicit_test and value < test_fraction and len(unique) >= 5:
            mapping[group] = "test"
        elif value < (validation_fraction if explicit_test else test_fraction + validation_fraction) and len(unique) >= 3:
            mapping[group] = "validation"
        else:
            mapping[group] = "train"

    result = groups.map(mapping)
    if not result.eq("train").any():
        first = next((group for group in unique if group not in test_groups), unique[0])
        result.loc[groups.eq(first)] = "train"
    if not result.eq("test").any() and len(unique) > 1:
        result.loc[groups.eq(unique[-1])] = "test"
    return result


def write_training_pairs(frame: pd.DataFrame, out_path: str | Path) -> Path:
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(out, sep="\t", index=False)
    return out
