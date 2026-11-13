from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from emt_state_atlas.scoring import score_expression  # noqa: E402
from emt_state_atlas.signatures import SIGNATURES  # noqa: E402


def load_tnbc_signatures(config_path: Path) -> dict[str, list[str]]:
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    combined = {name: genes[:] for name, genes in SIGNATURES.items()}
    blocks = config.get("signature_blocks", {})
    for name, value in blocks.items():
        if isinstance(value, list):
            combined[f"tnbc_{name}"] = [gene.upper() for gene in value]
        elif isinstance(value, dict):
            for nested_name, genes in value.items():
                if isinstance(genes, list):
                    combined[f"tnbc_{nested_name}"] = [gene.upper() for gene in genes]
    combined["tnbc_proliferation"] = ["MKI67", "TOP2A", "PCNA", "MCM2", "MCM4", "MCM6", "CCNB1", "AURKA", "BIRC5"]
    combined["tnbc_immune_checkpoint"] = ["CD274", "PDCD1", "CTLA4", "LAG3", "TIGIT", "HAVCR2", "PDCD1LG2"]
    return combined


def robust_percentile(series: pd.Series) -> pd.Series:
    if series.isna().all():
        return pd.Series(0.5, index=series.index)
    return series.rank(pct=True).fillna(0.5)


def softmax_states(scores: pd.DataFrame) -> pd.DataFrame:
    state_raw = pd.DataFrame(index=scores.index)
    state_raw["E"] = scores.get("epithelial", 0).fillna(0) + scores.get("tnbc_epithelial", 0).fillna(0)
    state_raw["H"] = scores.get("partial_emt_score", 0).fillna(0) + scores.get("tnbc_hybrid_plasticity", 0).fillna(0)
    state_raw["M"] = scores.get("mesenchymal", 0).fillna(0) + scores.get("tnbc_mesenchymal", 0).fillna(0)
    state_raw["P"] = scores.get("tnbc_stemness_persister", 0).fillna(0)
    centered = state_raw.sub(state_raw.max(axis=1), axis=0)
    exp_values = np.exp(centered)
    fractions = exp_values.div(exp_values.sum(axis=1), axis=0)
    return pd.DataFrame(
        {
            "epithelial_fraction_estimate": fractions["E"],
            "hybrid_fraction_estimate": fractions["H"],
            "mesenchymal_fraction_estimate": fractions["M"],
            "persister_fraction_estimate": fractions["P"],
        },
        index=scores.index,
    )


def add_digital_twin_features(scores: pd.DataFrame) -> pd.DataFrame:
    out = scores.copy()
    fractions = softmax_states(out)
    out = pd.concat([out, fractions], axis=1)
    out["plasticity_index"] = out["hybrid_fraction_estimate"] + out["persister_fraction_estimate"]
    out["resistant_fraction_estimate"] = (
        out["hybrid_fraction_estimate"] + out["mesenchymal_fraction_estimate"] + out["persister_fraction_estimate"]
    )

    pressure_terms = []
    for col in ["tnbc_axl_tam", "tnbc_tgfb", "tnbc_yap_taz", "tnbc_hypoxia", "caf_tam_niche"]:
        if col in out:
            pressure_terms.append(robust_percentile(out[col]))
    pressure_terms.append(out["resistant_fraction_estimate"])
    out["therapy_selection_pressure"] = pd.concat(pressure_terms, axis=1).mean(axis=1)

    axes = [col for col in ["tnbc_axl_tam", "tnbc_tgfb", "tnbc_yap_taz", "tnbc_hypoxia", "tnbc_stemness_persister", "caf_tam_niche"] if col in out]
    if axes:
        axis_values = out[axes].copy()
        axis_values.columns = [col.replace("tnbc_", "") for col in axis_values.columns]
        out["dominant_resistance_axis"] = axis_values.idxmax(axis=1)
    else:
        out["dominant_resistance_axis"] = "unknown"

    out["residual_disease_probability_proxy"] = np.clip(
        0.15 + 0.55 * out["therapy_selection_pressure"] + 0.30 * out["resistant_fraction_estimate"],
        0.01,
        0.99,
    )
    out["pcr_probability_proxy"] = 1.0 - out["residual_disease_probability_proxy"]
    out["prediction_confidence_proxy"] = np.clip(
        1.0 - out[["epithelial_fraction_estimate", "hybrid_fraction_estimate", "mesenchymal_fraction_estimate", "persister_fraction_estimate"]].std(axis=1),
        0.0,
        1.0,
    )
    return out


def score_expression_files(expression_dir: Path, config_path: Path) -> pd.DataFrame:
    signatures = load_tnbc_signatures(config_path)
    frames = []
    for path in sorted(expression_dir.glob("*_signature_gene_expression.tsv")):
        dataset_id = path.name.replace("_signature_gene_expression.tsv", "")
        expr = pd.read_csv(path, sep="\t")
        if "sample_id" not in expr.columns:
            continue
        expr = expr.set_index("sample_id")
        expr.columns = [str(col).upper() for col in expr.columns]
        scores = score_expression(expr, signatures=signatures)
        scores.insert(0, "dataset_id", dataset_id)
        frames.append(add_digital_twin_features(scores))
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def write_report(model_table: pd.DataFrame, out_path: Path) -> None:
    response_summary = (
        model_table.groupby(["dataset_id", "standard_response"], dropna=False)
        .size()
        .reset_index(name="samples")
        if not model_table.empty and "standard_response" in model_table
        else pd.DataFrame()
    )
    tnbc_summary = (
        model_table.groupby(["dataset_id", "tnbc_confirmed_or_likely"], dropna=False)
        .size()
        .reset_index(name="samples")
        if not model_table.empty and "tnbc_confirmed_or_likely" in model_table
        else pd.DataFrame()
    )
    lines = [
        "# TNBC NAC Digital-Twin Feature Scoring Report",
        "",
        "## Response-Labeled Samples",
        "",
        response_summary.to_markdown(index=False) if not response_summary.empty else "No response metadata merged.",
        "",
        "## TNBC-Likely Samples",
        "",
        tnbc_summary.to_markdown(index=False) if not tnbc_summary.empty else "No TNBC metadata merged.",
        "",
        "## Feature Blocks",
        "",
        "- EMT: epithelial, mesenchymal, partial EMT.",
        "- TME: stromal fibroblast, CAF, TAM, immune, hypoxia.",
        "- TNBC resistance axes: AXL/TAM, TGF-beta, YAP/TAZ, hypoxia, stemness/persister.",
        "- Digital-twin state estimates: E, H, M, P fractions plus plasticity and selection-pressure proxies.",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Score TNBC NAC gene-expression matrices for EMT and digital-twin features.")
    p.add_argument("--expression-dir", default="data/processed/tnbc_digital_twin/gene_expression")
    p.add_argument("--metadata", default="data/processed/tnbc_digital_twin/tnbc_nac_geo_sample_metadata.tsv")
    p.add_argument("--config", default="configs/tnbc_digital_twin.yml")
    p.add_argument("--out-dir", default="data/processed/tnbc_digital_twin")
    return p


def main() -> None:
    args = parser().parse_args()
    out_dir = ROOT / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    scores = score_expression_files(ROOT / args.expression_dir, ROOT / args.config)
    if scores.empty:
        raise SystemExit("No expression score outputs were generated.")
    metadata = pd.read_csv(ROOT / args.metadata, sep="\t", dtype=str)
    metadata["tnbc_confirmed_or_likely"] = metadata["tnbc_confirmed_or_likely"].map({"True": True, "False": False}).fillna(metadata["tnbc_confirmed_or_likely"])
    model_table = scores.merge(metadata, on=["dataset_id", "sample_id"], how="left")
    tnbc_model_table = model_table[
        (model_table["tnbc_confirmed_or_likely"] == True)
        & (model_table["standard_response"].isin(["pcr_or_good_response", "residual_or_poor_response"]))
    ].copy()

    scores.to_csv(out_dir / "tnbc_nac_emt_digital_twin_scores.tsv", sep="\t", index=False)
    model_table.to_csv(out_dir / "tnbc_nac_emt_digital_twin_model_table.tsv", sep="\t", index=False)
    tnbc_model_table.to_csv(out_dir / "tnbc_nac_emt_digital_twin_tnbc_response_model_table.tsv", sep="\t", index=False)
    write_report(model_table, out_dir / "tnbc_nac_emt_digital_twin_feature_report.md")
    print(
        f"scores={scores.shape[0]} model_rows={model_table.shape[0]} "
        f"tnbc_response_rows={tnbc_model_table.shape[0]} datasets={scores['dataset_id'].nunique()}"
    )


if __name__ == "__main__":
    main()
