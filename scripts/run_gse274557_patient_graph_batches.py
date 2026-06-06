from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from spatial_emt_niche_gnn.graph import build_spatial_graph, edge_type_summary
from spatial_emt_niche_gnn.model import train_graph_logistic


SCORES = Path("data/processed/spatial_emt_niche_gnn_geo_met_pdac_gse274557_fullprep/spatial_emt_niche_scores.tsv")
OUT_DIR = Path("data/processed/spatial_emt_niche_gnn_geo_met_pdac_gse274557_patient_batches")


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Run GSE274557 full graph workflow by patient batches.")
    p.add_argument("--scores", default=str(SCORES))
    p.add_argument("--out-dir", default=str(OUT_DIR))
    p.add_argument("--patients", nargs="*", default=None)
    p.add_argument("--k", type=int, default=6)
    p.add_argument("--radius", type=float, default=2.5)
    p.add_argument("--epochs", type=int, default=250)
    return p


def main() -> None:
    args = parser().parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    scores = pd.read_csv(args.scores, sep="\t")
    wanted = set(args.patients or [])
    patient_rows = []
    edge_rows = []
    metric_rows = []
    for patient_id, patient_scores in scores.groupby("patient_id", dropna=False):
        if wanted and str(patient_id) not in wanted:
            continue
        patient_out = out_dir / str(patient_id)
        patient_out.mkdir(parents=True, exist_ok=True)
        edges = build_spatial_graph(patient_scores, k=args.k, radius=args.radius)
        summary = edge_type_summary(edges)
        summary.insert(0, "patient_id", patient_id)
        edge_rows.append(summary)
        predictions, metrics = train_graph_logistic(patient_scores, edges, epochs=args.epochs)
        patient_scores.groupby(["site_label", "progression_label"], dropna=False).agg(
            spots=("spot_id", "count"),
            emt_niche_fraction=("emt_niche_label", "mean"),
            stromal_inflated_fraction=("stromal_inflated_emt_candidate", "mean"),
            tumor_cell_emt_fraction=("tumor_cell_emt_candidate", "mean"),
            mean_partial_emt=("partial_emt_score", "mean"),
            mean_caf_tam=("caf_tam_niche", "mean"),
            mean_hypoxia=("hypoxia", "mean"),
            mean_ecm_remodeling=("ecm_remodeling", "mean"),
            mean_angiogenesis=("angiogenesis", "mean"),
        ).reset_index().assign(patient_id=patient_id).to_csv(patient_out / "patient_site_summary.tsv", sep="\t", index=False)
        summary.to_csv(patient_out / "edge_type_summary.tsv", sep="\t", index=False)
        predictions.to_csv(patient_out / "emt_niche_predictions.tsv", sep="\t", index=False)
        (patient_out / "model_metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
        patient_rows.append(
            {
                "patient_id": patient_id,
                "samples": patient_scores["sample_id"].nunique(),
                "spots": len(patient_scores),
                "edges": len(edges),
                "edge_types": summary["edge_type"].nunique(),
                "train_accuracy": metrics.get("train_accuracy"),
                "test_accuracy": metrics.get("test_accuracy"),
            }
        )
        metric_rows.append({"patient_id": patient_id, **{key: value for key, value in metrics.items() if key.endswith("accuracy")}})
        print(f"Finished {patient_id}: {len(patient_scores)} spots, {len(edges)} edges")
    pd.DataFrame(patient_rows).to_csv(out_dir / "gse274557_patient_graph_batch_summary.tsv", sep="\t", index=False)
    pd.concat(edge_rows, ignore_index=True).to_csv(out_dir / "gse274557_patient_edge_type_summary.tsv", sep="\t", index=False)
    print(f"Wrote {out_dir / 'gse274557_patient_graph_batch_summary.tsv'}")


if __name__ == "__main__":
    main()
