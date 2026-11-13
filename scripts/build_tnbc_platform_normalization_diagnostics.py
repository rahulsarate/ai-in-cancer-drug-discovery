from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import ks_2samp


ROOT = Path(__file__).resolve().parents[1]

DIAGNOSTIC_FEATURES = [
    "epithelial",
    "mesenchymal",
    "emt_score",
    "partial_emt_score",
    "stromal_fibroblast",
    "caf",
    "immune_total",
    "tam_spp1",
    "hypoxia",
    "tnbc_axl_tam",
    "tnbc_tgfb",
    "tnbc_yap_taz",
    "tnbc_hypoxia",
    "tnbc_stemness_persister",
    "tnbc_persister_tumor_refined",
    "tnbc_persister_stress_tolerance",
    "tnbc_persister_niche",
    "epithelial_fraction_estimate",
    "hybrid_fraction_estimate",
    "mesenchymal_fraction_estimate",
    "persister_fraction_estimate",
    "plasticity_index",
    "resistant_fraction_estimate",
    "therapy_selection_pressure",
]


def feature_summary(df: pd.DataFrame, label: str, features: list[str]) -> pd.DataFrame:
    rows = []
    for feature in features:
        if feature not in df.columns:
            rows.append({"cohort": label, "feature": feature, "n": 0, "missing_fraction": 1.0})
            continue
        values = pd.to_numeric(df[feature], errors="coerce")
        present = values.dropna()
        rows.append(
            {
                "cohort": label,
                "feature": feature,
                "n": int(present.shape[0]),
                "missing_fraction": float(values.isna().mean()),
                "mean": float(present.mean()) if not present.empty else np.nan,
                "std": float(present.std(ddof=0)) if not present.empty else np.nan,
                "median": float(present.median()) if not present.empty else np.nan,
                "q025": float(present.quantile(0.025)) if not present.empty else np.nan,
                "q975": float(present.quantile(0.975)) if not present.empty else np.nan,
            }
        )
    return pd.DataFrame(rows)


def compare_distributions(internal: pd.DataFrame, external: pd.DataFrame, features: list[str]) -> pd.DataFrame:
    rows = []
    for feature in features:
        if feature not in internal.columns or feature not in external.columns:
            continue
        internal_values = pd.to_numeric(internal[feature], errors="coerce").dropna()
        external_values = pd.to_numeric(external[feature], errors="coerce").dropna()
        if internal_values.empty or external_values.empty:
            continue
        pooled_std = float(np.sqrt((internal_values.var(ddof=0) + external_values.var(ddof=0)) / 2.0))
        ks = ks_2samp(internal_values, external_values)
        rows.append(
            {
                "feature": feature,
                "internal_n": int(internal_values.shape[0]),
                "external_n": int(external_values.shape[0]),
                "internal_mean": float(internal_values.mean()),
                "external_mean": float(external_values.mean()),
                "mean_shift_external_minus_internal": float(external_values.mean() - internal_values.mean()),
                "standardized_mean_shift": float((external_values.mean() - internal_values.mean()) / pooled_std) if pooled_std > 0 else np.nan,
                "internal_median": float(internal_values.median()),
                "external_median": float(external_values.median()),
                "ks_statistic": float(ks.statistic),
                "ks_pvalue": float(ks.pvalue),
            }
        )
    return pd.DataFrame(rows).sort_values("ks_statistic", ascending=False)


def save_shift_plot(comparison: pd.DataFrame, out_path: Path) -> None:
    if comparison.empty:
        return
    plot_df = comparison.head(20).sort_values("standardized_mean_shift")
    fig, ax = plt.subplots(figsize=(8, 6.5), constrained_layout=True)
    ax.barh(plot_df["feature"].str.replace("_", " "), plot_df["standardized_mean_shift"], color="#4c78a8")
    ax.axvline(0, color="#777777", linewidth=1)
    ax.set_xlabel("Standardized mean shift: external minus internal")
    ax.set_title("Platform normalization diagnostic: strongest feature shifts")
    fig.savefig(out_path, dpi=180)
    plt.close(fig)


def save_response_balance_plot(external: pd.DataFrame, out_path: Path) -> None:
    if external.empty or "standard_response" not in external.columns:
        return
    counts = external["standard_response"].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(5.5, 4), constrained_layout=True)
    ax.bar(counts.index, counts.values, color=["#4c78a8", "#e15759"])
    ax.set_ylabel("Samples")
    ax.set_title("External validation response balance")
    ax.tick_params(axis="x", rotation=20)
    fig.savefig(out_path, dpi=180)
    plt.close(fig)


def write_report(summary: pd.DataFrame, comparison: pd.DataFrame, image_paths: dict[str, Path], out_path: Path) -> None:
    lines = [
        "# TNBC Platform Normalization Diagnostics",
        "",
        "## Purpose",
        "",
        "Quantify distribution shifts between the internal array-derived TNBC response-model features and the external RNA-seq TPM-derived validation features before interpreting cross-cohort performance.",
        "",
        "## Feature Summary",
        "",
        summary.to_markdown(index=False) if not summary.empty else "No feature summary available.",
        "",
        "## Internal Versus External Feature Shift",
        "",
        comparison.to_markdown(index=False) if not comparison.empty else "No comparable features available.",
        "",
        "## Plots",
        "",
        f"![Feature shifts]({image_paths['shift_plot'].as_posix()})",
        "",
        f"![Response balance]({image_paths['response_balance'].as_posix()})",
        "",
        "## Interpretation Rules",
        "",
        "- Large standardized mean shifts or KS statistics indicate platform/cohort effects that can dominate response-model performance.",
        "- Cross-platform external metrics should be interpreted only after reviewing these diagnostics.",
        "- If shifts are large, prefer rank/percentile calibration, same-platform validation, or explicit batch correction before model claims.",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Build platform normalization diagnostics for internal and external TNBC response features.")
    p.add_argument("--internal-table", default="data/processed/tnbc_digital_twin/tnbc_nac_emt_digital_twin_tnbc_response_model_table.tsv")
    p.add_argument("--external-table", default="data/processed/tnbc_digital_twin/external_validation/gse163882/external_validation_scored_input.tsv")
    p.add_argument("--out-dir", default="data/processed/tnbc_digital_twin/platform_normalization")
    p.add_argument("--docs-dir", default="docs/tnbc_digital_twin_emt_plasticity")
    return p


def main() -> None:
    args = parser().parse_args()
    out_dir = ROOT / args.out_dir
    asset_dir = ROOT / args.docs_dir / "assets" / "platform_normalization"
    out_dir.mkdir(parents=True, exist_ok=True)
    asset_dir.mkdir(parents=True, exist_ok=True)
    internal = pd.read_csv(ROOT / args.internal_table, sep="\t")
    external = pd.read_csv(ROOT / args.external_table, sep="\t")
    internal = internal[internal.get("standard_response", "").isin(["pcr_or_good_response", "residual_or_poor_response"])].copy()
    external = external[external.get("standard_response", "").isin(["pcr_or_good_response", "residual_or_poor_response"])].copy()
    features = [feature for feature in DIAGNOSTIC_FEATURES if feature in internal.columns or feature in external.columns]
    summary = pd.concat([feature_summary(internal, "internal_geo_array", features), feature_summary(external, "external_gse163882_rnaseq_tpm", features)], ignore_index=True)
    comparison = compare_distributions(internal, external, features)
    summary.to_csv(out_dir / "tnbc_platform_feature_summary.tsv", sep="\t", index=False)
    comparison.to_csv(out_dir / "tnbc_platform_feature_shift_diagnostics.tsv", sep="\t", index=False)
    image_paths = {
        "shift_plot": asset_dir / "tnbc_platform_feature_shift_diagnostics.png",
        "response_balance": asset_dir / "gse163882_external_response_balance.png",
    }
    save_shift_plot(comparison, image_paths["shift_plot"])
    save_response_balance_plot(external, image_paths["response_balance"])
    write_report(summary, comparison, image_paths, out_dir / "tnbc_platform_normalization_diagnostics_report.md")
    print(comparison.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
