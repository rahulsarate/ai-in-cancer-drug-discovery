from __future__ import annotations

from collections import defaultdict, deque

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree


MALIGNANT_TYPES = {"malignant_epithelial", "malignant_partial_emt"}


def build_physical_edges(scored: pd.DataFrame, k: int = 6) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for section_id, section in scored.groupby("section_id", sort=False):
        section = section.reset_index(drop=True)
        xy = section[["x", "y"]].to_numpy(dtype=float)
        neighbors = min(k + 1, len(section))
        distances, indices = cKDTree(xy).query(xy, k=neighbors)
        if neighbors == 1:
            continue
        seen: set[tuple[str, str]] = set()
        ids = section["spot_id"].astype(str).tolist()
        for source_index in range(len(section)):
            for distance, target_index in zip(np.atleast_1d(distances[source_index])[1:], np.atleast_1d(indices[source_index])[1:]):
                source, target = ids[source_index], ids[int(target_index)]
                pair = tuple(sorted((source, target)))
                if pair in seen:
                    continue
                seen.add(pair)
                rows.append(
                    {
                        "section_id": section_id,
                        "source": pair[0],
                        "target": pair[1],
                        "edge_type": "spatial_neighbor",
                        "distance": float(distance),
                        "weight": float(1.0 / (1.0 + distance)),
                    }
                )
    return pd.DataFrame(rows)


def _multi_source_steps(node_ids: list[str], edges: pd.DataFrame, seeds: set[str]) -> dict[str, int]:
    adjacency: dict[str, set[str]] = defaultdict(set)
    for row in edges.itertuples(index=False):
        adjacency[str(row.source)].add(str(row.target))
        adjacency[str(row.target)].add(str(row.source))
    distance = {node_id: 10_000 for node_id in node_ids}
    queue: deque[str] = deque()
    for seed in seeds:
        distance[seed] = 0
        queue.append(seed)
    while queue:
        source = queue.popleft()
        for target in adjacency[source]:
            if distance[target] > distance[source] + 1:
                distance[target] = distance[source] + 1
                queue.append(target)
    return distance


def annotate_interface(scored: pd.DataFrame, physical_edges: pd.DataFrame, front_hops: int = 3) -> tuple[pd.DataFrame, pd.DataFrame]:
    out_parts: list[pd.DataFrame] = []
    summary_rows: list[dict[str, object]] = []
    for section_id, section in scored.groupby("section_id", sort=False):
        section = section.copy().reset_index(drop=True)
        local_edges = physical_edges[physical_edges["section_id"].eq(section_id)]
        metastatic = bool(section["is_liver_metastasis"].iloc[0])
        compartment = section.set_index("spot_id")["dominant_compartment"].to_dict()
        boundary_pairs: list[tuple[str, str]] = []
        if metastatic:
            for edge in local_edges.itertuples(index=False):
                source_type = compartment.get(str(edge.source), "other")
                target_type = compartment.get(str(edge.target), "other")
                if (source_type in MALIGNANT_TYPES and target_type == "hepatocyte") or (
                    target_type in MALIGNANT_TYPES and source_type == "hepatocyte"
                ):
                    boundary_pairs.append((str(edge.source), str(edge.target)))
        seeds = {node for pair in boundary_pairs for node in pair}
        steps = _multi_source_steps(section["spot_id"].astype(str).tolist(), local_edges, seeds) if seeds else {}
        section["interface_steps"] = section["spot_id"].astype(str).map(steps).fillna(10_000).astype(int)
        section["approx_interface_distance_um"] = section["interface_steps"].clip(upper=50) * 100
        compartment_values = section["dominant_compartment"]
        tumour_side = compartment_values.isin(MALIGNANT_TYPES)
        liver_side = compartment_values.eq("hepatocyte")
        unresolved = ~(tumour_side | liver_side)
        tumour_side = tumour_side | (unresolved & section["malignant_crc"].gt(section["hepatocyte"]))
        liver_side = liver_side | (unresolved & ~tumour_side)
        section["interface_side"] = np.where(tumour_side, "tumour", "liver")
        section["interface_band"] = "non_interface"
        section.loc[tumour_side & section["interface_steps"].le(front_hops), "interface_band"] = "tumour_front"
        section.loc[liver_side & section["interface_steps"].le(front_hops), "interface_band"] = "liver_front"
        section.loc[tumour_side & section["interface_steps"].gt(front_hops), "interface_band"] = "tumour_core"
        section.loc[liver_side & section["interface_steps"].gt(front_hops), "interface_band"] = "liver_parenchyma"
        section["signed_interface_distance_um"] = np.where(
            tumour_side,
            -section["approx_interface_distance_um"],
            section["approx_interface_distance_um"],
        )
        section["is_interface_window"] = section["interface_steps"].le(front_hops)
        section["is_tumour_front"] = section["interface_band"].eq("tumour_front")

        direct_contact_fraction = len(boundary_pairs) / max(1, len(local_edges))
        front = section[section["is_interface_window"]]
        ecm_front = float(front["ecm_remodeling"].mean()) if not front.empty else np.nan
        damaged_front = float(front["damaged_hepatocyte"].mean()) if not front.empty else np.nan
        if not metastatic:
            growth_proxy = "not_applicable_primary_crc"
            section["interface_band"] = "not_applicable_primary_crc"
            section["interface_side"] = "not_applicable"
            section["is_interface_window"] = False
            section["is_tumour_front"] = False
            section["signed_interface_distance_um"] = np.nan
        elif not seeds:
            growth_proxy = "interface_not_resolved"
        elif ecm_front >= 0.60 and direct_contact_fraction < 0.015:
            growth_proxy = "desmoplastic_like_proxy"
        elif direct_contact_fraction >= 0.015 and damaged_front >= 0.50:
            growth_proxy = "replacement_like_proxy"
        else:
            growth_proxy = "mixed_or_uncertain_proxy"
        section["growth_pattern_proxy"] = growth_proxy
        summary_rows.append(
            {
                "section_id": section_id,
                "site": section["site"].iloc[0],
                "spots": len(section),
                "boundary_pairs": len(boundary_pairs),
                "interface_spots": int(section["is_interface_window"].sum()),
                "tumour_front_spots": int(section["is_tumour_front"].sum()),
                "mean_front_partial_emt": float(front["partial_emt"].mean()) if not front.empty else np.nan,
                "mean_front_macrophage": float(front["mrc1_ccl18_macrophage"].mean()) if not front.empty else np.nan,
                "mean_front_fibroblast": float(front["activated_fibroblast"].mean()) if not front.empty else np.nan,
                "mean_front_ecm": ecm_front,
                "mean_front_glycolysis": float(front["glycolysis"].mean()) if not front.empty else np.nan,
                "direct_contact_fraction": direct_contact_fraction,
                "growth_pattern_proxy": growth_proxy,
                "label_source": "marker_plus_spatial_weak_label",
            }
        )
        out_parts.append(section)
    return pd.concat(out_parts, ignore_index=True), pd.DataFrame(summary_rows)
