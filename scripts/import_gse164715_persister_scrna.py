from __future__ import annotations

import argparse
import csv
import gzip
import re
import sys
import tarfile
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml
from scipy.io import mmread


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from emt_state_atlas.scoring import score_expression  # noqa: E402
from emt_state_atlas.signatures import SIGNATURES  # noqa: E402


SELECTED_SAMPLE_PREFIXES = [
    "GSM5017696_HBCx95_chemonaive",
    "GSM5017697_HBCx95_persister",
    "GSM5017698_HBCx95_recurrent",
    "GSM5017699_HBCx95_residual",
    "GSM5017700_HBCx95_resistant",
    "GSM5662564_HBCx39_chemonaive",
    "GSM5662565_HBCx39_persister",
    "GSM5662566_HBCx172_chemonaive",
    "GSM5662567_HBCx172_persister",
]

STAGE_ORDER = ["chemonaive", "persister", "residual", "resistant", "recurrent"]
METADATA_SAMPLE_ALIASES = {
    "HBCx39_chemonaive": "BC408_chemonaive",
    "HBCx39_persister": "BC408_persister",
    "HBCx172_chemonaive": "BC1224_chemonaive",
    "HBCx172_persister": "BC1224_persister",
}


def load_signature_genes(config_path: Path) -> tuple[set[str], dict[str, list[str]]]:
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    signatures = {name: [gene.upper() for gene in genes] for name, genes in SIGNATURES.items()}

    def collect(prefix: str, value):
        if isinstance(value, list):
            signatures[prefix] = [gene.upper() for gene in value]
        elif isinstance(value, dict):
            for key, nested in value.items():
                collect(f"tnbc_{key}", nested)

    collect("tnbc", config.get("signature_blocks", {}))
    signatures["tnbc_proliferation"] = ["MKI67", "TOP2A", "PCNA", "MCM2", "MCM4", "MCM6", "CCNB1", "AURKA", "BIRC5"]
    signatures["tnbc_immune_checkpoint"] = ["CD274", "PDCD1", "CTLA4", "LAG3", "TIGIT", "HAVCR2", "PDCD1LG2"]
    genes = {gene for gene_list in signatures.values() for gene in gene_list}
    return genes, signatures


def safe_extract_selected(tar_path: Path, extract_dir: Path, prefixes: list[str]) -> pd.DataFrame:
    extract_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    with tarfile.open(tar_path) as tar:
        for member in tar.getmembers():
            name = Path(member.name).name
            if not any(name.startswith(prefix) for prefix in prefixes):
                continue
            if Path(member.name).is_absolute() or ".." in Path(member.name).parts:
                raise RuntimeError(f"Unsafe tar member path: {member.name}")
            target = extract_dir / name
            status = "exists" if target.exists() and target.stat().st_size == member.size else "extracted"
            if status == "extracted":
                with tar.extractfile(member) as source, open(target, "wb") as handle:
                    if source is None:
                        continue
                    while True:
                        chunk = source.read(1024 * 1024)
                        if not chunk:
                            break
                        handle.write(chunk)
            rows.append({"file_name": name, "size": member.size, "local_path": str(target.relative_to(ROOT)), "status": status})
    return pd.DataFrame(rows)


def infer_sample_name(prefix: str) -> str:
    match = re.match(r"GSM\d+_(.+)", prefix)
    return match.group(1) if match else prefix


def infer_stage(sample_name: str) -> str:
    lowered = sample_name.lower()
    for stage in STAGE_ORDER:
        if stage in lowered:
            return stage
    if "5fu" in lowered:
        return "treated"
    return "other"


def read_barcodes(path: Path) -> list[str]:
    with gzip.open(path, "rt", encoding="utf-8", errors="replace") as handle:
        return [line.strip().split("\t")[0] for line in handle if line.strip()]


def read_target_feature_indices(path: Path, target_genes: set[str]) -> tuple[dict[int, str], int]:
    target_indices: dict[int, str] = {}
    total = 0
    with gzip.open(path, "rt", encoding="utf-8", errors="replace") as handle:
        for idx, line in enumerate(handle, start=1):
            total += 1
            row = line.rstrip("\n").split("\t")
            symbol = row[1].upper() if len(row) > 1 else row[0].upper()
            symbol = re.sub(r"^(HG19|MM10|GRCH38|HUMAN|MOUSE)_", "", symbol)
            if symbol in target_genes:
                target_indices[idx] = symbol
    return target_indices, total


def read_signature_counts(matrix_path: Path, target_indices: dict[int, str], n_cells: int) -> pd.DataFrame:
    with gzip.open(matrix_path, "rb") as handle:
        matrix = mmread(handle).tocsr()
    gene_rows: dict[str, list[int]] = defaultdict(list)
    for one_based_idx, gene in target_indices.items():
        zero_based_idx = one_based_idx - 1
        if 0 <= zero_based_idx < matrix.shape[0]:
            gene_rows[gene].append(zero_based_idx)

    data = {}
    for gene, rows in sorted(gene_rows.items()):
        values = np.asarray(matrix[rows, :].sum(axis=0)).ravel().astype(np.float32)
        data[gene] = values[:n_cells] if values.shape[0] >= n_cells else np.pad(values, (0, n_cells - values.shape[0]))
    return pd.DataFrame(data)


def load_metadata(metadata_dir: Path) -> pd.DataFrame:
    frames = []
    for path in metadata_dir.glob("GSE164715_metadata_scRNA*.csv.gz"):
        df = pd.read_csv(path)
        df["metadata_file"] = path.name
        frames.append(df)
    if not frames:
        return pd.DataFrame()
    metadata = pd.concat(frames, ignore_index=True, sort=False)
    if "barcode" not in metadata.columns and "BC_10x" in metadata.columns:
        metadata["barcode"] = metadata["BC_10x"]
    if "barcode" in metadata.columns:
        metadata["barcode"] = metadata["barcode"].astype(str)
    if "sample_id" in metadata.columns:
        metadata["sample_id"] = metadata["sample_id"].astype(str)
    return metadata


def load_sample_expression(prefix: str, raw_dir: Path, metadata: pd.DataFrame, target_genes: set[str]) -> tuple[pd.DataFrame, dict[str, object], pd.DataFrame]:
    sample_name = infer_sample_name(prefix)
    barcodes_path = raw_dir / f"{prefix}_barcodes.tsv.gz"
    features_path = raw_dir / f"{prefix}_features.tsv.gz"
    matrix_path = raw_dir / f"{prefix}_matrix.mtx.gz"
    barcodes = read_barcodes(barcodes_path)
    target_indices, feature_count = read_target_feature_indices(features_path, target_genes)
    counts = read_signature_counts(matrix_path, target_indices, len(barcodes))
    counts.insert(0, "barcode", barcodes)
    counts.insert(0, "sample_name", sample_name)

    metadata_sample_name = METADATA_SAMPLE_ALIASES.get(sample_name, sample_name)
    sample_meta = metadata[metadata.get("sample_id", pd.Series(dtype=str)).astype(str).eq(metadata_sample_name)].copy()
    if sample_meta.empty and "cell_id" in metadata.columns:
        sample_meta = metadata[metadata["cell_id"].astype(str).str.startswith(metadata_sample_name + "_", na=False)].copy()
    if "barcode" in sample_meta.columns and not sample_meta.empty:
        meta_cols = [col for col in ["barcode", "cell_id", "total_counts", "total_features", "cell_cycle", "louvain_cluster", "louvain_partition", "Seurat_cluster"] if col in sample_meta.columns]
        counts = counts.merge(sample_meta[meta_cols].drop_duplicates("barcode"), on="barcode", how="left")

    gene_cols = [col for col in counts.columns if col.upper() in target_genes]
    if "total_counts" in counts.columns:
        total_counts = pd.to_numeric(counts["total_counts"], errors="coerce")
    else:
        total_counts = pd.Series(np.nan, index=counts.index)
    if total_counts.isna().all():
        total_counts = counts[gene_cols].sum(axis=1)
    total_counts = total_counts.replace(0, np.nan).fillna(total_counts.median() if not total_counts.dropna().empty else 1.0)
    norm = np.log1p(counts[gene_cols].div(total_counts, axis=0) * 10000.0)
    gene_means = norm.mean(axis=0).reset_index()
    gene_means.columns = ["gene_symbol", "mean_log1p_cpm"]
    gene_means["sample_name"] = sample_name
    gene_means["model"] = sample_name.split("_")[0]
    gene_means["stage"] = infer_stage(sample_name)
    gene_means = gene_means[["model", "sample_name", "stage", "gene_symbol", "mean_log1p_cpm"]]
    cell_expr = norm.copy()
    cell_expr.insert(0, "stage", infer_stage(sample_name))
    cell_expr.insert(0, "model", sample_name.split("_")[0])
    cell_expr.insert(0, "sample_name", sample_name)
    cell_expr.insert(3, "barcode", counts["barcode"].values)
    if "cell_id" in counts.columns:
        cell_expr["cell_id"] = counts["cell_id"].values
    audit = {
        "sample_name": sample_name,
        "metadata_sample_name": metadata_sample_name,
        "stage": infer_stage(sample_name),
        "cells": len(barcodes),
        "features_total": feature_count,
        "target_feature_rows": len(target_indices),
        "target_genes_detected": len(set(target_indices.values())),
        "metadata_rows_matched": int(sample_meta.shape[0]),
    }
    return cell_expr, audit, gene_means


def summarize_scores(scores: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    score_cols = [
        "emt_score",
        "partial_emt_score",
        "mesenchymal",
        "epithelial",
        "tnbc_stemness_persister",
        "tnbc_persister_tumor_refined",
        "tnbc_persister_stress_tolerance",
        "tnbc_persister_niche",
        "tnbc_tgfb",
        "tnbc_axl_tam",
        "tnbc_hypoxia",
        "tnbc_yap_taz",
        "caf_tam_niche",
    ]
    score_cols = [col for col in score_cols if col in scores.columns]
    summary = scores.groupby(["model", "sample_name", "stage"])[score_cols].agg(["mean", "median", "std"]).reset_index()
    summary.columns = ["_".join(col).strip("_") if isinstance(col, tuple) else col for col in summary.columns]

    contrasts = []
    for model, group in scores.groupby("model"):
        baseline = group[group["stage"] == "chemonaive"]
        if baseline.empty:
            continue
        for stage, stage_group in group.groupby("stage"):
            if stage == "chemonaive":
                continue
            row = {"model": model, "contrast": f"{stage}_minus_chemonaive", "stage_cells": int(stage_group.shape[0]), "chemonaive_cells": int(baseline.shape[0])}
            for col in score_cols:
                row[f"{col}_delta_mean"] = float(stage_group[col].mean() - baseline[col].mean())
            contrasts.append(row)
    return summary, pd.DataFrame(contrasts)


def build_gene_contrasts(gene_means: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for model, group in gene_means.groupby("model"):
        baseline = group[group["stage"] == "chemonaive"]
        if baseline.empty:
            continue
        baseline_mean = baseline.groupby("gene_symbol")["mean_log1p_cpm"].mean()
        for stage, stage_group in group.groupby("stage"):
            if stage == "chemonaive":
                continue
            stage_mean = stage_group.groupby("gene_symbol")["mean_log1p_cpm"].mean()
            for gene in sorted(set(stage_mean.index).intersection(baseline_mean.index)):
                rows.append(
                    {
                        "model": model,
                        "contrast": f"{stage}_minus_chemonaive",
                        "stage": stage,
                        "gene_symbol": gene,
                        "stage_mean_log1p_cpm": float(stage_mean[gene]),
                        "chemonaive_mean_log1p_cpm": float(baseline_mean[gene]),
                        "delta_mean_log1p_cpm": float(stage_mean[gene] - baseline_mean[gene]),
                    }
                )
    if not rows:
        return pd.DataFrame()
    contrasts = pd.DataFrame(rows)
    return contrasts.sort_values(["contrast", "delta_mean_log1p_cpm"], ascending=[True, False])


def save_stage_plot(scores: pd.DataFrame, out_path: Path) -> None:
    features = [
        feature
        for feature in ["tnbc_stemness_persister", "tnbc_persister_tumor_refined", "tnbc_persister_stress_tolerance", "tnbc_persister_niche"]
        if feature in scores.columns
    ]
    fig, axes = plt.subplots(1, len(features), figsize=(4.3 * len(features), 4.2), constrained_layout=True)
    if len(features) == 1:
        axes = [axes]
    ordered = [stage for stage in STAGE_ORDER if stage in set(scores["stage"])]
    for ax, feature in zip(axes, features):
        data = [scores[scores["stage"] == stage][feature].dropna() for stage in ordered]
        ax.boxplot(data, tick_labels=ordered, showfliers=False, patch_artist=True)
        ax.set_title(feature.replace("_", " "))
        ax.tick_params(axis="x", rotation=30)
    fig.suptitle("GSE164715 scRNA signature scores by persister stage", fontsize=13)
    fig.savefig(out_path, dpi=180)
    plt.close(fig)


def save_model_contrast_plot(contrasts: pd.DataFrame, out_path: Path) -> None:
    if contrasts.empty:
        return
    feature = "tnbc_persister_tumor_refined_delta_mean" if "tnbc_persister_tumor_refined_delta_mean" in contrasts.columns else "tnbc_stemness_persister_delta_mean"
    if feature not in contrasts.columns:
        feature = [col for col in contrasts.columns if col.endswith("_delta_mean")][0]
    pivot = contrasts.pivot(index="model", columns="contrast", values=feature).fillna(0)
    ax = pivot.plot(kind="bar", figsize=(8, 4.5))
    ax.set_ylabel(feature.replace("_delta_mean", " delta mean").replace("_", " "))
    ax.set_title("Persister-stage shift versus chemonaive")
    ax.axhline(0, color="#777777", linewidth=1)
    ax.tick_params(axis="x", rotation=0)
    ax.legend(frameon=False, bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.tight_layout()
    plt.savefig(out_path, dpi=180)
    plt.close()


def write_report(audit: pd.DataFrame, summary: pd.DataFrame, contrasts: pd.DataFrame, gene_contrasts: pd.DataFrame, image_paths: dict[str, Path], out_path: Path) -> None:
    top_genes = gene_contrasts[gene_contrasts["contrast"].str.contains("persister", na=False)].head(25) if not gene_contrasts.empty else pd.DataFrame()
    lines = [
        "# GSE164715 Persister scRNA Import Report",
        "",
        "## Imported Samples",
        "",
        audit.to_markdown(index=False),
        "",
        "## Stage-Level Signature Summary",
        "",
        summary.head(30).to_markdown(index=False),
        "",
        "## Chemonaive Contrast Summary",
        "",
        contrasts.to_markdown(index=False) if not contrasts.empty else "No chemonaive contrasts available.",
        "",
        "## Top Targeted Genes Increased in Persister Contrasts",
        "",
        top_genes.to_markdown(index=False) if not top_genes.empty else "No persister gene contrasts available.",
        "",
        "## Plots",
        "",
        f"![Stage score distributions]({image_paths['stage_plot'].as_posix()})",
        "",
        f"![Model contrasts]({image_paths['contrast_plot'].as_posix()})",
        "",
        "## Digital-Twin Impact",
        "",
        "- These scRNA-derived score distributions are the first real single-cell evidence layer for the `P` persister state.",
        "- The current import is signature-targeted rather than full transcriptome object construction, keeping the project lightweight and reproducible.",
        "- The next refinement should convert high-scoring persister cells into a marker list for updating `tnbc_stemness_persister` and the E/H/M/P state estimator.",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Import selected GSE164715 scRNA matrices and score persister-state signatures.")
    p.add_argument("--tar", default="data/raw/tnbc_nac/geo/GSE164715/suppl/GSE164715_RAW.tar")
    p.add_argument("--metadata-dir", default="data/raw/tnbc_nac/geo/GSE164715/suppl")
    p.add_argument("--extract-dir", default="data/raw/tnbc_nac/geo/GSE164715/selected_raw")
    p.add_argument("--out-dir", default="data/processed/tnbc_digital_twin/gse164715_persister_scrna")
    p.add_argument("--docs-dir", default="docs/tnbc_digital_twin_emt_plasticity")
    p.add_argument("--config", default="configs/tnbc_digital_twin.yml")
    return p


def main() -> None:
    args = parser().parse_args()
    out_dir = ROOT / args.out_dir
    asset_dir = ROOT / args.docs_dir / "assets" / "gse164715_persister_scrna"
    out_dir.mkdir(parents=True, exist_ok=True)
    asset_dir.mkdir(parents=True, exist_ok=True)
    extract_dir = ROOT / args.extract_dir

    target_genes, signatures = load_signature_genes(ROOT / args.config)
    extraction_audit = safe_extract_selected(ROOT / args.tar, extract_dir, SELECTED_SAMPLE_PREFIXES)
    metadata = load_metadata(ROOT / args.metadata_dir)

    expr_frames = []
    gene_mean_frames = []
    audit_rows = []
    for prefix in SELECTED_SAMPLE_PREFIXES:
        cell_expr, audit, gene_means = load_sample_expression(prefix, extract_dir, metadata, target_genes)
        expr_frames.append(cell_expr)
        gene_mean_frames.append(gene_means)
        audit_rows.append(audit)
    expr_all = pd.concat(expr_frames, ignore_index=True)
    metadata_cols = [col for col in ["model", "sample_name", "stage", "barcode", "cell_id"] if col in expr_all.columns]
    gene_cols = [col for col in expr_all.columns if col not in metadata_cols]
    score_input = expr_all[gene_cols].copy()
    score_input.index = [
        f"{row.sample_name}_{row.barcode}"
        for row in expr_all[["sample_name", "barcode"]].itertuples(index=False)
    ]
    scores_all = score_expression(score_input, signatures=signatures)
    scores_all = pd.concat([expr_all[metadata_cols].reset_index(drop=True), scores_all.reset_index(drop=True)], axis=1)
    gene_means_all = pd.concat(gene_mean_frames, ignore_index=True)
    import_audit = pd.DataFrame(audit_rows)
    summary, contrasts = summarize_scores(scores_all)
    gene_contrasts = build_gene_contrasts(gene_means_all)

    extraction_audit.to_csv(out_dir / "gse164715_selected_extraction_audit.tsv", sep="\t", index=False)
    import_audit.to_csv(out_dir / "gse164715_scrna_import_audit.tsv", sep="\t", index=False)
    scores_all.to_csv(out_dir / "gse164715_persister_scrna_cell_scores.tsv.gz", sep="\t", index=False, compression="gzip")
    gene_means_all.to_csv(out_dir / "gse164715_persister_signature_gene_means.tsv", sep="\t", index=False)
    gene_contrasts.to_csv(out_dir / "gse164715_persister_signature_gene_contrasts.tsv", sep="\t", index=False)
    summary.to_csv(out_dir / "gse164715_persister_scrna_stage_summary.tsv", sep="\t", index=False)
    contrasts.to_csv(out_dir / "gse164715_persister_scrna_chemonaive_contrasts.tsv", sep="\t", index=False)

    image_paths = {
        "stage_plot": asset_dir / "gse164715_stage_score_distributions.png",
        "contrast_plot": asset_dir / "gse164715_chemonaive_contrasts.png",
    }
    save_stage_plot(scores_all, image_paths["stage_plot"])
    save_model_contrast_plot(contrasts, image_paths["contrast_plot"])
    write_report(import_audit, summary, contrasts, gene_contrasts, image_paths, out_dir / "gse164715_persister_scrna_import_report.md")
    print(f"cells={scores_all.shape[0]} samples={import_audit.shape[0]} genes_targeted={len(target_genes)}")
    print(import_audit.to_string(index=False))


if __name__ == "__main__":
    main()
