import pandas as pd

from metastasis_target_ranker.ranking import rank_targets


def test_rank_targets_prioritizes_high_evidence_target():
    frame = pd.DataFrame(
        {
            "target": ["AXL", "RANDOM1"],
            "family": ["AXL_TAM", "other"],
            "emt_state_specificity": [0.9, 0.1],
            "metastatic_association": [0.9, 0.1],
            "druggability": [0.8, 0.2],
            "crispr_dependency": [0.8, 0.1],
            "compound_availability": [0.7, 0.1],
            "normal_tissue_safety": [0.6, 0.3],
            "literature_support": [0.9, 0.1],
        }
    )
    ranked = rank_targets(frame)
    assert ranked.loc[0, "target"] == "AXL"


def test_rank_targets_reports_missing_evidence():
    frame = pd.DataFrame(
        {
            "target": ["AXL"],
            "family": ["AXL_TAM"],
            "emt_state_specificity": [0.9],
        }
    )
    ranked = rank_targets(frame)
    assert ranked.loc[0, "missing_evidence_count"] == 6
    assert ranked.loc[0, "evidence_completeness"] < 1.0
