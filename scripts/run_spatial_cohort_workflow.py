from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Run score, graph, model, interpretation, and paper-table steps for one spatial cohort.")
    p.add_argument("--expression", required=True)
    p.add_argument("--metadata", required=True)
    p.add_argument("--out-dir", required=True)
    p.add_argument("--k", type=int, default=6)
    p.add_argument("--radius", type=float, default=2.5)
    p.add_argument("--ablation-epochs", type=int, default=150)
    p.add_argument("--skip-edge-ablation", action="store_true")
    p.add_argument("--histology-features", default="", help="Optional per-spot H&E tile feature TSV.")
    return p


def run(cmd: list[str]) -> None:
    print("Running:", " ".join(cmd))
    subprocess.run([sys.executable, *cmd], check=True)


def main() -> None:
    args = parser().parse_args()
    out = Path(args.out_dir)
    scores = out / "spatial_emt_niche_scores.tsv"
    edges = out / "spatial_graph_edges.tsv"
    predictions = out / "emt_niche_predictions.tsv"
    proxy = out / "cell_type_proxy_proportions.tsv"
    run(["scripts/export_spatial_h5ad.py", "--expression", args.expression, "--metadata", args.metadata, "--out", str(out / "processed_h5ad" / "spatial_signature_matrix.h5ad")])
    run(["scripts/02_score_spatial_emt_niches.py", "--expression", args.expression, "--metadata", args.metadata, "--out-dir", args.out_dir])
    if args.histology_features:
        run(["scripts/add_histology_features_to_scores.py", "--scores", str(scores), "--features", args.histology_features, "--out", str(scores)])
    run(["scripts/07_estimate_cell_type_proxy_deconvolution.py", "--scores", str(scores), "--out-dir", args.out_dir])
    run(["scripts/03_build_spatial_graphs.py", "--scores", str(scores), "--out-dir", args.out_dir, "--k", str(args.k), "--radius", str(args.radius)])
    run(["scripts/08_build_heterogeneous_niche_graph.py", "--scores", str(scores), "--proxy", str(proxy), "--out-dir", args.out_dir])
    run(["scripts/04_train_gnn.py", "--scores", str(scores), "--edges", str(edges), "--out-dir", args.out_dir])
    interpret = [
        "scripts/05_interpret_niche_drivers.py",
        "--scores",
        str(scores),
        "--edges",
        str(edges),
        "--predictions",
        str(predictions),
        "--out-dir",
        args.out_dir,
        "--ablation-epochs",
        str(args.ablation_epochs),
    ]
    if args.skip_edge_ablation:
        interpret.append("--skip-edge-ablation")
    run(interpret)
    run(
        [
            "scripts/06_generate_paper_figures.py",
            "--scores",
            str(scores),
            "--edges",
            str(edges),
            "--predictions",
            str(predictions),
            "--interpret-dir",
            args.out_dir,
            "--out-dir",
            str(out / "paper"),
        ]
    )


if __name__ == "__main__":
    main()
