from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Generate EMT-ViSTA benchmark figures.")
    p.add_argument("--metrics", required=True)
    p.add_argument("--predictions", required=True)
    p.add_argument("--pairs", required=True)
    p.add_argument("--out-dir", required=True)
    return p


def main() -> None:
    args = parser().parse_args()
    metrics = pd.read_csv(args.metrics, sep="\t")
    predictions = pd.read_csv(args.predictions, sep="\t", low_memory=False)
    pairs = pd.read_csv(args.pairs, sep="\t", low_memory=False)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    test = metrics.loc[metrics["split"].astype(str).eq("test")].copy()
    figure, axis = plt.subplots(figsize=(9, 4.8))
    sns.barplot(data=test, x="target", y="spearman", color="#26828e", ax=axis)
    axis.axhline(0.35, color="#b23a48", linestyle="--", linewidth=1.2, label="predefined gate")
    axis.set_ylim(min(-0.2, test["spearman"].min() - 0.05), 1.0)
    axis.set_xlabel("")
    axis.set_ylabel("Held-out Spearman correlation")
    axis.tick_params(axis="x", rotation=35)
    axis.legend(frameon=False)
    figure.tight_layout()
    figure.savefig(out_dir / "figure_model_performance.png", dpi=200, bbox_inches="tight")
    plt.close(figure)

    merged = pairs[["spot_uid", "dataset_id", "partial_emt_score", "stromal_contamination_risk"]].merge(
        predictions[["spot_uid", "pred_partial_emt_gated_probability", "pred_stromal_inflated_emt_risk", "abstain"]],
        on="spot_uid",
        how="inner",
    )
    figure, axis = plt.subplots(figsize=(7.5, 5.5))
    sns.scatterplot(
        data=merged,
        x="partial_emt_score",
        y="pred_partial_emt_gated_probability",
        hue="dataset_id",
        style="abstain",
        s=18,
        alpha=0.65,
        ax=axis,
    )
    axis.set_xlabel("Measured partial-EMT score")
    axis.set_ylabel("Predicted gated partial-EMT probability")
    axis.legend(bbox_to_anchor=(1.02, 1), loc="upper left", frameon=False, fontsize=7)
    figure.tight_layout()
    figure.savefig(out_dir / "figure_partial_emt_validation.png", dpi=200, bbox_inches="tight")
    plt.close(figure)
    print(f"Wrote EMT-ViSTA paper figures to {out_dir}")


if __name__ == "__main__":
    main()
