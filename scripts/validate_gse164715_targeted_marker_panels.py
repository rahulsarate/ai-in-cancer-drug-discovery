from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
MARKER_EXPECTATIONS = {
    "malignant_like": ["epithelial", "mesenchymal", "tnbc_persister_tumor_refined"],
    "endothelial_like": ["angiogenesis", "tnbc_persister_niche"],
    "stromal_like": ["stromal_fibroblast", "caf", "ecm_remodeling"],
    "immune_like": ["immune_total", "t_cell_cytotoxic", "tam_spp1"],
}


def validate_markers(cells: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    marker_cols = sorted({marker for markers in MARKER_EXPECTATIONS.values() for marker in markers if marker in cells.columns})
    summary = (
        cells.groupby("targeted_annotation")[marker_cols]
        .mean()
        .reset_index()
        .sort_values("targeted_annotation")
    )
    rows = []
    for annotation, markers in MARKER_EXPECTATIONS.items():
        if annotation not in set(summary["targeted_annotation"]):
            continue
        row = summary[summary["targeted_annotation"] == annotation].iloc[0]
        expected = [marker for marker in markers if marker in summary.columns]
        others = summary[summary["targeted_annotation"] != annotation]
        for marker in expected:
            margin = float(row[marker] - others[marker].mean()) if not others.empty else 0.0
            rows.append(
                {
                    "targeted_annotation": annotation,
                    "expected_marker_score": marker,
                    "annotation_mean": float(row[marker]),
                    "other_annotations_mean": float(others[marker].mean()) if not others.empty else 0.0,
                    "marker_margin": margin,
                    "passes_direction_check": margin > 0,
                }
            )
    checks = pd.DataFrame(rows)
    return summary, checks


def save_marker_heatmap(summary: pd.DataFrame, out_path: Path) -> None:
    marker_cols = [col for col in summary.columns if col != "targeted_annotation"]
    if summary.empty or not marker_cols:
        return
    data = summary.set_index("targeted_annotation")[marker_cols]
    fig, ax = plt.subplots(figsize=(9, 4.8), constrained_layout=True)
    vmax = max(abs(float(data.min().min())), abs(float(data.max().max())), 0.1)
    im = ax.imshow(data.to_numpy(dtype=float), aspect="auto", cmap="coolwarm", vmin=-vmax, vmax=vmax)
    ax.set_yticks(range(data.shape[0]), data.index)
    ax.set_xticks(range(len(marker_cols)), [col.replace("_", "\n") for col in marker_cols], fontsize=8)
    ax.set_title("GSE164715 targeted annotation marker validation")
    fig.colorbar(im, ax=ax, label="Mean score")
    fig.savefig(out_path, dpi=180)
    plt.close(fig)


def write_report(summary: pd.DataFrame, checks: pd.DataFrame, image_path: Path, out_path: Path) -> None:
    pass_rate = checks["passes_direction_check"].mean() if not checks.empty else 0.0
    lines = [
        "# GSE164715 Targeted Marker-Panel Validation",
        "",
        "## Purpose",
        "",
        "Validate whether targeted annotations show expected marker-score enrichment. This is a directional marker-panel check, not a full single-cell atlas annotation.",
        "",
        f"- Direction-check pass rate: {pass_rate:.3f}",
        "",
        "## Annotation Marker Means",
        "",
        summary.to_markdown(index=False) if not summary.empty else "No marker summary available.",
        "",
        "## Direction Checks",
        "",
        checks.to_markdown(index=False) if not checks.empty else "No marker checks available.",
        "",
        "## Plot",
        "",
        f"![Marker validation heatmap]({image_path.as_posix()})",
        "",
        "## Interpretation",
        "",
        "- Positive marker margins support the targeted annotation.",
        "- Failed margins should trigger review before publication-grade single-cell claims.",
        "- Ambiguous cells are expected to remain heterogeneous and are not forced into lineage claims.",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Validate targeted marker panels for GSE164715 cell annotations.")
    p.add_argument("--cell-annotations", default="data/processed/tnbc_digital_twin/gse164715_targeted_annotation/gse164715_targeted_cell_annotations.tsv.gz")
    p.add_argument("--out-dir", default="data/processed/tnbc_digital_twin/gse164715_marker_validation")
    p.add_argument("--docs-dir", default="docs/tnbc_digital_twin_emt_plasticity")
    return p


def main() -> None:
    args = parser().parse_args()
    out_dir = ROOT / args.out_dir
    asset_dir = ROOT / args.docs_dir / "assets" / "gse164715_marker_validation"
    out_dir.mkdir(parents=True, exist_ok=True)
    asset_dir.mkdir(parents=True, exist_ok=True)
    cells = pd.read_csv(ROOT / args.cell_annotations, sep="\t")
    summary, checks = validate_markers(cells)
    summary.to_csv(out_dir / "gse164715_marker_panel_summary.tsv", sep="\t", index=False)
    checks.to_csv(out_dir / "gse164715_marker_panel_direction_checks.tsv", sep="\t", index=False)
    image_path = asset_dir / "gse164715_marker_panel_heatmap.png"
    save_marker_heatmap(summary, image_path)
    write_report(summary, checks, image_path, out_dir / "gse164715_marker_panel_validation_report.md")
    print(checks.to_string(index=False))


if __name__ == "__main__":
    main()
