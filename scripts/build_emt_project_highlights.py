from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
GROUP_SUMMARY = ROOT / "data/processed/pan_cancer_emt_state_atlas/cards/cancer_group_state_summary.tsv"
ANNOTATED_SUMMARY = ROOT / "data/processed/pan_cancer_emt_state_atlas/annotated_single_cell/tumor_vs_stroma_emt_summary.tsv"
OUT_DIR = ROOT / "docs/pan_cancer_emt_state_atlas"


def build_figure(out_path: str | Path = OUT_DIR / "project_highlights.png") -> Path:
    group = pd.read_csv(GROUP_SUMMARY, sep="\t")
    annotated = pd.read_csv(ANNOTATED_SUMMARY, sep="\t")
    group = group.copy()
    for col in ["mesenchymal_like_fraction", "hybrid_fraction", "stromal_dominant_fraction"]:
        if col not in group.columns:
            group[col] = 0.0
    group["emt_pressure"] = (
        group["mesenchymal_like_fraction"].fillna(0)
        + 0.5 * group["hybrid_fraction"].fillna(0)
        + 0.25 * group["stromal_dominant_fraction"].fillna(0)
    )
    three_ca = annotated[annotated["source"].astype(str).eq("3CA")].copy()
    three_ca = three_ca.sort_values("cells", ascending=False)

    fig, axes = plt.subplots(2, 2, figsize=(14, 9), constrained_layout=True)
    fig.suptitle("Pan-Cancer EMT State Atlas: Project Highlights", fontsize=18, fontweight="bold", color="#1f4e79")

    ranked = group.sort_values("emt_pressure", ascending=True).tail(10)
    axes[0, 0].barh(ranked["cancer_group"], ranked["emt_pressure"], color="#c51b7d")
    axes[0, 0].set_title("Combined EMT pressure")
    axes[0, 0].set_xlabel("mesenchymal + hybrid contribution")

    caution = group.sort_values("stromal_dominant_fraction", ascending=True).tail(10)
    axes[0, 1].barh(caution["cancer_group"], caution["stromal_dominant_fraction"], color="#8c6d31")
    axes[0, 1].set_title("Stromal mimicry caution")
    axes[0, 1].set_xlabel("stromal-dominant fraction")

    axes[1, 0].barh(three_ca["cancer_group"], three_ca["cells"], color="#2b8cbe")
    axes[1, 0].set_title("Real annotated 3CA coverage")
    axes[1, 0].set_xlabel("cells scored")

    interpretation_counts = three_ca["interpretation"].value_counts().sort_values()
    interpretation_counts.index = [str(label).replace("_", " ") for label in interpretation_counts.index]
    axes[1, 1].barh(interpretation_counts.index, interpretation_counts.values, color="#238b45")
    axes[1, 1].set_title("Tumor-versus-stroma interpretations")
    axes[1, 1].set_xlabel("annotated cohorts")

    for axis in axes.flat:
        axis.spines[["top", "right"]].set_visible(False)
        axis.grid(axis="x", alpha=0.2)
        axis.set_axisbelow(True)
        axis.tick_params(labelsize=8)

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return out


if __name__ == "__main__":
    print(f"Wrote {build_figure()}")
