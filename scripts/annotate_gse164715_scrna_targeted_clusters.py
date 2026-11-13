from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]

LINEAGE_SCORE_MAP = {
    "malignant_like": ["epithelial", "mesenchymal", "partial_emt_score", "tnbc_persister_tumor_refined"],
    "endothelial_like": ["angiogenesis", "tnbc_persister_niche"],
    "stromal_like": ["stromal_fibroblast", "caf", "ecm_remodeling"],
    "immune_like": ["immune_total", "t_cell_cytotoxic", "tam_spp1"],
}
CLUSTER_FEATURES = [
    "epithelial",
    "mesenchymal",
    "partial_emt_score",
    "tnbc_persister_tumor_refined",
    "tnbc_persister_stress_tolerance",
    "tnbc_persister_niche",
    "angiogenesis",
    "stromal_fibroblast",
    "caf",
    "ecm_remodeling",
    "immune_total",
    "t_cell_cytotoxic",
    "tam_spp1",
    "tnbc_hypoxia",
    "tnbc_yap_taz",
]


def available_features(df: pd.DataFrame, features: list[str]) -> list[str]:
    return [feature for feature in features if feature in df.columns]


def score_lineages(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for label, features in LINEAGE_SCORE_MAP.items():
        present = available_features(out, features)
        if present:
            out[f"{label}_score"] = out[present].max(axis=1)
        else:
            out[f"{label}_score"] = np.nan
    score_cols = [f"{label}_score" for label in LINEAGE_SCORE_MAP]
    values = out[score_cols].fillna(-np.inf)
    winning = values.idxmax(axis=1).str.replace("_score", "", regex=False)
    winning_score = values.max(axis=1)
    second_score = values.apply(lambda row: row.nlargest(2).iloc[-1] if np.isfinite(row).sum() >= 2 else np.nan, axis=1)
    out["targeted_annotation"] = winning
    out.loc[winning_score < -0.15, "targeted_annotation"] = "low_signal_human"
    out["annotation_margin"] = winning_score - second_score
    out.loc[out["annotation_margin"] < 0.10, "targeted_annotation"] = "ambiguous_human"
    return out


def add_kmeans_clusters(df: pd.DataFrame, n_clusters: int, seed: int) -> pd.DataFrame:
    features = available_features(df, CLUSTER_FEATURES)
    out = df.copy()
    if len(features) < 4 or out.shape[0] < n_clusters:
        out["targeted_cluster"] = "cluster_0"
        return out
    try:
        from sklearn.cluster import KMeans
        from sklearn.preprocessing import StandardScaler
    except Exception:
        out["targeted_cluster"] = "cluster_0"
        return out
    matrix = out[features].replace([np.inf, -np.inf], np.nan).fillna(out[features].median(numeric_only=True))
    matrix = StandardScaler().fit_transform(matrix)
    labels = KMeans(n_clusters=n_clusters, random_state=seed, n_init=20).fit_predict(matrix)
    out["targeted_cluster"] = [f"cluster_{label}" for label in labels]
    return out


def summarize_clusters(annotated: pd.DataFrame) -> pd.DataFrame:
    lineage_cols = [f"{label}_score" for label in LINEAGE_SCORE_MAP]
    feature_cols = available_features(annotated, CLUSTER_FEATURES + lineage_cols)
    summary = (
        annotated.groupby("targeted_cluster")
        .agg(
            cells=("barcode", "count"),
            models=("model", lambda s: ",".join(sorted(s.astype(str).unique()))),
            dominant_annotation=("targeted_annotation", lambda s: s.value_counts().idxmax()),
        )
        .reset_index()
    )
    means = annotated.groupby("targeted_cluster")[feature_cols].mean().reset_index()
    return summary.merge(means, on="targeted_cluster", how="left").sort_values("targeted_cluster")


def summarize_stage_annotations(annotated: pd.DataFrame) -> pd.DataFrame:
    counts = (
        annotated.groupby(["model", "sample_name", "stage", "targeted_annotation"])
        .agg(cells=("barcode", "count"))
        .reset_index()
    )
    totals = counts.groupby(["model", "sample_name", "stage"])["cells"].transform("sum")
    counts["fraction"] = counts["cells"] / totals
    return counts.sort_values(["model", "sample_name", "targeted_annotation"])


def summarize_persister_enrichment(stage_summary: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for model, group in stage_summary.groupby("model"):
        baseline = group[group["stage"] == "chemonaive"].set_index("targeted_annotation")
        if baseline.empty:
            continue
        for stage, stage_group in group.groupby("stage"):
            if stage == "chemonaive":
                continue
            stage_indexed = stage_group.set_index("targeted_annotation")
            annotations = sorted(set(baseline.index).union(stage_indexed.index))
            for annotation in annotations:
                rows.append(
                    {
                        "model": model,
                        "contrast": f"{stage}_minus_chemonaive",
                        "targeted_annotation": annotation,
                        "stage_fraction": float(stage_indexed["fraction"].get(annotation, 0.0)),
                        "chemonaive_fraction": float(baseline["fraction"].get(annotation, 0.0)),
                        "delta_fraction": float(stage_indexed["fraction"].get(annotation, 0.0) - baseline["fraction"].get(annotation, 0.0)),
                    }
                )
    return pd.DataFrame(rows).sort_values(["contrast", "model", "delta_fraction"], ascending=[True, True, False])


def save_annotation_plot(stage_summary: pd.DataFrame, out_path: Path) -> None:
    if stage_summary.empty:
        return
    pivot = stage_summary.pivot_table(index="sample_name", columns="targeted_annotation", values="fraction", aggfunc="sum", fill_value=0)
    pivot = pivot.reindex(sorted(pivot.index))
    colors = {
        "malignant_like": "#4c78a8",
        "endothelial_like": "#72b7b2",
        "stromal_like": "#59a14f",
        "immune_like": "#e15759",
        "ambiguous_human": "#bab0ac",
        "low_signal_human": "#b07aa1",
    }
    ax = pivot.plot(kind="bar", stacked=True, figsize=(11, 5), color=[colors.get(col, "#999999") for col in pivot.columns])
    ax.set_ylabel("Human-dominant cell fraction")
    ax.set_title("GSE164715 targeted annotation by sample")
    ax.tick_params(axis="x", rotation=35)
    ax.legend(frameon=False, bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.tight_layout()
    plt.savefig(out_path, dpi=180)
    plt.close()


def save_cluster_heatmap(cluster_summary: pd.DataFrame, out_path: Path) -> None:
    features = available_features(cluster_summary, [f"{label}_score" for label in LINEAGE_SCORE_MAP] + ["tnbc_persister_tumor_refined", "tnbc_persister_stress_tolerance", "tnbc_persister_niche"])
    if cluster_summary.empty or not features:
        return
    data = cluster_summary.set_index("targeted_cluster")[features]
    values = data.to_numpy(dtype=float)
    fig, ax = plt.subplots(figsize=(8, 4.8), constrained_layout=True)
    vmax = max(abs(float(np.nanmin(values))), abs(float(np.nanmax(values))), 0.1)
    im = ax.imshow(values, aspect="auto", cmap="coolwarm", vmin=-vmax, vmax=vmax)
    ax.set_yticks(range(data.shape[0]), data.index)
    ax.set_xticks(range(len(features)), [feature.replace("_", "\n") for feature in features], fontsize=8)
    ax.set_title("Targeted cluster mean scores")
    fig.colorbar(im, ax=ax, label="Mean score")
    fig.savefig(out_path, dpi=180)
    plt.close(fig)


def write_report(
    cluster_summary: pd.DataFrame,
    stage_summary: pd.DataFrame,
    enrichment: pd.DataFrame,
    image_paths: dict[str, Path],
    out_path: Path,
) -> None:
    persister_enrichment = enrichment[enrichment["contrast"].str.contains("persister", na=False)].head(30)
    lines = [
        "# GSE164715 Targeted Cluster Annotation",
        "",
        "## Purpose",
        "",
        "Annotate human-dominant `GSE164715` PDX scRNA cells into interpretable targeted compartments using existing EMT, persister, endothelial, stromal, and immune signature scores.",
        "",
        "## Cluster Summary",
        "",
        cluster_summary.to_markdown(index=False),
        "",
        "## Stage Annotation Summary",
        "",
        stage_summary.head(60).to_markdown(index=False),
        "",
        "## Persister Enrichment Versus Chemonaive",
        "",
        persister_enrichment.to_markdown(index=False) if not persister_enrichment.empty else "No persister enrichment rows available.",
        "",
        "## Plots",
        "",
        f"![Annotation fractions]({image_paths['annotation_plot'].as_posix()})",
        "",
        f"![Cluster heatmap]({image_paths['cluster_heatmap'].as_posix()})",
        "",
        "## Interpretation",
        "",
        "- These are targeted annotations, not a full unsupervised single-cell atlas.",
        "- Human-dominant cells are prioritized for malignant-like persister interpretation.",
        "- Endothelial/stromal/immune-like calls should be treated as residual microenvironment or annotation uncertainty until validated with full marker panels.",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Annotate species-filtered GSE164715 human-dominant scRNA cells with targeted clusters.")
    p.add_argument("--cell-scores", default="data/processed/tnbc_digital_twin/gse164715_human_filter/gse164715_human_dominant_cell_scores.tsv.gz")
    p.add_argument("--out-dir", default="data/processed/tnbc_digital_twin/gse164715_targeted_annotation")
    p.add_argument("--docs-dir", default="docs/tnbc_digital_twin_emt_plasticity")
    p.add_argument("--clusters", type=int, default=6)
    p.add_argument("--seed", type=int, default=2026)
    return p


def main() -> None:
    args = parser().parse_args()
    out_dir = ROOT / args.out_dir
    asset_dir = ROOT / args.docs_dir / "assets" / "gse164715_targeted_annotation"
    out_dir.mkdir(parents=True, exist_ok=True)
    asset_dir.mkdir(parents=True, exist_ok=True)

    scores = pd.read_csv(ROOT / args.cell_scores, sep="\t")
    annotated = score_lineages(scores)
    annotated = add_kmeans_clusters(annotated, n_clusters=args.clusters, seed=args.seed)
    cluster_summary = summarize_clusters(annotated)
    stage_summary = summarize_stage_annotations(annotated)
    enrichment = summarize_persister_enrichment(stage_summary)

    annotated.to_csv(out_dir / "gse164715_targeted_cell_annotations.tsv.gz", sep="\t", index=False, compression="gzip")
    cluster_summary.to_csv(out_dir / "gse164715_targeted_cluster_summary.tsv", sep="\t", index=False)
    stage_summary.to_csv(out_dir / "gse164715_targeted_annotation_stage_summary.tsv", sep="\t", index=False)
    enrichment.to_csv(out_dir / "gse164715_persister_annotation_enrichment.tsv", sep="\t", index=False)

    image_paths = {
        "annotation_plot": asset_dir / "gse164715_targeted_annotation_fractions.png",
        "cluster_heatmap": asset_dir / "gse164715_targeted_cluster_heatmap.png",
    }
    save_annotation_plot(stage_summary, image_paths["annotation_plot"])
    save_cluster_heatmap(cluster_summary, image_paths["cluster_heatmap"])
    write_report(cluster_summary, stage_summary, enrichment, image_paths, out_dir / "gse164715_targeted_annotation_report.md")

    print(f"annotated_cells={annotated.shape[0]} clusters={cluster_summary.shape[0]}")
    print(stage_summary.groupby("targeted_annotation")["cells"].sum().sort_values(ascending=False).to_string())


if __name__ == "__main__":
    main()
