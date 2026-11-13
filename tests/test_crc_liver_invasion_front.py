from __future__ import annotations

import pandas as pd

from crc_liver_invasion_front.graph import build_heterogeneous_interface_graph
from crc_liver_invasion_front.interface import annotate_interface, build_physical_edges
from crc_liver_invasion_front.signatures import classify_compartments


def synthetic_scores() -> pd.DataFrame:
    rows = []
    for index in range(8):
        malignant = index < 4
        rows.append(
            {
                "spot_id": f"L1::{index}",
                "section_id": "L1",
                "site": "liver_metastasis",
                "is_liver_metastasis": True,
                "x": index,
                "y": 0,
                "pixel_x": index * 10,
                "pixel_y": 0,
                "malignant_crc": 0.9 if malignant else 0.1,
                "epithelial": 0.8 if malignant else 0.1,
                "mesenchymal": 0.7 if index in {2, 3} else 0.2,
                "partial_emt": 0.75 if index in {2, 3} else 0.2,
                "hepatocyte": 0.1 if malignant else 0.9,
                "damaged_hepatocyte": 0.7 if index in {4, 5} else 0.2,
                "mrc1_ccl18_macrophage": 0.5,
                "activated_fibroblast": 0.3,
                "endothelial": 0.4,
                "ecm_remodeling": 0.0 if index < 4 else 1.0,
                "glycolysis": 1.0 if index < 4 else 0.0,
                "hypoxia": 0.4,
                "immune_total": 0.3,
            }
        )
    return classify_compartments(pd.DataFrame(rows))


def test_partial_emt_requires_malignant_context() -> None:
    frame = synthetic_scores()
    assert frame.loc[frame["spot_id"].eq("L1::3"), "dominant_compartment"].iloc[0] == "malignant_partial_emt"
    stromal = frame.iloc[[0]].copy()
    stromal["malignant_crc"] = 0.1
    stromal["mesenchymal"] = 0.9
    stromal["activated_fibroblast"] = 0.9
    classified = classify_compartments(stromal)
    assert bool(classified["stromal_inflated_emt_risk"].iloc[0])
    assert not bool(classified["malignant_pemt_candidate"].iloc[0])


def test_interface_has_signed_tumour_and_liver_bands() -> None:
    frame = synthetic_scores()
    physical = build_physical_edges(frame, k=2)
    annotated, summary = annotate_interface(frame, physical, front_hops=2)
    assert summary["boundary_pairs"].iloc[0] > 0
    tumour_front = annotated[annotated["interface_band"].eq("tumour_front")]
    liver_front = annotated[annotated["interface_band"].eq("liver_front")]
    assert not tumour_front.empty and not liver_front.empty
    assert tumour_front["signed_interface_distance_um"].le(0).all()
    assert liver_front["signed_interface_distance_um"].ge(0).all()


def test_heterograph_contains_required_biological_edges() -> None:
    frame = synthetic_scores()
    physical = build_physical_edges(frame, k=2)
    annotated, _ = annotate_interface(frame, physical, front_hops=2)
    nodes, edges = build_heterogeneous_interface_graph(annotated, physical)
    assert {"malignant_partial_emt", "hepatocyte"}.issubset(set(nodes["node_type"]))
    assert "cross_interface" in set(edges["edge_family"])
    assert "ecm_gradient" in set(edges["edge_family"])
    assert "glycolysis_gradient" in set(edges["edge_family"])
