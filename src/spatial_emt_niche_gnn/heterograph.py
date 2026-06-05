from __future__ import annotations

import pandas as pd


COMPARTMENT_NODE_TYPES = [
    "tumor_epithelial",
    "tumor_mesenchymal",
    "caf",
    "tam",
    "t_cell",
    "hypoxic_zone",
    "ecm_rich_zone",
]


def build_heterogeneous_graph_nodes(scored: pd.DataFrame, proxy: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    nodes = []
    spot_cols = ["spot_id", "sample_id", "section_id", "cohort", "cancer_type", "emt_niche_label"]
    for _, row in scored.iterrows():
        nodes.append(
            {
                "node_id": row["spot_id"],
                "node_type": "spot",
                **{col: row.get(col, "") for col in spot_cols if col in scored.columns},
            }
        )
    for compartment in COMPARTMENT_NODE_TYPES:
        nodes.append({"node_id": f"compartment::{compartment}", "node_type": compartment})

    edges = []
    proxy = proxy.set_index("spot_id")
    for spot_id, row in proxy.iterrows():
        for compartment in COMPARTMENT_NODE_TYPES:
            if compartment not in row:
                continue
            weight = float(row[compartment])
            if weight > 0:
                edges.append(
                    {
                        "source": spot_id,
                        "target": f"compartment::{compartment}",
                        "edge_type": "spot_has_compartment_proxy",
                        "weight": weight,
                    }
                )
    return pd.DataFrame(nodes), pd.DataFrame(edges)
