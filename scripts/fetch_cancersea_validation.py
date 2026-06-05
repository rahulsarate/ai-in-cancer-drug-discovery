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
    "EXP0054": "Breast cancer CTC Jordan 2016",
    "EXP0055": "Breast cancer CTC Aceto 2018",
    "EXP0070": "Prostate cancer CTC Miyamoto 2015",
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
    if not candidates:
        candidates = [extract_dir / names[0]]
    return candidates[0]


def main() -> None:
    args = parser().parse_args()
    datasets = args.dataset or ["EXP0054", "EXP0055"]
    raw_dir = ROOT / args.raw_dir
    out_dir = ROOT / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

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
        summary = summarize_single_cell_states(scores, group_cols=["dataset", "dataset_label"])
        all_scores.append(scores)
        summaries.append(summary)
        manifest.append({"dataset": dataset, "label": DEFAULT_DATASETS[dataset], "url": url, "table_path": str(table_path)})

    pd.concat(all_scores, ignore_index=True).to_csv(out_dir / "cancersea_single_cell_emt_scores.tsv", sep="\t", index=False)
    pd.concat(summaries, ignore_index=True).to_csv(out_dir / "cancersea_state_summary.tsv", sep="\t", index=False)
    pd.DataFrame(manifest).to_csv(out_dir / "cancersea_manifest.tsv", sep="\t", index=False)
    print(f"Wrote {out_dir}")


if __name__ == "__main__":
    main()
