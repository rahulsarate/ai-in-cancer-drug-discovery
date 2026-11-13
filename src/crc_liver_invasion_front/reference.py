from __future__ import annotations

import gzip
from pathlib import Path

import numpy as np
import pandas as pd

from .signatures import required_genes


def map_author_cluster(cluster: str) -> str | None:
    cluster = str(cluster)
    if cluster.startswith("Tu"):
        return "malignant_crc"
    if cluster.startswith("F"):
        return "activated_fibroblast"
    if cluster.startswith("E"):
        return "endothelial"
    if "Mac" in cluster or cluster.startswith("M01_Mono"):
        return "macrophage_myeloid"
    return None


def _read_selected_gene_rows(counts_path: Path, wanted: set[str]) -> tuple[list[str], dict[str, np.ndarray]]:
    selected: dict[str, np.ndarray] = {}
    with gzip.open(counts_path, "rt", encoding="utf-8") as handle:
        header = [value.strip('"').replace(".", "-", 1) for value in handle.readline().rstrip("\n").split("\t")][1:]
        for line in handle:
            gene_field, values_field = line.rstrip("\n").split("\t", 1)
            gene = gene_field.strip('"').upper()
            if gene not in wanted:
                continue
            values = np.fromstring(values_field.replace('"', ""), sep="\t", dtype=float)
            if len(values) == len(header):
                selected[gene] = values
    return header, selected


def _pseudobulk_one(meta_path: Path, counts_path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    metadata = pd.read_csv(meta_path, sep="\t", index_col=0)
    metadata["reference_cell_type"] = metadata["cluster"].map(map_author_cluster)
    metadata = metadata[metadata["reference_cell_type"].notna()].copy()
    cell_ids, gene_rows = _read_selected_gene_rows(counts_path, required_genes())
    cell_type_by_id = metadata["reference_cell_type"].to_dict()
    assignments = np.asarray([cell_type_by_id.get(cell_id) for cell_id in cell_ids], dtype=object)
    cell_types = sorted({value for value in assignments if value is not None})
    rows: list[dict[str, object]] = []
    audit_rows: list[dict[str, object]] = []
    for cell_type in cell_types:
        mask = assignments == cell_type
        row: dict[str, object] = {"cell_type": cell_type}
        for gene, values in gene_rows.items():
            row[gene] = float(values[mask].mean()) if mask.any() else 0.0
        rows.append(row)
        audit_rows.append(
            {
                "source_file": meta_path.name,
                "cell_type": cell_type,
                "cells": int(mask.sum()),
                "genes_recovered": len(gene_rows),
            }
        )
    return pd.DataFrame(rows), pd.DataFrame(audit_rows)


def build_study_matched_reference(extract_dir: str | Path, output_dir: str | Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    root = Path(extract_dir)
    references: list[pd.DataFrame] = []
    audits: list[pd.DataFrame] = []
    for prefix in ("immune", "non_immune"):
        meta_matches = list(root.glob(f"*_{prefix}_meta.txt.gz"))
        count_matches = list(root.glob(f"*_{prefix}_counts.txt.gz"))
        if not meta_matches or not count_matches:
            continue
        reference, audit = _pseudobulk_one(meta_matches[0], count_matches[0])
        references.append(reference)
        audits.append(audit)
    if not references:
        raise FileNotFoundError("GSE225857 immune/non-immune count and metadata files were not found.")
    combined = pd.concat(references, ignore_index=True).fillna(0.0)
    genes = sorted(set(combined.columns) - {"cell_type"})
    reference = combined.groupby("cell_type", as_index=False)[genes].mean()
    values = reference[genes].to_numpy(dtype=float)
    totals = values.sum(axis=1, keepdims=True)
    totals[totals == 0] = 1.0
    reference[genes] = np.log1p(values / totals * 10_000.0)
    audit = pd.concat(audits, ignore_index=True)
    absent = pd.DataFrame(
        [
            {
                "source_file": "GSE225857 processed scRNA clusters",
                "cell_type": "hepatocyte",
                "cells": 0,
                "genes_recovered": len(genes),
                "status": "absent_from_author_processed_clusters",
            }
        ]
    )
    audit["status"] = "study_matched_reference"
    audit = pd.concat([audit, absent], ignore_index=True)
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    reference.to_csv(output / "gse225857_scrna_pseudobulk_reference.tsv", sep="\t", index=False)
    audit.to_csv(output / "gse225857_scrna_reference_audit.tsv", sep="\t", index=False)
    return reference, audit
