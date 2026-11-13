from __future__ import annotations

import pandas as pd

from emt_state_atlas.therapy import write_therapy_evidence_cards, write_therapy_report


def test_write_therapy_cards_links_targets_to_state_contexts(tmp_path):
    ranking = pd.DataFrame(
        {
            "target": ["AXL", "PTK2"],
            "family": ["AXL_TAM", "FAK_SRC_integrin"],
            "priority_score": [0.8, 0.6],
            "emt_state_specificity": [0.7, 0.6],
            "metastatic_association": [0.7, 0.6],
            "druggability": [0.8, 0.5],
            "crispr_dependency": [0.3, 0.7],
            "compound_availability": [0.9, 0.4],
            "normal_tissue_safety": [0.6, 0.5],
            "literature_support": [0.8, 0.4],
        }
    )
    state_summary = pd.DataFrame(
        {
            "cancer_type": ["PAAD", "SARC"],
            "sample_count": [100, 80],
            "immune_inflamed_emt_count": [30, 1],
            "stromal_dominant_count": [10, 50],
            "mesenchymal_count": [5, 10],
            "hybrid_e_m_count": [40, 2],
            "mesenchymal_like_fraction": [0.45, 0.75],
            "hybrid_fraction": [0.4, 0.025],
            "stromal_dominant_fraction": [0.1, 0.625],
        }
    )

    paths = write_therapy_evidence_cards(ranking, state_summary, tmp_path / "target_md", top_n=2)
    report = write_therapy_report(ranking, state_summary, tmp_path / "therapy_report.md")

    assert len(paths) == 2
    assert paths[0].exists()
    assert "Suggested Validation Assays" in paths[0].read_text(encoding="utf-8")
    assert report.exists()
