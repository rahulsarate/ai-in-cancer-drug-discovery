"""Curated starter signatures for EMT and tumor microenvironment scoring.

These signatures are intentionally small and interpretable. They should be
expanded or replaced with benchmarked signatures for publication-grade work.
"""

SIGNATURES = {
    "epithelial": [
        "CDH1", "EPCAM", "KRT8", "KRT18", "KRT19", "KRT7", "MUC1",
        "CLDN3", "CLDN4", "CLDN7", "OCLN", "TJP1", "GRHL2", "OVOL2",
    ],
    "mesenchymal": [
        "VIM", "CDH2", "FN1", "SNAI1", "SNAI2", "TWIST1", "TWIST2",
        "ZEB1", "ZEB2", "MMP2", "MMP9", "MMP14", "ITGA5", "ITGB1",
        "SERPINE1", "LOX",
    ],
    "partial_emt_anchor": [
        "EPCAM", "CDH1", "KRT8", "KRT18", "VIM", "FN1", "ITGA5",
        "LAMC2", "S100A4", "TGFBI", "SERPINE1", "MMP14",
    ],
    "stromal_fibroblast": [
        "COL1A1", "COL1A2", "COL3A1", "COL5A1", "DCN", "LUM", "FAP",
        "ACTA2", "PDGFRA", "PDGFRB", "TAGLN", "THY1",
    ],
    "caf": [
        "FAP", "ACTA2", "PDGFRB", "COL1A1", "COL1A2", "CXCL12",
        "POSTN", "MMP11", "TGFBI", "INHBA", "CTHRC1",
    ],
    "immune_total": [
        "PTPRC", "CD3D", "CD3E", "CD2", "CD4", "CD8A", "CD8B",
        "NKG7", "GNLY", "GZMB", "MS4A1", "LST1", "TYROBP",
    ],
    "t_cell_cytotoxic": [
        "CD3D", "CD3E", "CD8A", "CD8B", "NKG7", "GNLY", "GZMB",
        "PRF1", "IFNG", "CXCL9", "CXCL10",
    ],
    "tam_spp1": [
        "CD68", "CD163", "MRC1", "LST1", "TYROBP", "APOE", "SPP1",
        "TREM2", "C1QA", "C1QB", "C1QC", "GAS6",
    ],
    "hypoxia": [
        "HIF1A", "CA9", "VEGFA", "SLC2A1", "LDHA", "ENO1", "PGK1",
        "BNIP3", "NDRG1", "EGLN3", "ADM",
    ],
    "ecm_remodeling": [
        "COL1A1", "COL1A2", "COL3A1", "COL5A1", "FN1", "POSTN", "LUM",
        "DCN", "LOX", "MMP2", "MMP9", "MMP11", "MMP14", "CTHRC1",
    ],
    "angiogenesis": [
        "VEGFA", "KDR", "FLT1", "ANGPT2", "TEK", "PECAM1", "VWF",
        "ENG", "ESAM", "CDH5", "MCAM", "RAMP2",
    ],
    "ferroptosis_sensitivity": [
        "ACSL4", "LPCAT3", "ALOX15", "ALOX12", "TFRC", "SAT1",
        "NOX4", "HMOX1",
    ],
    "ferroptosis_resistance": [
        "GPX4", "SLC7A11", "GCLC", "GCLM", "FTH1", "FTL", "NFE2L2",
        "SCD", "FADS2", "AIFM2",
    ],
}
