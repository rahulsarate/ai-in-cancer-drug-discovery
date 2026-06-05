from __future__ import annotations

import math

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
        return run_median_split_logrank(frame, score_columns, time_col=time_col, event_col=event_col)

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


def run_median_split_logrank(
    frame: pd.DataFrame,
    score_columns: list[str],
    time_col: str = "time",
    event_col: str = "event",
) -> pd.DataFrame:
    """Fallback survival screen when lifelines is unavailable."""
    rows = []
    for score in score_columns:
        data = frame[[time_col, event_col, score]].dropna()
        data[time_col] = pd.to_numeric(data[time_col], errors="coerce")
        data[event_col] = pd.to_numeric(data[event_col], errors="coerce")
        data = data.dropna()
        if len(data) < 20 or data[event_col].sum() < 5:
            continue

        median = data[score].median()
        data["group"] = data[score] >= median
        if data["group"].nunique() < 2:
            continue
        stat, p = logrank_statistic(data, time_col, event_col, "group")
        high = data[data["group"]]
        low = data[~data["group"]]
        rows.append(
            {
                "score": score,
                "method": "median_split_logrank_fallback",
                "n": len(data),
                "events": int(data[event_col].sum()),
                "high_group_median_time": float(high[time_col].median()),
                "low_group_median_time": float(low[time_col].median()),
                "logrank_chi2": stat,
                "p": p,
            }
        )
    return pd.DataFrame(rows)


def logrank_statistic(data: pd.DataFrame, time_col: str, event_col: str, group_col: str) -> tuple[float, float]:
    observed = expected = variance = 0.0
    event_times = sorted(data.loc[data[event_col] == 1, time_col].unique())
    for time in event_times:
        at_risk = data[data[time_col] >= time]
        events = data[(data[time_col] == time) & (data[event_col] == 1)]
        n = len(at_risk)
        n1 = int(at_risk[group_col].sum())
        d = len(events)
        d1 = int(events[group_col].sum())
        if n <= 1:
            continue
        observed += d1
        expected += d * n1 / n
        variance += n1 * (n - n1) * d * (n - d) / (n * n * (n - 1))
    if variance <= 0:
        return 0.0, 1.0
    chi2 = (observed - expected) ** 2 / variance
    p = math.erfc(math.sqrt(chi2 / 2))
    return float(chi2), float(p)
