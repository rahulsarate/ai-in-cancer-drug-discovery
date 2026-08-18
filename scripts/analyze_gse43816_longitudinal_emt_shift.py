from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]

KEY_FEATURES = [
    "emt_score",
    "partial_emt_score",
    "hybrid_fraction_estimate",
    "mesenchymal_fraction_estimate",
    "persister_fraction_estimate",
    "plasticity_index",
    "resistant_fraction_estimate",
    "therapy_selection_pressure",
    "residual_disease_probability_proxy",
]

RESISTANCE_AXES = [
    "tnbc_axl_tam",
    "tnbc_tgfb",
    "tnbc_yap_taz",
    "tnbc_hypoxia",
    "tnbc_stemness_persister",
    "caf_tam_niche",
]

STATE_FEATURES = [
    "epithelial_fraction_estimate",
    "hybrid_fraction_estimate",
    "mesenchymal_fraction_estimate",
    "persister_fraction_estimate",
]
REPORT_FEATURES = [
    "emt_score",
    "hybrid_fraction_estimate",
    "mesenchymal_fraction_estimate",
    "persister_fraction_estimate",
    "plasticity_index",
    "therapy_selection_pressure",
    "residual_disease_probability_proxy",
]


def ensure_dirs(out_dir: Path, docs_asset_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    docs_asset_dir.mkdir(parents=True, exist_ok=True)


def load_gse43816(model_table: Path) -> pd.DataFrame:
    df = pd.read_csv(model_table, sep="\t")
    df = df[df["dataset_id"] == "GSE43816"].copy()
    if df.empty:
        raise SystemExit("No GSE43816 rows found in model table.")
    if "patient" in df.columns:
        df["patient_pair_id"] = df["patient"].astype(str).str.replace(r"\.0$", "", regex=True)
    else:
        df["patient_pair_id"] = df["sample_title"].astype(str).str.extract(r"^(\d+)_", expand=False)
    df["therapy_time"] = df["standard_timepoint"].map({"T0": "before", "T2": "after"}).fillna(df["standard_timepoint"])
    return df


def build_pair_table(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    feature_cols = list(dict.fromkeys(col for col in KEY_FEATURES + RESISTANCE_AXES + STATE_FEATURES if col in df.columns))
    pairs = []
    wide_rows = []
    for patient_id, group in df.groupby("patient_pair_id"):
        before = group[group["therapy_time"] == "before"]
        after = group[group["therapy_time"] == "after"]
        if before.empty or after.empty:
            continue
        before_row = before.iloc[0]
        after_row = after.iloc[0]
        wide = {
            "patient_pair_id": patient_id,
            "before_sample_id": before_row["sample_id"],
            "after_sample_id": after_row["sample_id"],
            "before_dominant_resistance_axis": before_row.get("dominant_resistance_axis", "unknown"),
            "after_dominant_resistance_axis": after_row.get("dominant_resistance_axis", "unknown"),
        }
        for col in feature_cols:
            before_val = pd.to_numeric(before_row.get(col), errors="coerce")
            after_val = pd.to_numeric(after_row.get(col), errors="coerce")
            wide[f"before_{col}"] = before_val
            wide[f"after_{col}"] = after_val
            wide[f"delta_{col}"] = after_val - before_val
            pairs.append(
                {
                    "patient_pair_id": patient_id,
                    "feature": col,
                    "before": before_val,
                    "after": after_val,
                    "delta_after_minus_before": after_val - before_val,
                }
            )
        wide_rows.append(wide)
    return pd.DataFrame(wide_rows), pd.DataFrame(pairs)


def summarize_shifts(pair_wide: pd.DataFrame, pair_long: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for feature, group in pair_long.groupby("feature"):
        deltas = group["delta_after_minus_before"].dropna()
        if deltas.empty:
            continue
        rows.append(
            {
                "feature": feature,
                "pairs": int(deltas.shape[0]),
                "mean_delta": float(deltas.mean()),
                "median_delta": float(deltas.median()),
                "patients_increased": int((deltas > 0).sum()),
                "patients_decreased": int((deltas < 0).sum()),
                "largest_increase_patient": str(group.loc[group["delta_after_minus_before"].idxmax(), "patient_pair_id"]),
                "largest_decrease_patient": str(group.loc[group["delta_after_minus_before"].idxmin(), "patient_pair_id"]),
            }
        )
    summary = pd.DataFrame(rows).sort_values("feature")
    if not pair_wide.empty:
        summary.attrs["selected_patient"] = select_report_patient(pair_wide)
    return summary


def percentile_rank(values: pd.Series, value: float) -> float:
    numeric = pd.to_numeric(values, errors="coerce").dropna()
    if numeric.empty or pd.isna(value):
        return np.nan
    return float((numeric <= value).mean() * 100.0)


def add_percentile_columns(pair_wide: pd.DataFrame, df: pd.DataFrame) -> pd.DataFrame:
    out = pair_wide.copy()
    for feature in REPORT_FEATURES:
        if feature not in df.columns:
            continue
        cohort_values = pd.to_numeric(df[feature], errors="coerce")
        for prefix in ["before", "after"]:
            col = f"{prefix}_{feature}"
            if col in out.columns:
                out[f"{col}_cohort_percentile"] = out[col].apply(lambda value: percentile_rank(cohort_values, value))
    return out


def bootstrap_delta_intervals(pair_long: pd.DataFrame, seed: int = 2026, n_bootstrap: int = 2000) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    for feature, group in pair_long.groupby("feature"):
        values = pd.to_numeric(group["delta_after_minus_before"], errors="coerce").dropna().to_numpy(dtype=float)
        if values.size == 0:
            continue
        boot = np.array([rng.choice(values, size=values.size, replace=True).mean() for _ in range(n_bootstrap)])
        rows.append(
            {
                "feature": feature,
                "pairs": int(values.size),
                "mean_delta": float(values.mean()),
                "median_delta": float(np.median(values)),
                "delta_mean_q025": float(np.quantile(boot, 0.025)),
                "delta_mean_q975": float(np.quantile(boot, 0.975)),
            }
        )
    return pd.DataFrame(rows).sort_values("feature")


def select_report_patient(pair_wide: pd.DataFrame) -> str:
    candidates = pair_wide.copy()
    score = pd.Series(0.0, index=candidates.index)
    for col, weight in [
        ("delta_therapy_selection_pressure", 2.0),
        ("delta_plasticity_index", 1.5),
        ("delta_residual_disease_probability_proxy", 1.0),
        ("after_resistant_fraction_estimate", 1.0),
    ]:
        if col in candidates:
            score += weight * pd.to_numeric(candidates[col], errors="coerce").fillna(0)
    return str(candidates.loc[score.idxmax(), "patient_pair_id"])


def save_paired_feature_plot(pair_long: pd.DataFrame, out_path: Path) -> None:
    features = ["emt_score", "hybrid_fraction_estimate", "persister_fraction_estimate", "therapy_selection_pressure"]
    fig, axes = plt.subplots(2, 2, figsize=(10, 7), constrained_layout=True)
    for ax, feature in zip(axes.ravel(), features):
        subset = pair_long[pair_long["feature"] == feature]
        for _, row in subset.iterrows():
            ax.plot([0, 1], [row["before"], row["after"]], marker="o", linewidth=1.6, color="#4c78a8", alpha=0.75)
            ax.text(1.03, row["after"], str(row["patient_pair_id"]), va="center", fontsize=8)
        ax.set_xticks([0, 1], ["Before", "After"])
        ax.set_title(feature.replace("_", " "))
        ax.axhline(0, color="#888888", linewidth=0.8, alpha=0.4)
    fig.suptitle("GSE43816 paired EMT plasticity shifts under NAC", fontsize=13)
    fig.savefig(out_path, dpi=180)
    plt.close(fig)


def save_delta_heatmap(pair_wide: pd.DataFrame, out_path: Path) -> None:
    features = [feature for feature in KEY_FEATURES if f"delta_{feature}" in pair_wide.columns]
    data = pair_wide.set_index("patient_pair_id")[[f"delta_{feature}" for feature in features]]
    values = data.to_numpy(dtype=float)
    vmax = np.nanmax(np.abs(values)) if values.size else 1
    vmax = max(vmax, 0.01)
    fig, ax = plt.subplots(figsize=(10, 5.5), constrained_layout=True)
    im = ax.imshow(values, aspect="auto", cmap="coolwarm", vmin=-vmax, vmax=vmax)
    ax.set_yticks(range(data.shape[0]), data.index.astype(str))
    ax.set_xticks(range(len(features)), [feature.replace("_", "\n") for feature in features], rotation=0, fontsize=8)
    ax.set_title("After-minus-before digital-twin feature deltas")
    ax.set_ylabel("Patient")
    fig.colorbar(im, ax=ax, label="Delta")
    fig.savefig(out_path, dpi=180)
    plt.close(fig)


def save_state_fraction_plot(df: pd.DataFrame, patient_id: str, out_path: Path) -> None:
    subset = df[df["patient_pair_id"] == patient_id].sort_values("therapy_time", key=lambda s: s.map({"before": 0, "after": 1}))
    labels = ["Before", "After"]
    states = STATE_FEATURES
    colors = ["#59a14f", "#f2cf5b", "#e15759", "#76b7b2"]
    bottom = np.zeros(subset.shape[0])
    fig, ax = plt.subplots(figsize=(7, 4.5), constrained_layout=True)
    for state, color in zip(states, colors):
        vals = subset[state].astype(float).to_numpy()
        ax.bar(labels, vals, bottom=bottom, label=state.replace("_fraction_estimate", ""), color=color)
        bottom += vals
    ax.set_ylim(0, 1)
    ax.set_ylabel("Estimated fraction")
    ax.set_title(f"Patient {patient_id}: digital-twin state fractions")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=2, frameon=False)
    fig.savefig(out_path, dpi=180)
    plt.close(fig)


def save_axis_shift_plot(pair_wide: pd.DataFrame, out_path: Path) -> None:
    before_counts = pair_wide["before_dominant_resistance_axis"].value_counts()
    after_counts = pair_wide["after_dominant_resistance_axis"].value_counts()
    axes_names = sorted(set(before_counts.index).union(after_counts.index))
    x = np.arange(len(axes_names))
    width = 0.38
    fig, ax = plt.subplots(figsize=(8, 4.5), constrained_layout=True)
    ax.bar(x - width / 2, [before_counts.get(name, 0) for name in axes_names], width, label="Before", color="#4c78a8")
    ax.bar(x + width / 2, [after_counts.get(name, 0) for name in axes_names], width, label="After", color="#f58518")
    ax.set_xticks(x, axes_names, rotation=30, ha="right")
    ax.set_ylabel("Patients")
    ax.set_title("Dominant resistance-axis shifts")
    ax.legend(frameon=False)
    fig.savefig(out_path, dpi=180)
    plt.close(fig)


def format_value(value: object, digits: int = 3) -> str:
    try:
        if pd.isna(value):
            return "NA"
        return f"{float(value):.{digits}f}"
    except (TypeError, ValueError):
        return str(value)


def write_clinician_report(
    pair_wide: pd.DataFrame,
    summary: pd.DataFrame,
    uncertainty: pd.DataFrame,
    patient_id: str,
    image_paths: dict[str, Path],
    out_path: Path,
) -> None:
    row = pair_wide[pair_wide["patient_pair_id"] == patient_id].iloc[0]
    uncertainty_lookup = uncertainty.set_index("feature") if not uncertainty.empty else pd.DataFrame()
    risk_delta = row.get("delta_residual_disease_probability_proxy", np.nan)
    plasticity_delta = row.get("delta_plasticity_index", np.nan)
    pressure_delta = row.get("delta_therapy_selection_pressure", np.nan)
    interpretation = "increased post-therapy resistance pressure" if pressure_delta > 0 else "reduced post-therapy resistance pressure"
    lines = [
        "# Clinician-Style Digital Twin Report",
        "",
        "## Case Context",
        "",
        f"- Dataset: `GSE43816` longitudinal TNBC neoadjuvant chemotherapy cohort.",
        f"- Patient pair: `{patient_id}`.",
        f"- Pretreatment sample: `{row['before_sample_id']}`.",
        f"- Post-treatment/surgery sample: `{row['after_sample_id']}`.",
        "- Use: research interpretation only, not a clinical treatment recommendation.",
        "",
        "## Digital-Twin Readout",
        "",
        "| Feature | Before | After | Change | Before pctile | After pctile | Cohort mean delta 95% CI |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for feature in REPORT_FEATURES:
        if not uncertainty_lookup.empty and feature in uncertainty_lookup.index:
            ci = uncertainty_lookup.loc[feature]
            ci_text = f"{format_value(ci.get('delta_mean_q025'))} to {format_value(ci.get('delta_mean_q975'))}"
        else:
            ci_text = "NA"
        lines.append(
            f"| {feature.replace('_', ' ')} | {format_value(row.get(f'before_{feature}'))} | "
            f"{format_value(row.get(f'after_{feature}'))} | {format_value(row.get(f'delta_{feature}'))} | "
            f"{format_value(row.get(f'before_{feature}_cohort_percentile'), digits=1)} | "
            f"{format_value(row.get(f'after_{feature}_cohort_percentile'), digits=1)} | {ci_text} |"
        )
    lines.extend(
        [
            "",
            "## Resistance Axis",
            "",
            f"- Dominant pretreatment axis: `{row.get('before_dominant_resistance_axis', 'unknown')}`.",
            f"- Dominant post-treatment axis: `{row.get('after_dominant_resistance_axis', 'unknown')}`.",
            f"- Summary interpretation: this paired sample shows **{interpretation}**.",
            "",
            "## Practical Interpretation",
            "",
            f"- Plasticity index change: `{format_value(plasticity_delta)}`.",
            f"- Therapy-selection-pressure change: `{format_value(pressure_delta)}`.",
            f"- Residual-disease-risk proxy change: `{format_value(risk_delta)}`.",
            "- If this were a prospective research case, the appropriate follow-up would be molecular review of the post-treatment residual compartment, not automatic therapy selection.",
            "",
            "## Visual Summary",
            "",
            f"![Selected patient state fractions]({image_paths['state_fraction'].as_posix()})",
            "",
            f"![Paired cohort shifts]({image_paths['paired_shift'].as_posix()})",
            "",
            "## Limitations",
            "",
            "- The cohort has only 7 paired patients.",
            "- Percentiles are relative to the 14 available `GSE43816` samples, not a population reference range.",
            "- Uncertainty intervals are bootstrap intervals around the cohort mean paired delta.",
            "- GEO response labels are unavailable for this dataset, so this analysis measures therapy-induced plasticity, not pCR prediction.",
            "- The digital-twin state fractions are expression-derived proxies and require calibration with larger longitudinal cohorts, pathology, and ideally single-cell/spatial data.",
        ]
    )
    out_path.write_text("\n".join(lines), encoding="utf-8")


def write_analysis_report(pair_wide: pd.DataFrame, summary: pd.DataFrame, uncertainty: pd.DataFrame, image_paths: dict[str, Path], selected_patient: str, out_path: Path) -> None:
    key_summary = summary[summary["feature"].isin(KEY_FEATURES)].copy()
    lines = [
        "# GSE43816 Longitudinal EMT-Shift Analysis",
        "",
        "## Objective",
        "",
        "Quantify paired before-versus-after neoadjuvant chemotherapy shifts in EMT plasticity and digital-twin state estimates for TNBC samples.",
        "",
        "## Cohort",
        "",
        f"- Paired patients analyzed: {pair_wide.shape[0]}.",
        "- Timepoints: pretreatment biopsy (`T0`) and post-treatment/tumorectomy sample (`T2`).",
        "- Dataset response labels are not available, so this is a therapy-induced state-shift analysis.",
        "",
        "## Key Shift Summary",
        "",
        key_summary.to_markdown(index=False),
        "",
        "## Bootstrap Uncertainty",
        "",
        uncertainty[uncertainty["feature"].isin(KEY_FEATURES)].to_markdown(index=False) if not uncertainty.empty else "No uncertainty intervals available.",
        "",
        "## Selected Report Patient",
        "",
        f"`Patient {selected_patient}` was selected because it had the highest weighted post-therapy risk-shift score.",
        "",
        "## Plots",
        "",
        f"![Paired feature shifts]({image_paths['paired_shift'].as_posix()})",
        "",
        f"![Feature delta heatmap]({image_paths['delta_heatmap'].as_posix()})",
        "",
        f"![Dominant resistance axes]({image_paths['axis_shift'].as_posix()})",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Analyze longitudinal EMT shifts in GSE43816 paired TNBC NAC samples.")
    p.add_argument("--model-table", default="data/processed/tnbc_digital_twin/tnbc_nac_emt_digital_twin_model_table.tsv")
    p.add_argument("--out-dir", default="data/processed/tnbc_digital_twin/gse43816_longitudinal")
    p.add_argument("--docs-dir", default="docs/tnbc_digital_twin_emt_plasticity")
    return p


def main() -> None:
    args = parser().parse_args()
    out_dir = ROOT / args.out_dir
    docs_dir = ROOT / args.docs_dir
    asset_dir = docs_dir / "assets" / "gse43816_longitudinal"
    ensure_dirs(out_dir, asset_dir)

    df = load_gse43816(ROOT / args.model_table)
    pair_wide, pair_long = build_pair_table(df)
    if pair_wide.empty:
        raise SystemExit("No complete before/after GSE43816 patient pairs found.")
    pair_wide = add_percentile_columns(pair_wide, df)
    summary = summarize_shifts(pair_wide, pair_long)
    uncertainty = bootstrap_delta_intervals(pair_long)
    selected_patient = summary.attrs.get("selected_patient", select_report_patient(pair_wide))

    pair_wide.to_csv(out_dir / "gse43816_paired_shift_wide.tsv", sep="\t", index=False)
    pair_long.to_csv(out_dir / "gse43816_paired_shift_long.tsv", sep="\t", index=False)
    summary.to_csv(out_dir / "gse43816_shift_summary.tsv", sep="\t", index=False)
    uncertainty.to_csv(out_dir / "gse43816_shift_bootstrap_uncertainty.tsv", sep="\t", index=False)

    image_paths = {
        "paired_shift": asset_dir / "gse43816_paired_feature_shifts.png",
        "delta_heatmap": asset_dir / "gse43816_delta_heatmap.png",
        "axis_shift": asset_dir / "gse43816_resistance_axis_shift.png",
        "state_fraction": asset_dir / f"gse43816_patient_{selected_patient}_state_fractions.png",
    }
    save_paired_feature_plot(pair_long, image_paths["paired_shift"])
    save_delta_heatmap(pair_wide, image_paths["delta_heatmap"])
    save_axis_shift_plot(pair_wide, image_paths["axis_shift"])
    save_state_fraction_plot(df, selected_patient, image_paths["state_fraction"])

    write_analysis_report(pair_wide, summary, uncertainty, image_paths, selected_patient, out_dir / "gse43816_longitudinal_emt_shift_report.md")
    write_clinician_report(pair_wide, summary, uncertainty, selected_patient, image_paths, out_dir / "gse43816_clinician_style_digital_twin_report.md")
    print(f"paired_patients={pair_wide.shape[0]} selected_patient={selected_patient}")
    print(summary[summary["feature"].isin(KEY_FEATURES)].to_string(index=False))


if __name__ == "__main__":
    main()
