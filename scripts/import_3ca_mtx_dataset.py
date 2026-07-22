from __future__ import annotations

import argparse
import re
from pathlib import Path

import numpy as np
import pandas as pd

from emt_state_atlas.aliases import read_aliases
from emt_state_atlas.annotated_single_cell import add_malignant_stromal_emt_calls, normalize_annotation_columns
from emt_state_atlas.single_cell import score_single_cell_expression
from emt_state_atlas.signatures import SIGNATURES


ROOT = Path(__file__).resolve().parents[1]


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Import a 3CA MatrixMarket dataset into the annotated EMT single-cell layer.")
    p.add_argument("--dataset-name", default="Puram2017_Head-and-Neck")
    p.add_argument("--dataset-dir", default="data/raw/scrna/3ca/Data_Puram2017_Head-and-Neck")
    p.add_argument("--metadata-dir", default="data/raw/scrna/3ca/Meta-data_Puram2017_Head-and-Neck")
    p.add_argument("--cancer-group", default="Head and Neck Cancer")
    p.add_argument("--gene-aliases", default="data/raw/gene_aliases/signature_gene_aliases.tsv")
    p.add_argument("--out-dir", default="data/processed/pan_cancer_emt_state_atlas/annotated_single_cell/imports")
    return p


def wanted_genes(aliases: dict[str, list[str]]) -> set[str]:
    genes = {gene.upper() for values in SIGNATURES.values() for gene in values}
    for gene in list(genes):
        genes.update(alias.upper() for alias in aliases.get(gene, []))
    return genes


def read_genes(path: Path) -> list[str]:
    genes = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        genes.append(line.strip().strip('"').split("|")[0].upper())
    return genes


def read_cell_names(path: Path) -> list[str]:
    cells = pd.read_csv(path, usecols=["cell_name"])
    return cells["cell_name"].astype(str).tolist()


def find_file(folder: Path, names: list[str]) -> Path:
    for name in names:
        direct = folder / name
        if direct.exists():
            return direct
    for name in names:
        matches = sorted(folder.rglob(name))
        if matches:
            return matches[0]
    raise FileNotFoundError(f"Could not find any of {names} under {folder}")


def read_mtx_gene_subset(mtx_path: Path, genes_path: Path, cells_path: Path, keep_genes: set[str]) -> pd.DataFrame:
    genes = read_genes(genes_path)
    cell_names = read_cell_names(cells_path)
    keep_rows = {idx + 1: gene for idx, gene in enumerate(genes) if gene in keep_genes}
    selected = sorted(set(keep_rows.values()))
    gene_to_col = {gene: idx for idx, gene in enumerate(selected)}
    data = np.zeros((len(cell_names), len(selected)), dtype=np.float32)

    with open(mtx_path, "r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if not line or line.startswith("%"):
                continue
            parts = line.strip().split()
            if len(parts) == 3 and parts[0].isdigit() and parts[1].isdigit():
                n_rows, n_cols, _ = map(int, parts)
                if n_cols != len(cell_names):
                    raise ValueError(f"Matrix has {n_cols} cells but Cells.csv has {len(cell_names)}.")
                break
        for line in handle:
            parts = line.strip().split()
            if len(parts) != 3:
                continue
            gene_idx = int(parts[0])
            if gene_idx not in keep_rows:
                continue
            cell_idx = int(parts[1]) - 1
            value = float(parts[2])
            data[cell_idx, gene_to_col[keep_rows[gene_idx]]] = value
    frame = pd.DataFrame(np.log1p(data), index=cell_names, columns=selected)
    frame.index.name = "sample_id"
    return frame


def metadata(metadata_dir: Path, cancer_group: str, dataset_name: str) -> pd.DataFrame:
    cells = pd.read_csv(find_file(metadata_dir, ["Cells.csv"]))
    samples = pd.read_csv(find_file(metadata_dir, ["Samples.csv"]))
    cells["sample"] = cells["sample"].astype(str)
    samples["sample"] = samples["sample"].astype(str)
    merged = cells.merge(samples, on="sample", how="left", suffixes=("", "_sample"))
    merged["sample_id"] = merged["cell_name"].astype(str)
    inferred_missing_cell_type = "cell_type" not in merged.columns
    if inferred_missing_cell_type:
        merged["cell_type"] = "Malignant hematologic" if cancer_group == "Blood Tumors" else ""
        merged["cell_type_source"] = "inferred_from_cancer_group_due_missing_3ca_cell_type"
    merged["malignant_status"] = merged["cell_type"].astype(str).str.contains("malignant", case=False, na=False).map(
        {True: "malignant", False: "non-malignant"}
    )
    if cancer_group == "Blood Tumors" and inferred_missing_cell_type:
        merged["malignant_status"] = "malignant"
    merged["source"] = "3CA"
    merged["dataset"] = dataset_name
    merged["cancer_group"] = cancer_group
    return merged


def safe_slug(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", text).strip("_")


def main() -> None:
    args = parser().parse_args()
    dataset_dir = ROOT / args.dataset_dir
    metadata_dir = ROOT / args.metadata_dir
    out_dir = ROOT / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    aliases = read_aliases(ROOT / args.gene_aliases)
    expr = read_mtx_gene_subset(
        find_file(dataset_dir, ["Exp_data_TPM.mtx", "Exp_data_UMIcounts.mtx"]),
        find_file(dataset_dir, ["Genes.txt"]),
        find_file(dataset_dir, ["Cells.csv"]),
        wanted_genes(aliases),
    )
    meta = metadata(metadata_dir, args.cancer_group, args.dataset_name)
    scores = score_single_cell_expression(expr, meta, aliases=aliases)
    scores = normalize_annotation_columns(scores, dataset=args.dataset_name, source="3CA", cancer_group=args.cancer_group)
    scores = add_malignant_stromal_emt_calls(scores)
    stem = safe_slug(args.dataset_name)
    scores.to_csv(out_dir / f"{stem}_annotated_single_cell_emt_scores.tsv", sep="\t", index=False)
    summary = (
        scores.groupby(["source", "dataset", "cancer_group", "cell_compartment", "cell_type"], dropna=False)
        .agg(
            cells=("sample_id", "count"),
            emt_high_fraction=("emt_high_annotated", "mean"),
            tumor_intrinsic_emt_fraction=("tumor_intrinsic_emt_call", "mean"),
            caf_stromal_emt_fraction=("caf_stromal_emt_call", "mean"),
            tam_myeloid_emt_like_fraction=("tam_myeloid_emt_like_call", "mean"),
        )
        .reset_index()
    )
    summary.to_csv(out_dir / f"{stem}_annotated_single_cell_summary.tsv", sep="\t", index=False)
    print(f"Wrote {out_dir / f'{stem}_annotated_single_cell_emt_scores.tsv'}")


if __name__ == "__main__":
    main()
