from __future__ import annotations

import argparse
from pathlib import Path

from crc_liver_invasion_front.data import fetch_geomx_validation, prepare_gse225857
from crc_liver_invasion_front.figures import (
    plot_gradient_profiles,
    plot_heterograph_excerpt,
    plot_interface_maps,
    plot_model_summary,
    plot_workflow,
)
from crc_liver_invasion_front.graph import build_heterogeneous_interface_graph, summarize_edges, typed_message_features
from crc_liver_invasion_front.interface import annotate_interface, build_physical_edges
from crc_liver_invasion_front.modeling import compare_front_to_core, fit_interface_model, save_model
from crc_liver_invasion_front.reporting import write_executed_report
from crc_liver_invasion_front.signatures import score_crc_liver_programs


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Build the public-data CRC liver-metastasis invasion-front model.")
    p.add_argument("--raw-dir", default="data/raw/spatial/geo/GSE225857")
    p.add_argument("--geomx-raw-dir", default="data/raw/spatial/geomx/zenodo_7520789")
    p.add_argument("--out-dir", default="data/processed/crc_liver_invasion_front_v1")
    p.add_argument("--docs-dir", default="docs/crc_liver_invasion_front")
    p.add_argument("--neighbors", type=int, default=6)
    p.add_argument("--front-hops", type=int, default=3)
    p.add_argument("--permutations", type=int, default=100)
    return p


def main() -> None:
    args = parser().parse_args()
    output = Path(args.out_dir)
    docs = Path(args.docs_dir)
    figures = output / "figures"
    output.mkdir(parents=True, exist_ok=True)
    docs.mkdir(parents=True, exist_ok=True)

    expression, metadata, manifest = prepare_gse225857(args.raw_dir, output)
    fetch_geomx_validation(args.geomx_raw_dir, output)
    scored, coverage = score_crc_liver_programs(expression, metadata)
    physical = build_physical_edges(scored, k=args.neighbors)
    scored, interface_summary = annotate_interface(scored, physical, front_hops=args.front_hops)
    nodes, edges = build_heterogeneous_interface_graph(scored, physical)
    messages = typed_message_features(scored, edges)
    model, predictions, importance, ablations, metrics = fit_interface_model(
        scored,
        messages,
        n_permutations=args.permutations,
    )
    front_statistics = compare_front_to_core(scored)
    edge_summary = summarize_edges(edges)

    scored.to_csv(output / "spatial_interface_scores.tsv.gz", sep="\t", index=False, compression="gzip")
    coverage.to_csv(output / "signature_coverage.tsv", sep="\t", index=False)
    physical.to_csv(output / "physical_edges.tsv.gz", sep="\t", index=False, compression="gzip")
    nodes.to_csv(output / "heterogeneous_nodes.tsv.gz", sep="\t", index=False, compression="gzip")
    edges.to_csv(output / "heterogeneous_edges.tsv.gz", sep="\t", index=False, compression="gzip")
    edge_summary.to_csv(output / "edge_type_summary.tsv", sep="\t", index=False)
    interface_summary.to_csv(output / "interface_section_summary.tsv", sep="\t", index=False)
    front_statistics.to_csv(output / "front_vs_core_statistics.tsv", sep="\t", index=False)
    predictions.to_csv(output / "interface_predictions.tsv.gz", sep="\t", index=False, compression="gzip")
    importance.to_csv(output / "model_feature_importance.tsv", sep="\t", index=False)
    ablations.to_csv(output / "feature_group_ablation.tsv", sep="\t", index=False)
    save_model(model, metrics, output)

    plot_interface_maps(scored, figures)
    plot_gradient_profiles(scored, figures)
    plot_heterograph_excerpt(nodes, edges, figures)
    plot_model_summary(importance, ablations, metrics, figures)
    workflow = plot_workflow(figures)
    docs_assets = docs / "assets"
    docs_assets.mkdir(parents=True, exist_ok=True)
    (docs_assets / workflow.name).write_bytes(workflow.read_bytes())
    write_executed_report(
        docs / "executed_project_report.md",
        manifest,
        interface_summary,
        front_statistics,
        importance,
        metrics,
    )
    print(f"Completed CRC liver invasion-front workflow: {output}")
    print(f"Model ROC AUC: {metrics['roc_auc']:.3f}; permutation P: {metrics['permutation_p']:.3f}")


if __name__ == "__main__":
    main()
