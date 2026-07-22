from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from emt_state_atlas.annotated_single_cell import (
    add_malignant_stromal_emt_calls,
    infer_compartment,
    normalize_annotation_columns,
    source_requirements_table,
    summarize_compartments,
    summarize_tumor_vs_stroma,
    write_annotated_single_cell_report,
)
from emt_state_atlas.aliases import read_aliases
from emt_state_atlas.io import read_expression, read_metadata, read_table
from emt_state_atlas.single_cell import score_single_cell_expression


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Build annotated single-cell EMT source-separation layer.")
    p.add_argument("--scored", action="append", help="Pre-scored single-cell EMT table. Repeatable.")
    p.add_argument("--expression", action="append", help="Expression matrix to score before annotation. Repeatable.")
    p.add_argument("--metadata", action="append", help="Metadata table paired by position with --expression.")
    p.add_argument("--source", action="append", help="Source label paired with --scored/--expression.")
    p.add_argument("--dataset", action="append", help="Dataset label paired with --scored/--expression.")
    p.add_argument("--cancer-group", action="append", help="Cancer group paired with --scored/--expression.")
    p.add_argument("--gene-aliases", default="data/raw/gene_aliases/signature_gene_aliases.tsv")
    p.add_argument("--out-dir", default="data/processed/pan_cancer_emt_state_atlas/annotated_single_cell")
    p.add_argument("--report-out", default="docs/pan_cancer_emt_state_atlas/reports/pan_cancer_emt_annotated_single_cell_report.md")
    return p


def _item(values: list[str] | None, index: int, default: str | None = None) -> str | None:
    if values and index < len(values):
        return values[index]
    return default


def main() -> None:
    args = parser().parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    annotated_frames = []
    if args.scored:
        scored_paths = args.scored
    else:
        scored_paths = ["data/processed/pan_cancer_emt_state_atlas/single_cell_cancersea/cancersea_single_cell_emt_scores.tsv"]
        imports_dir = out_dir / "imports"
        scored_paths.extend(str(path) for path in sorted(imports_dir.glob("*_annotated_single_cell_emt_scores.tsv")))
    for index, path in enumerate(scored_paths):
        frame = read_table(path)
        source = _item(args.source, index, "CancerSEA")
        dataset = _item(args.dataset, index, None)
        cancer_group = _item(args.cancer_group, index, None)
        normalized = normalize_annotation_columns(frame, dataset=dataset, source=source, cancer_group=cancer_group)
        if source == "CancerSEA" and "malignant_status" in normalized.columns:
            normalized["malignant_status"] = normalized["malignant_status"].replace("", "malignant")
            normalized["cell_compartment"] = normalized.apply(infer_compartment, axis=1)
        annotated_frames.append(normalized)

    expression_paths = args.expression or []
    metadata_paths = args.metadata or []
    aliases = read_aliases(args.gene_aliases)
    offset = len(annotated_frames)
    for index, expression_path in enumerate(expression_paths):
        metadata = read_metadata(_item(metadata_paths, index)) if index < len(metadata_paths) else None
        expression = read_expression(expression_path)
        scored = score_single_cell_expression(expression, metadata, aliases=aliases)
        source = _item(args.source, offset + index, "annotated_export")
        dataset = _item(args.dataset, offset + index, Path(expression_path).stem)
        cancer_group = _item(args.cancer_group, offset + index, None)
        annotated_frames.append(normalize_annotation_columns(scored, dataset=dataset, source=source, cancer_group=cancer_group))

    combined = pd.concat(annotated_frames, ignore_index=True) if annotated_frames else pd.DataFrame()
    combined = add_malignant_stromal_emt_calls(combined)
    compartment_summary = summarize_compartments(combined)
    tumor_vs_stroma = summarize_tumor_vs_stroma(combined)
    requirements = source_requirements_table()

    combined.to_csv(out_dir / "annotated_single_cell_emt_scores.tsv", sep="\t", index=False)
    compartment_summary.to_csv(out_dir / "annotated_compartment_summary.tsv", sep="\t", index=False)
    tumor_vs_stroma.to_csv(out_dir / "tumor_vs_stroma_emt_summary.tsv", sep="\t", index=False)
    requirements.to_csv(out_dir / "external_single_cell_source_requirements.tsv", sep="\t", index=False)
    write_annotated_single_cell_report(compartment_summary, tumor_vs_stroma, requirements, args.report_out)
    print(f"Wrote annotated single-cell layer to {out_dir}")


if __name__ == "__main__":
    main()
