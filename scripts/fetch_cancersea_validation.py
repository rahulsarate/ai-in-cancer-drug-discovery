from __future__ import annotations

import argparse
import ssl
import zipfile
from pathlib import Path
from urllib.request import Request, urlopen

import pandas as pd

from emt_state_atlas.aliases import read_aliases
from emt_state_atlas.io import read_expression
from emt_state_atlas.single_cell import score_single_cell_expression, summarize_single_cell_states


ROOT = Path(__file__).resolve().parents[1]
CANCERSEA_BASE = "https://biocc.hrbmu.edu.cn/CancerSEA/download/Expression"
DEFAULT_DATASETS = {
    "EXP0023": "Oesophageal cancer cell line KYSE-180 Yang 2018",
    "EXP0037": "Pancreatic ductal adenocarcinoma cell lines Shah 2017",
    "EXP0047": "Acute myeloid leukemia bone marrow 10X Fan 2018",
    "EXP0051": "Colorectal cancer colon Li 2017",
    "EXP0053": "Breast cancer tissue Chung 2017",
    "EXP0054": "Breast cancer CTC Jordan 2016",
    "EXP0055": "Breast cancer CTC Aceto 2018",
    "EXP0057": "Glioblastoma brain Darmanis 2017",
    "EXP0063": "Head and neck cancer oral cavity Puram 2017",
    "EXP0068": "Non-small cell lung cancer lung Lambrechts 2018",
    "EXP0069": "Ovarian carcinoma PDX Guillaumet-Adkins 2017",
    "EXP0070": "Prostate cancer CTC Miyamoto 2015",
    "EXP0071": "Melanoma skin Tirosh 2016",
}

DATASET_GROUPS = {
    "EXP0023": "Oesophageal Cancer",
    "EXP0037": "Pancreatic Cancer",
    "EXP0047": "Blood Tumors",
    "EXP0051": "Colon / Intestine Cancer",
    "EXP0053": "Breast Cancer",
    "EXP0054": "Breast Cancer",
    "EXP0055": "Breast Cancer",
    "EXP0057": "Brain Tumors",
    "EXP0063": "Head and Neck Cancer",
    "EXP0068": "Lung Cancer",
    "EXP0069": "Ovarian Cancer",
    "EXP0070": "Prostate Cancer",
    "EXP0071": "Skin Cancer",
}


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Fetch selected CancerSEA PCG expression datasets and score EMT states.")
    p.add_argument("--dataset", action="append", choices=DEFAULT_DATASETS.keys(), help="CancerSEA dataset ID. Repeatable.")
    p.add_argument("--raw-dir", default="data/raw/cancersea")
    p.add_argument("--out-dir", default="data/processed/cancersea_validation")
    p.add_argument("--gene-aliases", default="data/raw/gene_aliases/signature_gene_aliases.tsv")
    return p


def download(url: str, out: Path) -> None:
    request = Request(url, headers={"User-Agent": "Mozilla/5.0 EMT-Metastasis-AI/0.1"})
    try:
        response = urlopen(request, timeout=180)
    except Exception:
        response = urlopen(request, timeout=180, context=ssl._create_unverified_context())
    with response:
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "wb") as handle:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                handle.write(chunk)


def extract_first_table(zip_path: Path, extract_dir: Path) -> Path:
    extract_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as archive:
        names = [name for name in archive.namelist() if not name.endswith("/")]
        archive.extractall(extract_dir)
    candidates = [extract_dir / name for name in names if name.lower().endswith((".txt", ".tsv", ".csv"))]
    after_qc = [path for path in candidates if "afterqc" in path.name.lower() or "after_qc" in path.name.lower()]
    if after_qc:
        return after_qc[0]
    if not candidates:
        candidates = [extract_dir / names[0]]
    return candidates[0]


def main() -> None:
    args = parser().parse_args()
    datasets = args.dataset or list(DEFAULT_DATASETS)
    raw_dir = ROOT / args.raw_dir
    out_dir = ROOT / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    per_dataset_dir = out_dir / "datasets"
    per_dataset_dir.mkdir(parents=True, exist_ok=True)

    all_scores = []
    summaries = []
    manifest = []
    aliases = read_aliases(ROOT / args.gene_aliases)
    for dataset in datasets:
        zip_path = raw_dir / f"{dataset}_PCG.zip"
        url = f"{CANCERSEA_BASE}/{dataset}_PCG.zip"
        if not zip_path.exists():
            download(url, zip_path)
        table_path = extract_first_table(zip_path, raw_dir / dataset)
        expr = read_expression(table_path)
        scores = score_single_cell_expression(expr, aliases=aliases)
        scores["dataset"] = dataset
        scores["dataset_label"] = DEFAULT_DATASETS[dataset]
        scores["cancer_group"] = DATASET_GROUPS[dataset]
        scores["validation_context"] = "CancerSEA malignant/cancer-cell expression profile"
        summary = summarize_single_cell_states(scores, group_cols=["dataset", "dataset_label", "cancer_group"])
        summary["cancer_group"] = DATASET_GROUPS[dataset]
        scores.to_csv(per_dataset_dir / f"{dataset}_single_cell_emt_scores.tsv", sep="\t", index=False)
        summary.to_csv(per_dataset_dir / f"{dataset}_state_summary.tsv", sep="\t", index=False)
        all_scores.append(scores)
        summaries.append(summary)
        manifest.append(
            {
                "dataset": dataset,
                "label": DEFAULT_DATASETS[dataset],
                "cancer_group": DATASET_GROUPS[dataset],
                "url": url,
                "table_path": str(table_path),
            }
        )

    existing_scores = sorted(per_dataset_dir.glob("*_single_cell_emt_scores.tsv"))
    existing_summaries = sorted(per_dataset_dir.glob("*_state_summary.tsv"))
    all_scores = [pd.read_csv(path, sep="\t") for path in existing_scores] or all_scores
    summaries = [pd.read_csv(path, sep="\t") for path in existing_summaries] or summaries

    completed = []
    for path in existing_scores:
        dataset = path.name.split("_", 1)[0]
        if dataset not in DEFAULT_DATASETS:
            continue
        table_candidates = sorted((raw_dir / dataset).glob("*"))
        table_path = next(
            (
                candidate
                for candidate in table_candidates
                if candidate.is_file()
                and candidate.suffix.lower() in {".txt", ".tsv", ".csv"}
                and ("afterqc" in candidate.name.lower() or "after_qc" in candidate.name.lower())
            ),
            None,
        )
        if table_path is None:
            table_path = next(
                (
                    candidate
                    for candidate in table_candidates
                    if candidate.is_file() and candidate.suffix.lower() in {".txt", ".tsv", ".csv"}
                ),
                raw_dir / dataset,
            )
        completed.append(
            {
                "dataset": dataset,
                "label": DEFAULT_DATASETS[dataset],
                "cancer_group": DATASET_GROUPS[dataset],
                "url": f"{CANCERSEA_BASE}/{dataset}_PCG.zip",
                "table_path": str(table_path),
                "score_path": str(path),
            }
        )

    if all_scores:
        pd.concat(all_scores, ignore_index=True).to_csv(out_dir / "cancersea_single_cell_emt_scores.tsv", sep="\t", index=False)
    if summaries:
        pd.concat(summaries, ignore_index=True).to_csv(out_dir / "cancersea_state_summary.tsv", sep="\t", index=False)
    manifest_frame = pd.DataFrame(completed or manifest).sort_values("dataset")
    manifest_frame.to_csv(out_dir / "cancersea_manifest.tsv", sep="\t", index=False)
    print(f"Wrote {out_dir}")


if __name__ == "__main__":
    main()
