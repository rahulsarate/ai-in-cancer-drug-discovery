from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


def read_table(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, sep="\t")


def classify_review(row: pd.Series) -> str:
    frac = float(row.get("fraction", 0.0))
    annotation = str(row.get("targeted_annotation", ""))
    if annotation == "ambiguous_human" and frac >= 0.50:
        return "high_ambiguity_review_required"
    if annotation == "ambiguous_human" and frac >= 0.30:
        return "moderate_ambiguity_report_with_caution"
    if annotation == "malignant_like" and frac >= 0.30:
        return "malignant_layer_interpretable"
    if annotation in {"stromal_like", "endothelial_like", "immune_like"} and frac >= 0.10:
        return "niche_layer_interpretable"
    return "supporting_context_only"


def write_report(
    stage_summary: pd.DataFrame,
    cluster_summary: pd.DataFrame,
    marker_checks: pd.DataFrame,
    sample_review: pd.DataFrame,
    cluster_review: pd.DataFrame,
    out_path: Path,
) -> None:
    ambiguous_samples = sample_review[sample_review["review_status"].str.contains("ambiguity", na=False)]
    ambiguous_clusters = cluster_review[cluster_review["dominant_annotation"] == "ambiguous_human"]
    marker_passes = 0
    marker_total = 0
    if not marker_checks.empty and "passes_direction_check" in marker_checks.columns:
        marker_total = len(marker_checks)
        marker_passes = int(marker_checks["passes_direction_check"].astype(str).str.lower().eq("true").sum())

    lines = [
        "# GSE164715 Ambiguous-Compartment Review",
        "",
        "## Decision Summary",
        "",
        "The GSE164715 layer is suitable for targeted digital-twin refinement of malignant-like, stress-tolerant, endothelial, stromal, and immune/niche signals. It should not be described as a complete single-cell atlas or a definitive malignant-cell classifier.",
        "",
        f"Marker-panel direction checks passed `{marker_passes}` of `{marker_total}` checks.",
        "",
        "## Sample-Level Review",
        "",
        sample_review.to_markdown(index=False),
        "",
        "## Ambiguous Sample/Stage Rows",
        "",
        ambiguous_samples.to_markdown(index=False) if not ambiguous_samples.empty else "No high/moderate ambiguous sample-stage rows detected.",
        "",
        "## Cluster-Level Review",
        "",
        cluster_review.to_markdown(index=False),
        "",
        "## Ambiguous Clusters",
        "",
        ambiguous_clusters.to_markdown(index=False) if not ambiguous_clusters.empty else "No ambiguous-dominant clusters detected.",
        "",
        "## Publication Rules",
        "",
        "- Claim broad targeted compartments only: malignant-like, endothelial-like, stromal-like, immune-like, and ambiguous human.",
        "- Treat `ambiguous_human` as unresolved human-dominant cells, not as a biological state.",
        "- Do not infer exact malignant/stromal/endothelial lineage for high-ambiguity sample-stage rows.",
        "- Emphasize that marker panels validate directionality, not full cell ontology.",
        "- Use HBCx172 and HBCx95 persister/residual claims cautiously because ambiguous fractions are high in some stage rows.",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Review ambiguous GSE164715 targeted compartments before publication claims.")
    p.add_argument("--processed-dir", default="data/processed/tnbc_digital_twin")
    p.add_argument("--docs-dir", default="docs/tnbc_digital_twin_emt_plasticity")
    return p


def main() -> None:
    args = parser().parse_args()
    processed = ROOT / args.processed_dir
    docs = ROOT / args.docs_dir
    out_dir = processed / "gse164715_ambiguity_review"
    out_dir.mkdir(parents=True, exist_ok=True)
    docs.mkdir(parents=True, exist_ok=True)

    stage = read_table(processed / "gse164715_targeted_annotation" / "gse164715_targeted_annotation_stage_summary.tsv")
    clusters = read_table(processed / "gse164715_targeted_annotation" / "gse164715_targeted_cluster_summary.tsv")
    marker_path = processed / "gse164715_marker_validation" / "gse164715_marker_panel_direction_checks.tsv"
    marker = read_table(marker_path) if marker_path.exists() else pd.DataFrame()

    sample_review = stage.copy()
    sample_review["review_status"] = sample_review.apply(classify_review, axis=1)
    sample_review = sample_review.sort_values(["sample_name", "targeted_annotation"])

    cluster_review = clusters.copy()
    cluster_review["review_status"] = cluster_review.apply(
        lambda row: "ambiguous_cluster_review_required"
        if row.get("dominant_annotation") == "ambiguous_human"
        else "targeted_cluster_interpretable",
        axis=1,
    )
    cluster_review = cluster_review.sort_values(["dominant_annotation", "targeted_cluster"])

    sample_review.to_csv(out_dir / "gse164715_sample_stage_ambiguity_review.tsv", sep="\t", index=False)
    cluster_review.to_csv(out_dir / "gse164715_cluster_ambiguity_review.tsv", sep="\t", index=False)
    write_report(stage, clusters, marker, sample_review, cluster_review, out_dir / "gse164715_ambiguity_review_report.md")
    write_report(stage, clusters, marker, sample_review, cluster_review, docs / "gse164715_ambiguity_review.md")
    print(f"wrote {out_dir / 'gse164715_ambiguity_review_report.md'}")


if __name__ == "__main__":
    main()
