import pandas as pd

from emt_state_atlas.scoring import score_expression


def test_score_expression_detects_mesenchymal_shift():
    expr = pd.DataFrame(
        {
            "CDH1": [10, 10, 2, 2],
            "EPCAM": [9, 9, 2, 2],
            "VIM": [1, 1, 8, 8],
            "FN1": [1, 1, 9, 9],
            "PTPRC": [1, 2, 1, 2],
        },
        index=["epi1", "epi2", "mes1", "mes2"],
    )

    scores = score_expression(expr)
    epi = scores[scores["sample_id"] == "epi1"]["emt_score"].iloc[0]
    mes = scores[scores["sample_id"] == "mes1"]["emt_score"].iloc[0]
    assert mes > epi


def test_partial_emt_requires_epithelial_and_mesenchymal_programs():
    expr = pd.DataFrame(
        {
            "CDH1": [10, 2, 8],
            "EPCAM": [10, 2, 8],
            "VIM": [2, 10, 8],
            "FN1": [2, 10, 8],
        },
        index=["epithelial_only", "mesenchymal_only", "hybrid"],
    )

    scores = score_expression(expr).set_index("sample_id")
    assert scores.loc["hybrid", "partial_emt_score"] > scores.loc["epithelial_only", "partial_emt_score"]
    assert scores.loc["hybrid", "partial_emt_score"] > scores.loc["mesenchymal_only", "partial_emt_score"]
