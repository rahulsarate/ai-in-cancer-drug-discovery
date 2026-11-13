from __future__ import annotations

import argparse
import re
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu


ROOT = Path(__file__).resolve().parents[1]
USER_AGENT = "EMT-Metastasis-AI-TNBC-Digital-Twin/0.1"

BIOLOGY_FEATURES = [
    "emt_score",
    "partial_emt_score",
    "plasticity_index",
    "persister_fraction_estimate",
    "resistant_fraction_estimate",
    "therapy_selection_pressure",
    "tnbc_axl_tam",
    "tnbc_tgfb",
    "tnbc_yap_taz",
    "tnbc_hypoxia",
    "tnbc_stemness_persister",
    "caf_tam_niche",
]


def fetch_supplement_listing(accession: str, timeout: int = 60) -> pd.DataFrame:
    match = re.fullmatch(r"GSE(\d+)", accession.upper())
    if not match:
        return pd.DataFrame()
    prefix = f"GSE{int(match.group(1)) // 1000}nnn"
    url = f"https://ftp.ncbi.nlm.nih.gov/geo/series/{prefix}/{accession}/suppl/"
    request = Request(url, headers={"User-Agent": USER_AGENT})
    rows = []
    try:
        with urlopen(request, timeout=timeout) as response:
            html = response.read().decode("utf-8", errors="replace")
    except (HTTPError, URLError, TimeoutError) as exc:
        return pd.DataFrame([{"accession": accession, "file_name": "", "url": url, "notes": str(exc)}])

    for href in re.findall(r'href="([^"]+)"', html):
        if href in {"../", "/"} or href.endswith("/") or href.startswith(("http://", "https://")):
            continue
        file_url = url + href
        rows.append({"accession": accession, "file_name": href, "url": file_url, "notes": ""})
    if not rows:
        rows.append({"accession": accession, "file_name": "", "url": url, "notes": "No supplementary files listed."})
    return pd.DataFrame(rows)


def bootstrap_difference(
    recurrence: pd.Series,
    no_recurrence: pd.Series,
    n_bootstrap: int,
    seed: int,
) -> dict[str, float]:
    recurrence_values = recurrence.to_numpy(dtype=float)
    no_recurrence_values = no_recurrence.to_numpy(dtype=float)
    if recurrence_values.size == 0 or no_recurrence_values.size == 0:
        return {
            "delta_mean_q025": np.nan,
            "delta_mean_q975": np.nan,
            "bootstrap_probability_delta_gt_0": np.nan,
            "bootstrap_probability_delta_lt_0": np.nan,
        }
    rng = np.random.default_rng(seed)
    recurrence_draws = rng.choice(recurrence_values, size=(n_bootstrap, recurrence_values.size), replace=True)
    no_recurrence_draws = rng.choice(no_recurrence_values, size=(n_bootstrap, no_recurrence_values.size), replace=True)
    deltas = recurrence_draws.mean(axis=1) - no_recurrence_draws.mean(axis=1)
    return {
        "delta_mean_q025": float(np.quantile(deltas, 0.025)),
        "delta_mean_q975": float(np.quantile(deltas, 0.975)),
        "bootstrap_probability_delta_gt_0": float((deltas > 0).mean()),
        "bootstrap_probability_delta_lt_0": float((deltas < 0).mean()),
    }


def analyze_gse43502(model_table: pd.DataFrame, n_bootstrap: int, seed: int) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    df = model_table[model_table["dataset_id"] == "GSE43502"].copy()
    df = df[df["prognosis"].isin(["recurrence", "no recurrence"])].copy()
    if df.empty:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    rows = []
    for feature in [f for f in BIOLOGY_FEATURES if f in df.columns]:
        recurrence = pd.to_numeric(df[df["prognosis"] == "recurrence"][feature], errors="coerce").dropna()
        no_recurrence = pd.to_numeric(df[df["prognosis"] == "no recurrence"][feature], errors="coerce").dropna()
        if recurrence.empty or no_recurrence.empty:
            continue
        try:
            stat, pvalue = mannwhitneyu(recurrence, no_recurrence, alternative="two-sided")
        except ValueError:
            stat, pvalue = float("nan"), float("nan")
        bootstrap = bootstrap_difference(recurrence, no_recurrence, n_bootstrap=n_bootstrap, seed=seed + len(rows))
        rows.append(
            {
                "feature": feature,
                "recurrence_n": int(recurrence.shape[0]),
                "no_recurrence_n": int(no_recurrence.shape[0]),
                "recurrence_mean": float(recurrence.mean()),
                "no_recurrence_mean": float(no_recurrence.mean()),
                "delta_recurrence_minus_no_recurrence": float(recurrence.mean() - no_recurrence.mean()),
                "recurrence_median": float(recurrence.median()),
                "no_recurrence_median": float(no_recurrence.median()),
                **bootstrap,
                "mannwhitney_p": float(pvalue),
            }
        )
    feature_summary = pd.DataFrame(rows).sort_values(["mannwhitney_p", "feature"])
    axis_counts = df.groupby(["prognosis", "dominant_resistance_axis"]).size().reset_index(name="samples")
    sample_table = df[["sample_id", "prognosis", "dominant_resistance_axis"] + [f for f in BIOLOGY_FEATURES if f in df.columns]].copy()
    return feature_summary, axis_counts, sample_table


def summarize_gse164715(metadata: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = metadata[metadata["dataset_id"] == "GSE164715"].copy()
    if df.empty:
        return pd.DataFrame(), pd.DataFrame()
    df["persister_stage"] = "other"
    df.loc[df["sample_title"].str.contains("chemonaive", case=False, na=False), "persister_stage"] = "chemonaive"
    df.loc[df["sample_title"].str.contains("persister", case=False, na=False), "persister_stage"] = "persister"
    df.loc[df["sample_title"].str.contains("residual", case=False, na=False), "persister_stage"] = "residual"
    df.loc[df["sample_title"].str.contains("resistant", case=False, na=False), "persister_stage"] = "resistant"
    df.loc[df["sample_title"].str.contains("recurrent", case=False, na=False), "persister_stage"] = "recurrent"
    summary = df.groupby(["persister_stage", "treatment"], dropna=False).size().reset_index(name="samples")
    sample_table = df[["sample_id", "sample_title", "day", "treatment", "persister_stage"]].copy()
    return summary, sample_table


def save_gse43502_boxplot(sample_table: pd.DataFrame, out_path: Path) -> None:
    features = ["persister_fraction_estimate", "plasticity_index", "therapy_selection_pressure", "tnbc_stemness_persister"]
    features = [feature for feature in features if feature in sample_table.columns]
    fig, axes = plt.subplots(1, len(features), figsize=(4 * len(features), 4), constrained_layout=True)
    if len(features) == 1:
        axes = [axes]
    for ax, feature in zip(axes, features):
        groups = [
            pd.to_numeric(sample_table[sample_table["prognosis"] == label][feature], errors="coerce").dropna()
            for label in ["no recurrence", "recurrence"]
        ]
        ax.boxplot(groups, tick_labels=["No recurrence", "Recurrence"], patch_artist=True)
        ax.set_title(feature.replace("_", " "))
        ax.tick_params(axis="x", rotation=20)
    fig.suptitle("GSE43502 residual TNBC biology by recurrence", fontsize=13)
    fig.savefig(out_path, dpi=180)
    plt.close(fig)


def save_axis_counts(axis_counts: pd.DataFrame, out_path: Path) -> None:
    pivot = axis_counts.pivot(index="dominant_resistance_axis", columns="prognosis", values="samples").fillna(0)
    ax = pivot.plot(kind="bar", figsize=(8, 4.5), color=["#4c78a8", "#e15759"])
    ax.set_ylabel("Samples")
    ax.set_title("GSE43502 dominant resistance axes")
    ax.tick_params(axis="x", rotation=30)
    ax.legend(frameon=False)
    plt.tight_layout()
    plt.savefig(out_path, dpi=180)
    plt.close()


def save_gse43502_bootstrap_plot(feature_summary: pd.DataFrame, out_path: Path) -> None:
    if feature_summary.empty:
        return
    plot_df = feature_summary.sort_values("delta_recurrence_minus_no_recurrence").copy()
    y = np.arange(plot_df.shape[0])
    x = plot_df["delta_recurrence_minus_no_recurrence"].to_numpy(dtype=float)
    low = plot_df["delta_mean_q025"].to_numpy(dtype=float)
    high = plot_df["delta_mean_q975"].to_numpy(dtype=float)
    fig, ax = plt.subplots(figsize=(8.5, 6.2), constrained_layout=True)
    ax.errorbar(x, y, xerr=[x - low, high - x], fmt="o", color="#4c78a8", ecolor="#9ecae9", capsize=3)
    ax.axvline(0, color="#777777", linewidth=1)
    ax.set_yticks(y, plot_df["feature"].str.replace("_", " "))
    ax.set_xlabel("Mean difference: recurrence minus no recurrence")
    ax.set_title("GSE43502 recurrence-axis bootstrap intervals")
    fig.savefig(out_path, dpi=180)
    plt.close(fig)


def write_report(
    feature_summary: pd.DataFrame,
    axis_counts: pd.DataFrame,
    gse164715_summary: pd.DataFrame,
    supplement_listing: pd.DataFrame,
    image_paths: dict[str, Path],
    out_path: Path,
) -> None:
    lines = [
        "# Residual and Persister Biology Calibration Report",
        "",
        "## GSE43502 Residual Chemoresistant TNBC",
        "",
        "This cohort contains residual chemoresistant TNBC samples after neoadjuvant chemotherapy with recurrence/no-recurrence prognosis labels.",
        "",
        "### Feature Differences",
        "",
        feature_summary.to_markdown(index=False) if not feature_summary.empty else "No feature summary available.",
        "",
        "Interpretation note: bootstrap intervals that cross zero should be treated as directionally suggestive only. This cohort has 16 recurrence and 9 no-recurrence samples.",
        "",
        "### Dominant Resistance Axes",
        "",
        axis_counts.to_markdown(index=False) if not axis_counts.empty else "No axis count table available.",
        "",
        f"![GSE43502 recurrence boxplots]({image_paths['gse43502_boxplot'].as_posix()})",
        "",
        f"![GSE43502 axis counts]({image_paths['gse43502_axis_counts'].as_posix()})",
        "",
        f"![GSE43502 bootstrap intervals]({image_paths['gse43502_bootstrap_intervals'].as_posix()})",
        "",
        "## GSE164715 Persister Metadata",
        "",
        "This cohort now has both metadata and a selected raw scRNA import in the local pipeline. The metadata table remains useful for tracking persister/residual/recurrent sample definitions.",
        "",
        gse164715_summary.to_markdown(index=False) if not gse164715_summary.empty else "No GSE164715 metadata summary available.",
        "",
        "### Supplementary File Availability",
        "",
        supplement_listing.to_markdown(index=False) if not supplement_listing.empty else "No supplementary listing available.",
        "",
        "## How This Feeds the Digital Twin",
        "",
        "- `GSE43502` can calibrate residual/recurrent risk axes after chemotherapy.",
        "- `GSE164715` now supports persister-state marker refinement through the selected raw scRNA import, human/mouse filtering, and targeted annotation layers.",
        "- Recurrence-associated axes should be used to adjust the `P` and therapy-selection-pressure priors, not to make treatment decisions.",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Analyze residual and persister biology cohorts for TNBC EMT digital twin calibration.")
    p.add_argument("--model-table", default="data/processed/tnbc_digital_twin/tnbc_nac_emt_digital_twin_model_table.tsv")
    p.add_argument("--metadata", default="data/processed/tnbc_digital_twin/tnbc_nac_geo_sample_metadata.tsv")
    p.add_argument("--out-dir", default="data/processed/tnbc_digital_twin/residual_persister_biology")
    p.add_argument("--docs-dir", default="docs/tnbc_digital_twin_emt_plasticity")
    p.add_argument("--bootstrap-samples", type=int, default=5000)
    p.add_argument("--seed", type=int, default=43502)
    return p


def main() -> None:
    args = parser().parse_args()
    out_dir = ROOT / args.out_dir
    asset_dir = ROOT / args.docs_dir / "assets" / "residual_persister_biology"
    out_dir.mkdir(parents=True, exist_ok=True)
    asset_dir.mkdir(parents=True, exist_ok=True)
    model_table = pd.read_csv(ROOT / args.model_table, sep="\t")
    metadata = pd.read_csv(ROOT / args.metadata, sep="\t", dtype=str)

    feature_summary, axis_counts, sample_table = analyze_gse43502(model_table, n_bootstrap=args.bootstrap_samples, seed=args.seed)
    gse164715_summary, gse164715_samples = summarize_gse164715(metadata)
    supplement_listing = fetch_supplement_listing("GSE164715")

    feature_summary.to_csv(out_dir / "gse43502_recurrence_feature_summary.tsv", sep="\t", index=False)
    axis_counts.to_csv(out_dir / "gse43502_resistance_axis_counts.tsv", sep="\t", index=False)
    sample_table.to_csv(out_dir / "gse43502_residual_biology_sample_table.tsv", sep="\t", index=False)
    gse164715_summary.to_csv(out_dir / "gse164715_persister_metadata_summary.tsv", sep="\t", index=False)
    gse164715_samples.to_csv(out_dir / "gse164715_persister_sample_table.tsv", sep="\t", index=False)
    supplement_listing.to_csv(out_dir / "gse164715_supplement_listing.tsv", sep="\t", index=False)

    image_paths = {
        "gse43502_boxplot": asset_dir / "gse43502_recurrence_boxplots.png",
        "gse43502_axis_counts": asset_dir / "gse43502_resistance_axis_counts.png",
        "gse43502_bootstrap_intervals": asset_dir / "gse43502_recurrence_bootstrap_intervals.png",
    }
    if not sample_table.empty:
        save_gse43502_boxplot(sample_table, image_paths["gse43502_boxplot"])
    if not axis_counts.empty:
        save_axis_counts(axis_counts, image_paths["gse43502_axis_counts"])
    if not feature_summary.empty:
        save_gse43502_bootstrap_plot(feature_summary, image_paths["gse43502_bootstrap_intervals"])
    write_report(feature_summary, axis_counts, gse164715_summary, supplement_listing, image_paths, out_dir / "residual_persister_biology_report.md")

    print(f"gse43502_samples={sample_table.shape[0]} gse164715_samples={gse164715_samples.shape[0]} supplements={supplement_listing.shape[0]}")
    if not feature_summary.empty:
        print(feature_summary.head(8).to_string(index=False))


if __name__ == "__main__":
    main()
