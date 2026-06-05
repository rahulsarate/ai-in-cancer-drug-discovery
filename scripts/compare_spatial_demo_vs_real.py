from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Compare demo and real spatial EMT niche workflow outputs.")
    p.add_argument("--demo-dir", default="data/processed/spatial_emt_niche_gnn_demo")
    p.add_argument("--real-dir", default="data/processed/spatial_emt_niche_gnn_10x_breast")
    p.add_argument("--out", default="data/processed/spatial_emt_niche_gnn_comparison/demo_vs_10x_breast_summary.tsv")
    return p


def load_table(folder: Path, filename: str) -> pd.DataFrame:
    path = folder / filename
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path, sep="\t")


def summarize_run(label: str, folder: Path) -> dict:
    scores = load_table(folder, "spatial_emt_niche_scores.tsv")
    predictions = load_table(folder, "emt_niche_predictions.tsv")
    edges = load_table(folder, "spatial_graph_edges.tsv")
    source = load_table(folder, "dataset_source.tsv")
    row = {"run": label, "folder": str(folder)}
    if not scores.empty:
        row.update(
            {
                "spots": len(scores),
                "mean_emt_score": scores["emt_score"].mean(),
                "mean_partial_emt": scores["partial_emt_score"].mean(),
                "emt_niche_fraction": scores["emt_niche_label"].mean(),
                "tumor_cell_emt_fraction": scores["tumor_cell_emt_candidate"].mean(),
                "stromal_inflated_fraction": scores["stromal_inflated_emt_candidate"].mean(),
                "mean_caf_tam": scores["caf_tam_niche"].mean(),
                "mean_hypoxia": scores["hypoxia"].mean(),
            }
        )
    if not predictions.empty:
        row.update(
            {
                "mean_predicted_emt_niche_probability": predictions["emt_niche_probability"].mean(),
                "high_probability_fraction": (predictions["emt_niche_probability"] >= 0.5).mean(),
            }
        )
    if not edges.empty:
        row["edges"] = len(edges)
        row["spatial_knn_edges"] = edges["edge_type"].eq("spatial_knn").sum()
        row["ligand_receptor_edges"] = edges["edge_type"].astype(str).str.startswith("ligand_receptor:").sum()
        row["hypoxia_gradient_edges"] = edges["edge_type"].eq("hypoxia_gradient").sum()
    if not source.empty:
        source_map = dict(zip(source.get("field", []), source.get("value", [])))
        row["source_page"] = source_map.get("source_page", "")
    return row


def write_interpretation(summary: pd.DataFrame, out_md: Path) -> None:
    markdown_table = summary.fillna("").astype(str)
    header = "| " + " | ".join(markdown_table.columns) + " |"
    separator = "| " + " | ".join(["---"] * len(markdown_table.columns)) + " |"
    rows = [
        "| " + " | ".join(row[col] for col in markdown_table.columns) + " |"
        for _, row in markdown_table.iterrows()
    ]
    lines = [
        "# Demo vs Real 10x Breast Spatial EMT Niche Comparison",
        "",
        "This report compares the synthetic pipeline demo against a public 10x Visium FFPE human breast cancer dataset.",
        "",
        "Interpretation rules:",
        "",
        "- The synthetic demo validates workflow mechanics only.",
        "- The real 10x run is still weak-label based because no spot-level pathologist labels are integrated yet.",
        "- High stromal-inflated EMT fractions should be treated as a contamination warning, not tumor-cell EMT.",
        "- Edge counts show graph construction behavior, not causal biology.",
        "",
        "## Summary Table",
        "",
        header,
        separator,
        *rows,
        "",
        "## Next Validation Moves",
        "",
        "1. Add pathologist region labels from a cohort with spot-level annotations.",
        "2. Add cell-type deconvolution to split malignant, CAF, TAM, and immune signal inside each spot.",
        "3. Run leave-dataset-out validation after adding HEST-1k/HTAN/GEO cohorts.",
        "4. Compare edge ablation on real data against randomized spatial coordinates and shuffled ligand-receptor edges.",
    ]
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parser().parse_args()
    demo = summarize_run("synthetic_demo", Path(args.demo_dir))
    real = summarize_run("10x_visium_ffpe_human_breast_cancer", Path(args.real_dir))
    summary = pd.DataFrame([demo, real])
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(out, sep="\t", index=False)
    write_interpretation(summary, out.with_suffix(".md"))
    print(f"Wrote {out}")
    print(f"Wrote {out.with_suffix('.md')}")


if __name__ == "__main__":
    main()
