from __future__ import annotations

from pathlib import Path

import pandas as pd


REFERENCE = {
    "tumor_epithelial_pdac": {
        "EPCAM": 10,
        "KRT8": 9,
        "KRT18": 9,
        "KRT19": 9,
        "MUC1": 8,
        "CLDN3": 7,
        "CLDN4": 7,
        "CDH1": 6,
    },
    "tumor_mesenchymal_plastic": {
        "VIM": 9,
        "FN1": 8,
        "LAMC2": 8,
        "TGFBI": 8,
        "S100A4": 7,
        "ITGA5": 7,
        "MMP14": 7,
        "SERPINE1": 6,
        "AXL": 6,
    },
    "caf_myofibroblast": {
        "FAP": 9,
        "ACTA2": 8,
        "COL1A1": 10,
        "COL1A2": 9,
        "COL3A1": 8,
        "PDGFRB": 7,
        "POSTN": 8,
        "CTHRC1": 8,
        "MMP11": 7,
    },
    "tam_spp1_macrophage": {
        "CD68": 8,
        "CD163": 8,
        "MRC1": 7,
        "SPP1": 9,
        "TREM2": 8,
        "APOE": 8,
        "C1QA": 7,
        "C1QB": 7,
        "C1QC": 7,
        "CSF1R": 7,
    },
    "t_cell_cytotoxic": {
        "CD3D": 8,
        "CD3E": 8,
        "CD8A": 8,
        "CD8B": 7,
        "NKG7": 8,
        "GNLY": 8,
        "GZMB": 8,
        "PRF1": 7,
        "IFNG": 6,
    },
    "endothelial_angiogenic": {
        "KDR": 8,
        "VEGFA": 5,
        "PECAM1": 8,
        "VWF": 8,
        "ENG": 7,
        "CDH5": 7,
        "ESAM": 7,
        "RAMP2": 6,
    },
    "hypoxic_stress_zone": {
        "CA9": 9,
        "HIF1A": 6,
        "SLC2A1": 8,
        "LDHA": 8,
        "ENO1": 7,
        "PGK1": 7,
        "BNIP3": 7,
        "NDRG1": 8,
        "ADM": 7,
    },
}


def main() -> None:
    genes = sorted({gene for markers in REFERENCE.values() for gene in markers})
    rows = []
    for cell_type, markers in REFERENCE.items():
        row = {"cell_type": cell_type}
        row.update({gene: float(markers.get(gene, 0.0)) for gene in genes})
        rows.append(row)
    out = Path("data/processed/spatial_emt_niche_gnn_references/pdac_marker_reference.tsv")
    out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out, sep="\t", index=False)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
