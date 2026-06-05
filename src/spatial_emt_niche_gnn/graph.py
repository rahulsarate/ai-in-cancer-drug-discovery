from __future__ import annotations

from itertools import combinations

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
    xy = scored[["x", "y"]].astype(float).to_numpy()
    spot_ids = scored["spot_id"].astype(str).tolist()
    rows = []

    for i in range(len(scored)):
        dist = np.linalg.norm(xy - xy[i], axis=1)
        order = np.argsort(dist)
        for j in order[1 : k + 1]:
            if radius is not None and dist[j] > radius:
                continue
            rows.append(
                {
                    "source": spot_ids[i],
                    "target": spot_ids[j],
                    "edge_type": "spatial_knn",
                    "distance": float(dist[j]),
                    "weight": float(1.0 / (1.0 + dist[j])),
                }
            )

    for i, j in combinations(range(len(scored)), 2):
        dist = float(np.linalg.norm(xy[i] - xy[j]))
        if radius is not None and dist > radius:
            continue
        niche_delta = abs(float(scored.loc[i, "hypoxia"]) - float(scored.loc[j, "hypoxia"]))
        if niche_delta >= scored["hypoxia"].std(ddof=0):
            rows.append(
                {
                    "source": spot_ids[i],
                    "target": spot_ids[j],
                    "edge_type": "hypoxia_gradient",
                    "distance": dist,
                    "weight": float(niche_delta / (1.0 + dist)),
                }
            )

    for ligand, receptor in lr_pairs:
        ligand_col = ligand.upper()
        receptor_col = receptor.upper()
        if ligand_col not in scored.columns or receptor_col not in scored.columns:
            continue
        ligand_high = scored[ligand_col] >= scored[ligand_col].quantile(0.8)
        receptor_high = scored[receptor_col] >= scored[receptor_col].quantile(0.8)
        for i in scored.index[ligand_high]:
            dist = np.linalg.norm(xy - xy[i], axis=1)
            nearby = np.where((dist > 0) & (dist <= (radius or np.quantile(dist[dist > 0], 0.1))))[0]
            for j in nearby:
                if receptor_high.iloc[j]:
                    rows.append(
                        {
                            "source": spot_ids[i],
                            "target": spot_ids[j],
                            "edge_type": f"ligand_receptor:{ligand_col}-{receptor_col}",
                            "distance": float(dist[j]),
                            "weight": float(1.0 / (1.0 + dist[j])),
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
