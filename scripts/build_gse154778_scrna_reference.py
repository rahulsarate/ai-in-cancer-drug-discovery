from __future__ import annotations

import argparse
import csv
import gzip
import shutil
from pathlib import Path
from urllib.request import Request, urlopen

import numpy as np
import pandas as pd

from emt_state_atlas.signatures import SIGNATURES
from spatial_emt_niche_gnn.tenx_visium import required_genes


DATA_URL = "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE154nnn/GSE154778/suppl/GSE154778_dgeMtx.csv.gz"
SOFT_URL = "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE154778&targ=gsm&form=text&view=full"


MARKERS = {
    "tumor_epithelial_pdac_scrna": ["EPCAM", "KRT8", "KRT18", "KRT19", "MUC1", "CDH1", "CLDN4"],
    "tumor_mesenchymal_plastic_scrna": ["VIM", "FN1", "LAMC2", "TGFBI", "S100A4", "ITGA5", "MMP14", "SERPINE1", "AXL"],
    "caf_myofibroblast_scrna": ["FAP", "ACTA2", "COL1A1", "COL1A2", "COL3A1", "PDGFRB", "POSTN", "CTHRC1", "MMP11", "DCN", "LUM"],
    "tam_spp1_macrophage_scrna": ["CD68", "CD163", "MRC1", "SPP1", "TREM2", "APOE", "C1QA", "C1QB", "C1QC", "CSF1R"],
    "t_cell_cytotoxic_scrna": ["CD3D", "CD3E", "CD8A", "CD8B", "NKG7", "GNLY", "GZMB", "PRF1"],
    "endothelial_angiogenic_scrna": ["KDR", "PECAM1", "VWF", "ENG", "CDH5", "ESAM", "RAMP2"],
    "hypoxic_stress_scrna": ["CA9", "HIF1A", "SLC2A1", "LDHA", "ENO1", "PGK1", "BNIP3", "NDRG1", "ADM"],
}


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Build a real GSE154778 PDAC scRNA marker-assigned cell_type x gene reference.")
    p.add_argument("--raw-dir", default="data/raw/scrna/GSE154778")
    p.add_argument("--out-dir", default="data/processed/spatial_emt_niche_gnn_references/gse154778")
    p.add_argument("--min-score", type=float, default=0.05)
    return p


def download(url: str, out: Path) -> None:
    if out.exists():
        return
    out.parent.mkdir(parents=True, exist_ok=True)
    request = Request(url, headers={"User-Agent": "Mozilla/5.0 spatial-emt-niche-gnn/0.1"})
    with urlopen(request, timeout=240) as response, open(out, "wb") as handle:
        shutil.copyfileobj(response, handle)


def fetch_soft(raw_dir: Path) -> Path:
    out = raw_dir / "GSE154778_samples.soft"
    download(SOFT_URL, out)
    return out


def parse_soft(path: Path) -> pd.DataFrame:
    rows = []
    current: dict[str, str] | None = None
    for raw_line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw_line.strip()
        if line.startswith("^SAMPLE = "):
            if current:
                rows.append(current)
            current = {"geo_accession": line.split("=", 1)[1].strip()}
        elif current is None:
            continue
        elif line.startswith("!Sample_title = "):
            title = line.split("=", 1)[1].strip()
            current["sample_title"] = title
            current["sample_prefix"] = title.split(":", 1)[0]
        elif line.startswith("!Sample_characteristics_ch1 = tissue type: "):
            current["tissue_type"] = line.split("tissue type:", 1)[1].strip()
        elif line.startswith("!Sample_characteristics_ch1 = gender: "):
            current["gender"] = line.split("gender:", 1)[1].strip()
    if current:
        rows.append(current)
    return pd.DataFrame(rows)


def wanted_genes() -> list[str]:
    genes = {gene.upper() for values in MARKERS.values() for gene in values}
    genes |= {gene.upper() for values in SIGNATURES.values() for gene in values}
    genes |= required_genes()
    return sorted(genes)


def load_gene_subset(path: Path, genes: list[str]) -> pd.DataFrame:
    wanted = set(genes)
    rows = {}
    with gzip.open(path, "rt", encoding="utf-8", errors="replace", newline="") as handle:
        reader = csv.reader(handle)
        header = next(reader)
        cells = header[1:]
        for row in reader:
            if not row:
                continue
            gene = row[0].upper()
            if gene in wanted and gene not in rows:
                rows[gene] = np.array([float(value) if value else 0.0 for value in row[1:]], dtype=np.float32)
    if not rows:
        raise RuntimeError("No requested genes found in GSE154778 matrix.")
    frame = pd.DataFrame(rows, index=cells)
    frame.index.name = "cell_id"
    return frame


def marker_scores(log_expr: pd.DataFrame) -> pd.DataFrame:
    scores = pd.DataFrame(index=log_expr.index)
    for cell_type, markers in MARKERS.items():
        present = [gene for gene in markers if gene in log_expr.columns]
        if present:
            scores[cell_type] = log_expr[present].mean(axis=1)
        else:
            scores[cell_type] = 0.0
    return scores


def assign_cells(scores: pd.DataFrame, min_score: float) -> pd.DataFrame:
    best = scores.idxmax(axis=1)
    best_score = scores.max(axis=1)
    second = scores.apply(lambda row: row.nlargest(2).iloc[-1] if len(row) > 1 else 0.0, axis=1)
    label = best.where((best_score >= min_score) & ((best_score - second) >= 0.01), "unassigned_low_confidence")
    return pd.DataFrame(
        {
            "cell_id": scores.index.astype(str),
            "assigned_cell_type": label.to_numpy(),
            "assignment_score": best_score.to_numpy(),
            "assignment_margin": (best_score - second).to_numpy(),
        }
    )


def build_reference(log_expr: pd.DataFrame, assignments: pd.DataFrame) -> pd.DataFrame:
    table = log_expr.copy()
    table["cell_type"] = assignments.set_index("cell_id").loc[table.index, "assigned_cell_type"].to_numpy()
    table = table[table["cell_type"].ne("unassigned_low_confidence")]
    ref = table.groupby("cell_type").mean(numeric_only=True).reset_index()
    return ref


def main() -> None:
    args = parser().parse_args()
    raw_dir = Path(args.raw_dir)
    out_dir = Path(args.out_dir)
    raw_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)
    matrix_path = raw_dir / "GSE154778_dgeMtx.csv.gz"
    download(DATA_URL, matrix_path)
    metadata = parse_soft(fetch_soft(raw_dir))
    metadata.to_csv(out_dir / "gse154778_sample_metadata.tsv", sep="\t", index=False)

    expr = load_gene_subset(matrix_path, wanted_genes())
    log_expr = np.log1p(expr)
    scores = marker_scores(log_expr)
    assignments = assign_cells(scores, args.min_score)
    assignments["sample_prefix"] = assignments["cell_id"].str.split(":", n=1).str[0]
    assignments = assignments.merge(metadata[["sample_prefix", "tissue_type"]], on="sample_prefix", how="left")
    assignments.to_csv(out_dir / "gse154778_marker_cell_assignments.tsv", sep="\t", index=False)
    reference = build_reference(log_expr, assignments)
    reference.to_csv(out_dir / "gse154778_scrna_marker_reference.tsv", sep="\t", index=False)
    summary = (
        assignments.groupby(["assigned_cell_type", "tissue_type"], dropna=False)
        .agg(cells=("cell_id", "count"), mean_score=("assignment_score", "mean"), mean_margin=("assignment_margin", "mean"))
        .reset_index()
    )
    summary.to_csv(out_dir / "gse154778_marker_assignment_summary.tsv", sep="\t", index=False)
    print(f"Wrote {out_dir / 'gse154778_scrna_marker_reference.tsv'}")
    print(f"Wrote {out_dir / 'gse154778_marker_assignment_summary.tsv'}")


if __name__ == "__main__":
    main()
