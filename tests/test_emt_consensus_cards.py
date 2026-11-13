from __future__ import annotations

import pandas as pd

from emt_state_atlas.cards import write_card_report, write_state_cards
from emt_state_atlas.consensus import ConsensusThresholds, add_consensus_states, consensus_cancer_type_summary


def _demo_scores() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "sample_id": ["epi", "hybrid", "mes", "stromal", "immune", "hypoxic"],
            "cancer_type": ["A", "A", "A", "B", "B", "B"],
            "epithelial": [4.0, 3.0, 0.2, 0.1, 0.3, 0.4],
            "mesenchymal": [0.1, 4.05, 4.0, 4.3, 4.4, 4.2],
            "emt_score": [-3.9, 0.2, 3.8, 4.2, 4.1, 4.25],
            "partial_emt_score": [0.1, 3.0, 0.2, 0.1, 0.3, 0.4],
            "stromal_contamination_risk": [0.1, 0.2, 0.3, 0.99, 0.4, 0.5],
            "immune_total": [0.1, 0.2, 0.3, 0.4, 5.0, 0.5],
            "caf_tam_niche": [0.1, 0.2, 0.3, 0.4, 5.0, 0.5],
            "hypoxia": [0.1, 0.2, 0.3, 0.4, 0.5, 5.0],
        }
    )


def test_add_consensus_states_labels_interpretable_states():
    thresholds = ConsensusThresholds(
        mesenchymal_high_quantile=0.50,
        stromal_warning_quantile=0.95,
        immune_inflamed_quantile=0.95,
    )
    scored = add_consensus_states(_demo_scores(), thresholds=thresholds).set_index("sample_id")

    assert scored.loc["epi", "consensus_emt_state"] == "epithelial"
    assert scored.loc["hybrid", "consensus_emt_state"] == "hybrid_e_m"
    assert scored.loc["stromal", "consensus_emt_state"] == "stromal_dominant"
    assert scored.loc["immune", "consensus_emt_state"] == "immune_inflamed_emt"
    assert scored.loc["hypoxic", "consensus_emt_state"] == "hypoxic_emt"
    assert scored.loc["epi", "confidence_label"] in {"high", "medium"}


def test_consensus_cancer_type_summary_counts_states():
    scored = add_consensus_states(_demo_scores())
    summary = consensus_cancer_type_summary(scored)

    assert {"cancer_type", "sample_count", "hybrid_fraction"}.issubset(summary.columns)
    assert int(summary["sample_count"].sum()) == len(scored)


def test_write_state_cards_creates_markdown_json_and_report(tmp_path):
    scored = add_consensus_states(_demo_scores())
    outputs = write_state_cards(scored, tmp_path / "cards", max_sample_cards=3)
    report = write_card_report(scored, tmp_path / "report.md")

    assert outputs["scores"].exists()
    assert outputs["cancer_type_summary"].exists()
    assert outputs["cancer_group_summary"].exists()
    assert outputs["requested_cancer_groups"].exists()
    assert len(list(outputs["sample_md_dir"].glob("*.md"))) == 3
    assert len(list(outputs["sample_json_dir"].glob("*.json"))) == 3
    assert len(list(outputs["cancer_type_md_dir"].glob("*.md"))) == 2
    assert len(list(outputs["cancer_group_md_dir"].glob("*.md"))) >= 1
    assert report.exists()
