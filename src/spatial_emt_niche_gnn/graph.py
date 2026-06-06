from __future__ import annotations

import numpy as np
import pandas as pd


DEFAULT_LR_PAIRS = [
    ("GAS6", "AXL"),
    ("TGFB1", "TGFBR1"),
    ("TGFB1", "TGFBR2"),
    ("CXCL12", "CXCR4"),
    ("SPP1", "ITGAV"),
    ("SPP1", "CD44"),
    ("VEGFA", "KDR"),
    ("CSF1", "CSF1R"),
]


def build_spatial_graph(
    scored: pd.DataFrame,
    k: int = 6,
    radius: float | None = None,
    lr_pairs: list[tuple[str, str]] | None = None,
) -> pd.DataFrame:
    """Build a typed graph from spots.

    Edges are undirected for physical neighbors and directed for niche-signal
    links. The typed edge table is intentionally plain TSV-friendly.
    """
    lr_pairs = lr_pairs or DEFAULT_LR_PAIRS
    scored = scored.reset_index(drop=True)
    rows = []
    group_cols = [col for col in ["sample_id", "section_id"] if col in scored.columns]
    groups = scored.groupby(group_cols, dropna=False) if group_cols else [(None, scored)]

    for _, group in groups:
        group = group.reset_index(drop=True)
        xy = group[["x", "y"]].astype(float).to_numpy()
        spot_ids = group["spot_id"].astype(str).tolist()
        local_edges = []
        for i in range(len(group)):
            dist = np.linalg.norm(xy - xy[i], axis=1)
            order = np.argsort(dist)
            for j in order[1 : k + 1]:
                if radius is not None and dist[j] > radius:
                    continue
                edge = {
                    "source": spot_ids[i],
                    "target": spot_ids[j],
                    "source_idx": i,
                    "target_idx": j,
                    "edge_type": "spatial_knn",
                    "distance": float(dist[j]),
                    "weight": float(1.0 / (1.0 + dist[j])),
                }
                local_edges.append(edge)
                rows.append({key: value for key, value in edge.items() if not key.endswith("_idx")})

        gradient_specs = [
            ("hypoxia", "hypoxia_gradient"),
            ("ecm_remodeling", "ecm_gradient"),
        ]
        for feature_col, edge_type in gradient_specs:
            if feature_col not in group.columns:
                continue
            feature_sd = float(group[feature_col].std(ddof=0))
            if feature_sd <= 0:
                continue
            for edge in local_edges:
                i = edge["source_idx"]
                j = edge["target_idx"]
                niche_delta = abs(float(group.loc[i, feature_col]) - float(group.loc[j, feature_col]))
                if niche_delta >= feature_sd:
                    rows.append(
                        {
                            "source": edge["source"],
                            "target": edge["target"],
                            "edge_type": edge_type,
                            "distance": edge["distance"],
                            "weight": float(niche_delta / (1.0 + edge["distance"])),
                        }
                    )

        for ligand, receptor in lr_pairs:
            ligand_col = ligand.upper()
            receptor_col = receptor.upper()
            if ligand_col not in group.columns or receptor_col not in group.columns:
                continue
            ligand_high = group[ligand_col] >= group[ligand_col].quantile(0.8)
            receptor_high = group[receptor_col] >= group[receptor_col].quantile(0.8)
            for edge in local_edges:
                i = edge["source_idx"]
                j = edge["target_idx"]
                if ligand_high.iloc[i] and receptor_high.iloc[j]:
                    rows.append(
                        {
                            "source": edge["source"],
                            "target": edge["target"],
                            "edge_type": f"ligand_receptor:{ligand_col}-{receptor_col}",
                            "distance": edge["distance"],
                            "weight": edge["weight"],
                        }
                    )

    edges = pd.DataFrame(rows).drop_duplicates()
    return edges.sort_values(["source", "target", "edge_type"]).reset_index(drop=True)


def graph_features(scored: pd.DataFrame, edges: pd.DataFrame, feature_cols: list[str]) -> pd.DataFrame:
    base = scored[["spot_id"] + feature_cols].copy()
    indexed = base.set_index("spot_id")
    rows = []
    for spot_id, group in edges.groupby("source"):
        neighbors = [target for target in group["target"].astype(str) if target in indexed.index]
        if not neighbors or spot_id not in indexed.index:
            continue
        weights = group[group["target"].astype(str).isin(neighbors)]["weight"].to_numpy(dtype=float)
        values = indexed.loc[neighbors, feature_cols].to_numpy(dtype=float)
        if weights.sum() == 0:
            agg = values.mean(axis=0)
        else:
            agg = np.average(values, axis=0, weights=weights)
        rows.append({"spot_id": spot_id, **{f"neighbor_{col}": val for col, val in zip(feature_cols, agg)}})
    neighbor = pd.DataFrame(rows)
    return base.merge(neighbor, on="spot_id", how="left").fillna(0.0)


def edge_type_summary(edges: pd.DataFrame) -> pd.DataFrame:
    if edges.empty:
        return pd.DataFrame(columns=["edge_type", "edge_count", "mean_weight", "mean_distance"])
    return (
        edges.groupby("edge_type", dropna=False)
        .agg(edge_count=("edge_type", "count"), mean_weight=("weight", "mean"), mean_distance=("distance", "mean"))
        .reset_index()
        .sort_values("edge_count", ascending=False)
    )
