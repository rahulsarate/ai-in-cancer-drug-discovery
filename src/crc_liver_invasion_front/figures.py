from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


COLORS = {
    "malignant_epithelial": "#b33b45",
    "malignant_partial_emt": "#d97932",
    "hepatocyte": "#5e9f55",
    "mrc1_ccl18_macrophage": "#78589d",
    "activated_fibroblast": "#c58a23",
    "endothelial": "#257d8a",
    "other": "#a5adb4",
}


def _save(fig: plt.Figure, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def plot_interface_maps(scored: pd.DataFrame, output_dir: str | Path) -> Path:
    liver_sections = list(scored.loc[scored["is_liver_metastasis"].astype(bool), "section_id"].unique())
    fig, axes = plt.subplots(len(liver_sections), 2, figsize=(12, 5.2 * len(liver_sections)), squeeze=False)
    for row_index, section_id in enumerate(liver_sections):
        section = scored[scored["section_id"].eq(section_id)]
        ax = axes[row_index, 0]
        for node_type, subset in section.groupby("dominant_compartment"):
            ax.scatter(subset["pixel_x"], -subset["pixel_y"], s=6, alpha=0.82, c=COLORS.get(node_type, "#a5adb4"), label=node_type.replace("_", " "))
        ax.set_title(f"{section_id}: inferred compartments")
        ax.set_aspect("equal")
        ax.axis("off")
        if row_index == 0:
            ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1), frameon=False, fontsize=8)

        ax = axes[row_index, 1]
        scatter = ax.scatter(
            section["pixel_x"], -section["pixel_y"], c=section["signed_interface_distance_um"].clip(-1000, 1000),
            cmap="RdYlGn", vmin=-1000, vmax=1000, s=7,
        )
        front = section[section["is_interface_window"]]
        ax.scatter(front["pixel_x"], -front["pixel_y"], facecolors="none", edgecolors="#15191d", s=14, linewidths=0.35)
        ax.set_title("Signed distance to tumour-liver interface")
        ax.set_aspect("equal")
        ax.axis("off")
        fig.colorbar(scatter, ax=ax, fraction=0.035, pad=0.02, label="micrometres (approx.)")
    fig.suptitle("CRC liver-metastasis invasion-front maps", fontsize=15, fontweight="bold")
    return _save(fig, Path(output_dir) / "interface_maps.png")


def plot_gradient_profiles(scored: pd.DataFrame, output_dir: str | Path) -> Path:
    liver = scored[scored["is_liver_metastasis"].astype(bool)].copy()
    liver["distance_bin_um"] = (liver["signed_interface_distance_um"].clip(-1000, 1000) / 200).round() * 200
    programs = ["partial_emt", "mrc1_ccl18_macrophage", "activated_fibroblast", "endothelial", "ecm_remodeling", "glycolysis"]
    profile = liver.groupby(["section_id", "distance_bin_um"])[programs].mean().reset_index()
    fig, axes = plt.subplots(2, 3, figsize=(13, 7.5), sharex=True, sharey=True)
    palette = ["#246a9b", "#b33b45"]
    for ax, program in zip(axes.flat, programs):
        for color, (section_id, section) in zip(palette, profile.groupby("section_id")):
            ax.plot(section["distance_bin_um"], section[program], marker="o", ms=3, lw=1.6, color=color, label=section_id)
        ax.axvspan(-300, 300, color="#e7ecef", alpha=0.75)
        ax.axvline(0, color="#30363b", lw=0.8)
        ax.set_title(program.replace("_", " ").title())
        ax.grid(alpha=0.15)
    axes[1, 1].set_xlabel("Signed distance: tumour (-) to liver (+), micrometres")
    axes[0, 0].set_ylabel("Mean within-section percentile")
    axes[1, 0].set_ylabel("Mean within-section percentile")
    axes[0, 0].legend(frameon=False, fontsize=8)
    fig.suptitle("Molecular gradients across the inferred interface", fontsize=15, fontweight="bold")
    return _save(fig, Path(output_dir) / "interface_gradient_profiles.png")


def plot_model_summary(importance: pd.DataFrame, ablations: pd.DataFrame, metrics: dict[str, object], output_dir: str | Path) -> Path:
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))
    top = importance.head(15).sort_values("coefficient")
    axes[0].barh(top["feature"].str.replace("_", " "), top["coefficient"], color=np.where(top["coefficient"] >= 0, "#b33b45", "#246a9b"))
    axes[0].axvline(0, color="#30363b", lw=0.8)
    axes[0].set_title("Standardized model coefficients")
    axes[0].set_xlabel("Tumour-front direction")
    axes[0].tick_params(axis="y", labelsize=8)

    shown = ablations[ablations["removed_feature_group"].ne("none")].sort_values("auc_drop_vs_full")
    axes[1].barh(shown["removed_feature_group"].str.replace("_", " "), shown["auc_drop_vs_full"], color="#c58a23")
    axes[1].axvline(0, color="#30363b", lw=0.8)
    axes[1].set_title("Feature-group ablation")
    axes[1].set_xlabel("Cross-section AUC drop")
    fig.suptitle(
        f"Typed message-passing baseline: LOSO AUC {metrics.get('roc_auc', float('nan')):.3f}, permutation P {metrics.get('permutation_p', float('nan')):.3f}",
        fontsize=14,
        fontweight="bold",
    )
    return _save(fig, Path(output_dir) / "interface_model_interpretation.png")


def plot_workflow(output_dir: str | Path) -> Path:
    fig, ax = plt.subplots(figsize=(14, 4.8))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 5)
    ax.axis("off")
    stages = [
        (0.3, "Public data", "6 Visium sections\n+ scRNA references"),
        (3.0, "Spatial states", "CRC, pEMT, liver,\nmacrophage, CAF, vessel"),
        (5.7, "Interface", "Signed 300 um bands\n+ contamination flags"),
        (8.4, "Heterograph", "Contact, LR, ECM and\nglycolysis edges"),
        (11.1, "Validation", "Leave-section-out\n+ permutation + ablation"),
    ]
    colors = ["#246a9b", "#26786f", "#b33b45", "#78589d", "#c58a23"]
    for index, ((x, title, body), color) in enumerate(zip(stages, colors)):
        rect = plt.Rectangle((x, 1.15), 2.25, 2.5, facecolor="#f4f6f8", edgecolor=color, linewidth=2)
        ax.add_patch(rect)
        ax.text(x + 1.125, 2.95, title, ha="center", va="center", fontsize=12, fontweight="bold", color=color)
        ax.text(x + 1.125, 2.15, body, ha="center", va="center", fontsize=9, color="#17212b")
        if index < len(stages) - 1:
            ax.annotate("", xy=(x + 2.68, 2.4), xytext=(x + 2.3, 2.4), arrowprops={"arrowstyle": "->", "lw": 1.6, "color": "#5f6b76"})
    ax.text(7, 4.45, "CRC Liver-Metastasis Invasion-Front Model", ha="center", fontsize=17, fontweight="bold", color="#17212b")
    ax.text(7, 0.5, "Research hypothesis engine | compartment-aware | section-safe validation | not a clinical classifier", ha="center", fontsize=10, color="#5f6b76")
    return _save(fig, Path(output_dir) / "workflow_overview.png")


def plot_heterograph_excerpt(nodes: pd.DataFrame, edges: pd.DataFrame, output_dir: str | Path) -> Path:
    liver = nodes[nodes["section_id"].eq("GSM7058760_L1") & nodes["interface_band"].isin(["tumour_front", "liver_front"])].copy()
    if liver.empty:
        raise ValueError("No L1 interface nodes were available for graph visualization.")
    center = liver[["x", "y"]].median()
    liver["center_distance"] = np.sqrt((liver["x"] - center["x"]) ** 2 + (liver["y"] - center["y"]) ** 2)
    selected = liver.nsmallest(min(650, len(liver)), "center_distance")
    selected_ids = set(selected["spot_id"].astype(str))
    local_edges = edges[
        edges["source"].astype(str).isin(selected_ids)
        & edges["target"].astype(str).isin(selected_ids)
        & edges["edge_family"].isin(["spatial", "cross_interface"])
    ].copy()
    positions = selected.set_index("spot_id")[["x", "y"]]
    fig, axes = plt.subplots(1, 2, figsize=(15, 6.8), gridspec_kw={"width_ratios": [1.15, 1.0]})
    ax = axes[0]
    spatial = local_edges[local_edges["edge_family"].eq("spatial")].drop_duplicates(["source", "target"])
    for edge in spatial.itertuples(index=False):
        source, target = positions.loc[str(edge.source)], positions.loc[str(edge.target)]
        ax.plot([source["x"], target["x"]], [-source["y"], -target["y"]], color="#d9dee2", lw=0.35, alpha=0.55, zorder=1)
    contacts = local_edges[local_edges["edge_family"].eq("cross_interface")].drop_duplicates(["source", "target"])
    for edge in contacts.itertuples(index=False):
        source, target = positions.loc[str(edge.source)], positions.loc[str(edge.target)]
        ax.plot([source["x"], target["x"]], [-source["y"], -target["y"]], color="#17212b", lw=1.0, alpha=0.8, zorder=2)
    for node_type, group in selected.groupby("node_type"):
        ax.scatter(group["x"], -group["y"], s=22, color=COLORS.get(node_type, "#a5adb4"), label=node_type.replace("_", " "), edgecolors="white", linewidths=0.2, zorder=3)
    ax.set_title("Contiguous L1 interface graph excerpt")
    ax.set_aspect("equal")
    ax.axis("off")
    ax.legend(frameon=False, fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.04), ncol=2)

    ax = axes[1]
    family_counts = edges.groupby("edge_family").size().sort_values().tail(10)
    family_labels = {
        "spatial": "Spatial",
        "compartment_contact": "Compartment contact",
        "glycolysis_gradient": "Glycolysis gradient",
        "ecm_gradient": "ECM gradient",
        "cross_interface": "Tumour-liver contact",
        "ligand_receptor:fibroblast_to_malignant": "Fibroblast to tumour LR",
        "ligand_receptor:myeloid_ecm_to_malignant": "Myeloid/ECM to tumour LR",
        "ligand_receptor:myeloid_to_pemt": "Myeloid to pEMT LR",
        "ligand_receptor:ecm_adhesion": "ECM adhesion LR",
    }
    labels = [family_labels.get(value, value.replace("_", " ")) for value in family_counts.index]
    ax.barh(labels, family_counts.values, color="#78589d")
    ax.set_title("Typed graph relations")
    ax.set_xlabel("Directed edges")
    ax.tick_params(axis="y", labelsize=8)
    ax.grid(axis="x", alpha=0.15)
    fig.suptitle("Heterogeneous tumour-liver interface graph", fontsize=15, fontweight="bold")
    fig.subplots_adjust(left=0.04, right=0.98, top=0.84, bottom=0.17, wspace=0.30)
    return _save(fig, Path(output_dir) / "heterograph_interface_excerpt.png")
