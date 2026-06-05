from __future__ import annotations

from pathlib import Path

import pandas as pd


def write_atlas_plots(frame: pd.DataFrame, out_dir: str | Path) -> list[Path]:
    """Write core EMT atlas plots when matplotlib/seaborn are available."""
    try:
        import matplotlib.pyplot as plt
        import seaborn as sns
    except ImportError:
        return []

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []

    if {"emt_score", "stromal_fibroblast"}.issubset(frame.columns):
        path = out / "emt_vs_stromal.png"
        plt.figure(figsize=(7, 5))
        hue = "cancer_type" if "cancer_type" in frame.columns and frame["cancer_type"].nunique() <= 12 else None
        sns.scatterplot(data=frame, x="stromal_fibroblast", y="emt_score", hue=hue, s=24, linewidth=0)
        plt.title("EMT score vs stromal/fibroblast signal")
        plt.tight_layout()
        plt.savefig(path, dpi=180)
        plt.close()
        paths.append(path)

    if "partial_emt_score" in frame.columns:
        path = out / "partial_emt_distribution.png"
        plt.figure(figsize=(7, 4))
        sns.histplot(data=frame, x="partial_emt_score", bins=40)
        plt.title("Partial EMT score distribution")
        plt.tight_layout()
        plt.savefig(path, dpi=180)
        plt.close()
        paths.append(path)

    heat_cols = [col for col in ["immune_total", "caf_tam_niche", "hypoxia", "ferroptosis_window"] if col in frame.columns]
    if "cancer_type" in frame.columns and heat_cols:
        path = out / "niche_heatmap.png"
        heat = frame.groupby("cancer_type")[heat_cols].mean()
        plt.figure(figsize=(8, max(4, len(heat) * 0.22)))
        sns.heatmap(heat, cmap="vlag", center=0)
        plt.title("TME and vulnerability signals by cancer type")
        plt.tight_layout()
        plt.savefig(path, dpi=180)
        plt.close()
        paths.append(path)

    if {"sample_id", "ferroptosis_window"}.issubset(frame.columns):
        path = out / "ferroptosis_window_top.png"
        top = frame.nlargest(min(25, len(frame)), "ferroptosis_window")
        plt.figure(figsize=(8, 5))
        sns.barplot(data=top, y="sample_id", x="ferroptosis_window", color="#4477aa")
        plt.title("Top ferroptosis-window samples")
        plt.tight_layout()
        plt.savefig(path, dpi=180)
        plt.close()
        paths.append(path)

    return paths

