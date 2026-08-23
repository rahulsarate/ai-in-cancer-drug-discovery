from __future__ import annotations

import numpy as np
import pandas as pd


CRC_LIVER_SIGNATURES: dict[str, list[str]] = {
    "malignant_crc": [
        "EPCAM", "KRT8", "KRT18", "KRT19", "KRT20", "CDX2", "CEACAM5",
        "CEACAM6", "VIL1", "TACSTD2", "MUC13", "CTNNB1",
    ],
    "epithelial": [
        "EPCAM", "CDH1", "KRT8", "KRT18", "KRT19", "KRT20", "CLDN3",
        "CLDN4", "CLDN7", "OCLN", "TJP1", "GRHL2", "OVOL2",
    ],
    "mesenchymal": [
        "VIM", "FN1", "CDH2", "ZEB1", "ZEB2", "SNAI1", "SNAI2", "TWIST1",
        "ITGA5", "SERPINE1", "LAMC2", "TGFBI", "MMP14", "LOX",
    ],
    "hepatocyte": [
        "ALB", "APOA1", "APOA2", "CPS1", "TTR", "HP", "FGA", "FGB", "FGG",
        "CYP2E1", "CYP3A4", "ASGR1", "HNF4A", "C3",
    ],
    "damaged_hepatocyte": [
        "SAA1", "SAA2", "CRP", "PLA2G2A", "LCN2", "C3", "KRT7", "SPP1",
    ],
    "mrc1_ccl18_macrophage": [
        "MRC1", "CCL18", "CD163", "MSR1", "MARCO", "APOE", "C1QA", "C1QB",
        "C1QC", "LST1", "TYROBP", "GAS6", "TREM2",
    ],
    "activated_fibroblast": [
        "FAP", "ACTA2", "PDGFRB", "COL1A1", "COL1A2", "COL3A1", "POSTN",
        "CTHRC1", "INHBA", "CXCL12", "MMP11", "TGFBI", "MCAM",
    ],
    "endothelial": [
        "PECAM1", "VWF", "KDR", "FLT1", "EMCN", "ENG", "ESAM", "CDH5",
        "RAMP2", "PLVAP", "KLF2", "TEK",
    ],
    "ecm_remodeling": [
        "COL1A1", "COL1A2", "COL3A1", "COL4A1", "COL5A1", "FN1", "POSTN",
        "LUM", "DCN", "LOX", "MMP2", "MMP9", "MMP11", "MMP14", "CTHRC1",
    ],
    "glycolysis": [
        "SLC2A1", "HK2", "GPI", "PFKP", "ALDOA", "GAPDH", "PGK1", "ENO1",
        "PKM", "LDHA", "PDK1", "SLC16A3",
    ],
    "hypoxia": [
        "HIF1A", "CA9", "VEGFA", "SLC2A1", "LDHA", "BNIP3", "NDRG1",
        "EGLN3", "ADM", "PGK1",
    ],
    "immune_total": [
        "PTPRC", "CD3D", "CD3E", "CD8A", "MS4A1", "NKG7", "LST1", "TYROBP",
    ],
}

LIGAND_RECEPTOR_GENES = {
    "CCL18", "PITPNM3", "SPP1", "CD44", "ITGAV", "TGFB1", "TGFBR1",
    "TGFBR2", "CXCL12", "CXCR4", "HGF", "MET", "VEGFA", "KDR", "ANGPT2",
    "TEK", "COL1A1", "ITGA2", "GAS6", "AXL",
}


def required_genes() -> set[str]:
    return {gene for genes in CRC_LIVER_SIGNATURES.values() for gene in genes} | LIGAND_RECEPTOR_GENES


def _rank_signature(expression: pd.DataFrame, genes: list[str]) -> tuple[pd.Series, int]:
    present = [gene for gene in genes if gene in expression.columns]
    if not present:
        return pd.Series(0.0, index=expression.index), 0
    values = expression[present].apply(pd.to_numeric, errors="coerce").fillna(0.0)
    scaled = values.apply(lambda col: (col - col.mean()) / (col.std(ddof=0) or 1.0), axis=0)
    raw = scaled.mean(axis=1)
    return raw.rank(method="average", pct=True).fillna(0.0), len(present)


def score_crc_liver_programs(expression: pd.DataFrame, metadata: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Score lineage and niche programs within each section.

    Scores are percentile ranks within a section, which makes the interface
    logic robust to library-size and FFPE capture differences. They are
    comparative spatial scores, not absolute cell-type proportions.
    """
    expr = expression.set_index("spot_id")
    meta = metadata.set_index("spot_id")
    rows: list[pd.DataFrame] = []
    coverage_rows: list[dict[str, object]] = []
    for section_id, section_meta in meta.groupby("section_id", sort=False):
        ids = section_meta.index.intersection(expr.index)
        section_expr = expr.loc[ids]
        scored = pd.DataFrame(index=ids)
        for program, genes in CRC_LIVER_SIGNATURES.items():
            scored[program], covered = _rank_signature(section_expr, genes)
            coverage_rows.append(
                {
                    "section_id": section_id,
                    "program": program,
                    "genes_expected": len(genes),
                    "genes_detected": covered,
                    "coverage_fraction": covered / len(genes),
                }
            )
        scored["partial_emt"] = (
            np.sqrt(scored["epithelial"] * scored["mesenchymal"])
            * (0.5 + 0.5 * scored["malignant_crc"])
        ).clip(0.0, 1.0)
        scored = scored.join(section_meta, how="left")
        if scored["site"].eq("primary_crc").all():
            scored["hepatocyte"] = 0.0
            scored["damaged_hepatocyte"] = 0.0
        for gene in sorted(LIGAND_RECEPTOR_GENES):
            if gene in section_expr.columns:
                scored[gene] = section_expr[gene]
        rows.append(scored.reset_index(names="spot_id"))
    result = pd.concat(rows, ignore_index=True)
    return classify_compartments(result), pd.DataFrame(coverage_rows)


def classify_compartments(scored: pd.DataFrame) -> pd.DataFrame:
    out = scored.copy()
    lineage_columns = [
        "malignant_crc", "hepatocyte", "mrc1_ccl18_macrophage",
        "activated_fibroblast", "endothelial",
    ]
    lineages = out[lineage_columns]
    lineage_values = lineages.to_numpy(dtype=float)
    top_two = np.partition(lineage_values, -2, axis=1)[:, -2:]
    out["lineage_confidence"] = top_two.max(axis=1)
    out["lineage_margin"] = top_two.max(axis=1) - top_two.min(axis=1)
    dominant = lineages.idxmax(axis=1)
    dominant = dominant.replace(
        {
            "malignant_crc": "malignant_epithelial",
            "mrc1_ccl18_macrophage": "mrc1_ccl18_macrophage",
            "activated_fibroblast": "activated_fibroblast",
        }
    )
    malignant = out["malignant_crc"].ge(0.55)
    partial = malignant & out["partial_emt"].ge(0.58) & out["mesenchymal"].ge(0.50)
    dominant.loc[partial] = "malignant_partial_emt"
    dominant.loc[out["lineage_confidence"].lt(0.45)] = "other"
    out["dominant_compartment"] = dominant
    out["ecm_rich_zone"] = out["ecm_remodeling"].ge(0.75)
    out["glycolytic_zone"] = out["glycolysis"].ge(0.75)
    out["stromal_inflated_emt_risk"] = (
        out["mesenchymal"].ge(0.70)
        & out["malignant_crc"].lt(0.45)
        & out["activated_fibroblast"].ge(0.60)
    )
    out["malignant_pemt_candidate"] = partial & ~out["stromal_inflated_emt_risk"]
    out["mixed_lineage_warning"] = out["lineage_margin"].lt(0.10)
    return out
