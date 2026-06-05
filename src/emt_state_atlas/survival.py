from __future__ import annotations

import pandas as pd


def run_univariate_survival(
    frame: pd.DataFrame,
    score_columns: list[str],
    time_col: str = "time",
    event_col: str = "event",
) -> pd.DataFrame:
    """Run Cox proportional hazard models when lifelines is installed."""
    try:
        from lifelines import CoxPHFitter
    except ImportError as exc:
        raise RuntimeError("Install lifelines or use `pip install -e .[survival]`.") from exc

    rows = []
    for score in score_columns:
        cols = [time_col, event_col, score]
        data = frame[cols].dropna()
        if data[event_col].nunique() < 2 or len(data) < 20:
            continue
        model = CoxPHFitter()
        model.fit(data, duration_col=time_col, event_col=event_col)
        summary = model.summary.loc[score]
        rows.append(
            {
                "score": score,
                "n": len(data),
                "hazard_ratio": float(summary["exp(coef)"]),
                "p": float(summary["p"]),
                "concordance": float(model.concordance_index_),
            }
        )
    return pd.DataFrame(rows)

