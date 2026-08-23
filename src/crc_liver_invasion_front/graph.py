from __future__ import annotations

import numpy as np
import pandas as pd

from .interface import MALIGNANT_TYPES


LR_PAIRS = [
    ("CCL18", "PITPNM3", "macrophage_to_malignant"),
    ("SPP1", "CD44", "myeloid_ecm_to_malignant"),
    ("SPP1", "ITGAV", "myeloid_ecm_to_malignant"),
    ("TGFB1", "TGFBR2", "fibroblast_to_malignant"),
    ("CXCL12", "CXCR4", "fibroblast_to_malignant"),
    ("HGF", "MET", "liver_to_malignant"),
    ("VEGFA", "KDR", "angiogenic"),
    ("ANGPT2", "TEK", "angiogenic"),
    ("COL1A1", "ITGA2", "ecm_adhesion"),
    ("GAS6", "AXL", "myeloid_to_pemt"),
]

MESSAGE_FEATURES = [
    "partial_emt", "mrc1_ccl18_macrophage", "activated_fibroblast", "endothelial",
    "ecm_remodeling", "glycolysis", "hypoxia", "damaged_hepatocyte",
]


def build_heterogeneous_interface_graph(scored: pd.DataFrame, physical_edges: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    nodes = scored[
        [
            "spot_id", "section_id", "site", "x", "y", "dominant_compartment",
            "interface_band", "signed_interface_distance_um", "ecm_rich_zone",
            "glycolytic_zone", "stromal_inflated_emt_risk", *MESSAGE_FEATURES,
        ]
    ].copy()
    nodes = nodes.rename(columns={"dominant_compartment": "node_type"})
    indexed = scored.set_index("spot_id")
    edge_rows: list[dict[str, object]] = []

    for edge in physical_edges.itertuples(index=False):
        for source, target in ((str(edge.source), str(edge.target)), (str(edge.target), str(edge.source))):
            source_type = str(indexed.at[source, "dominant_compartment"])
            target_type = str(indexed.at[target, "dominant_compartment"])
            base = {
                "section_id": edge.section_id,
                "source": source,
                "target": target,
                "source_type": source_type,
                "target_type": target_type,
                "distance": float(edge.distance),
                "weight": float(edge.weight),
            }
            edge_rows.append({**base, "edge_type": "spatial_neighbor", "edge_family": "spatial"})
            if source_type != target_type:
                edge_rows.append({**base, "edge_type": f"contact:{source_type}__{target_type}", "edge_family": "compartment_contact"})
            is_liver_section = bool(indexed.at[source, "is_liver_metastasis"])
            if is_liver_section and ((source_type in MALIGNANT_TYPES and target_type == "hepatocyte") or (
                source_type == "hepatocyte" and target_type in MALIGNANT_TYPES
            )):
                edge_rows.append({**base, "edge_type": "direct_tumour_hepatocyte_contact", "edge_family": "cross_interface"})

    for section_id, section in scored.groupby("section_id", sort=False):
        section_index = section.set_index("spot_id")
        local_physical = physical_edges[physical_edges["section_id"].eq(section_id)]
        if not bool(section["is_liver_metastasis"].iloc[0]):
            continue
        context_ids = set(section.loc[section["interface_steps"].le(5), "spot_id"].astype(str))
        local_physical = local_physical[
            local_physical["source"].astype(str).isin(context_ids)
            | local_physical["target"].astype(str).isin(context_ids)
        ].copy()
        directed = pd.concat(
            [
                local_physical[["source", "target", "distance", "weight"]],
                local_physical[["target", "source", "distance", "weight"]].rename(columns={"target": "source", "source": "target"}),
            ],
            ignore_index=True,
        )
        for feature, family in (("ecm_remodeling", "ecm_gradient"), ("glycolysis", "glycolysis_gradient")):
            threshold = float(section[feature].std(ddof=0))
            gradient = local_physical[["source", "target", "distance"]].copy()
            gradient["source_value"] = gradient["source"].map(section_index[feature])
            gradient["target_value"] = gradient["target"].map(section_index[feature])
            gradient["delta"] = gradient["target_value"] - gradient["source_value"]
            gradient = gradient[gradient["delta"].abs().ge(threshold)].copy()
            reverse = gradient["delta"].lt(0)
            gradient.loc[reverse, ["source", "target"]] = gradient.loc[reverse, ["target", "source"]].to_numpy()
            gradient["delta"] = gradient["delta"].abs()
            gradient["section_id"] = section_id
            gradient["source_type"] = gradient["source"].map(section_index["dominant_compartment"])
            gradient["target_type"] = gradient["target"].map(section_index["dominant_compartment"])
            gradient["edge_type"] = f"{family}:up_gradient"
            gradient["edge_family"] = family
            gradient["weight"] = gradient["delta"] / (1.0 + gradient["distance"])
            edge_rows.extend(gradient[["section_id", "source", "target", "source_type", "target_type", "edge_type", "edge_family", "distance", "weight"]].to_dict("records"))
        for ligand, receptor, axis in LR_PAIRS:
            if ligand not in section.columns or receptor not in section.columns:
                continue
            ligand_cut = section[ligand].quantile(0.80)
            receptor_cut = section[receptor].quantile(0.80)
            if ligand_cut <= 0 or receptor_cut <= 0 or section[ligand].max() <= 0 or section[receptor].max() <= 0:
                continue
            lr = directed.copy()
            lr["ligand_value"] = lr["source"].map(section_index[ligand])
            lr["receptor_value"] = lr["target"].map(section_index[receptor])
            lr = lr[lr["ligand_value"].gt(ligand_cut) & lr["receptor_value"].gt(receptor_cut)].copy()
            lr["section_id"] = section_id
            lr["source_type"] = lr["source"].map(section_index["dominant_compartment"])
            lr["target_type"] = lr["target"].map(section_index["dominant_compartment"])
            lr["edge_type"] = f"ligand_receptor:{ligand}-{receptor}"
            lr["edge_family"] = f"ligand_receptor:{axis}"
            lr["weight"] = np.sqrt(lr["ligand_value"] * lr["receptor_value"]) / (1.0 + lr["distance"])
            edge_rows.extend(lr[["section_id", "source", "target", "source_type", "target_type", "edge_type", "edge_family", "distance", "weight"]].to_dict("records"))
    edges = pd.DataFrame(edge_rows).drop_duplicates(["source", "target", "edge_type"])
    return nodes, edges.reset_index(drop=True)


def typed_message_features(scored: pd.DataFrame, edges: pd.DataFrame) -> pd.DataFrame:
    base = scored[["spot_id", *MESSAGE_FEATURES]].copy().set_index("spot_id")
    result = base.copy()
    family_map = {
        "spatial": "spatial",
        "compartment_contact": "contact",
        "cross_interface": "cross_interface",
        "ecm_gradient": "ecm_gradient",
        "glycolysis_gradient": "glycolysis_gradient",
    }
    families = edges["edge_family"].map(lambda value: "ligand_receptor" if str(value).startswith("ligand_receptor:") else value)
    work = edges.assign(message_family=families)
    for family, prefix in {**family_map, "ligand_receptor": "lr"}.items():
        local = work[work["message_family"].eq(family)]
        if local.empty:
            continue
        valid = local[local["target"].astype(str).isin(base.index)].copy()
        if valid.empty:
            continue
        target_features = base.add_prefix("target_").reset_index().rename(columns={"spot_id": "target"})
        valid = valid.merge(target_features, on="target", how="inner")
        weighted_columns = []
        for feature in MESSAGE_FEATURES:
            weighted = f"weighted_{feature}"
            valid[weighted] = valid[f"target_{feature}"] * valid["weight"]
            weighted_columns.append(weighted)
        grouped = valid.groupby("source", sort=False)[["weight", *weighted_columns]].sum()
        denominator = grouped["weight"].replace(0, np.nan)
        aggregate = pd.DataFrame(index=grouped.index)
        for feature, weighted in zip(MESSAGE_FEATURES, weighted_columns):
            aggregate[f"{prefix}_neighbor_{feature}"] = grouped[weighted] / denominator
        result = result.join(aggregate, how="left")
    return result.fillna(0.0).reset_index()


def summarize_edges(edges: pd.DataFrame) -> pd.DataFrame:
    if edges.empty:
        return pd.DataFrame(columns=["edge_family", "edge_type", "edge_count", "mean_weight"])
    return (
        edges.groupby(["edge_family", "edge_type"], dropna=False)
        .agg(edge_count=("edge_type", "size"), mean_weight=("weight", "mean"), sections=("section_id", "nunique"))
        .reset_index()
        .sort_values("edge_count", ascending=False)
    )
