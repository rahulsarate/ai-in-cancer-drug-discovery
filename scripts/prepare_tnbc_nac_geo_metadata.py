from __future__ import annotations

import argparse
import csv
import gzip
import re
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


def clean_name(value: str) -> str:
    value = value.strip().strip('"').lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_") or "value"


def open_text(path: Path):
    return gzip.open(path, "rt", encoding="utf-8", errors="replace") if path.suffix == ".gz" else open(path, "rt", encoding="utf-8", errors="replace")


def parse_matrix_metadata(path: Path, dataset_id: str) -> tuple[pd.DataFrame, dict[str, object]]:
    sample_ids: list[str] = []
    sample_fields: dict[str, list[str]] = {}
    characteristics: dict[str, list[str]] = {}
    expression_rows = 0
    expression_columns = 0
    in_table = False

    with open_text(path) as handle:
        for line in handle:
            if line.startswith("!series_matrix_table_begin"):
                in_table = True
                continue
            if line.startswith("!series_matrix_table_end"):
                in_table = False
                continue
            row = next(csv.reader([line], delimiter="\t"))
            if not row:
                continue
            key = row[0]
            values = [value.strip().strip('"') for value in row[1:]]
            if in_table:
                if key == "ID_REF":
                    expression_columns = len(values)
                else:
                    expression_rows += 1
                continue
            if key == "!Sample_geo_accession":
                sample_ids = values
            elif key == "!Sample_characteristics_ch1" and values:
                split_values = []
                labels = []
                for value in values:
                    if ":" in value:
                        label, val = value.split(":", 1)
                        labels.append(clean_name(label))
                        split_values.append(val.strip())
                    else:
                        labels.append("characteristics")
                        split_values.append(value)
                label = most_common(labels)
                characteristics.setdefault(label, split_values)
            elif key.startswith("!Sample_") and values:
                field = clean_name(key.replace("!Sample_", ""))
                sample_fields[field] = values

    rows = []
    for i, sample_id in enumerate(sample_ids):
        record = {"dataset_id": dataset_id, "sample_id": sample_id}
        for key, values in sample_fields.items():
            if i < len(values):
                record[f"sample_{key}"] = values[i]
        for key, values in characteristics.items():
            if i < len(values):
                column = key if key not in record and key != "sample_id" else f"characteristic_{key}"
                record[column] = values[i]
        rows.append(record)

    dimensions = {
        "dataset_id": dataset_id,
        "matrix_path": str(path.relative_to(ROOT)),
        "sample_count": len(sample_ids),
        "expression_feature_count": expression_rows,
        "expression_sample_columns": expression_columns,
    }
    return pd.DataFrame(rows), dimensions


def most_common(values: list[str]) -> str:
    counts: dict[str, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))[0][0]


def value_contains(row: pd.Series, columns: list[str], patterns: list[str]) -> bool:
    text = " ".join(str(row.get(column, "")) for column in columns).lower()
    return any(re.search(pattern, text) for pattern in patterns)


def standardize_metadata(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.copy()
    all_cols = list(out.columns)
    receptor_cols = [c for c in all_cols if any(token in c for token in ["er_status", "pr_status", "her2", "erbb2", "estrogen", "progesterone", "er_pr_her2"])]
    response_cols = [c for c in all_cols if any(token in c for token in ["response", "pcr", "rcb", "miller", "clinical_response"])]
    time_cols = [c for c in all_cols if any(token in c for token in ["time_point", "day", "tissue", "source_name", "title"])]
    patient_cols = [c for c in all_cols if c in {"patient", "sample_id", "sample_title"} or c.endswith("_patient")]

    def infer_tnbc(row: pd.Series) -> bool:
        if str(row.get("dataset_id", "")) in {"GSE18864", "GSE43816", "GSE45898", "GSE43502", "GSE164715"}:
            return True
        er_value = first_nonempty(row, [c for c in receptor_cols if "er_status" in c or "estrogen" in c])
        pr_value = first_nonempty(row, [c for c in receptor_cols if "pr_status" in c or "progesterone" in c])
        her2_value = first_nonempty(row, [c for c in receptor_cols if "her2" in c or "erbb2" in c])
        direct_negative = is_negative_receptor(er_value) and is_negative_receptor(pr_value) and is_negative_receptor(her2_value)
        return (
            direct_negative
            or value_contains(row, receptor_cols, [r"triple.?negative", r"\bnegative\b.*\bnegative\b.*\bnegative\b", r"\bneg/neg/neg\b"])
            or (
                value_contains(row, receptor_cols, [r"er.?status.*neg|estrogen.*neg|er\s*[-:=]\s*neg|er_status_ihc.*neg"])
                and value_contains(row, receptor_cols, [r"pr.?status.*neg|progesterone.*neg|pr\s*[-:=]\s*neg|pr_status_ihc.*neg"])
                and value_contains(row, receptor_cols, [r"her2.*neg|erbb2.*neg|her2_status.*neg"])
            )
        )

    out["tnbc_confirmed_or_likely"] = out.apply(infer_tnbc, axis=1)

    def infer_timepoint(row: pd.Series) -> str:
        text = " ".join(str(row.get(column, "")) for column in time_cols).lower()
        dataset_id = str(row.get("dataset_id", ""))
        if any(token in text for token in ["before", "pretreatment", "pre-treatment", "biopsy", "day 0", "d0"]):
            return "T0"
        if any(token in text for token in ["after", "post", "tumorectomy", "surgery", "residual"]):
            return "T2"
        if any(token in text for token in ["day 3", "day 7", "day 14", "on-treatment", "on treatment"]):
            return "T1"
        if dataset_id in {"GSE18864", "GSE45898", "GSE25055", "GSE25065", "GSE25066", "GSE163882"}:
            return "T0"
        return "unknown"

    out["standard_timepoint"] = out.apply(infer_timepoint, axis=1)

    def infer_response(row: pd.Series) -> str:
        for column in response_cols:
            if "miller" in column:
                try:
                    value = float(str(row.get(column, "")).strip())
                except ValueError:
                    continue
                if value >= 4:
                    return "pcr_or_good_response"
                if value <= 3:
                    return "residual_or_poor_response"
        text = " ".join(str(row.get(column, "")) for column in response_cols).lower()
        if re.search(r"\bpcr\b|complete response|rcb[_\s-]*(0|i)\b|good", text):
            return "pcr_or_good_response"
        if re.search(r"\brd\b|residual disease|non.?pcr|poor|minor|absent|rcb[_\s-]*(ii|iii|2|3)", text):
            return "residual_or_poor_response"
        return "unknown"

    out["standard_response"] = out.apply(infer_response, axis=1)
    out["standard_patient_id"] = out.apply(lambda row: first_nonempty(row, patient_cols + ["characteristic_sample_id"]) or str(row["sample_id"]), axis=1)
    return out


def is_negative_receptor(value: str) -> bool:
    normalized = str(value).strip().lower()
    return normalized in {"n", "neg", "negative", "0", "false"}


def first_nonempty(row: pd.Series, columns: list[str]) -> str:
    for column in columns:
        value = str(row.get(column, "")).strip()
        if value and value.lower() not in {"nan", "none", "na"}:
            return value
    return ""


def write_markdown_summary(metadata: pd.DataFrame, dimensions: pd.DataFrame, out_path: Path) -> None:
    lines = [
        "# TNBC NAC GEO Metadata Preparation Summary",
        "",
        "## Matrix Dimensions",
        "",
        dimensions.to_markdown(index=False),
        "",
        "## Sample Counts By Dataset",
        "",
        metadata.groupby(["dataset_id", "standard_timepoint", "standard_response"], dropna=False)
        .size()
        .reset_index(name="samples")
        .to_markdown(index=False),
        "",
        "## TNBC-Likely Samples",
        "",
        metadata.groupby(["dataset_id", "tnbc_confirmed_or_likely"], dropna=False)
        .size()
        .reset_index(name="samples")
        .to_markdown(index=False),
        "",
        "## Notes",
        "",
        "- These are sample metadata and matrix-shape extracts from GEO series matrices.",
        "- Probe-to-gene mapping is the next step before EMT expression scoring on array datasets.",
        "- Response fields are standardized conservatively from GEO characteristics and should be manually reviewed before publication-grade modeling.",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Extract sample metadata from downloaded TNBC NAC GEO series matrices.")
    p.add_argument("--audit", default="data/processed/tnbc_digital_twin/tnbc_nac_geo_download_audit.tsv")
    p.add_argument("--out-dir", default="data/processed/tnbc_digital_twin")
    return p


def main() -> None:
    args = parser().parse_args()
    audit = pd.read_csv(ROOT / args.audit, sep="\t")
    out_dir = ROOT / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    metadata_frames = []
    dimension_rows = []
    for _, row in audit.iterrows():
        if row.get("download_status") == "failed":
            continue
        path = ROOT / str(row["local_path"])
        if not path.exists():
            continue
        metadata, dimensions = parse_matrix_metadata(path, str(row["dataset_id"]))
        metadata_frames.append(metadata)
        dimension_rows.append(dimensions)

    metadata_all = pd.concat(metadata_frames, ignore_index=True) if metadata_frames else pd.DataFrame()
    metadata_all = standardize_metadata(metadata_all)
    dimensions = pd.DataFrame(dimension_rows)

    metadata_all.to_csv(out_dir / "tnbc_nac_geo_sample_metadata.tsv", sep="\t", index=False)
    metadata_all[metadata_all["tnbc_confirmed_or_likely"]].to_csv(out_dir / "tnbc_nac_geo_tnbc_likely_samples.tsv", sep="\t", index=False)
    dimensions.to_csv(out_dir / "tnbc_nac_geo_matrix_dimensions.tsv", sep="\t", index=False)
    write_markdown_summary(metadata_all, dimensions, out_dir / "tnbc_nac_geo_metadata_summary.md")
    print(f"metadata_samples={metadata_all.shape[0]}")
    print(f"tnbc_likely_samples={int(metadata_all['tnbc_confirmed_or_likely'].sum()) if not metadata_all.empty else 0}")
    print(f"datasets={dimensions.shape[0]}")


if __name__ == "__main__":
    main()
