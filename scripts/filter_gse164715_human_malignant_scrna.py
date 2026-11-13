from __future__ import annotations

import argparse
import gzip
import re
import sys
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


def load_signatures(config_path: Path) -> tuple[set[str], dict[str, list[str]]]:
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


def sample_name_from_prefix(prefix: str) -> str:
    match = re.match(r"GSM\d+_(.+)", prefix)
    return match.group(1) if match else prefix


def infer_stage(sample_name: str) -> str:
    lowered = sample_name.lower()
    for stage in STAGE_ORDER:
        if stage in lowered:
            return stage
    return "other"


def read_barcodes(path: Path) -> list[str]:
    with gzip.open(path, "rt", encoding="utf-8", errors="replace") as handle:
        return [line.strip().split("\t")[0] for line in handle if line.strip()]


def parse_features(path: Path, target_genes: set[str]) -> tuple[list[str], dict[str, list[int]], dict[str, dict[str, list[int]]]]:
    species_by_row: list[str] = []
    species_rows: dict[str, list[int]] = defaultdict(list)
    target_rows: dict[str, dict[str, list[int]]] = {"hg19": defaultdict(list), "mm10": defaultdict(list)}
    with gzip.open(path, "rt", encoding="utf-8", errors="replace") as handle:
        for zero_idx, line in enumerate(handle):
            row = line.rstrip("\n").split("\t")
            symbol = row[1].upper() if len(row) > 1 else row[0].upper()
            species = symbol.split("_", 1)[0].lower() if "_" in symbol else "unknown"
            gene = re.sub(r"^(HG19|MM10|GRCH38|HUMAN|MOUSE)_", "", symbol)
            species_by_row.append(species)
            species_rows[species].append(zero_idx)
            if species in target_rows and gene in target_genes:
                target_rows[species][gene].append(zero_idx)
    return species_by_row, species_rows, target_rows


def load_sample(prefix: str, raw_dir: Path, target_genes: set[str]) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, object]]:
    sample_name = sample_name_from_prefix(prefix)
    barcodes = read_barcodes(raw_dir / f"{prefix}_barcodes.tsv.gz")
    _, species_rows, target_rows = parse_features(raw_dir / f"{prefix}_features.tsv.gz", target_genes)
    with gzip.open(raw_dir / f"{prefix}_matrix.mtx.gz", "rb") as handle:
        matrix = mmread(handle).tocsr()

    human_total = np.asarray(matrix[species_rows.get("hg19", []), :].sum(axis=0)).ravel().astype(np.float32)
    mouse_total = np.asarray(matrix[species_rows.get("mm10", []), :].sum(axis=0)).ravel().astype(np.float32)
    total = human_total + mouse_total
    human_fraction = np.divide(human_total, total, out=np.zeros_like(human_total), where=total > 0)
    mouse_fraction = np.divide(mouse_total, total, out=np.zeros_like(mouse_total), where=total > 0)

    qc = pd.DataFrame(
        {
            "model": sample_name.split("_")[0],
            "sample_name": sample_name,
            "stage": infer_stage(sample_name),
            "barcode": barcodes,
            "human_counts": human_total[: len(barcodes)],
            "mouse_counts": mouse_total[: len(barcodes)],
            "total_counts_species": total[: len(barcodes)],
            "human_fraction": human_fraction[: len(barcodes)],
            "mouse_fraction": mouse_fraction[: len(barcodes)],
        }
    )
    qc["species_call"] = np.select(
        [qc["human_fraction"] >= 0.8, qc["mouse_fraction"] >= 0.8],
        ["human_dominant", "mouse_dominant"],
        default="mixed_or_low",
    )

    human_gene_counts = {}
    for gene, rows in target_rows["hg19"].items():
        human_gene_counts[gene] = np.asarray(matrix[rows, :].sum(axis=0)).ravel().astype(np.float32)[: len(barcodes)]
    gene_counts = pd.DataFrame(human_gene_counts)
    denom = pd.Series(human_total[: len(barcodes)]).replace(0, np.nan)
    denom = denom.fillna(denom[denom > 0].median() if (denom > 0).any() else 1.0)
    human_norm = np.log1p(gene_counts.div(denom, axis=0) * 10000.0)
    human_norm.insert(0, "barcode", barcodes)
    human_norm.insert(0, "stage", infer_stage(sample_name))
    human_norm.insert(0, "sample_name", sample_name)
    human_norm.insert(0, "model", sample_name.split("_")[0])

    audit = {
        "sample_name": sample_name,
        "stage": infer_stage(sample_name),
        "cells": len(barcodes),
        "human_features": len(species_rows.get("hg19", [])),
        "mouse_features": len(species_rows.get("mm10", [])),
        "human_target_genes_detected": len(target_rows["hg19"]),
        "mouse_target_genes_detected": len(target_rows["mm10"]),
        "human_dominant_cells": int((qc["species_call"] == "human_dominant").sum()),
        "mouse_dominant_cells": int((qc["species_call"] == "mouse_dominant").sum()),
        "mixed_or_low_cells": int((qc["species_call"] == "mixed_or_low").sum()),
    }
    return qc, human_norm, audit


def score_human_cells(human_norm_all: pd.DataFrame, qc_all: pd.DataFrame, signatures: dict[str, list[str]]) -> pd.DataFrame:
    metadata_cols = ["model", "sample_name", "stage", "barcode"]
    gene_cols = [col for col in human_norm_all.columns if col not in metadata_cols]
    merged_meta = human_norm_all[metadata_cols].merge(
        qc_all[["sample_name", "barcode", "species_call", "human_fraction", "mouse_fraction", "human_counts", "mouse_counts"]],
        on=["sample_name", "barcode"],
        how="left",
    )
    human_only = merged_meta["species_call"] == "human_dominant"
    expr = human_norm_all.loc[human_only.values, gene_cols].copy()
    meta = merged_meta.loc[human_only.values].reset_index(drop=True)
    expr.index = [f"{row.sample_name}_{row.barcode}" for row in meta[["sample_name", "barcode"]].itertuples(index=False)]
    scores = score_expression(expr, signatures=signatures)
    return pd.concat([meta, scores.reset_index(drop=True)], axis=1)


def summarize_species(qc_all: pd.DataFrame) -> pd.DataFrame:
    return (
        qc_all.groupby(["model", "sample_name", "stage", "species_call"])
        .agg(cells=("barcode", "count"), mean_human_fraction=("human_fraction", "mean"), median_human_fraction=("human_fraction", "median"))
        .reset_index()
    )


def summarize_human_scores(scores: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    score_cols = [
        "emt_score",
        "partial_emt_score",
        "tnbc_persister_tumor_refined",
        "tnbc_persister_stress_tolerance",
        "tnbc_persister_niche",
        "tnbc_stemness_persister",
        "tnbc_tgfb",
        "tnbc_axl_tam",
        "tnbc_hypoxia",
        "tnbc_yap_taz",
    ]
    score_cols = [col for col in score_cols if col in scores.columns]
    summary = scores.groupby(["model", "sample_name", "stage"])[score_cols].agg(["mean", "median", "std"]).reset_index()
    summary.columns = ["_".join(col).strip("_") if isinstance(col, tuple) else col for col in summary.columns]

    rows = []
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
            rows.append(row)
    return summary, pd.DataFrame(rows)


def build_human_gene_contrasts(human_norm_all: pd.DataFrame, qc_all: pd.DataFrame) -> pd.DataFrame:
    metadata_cols = ["model", "sample_name", "stage", "barcode"]
    gene_cols = [col for col in human_norm_all.columns if col not in metadata_cols]
    meta = human_norm_all[metadata_cols].merge(qc_all[["sample_name", "barcode", "species_call"]], on=["sample_name", "barcode"], how="left")
    expr = human_norm_all[gene_cols].copy()
    expr = pd.concat([meta, expr], axis=1)
    expr = expr[expr["species_call"] == "human_dominant"]
    means = expr.groupby(["model", "stage"])[gene_cols].mean()
    rows = []
    for model in means.index.get_level_values("model").unique():
        if (model, "chemonaive") not in means.index:
            continue
        baseline = means.loc[(model, "chemonaive")]
        for stage in means.loc[model].index:
            if stage == "chemonaive":
                continue
            stage_mean = means.loc[(model, stage)]
            for gene in gene_cols:
                rows.append(
                    {
                        "model": model,
                        "contrast": f"{stage}_minus_chemonaive",
                        "stage": stage,
                        "gene_symbol": gene,
                        "stage_mean_log1p_cpm": float(stage_mean[gene]),
                        "chemonaive_mean_log1p_cpm": float(baseline[gene]),
                        "delta_mean_log1p_cpm": float(stage_mean[gene] - baseline[gene]),
                    }
                )
    return pd.DataFrame(rows).sort_values(["contrast", "delta_mean_log1p_cpm"], ascending=[True, False])


def save_species_plot(species_summary: pd.DataFrame, out_path: Path) -> None:
    pivot = species_summary.pivot_table(index="sample_name", columns="species_call", values="cells", aggfunc="sum", fill_value=0)
    pivot = pivot.reindex(sorted(pivot.index))
    ax = pivot.plot(kind="bar", stacked=True, figsize=(10, 4.8), color={"human_dominant": "#4c78a8", "mouse_dominant": "#f58518", "mixed_or_low": "#bab0ac"})
    ax.set_ylabel("Cells")
    ax.set_title("GSE164715 species call by sample")
    ax.tick_params(axis="x", rotation=35)
    ax.legend(frameon=False)
    plt.tight_layout()
    plt.savefig(out_path, dpi=180)
    plt.close()


def save_human_contrast_plot(contrasts: pd.DataFrame, out_path: Path) -> None:
    feature = "tnbc_persister_tumor_refined_delta_mean"
    if contrasts.empty or feature not in contrasts.columns:
        return
    pivot = contrasts.pivot(index="model", columns="contrast", values=feature).fillna(0)
    ax = pivot.plot(kind="bar", figsize=(8, 4.8))
    ax.axhline(0, color="#777777", linewidth=1)
    ax.set_ylabel("Human-only tumor-persister delta")
    ax.set_title("Human-dominant persister shifts versus chemonaive")
    ax.tick_params(axis="x", rotation=0)
    ax.legend(frameon=False, bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.tight_layout()
    plt.savefig(out_path, dpi=180)
    plt.close()


def write_report(audit: pd.DataFrame, species_summary: pd.DataFrame, score_summary: pd.DataFrame, contrasts: pd.DataFrame, gene_contrasts: pd.DataFrame, image_paths: dict[str, Path], out_path: Path) -> None:
    top_persister_genes = gene_contrasts[gene_contrasts["contrast"].str.contains("persister", na=False)].head(25)
    lines = [
        "# GSE164715 Human-Dominant Persister Filtering Report",
        "",
        "## Purpose",
        "",
        "Separate human malignant-cell signal from mouse host/stromal signal in selected PDX scRNA matrices before refining the digital twin `P` state.",
        "",
        "## Import Audit",
        "",
        audit.to_markdown(index=False),
        "",
        "## Species Summary",
        "",
        species_summary.to_markdown(index=False),
        "",
        "## Human-Dominant Score Summary",
        "",
        score_summary.head(30).to_markdown(index=False),
        "",
        "## Human-Dominant Chemonaive Contrasts",
        "",
        contrasts.to_markdown(index=False) if not contrasts.empty else "No contrasts available.",
        "",
        "## Top Human-Dominant Persister Genes",
        "",
        top_persister_genes.to_markdown(index=False) if not top_persister_genes.empty else "No gene contrasts available.",
        "",
        "## Plots",
        "",
        f"![Species calls]({image_paths['species_plot'].as_posix()})",
        "",
        f"![Human persister contrasts]({image_paths['human_contrast_plot'].as_posix()})",
        "",
        "## Digital-Twin Decision",
        "",
        "- Use human-dominant cells for tumor-cell `P` state refinement.",
        "- Keep mouse-dominant and mixed cells as host/niche context, not malignant persister identity.",
        "- Keep `persister_niche` as a separate modifier rather than merging vascular/stromal genes into the tumor `P` compartment.",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Species-filter selected GSE164715 PDX scRNA matrices and rescore human-dominant cells.")
    p.add_argument("--raw-dir", default="data/raw/tnbc_nac/geo/GSE164715/selected_raw")
    p.add_argument("--config", default="configs/tnbc_digital_twin.yml")
    p.add_argument("--out-dir", default="data/processed/tnbc_digital_twin/gse164715_human_filter")
    p.add_argument("--docs-dir", default="docs/tnbc_digital_twin_emt_plasticity")
    return p


def main() -> None:
    args = parser().parse_args()
    out_dir = ROOT / args.out_dir
    asset_dir = ROOT / args.docs_dir / "assets" / "gse164715_human_filter"
    out_dir.mkdir(parents=True, exist_ok=True)
    asset_dir.mkdir(parents=True, exist_ok=True)

    target_genes, signatures = load_signatures(ROOT / args.config)
    qc_frames = []
    expr_frames = []
    audit_rows = []
    for prefix in SELECTED_SAMPLE_PREFIXES:
        qc, human_norm, audit = load_sample(prefix, ROOT / args.raw_dir, target_genes)
        qc_frames.append(qc)
        expr_frames.append(human_norm)
        audit_rows.append(audit)
    qc_all = pd.concat(qc_frames, ignore_index=True)
    human_norm_all = pd.concat(expr_frames, ignore_index=True)
    audit = pd.DataFrame(audit_rows)
    human_scores = score_human_cells(human_norm_all, qc_all, signatures)
    species_summary = summarize_species(qc_all)
    score_summary, contrasts = summarize_human_scores(human_scores)
    gene_contrasts = build_human_gene_contrasts(human_norm_all, qc_all)

    audit.to_csv(out_dir / "gse164715_species_filter_import_audit.tsv", sep="\t", index=False)
    species_summary.to_csv(out_dir / "gse164715_species_call_summary.tsv", sep="\t", index=False)
    qc_all.to_csv(out_dir / "gse164715_species_qc_by_cell.tsv.gz", sep="\t", index=False, compression="gzip")
    human_scores.to_csv(out_dir / "gse164715_human_dominant_cell_scores.tsv.gz", sep="\t", index=False, compression="gzip")
    score_summary.to_csv(out_dir / "gse164715_human_dominant_stage_summary.tsv", sep="\t", index=False)
    contrasts.to_csv(out_dir / "gse164715_human_dominant_chemonaive_contrasts.tsv", sep="\t", index=False)
    gene_contrasts.to_csv(out_dir / "gse164715_human_dominant_gene_contrasts.tsv", sep="\t", index=False)

    image_paths = {
        "species_plot": asset_dir / "gse164715_species_calls.png",
        "human_contrast_plot": asset_dir / "gse164715_human_persister_contrasts.png",
    }
    save_species_plot(species_summary, image_paths["species_plot"])
    save_human_contrast_plot(contrasts, image_paths["human_contrast_plot"])
    write_report(audit, species_summary, score_summary, contrasts, gene_contrasts, image_paths, out_dir / "gse164715_human_dominant_filter_report.md")
    print(f"total_cells={qc_all.shape[0]} human_dominant_cells={human_scores.shape[0]}")
    print(audit.to_string(index=False))
    if not contrasts.empty:
        print(contrasts.to_string(index=False))


if __name__ == "__main__":
    main()
