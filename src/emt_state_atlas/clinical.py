from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from .reports import table_to_markdown

SCORE_COLUMNS = [
    "emt_score",
    "partial_emt_score",
    "stromal_contamination_risk",
    "immune_context",
    "caf_tam_niche",
    "hypoxia",
    "ferroptosis_window",
]


def simplify_stage(value: object) -> str:
    text = str(value).upper().strip()
    if not text or text in {"NAN", "NONE"}:
        return "unknown"
    for stage in ["IV", "III", "II", "I"]:
        if f"STAGE {stage}" in text or text == stage:
            return f"stage_{stage.lower()}"
    return "other_stage"


def simplify_grade(value: object) -> str:
    text = str(value).upper().strip()
    if not text or text in {"NAN", "NONE"}:
        return "unknown"
    for grade in ["G4", "G3", "G2", "G1"]:
        if grade in text:
            return grade.lower()
    if "HIGH" in text:
        return "high_grade"
    if "LOW" in text:
        return "low_grade"
    return "other_grade"


def simplify_treatment_outcome(value: object) -> str:
    text = str(value).upper().strip()
    if not text or text in {"NAN", "NONE"}:
        return "unknown"
    if "COMPLETE" in text or "REMISSION" in text:
        return "complete_response"
    if "PARTIAL" in text:
        return "partial_response"
    if "STABLE" in text:
        return "stable_disease"
    if "PROGRESS" in text:
        return "progressive_disease"
    return "other_treatment_outcome"


def simplify_residual_tumor(value: object) -> str:
    text = str(value).upper().strip()
    if not text or text in {"NAN", "NONE"}:
        return "unknown"
    if text in {"R0", "RX"} or "NO RESIDUAL" in text:
        return "no_or_unknown_residual"
    if text in {"R1", "R2"} or "RESIDUAL" in text:
        return "residual_tumor"
    return "other_residual_status"


def available_score_columns(frame: pd.DataFrame) -> list[str]:
    return [col for col in SCORE_COLUMNS if col in frame.columns and pd.api.types.is_numeric_dtype(frame[col])]


def clinical_group_summary(scores: pd.DataFrame, group_col: str = "cancer_group") -> pd.DataFrame:
    if group_col not in scores.columns:
        return pd.DataFrame()
    frame = scores.copy()
    for col in ["event", "time", "is_metastatic"]:
        if col in frame.columns:
            frame[col] = pd.to_numeric(frame[col], errors="coerce")

    rows = []
    for group, group_frame in frame.groupby(group_col, dropna=False):
        n = len(group_frame)
        events = int(group_frame["event"].sum()) if "event" in group_frame.columns else 0
        row = {
            group_col: group,
            "sample_count": n,
            "survival_events": events,
            "event_fraction": events / n if n else pd.NA,
            "median_followup_time": group_frame["time"].median() if "time" in group_frame.columns else pd.NA,
            "high_confidence_fraction": group_frame["confidence_label"].eq("high").mean()
            if "confidence_label" in group_frame.columns
            else pd.NA,
            "stromal_warning_fraction": group_frame["stromal_warning"].mean() if "stromal_warning" in group_frame.columns else pd.NA,
            "stage_available_fraction": group_frame["ajcc_pathologic_tumor_stage"].notna().mean()
            if "ajcc_pathologic_tumor_stage" in group_frame.columns
            else pd.NA,
            "grade_available_fraction": group_frame["histological_grade"].notna().mean()
            if "histological_grade" in group_frame.columns
            else pd.NA,
            "metastasis_available_fraction": group_frame["is_metastatic"].notna().mean()
            if "is_metastatic" in group_frame.columns
            else pd.NA,
            "treatment_outcome_available_fraction": group_frame["treatment_outcome_first_course"].notna().mean()
            if "treatment_outcome_first_course" in group_frame.columns
            else pd.NA,
            "residual_tumor_available_fraction": group_frame["residual_tumor"].notna().mean()
            if "residual_tumor" in group_frame.columns
            else pd.NA,
            "metastatic_fraction": group_frame["is_metastatic"].mean() if "is_metastatic" in group_frame.columns else pd.NA,
        }
        for score_col in available_score_columns(group_frame):
            row[f"{score_col}_mean"] = group_frame[score_col].mean()
        rows.append(row)
    return pd.DataFrame(rows).sort_values(["sample_count", group_col], ascending=[False, True]).reset_index(drop=True)


def survival_by_stratum(scores: pd.DataFrame, group_col: str = "cancer_group", min_n: int = 30, min_events: int = 5) -> pd.DataFrame:
    if group_col not in scores.columns or "time" not in scores.columns or "event" not in scores.columns:
        return pd.DataFrame()
    rows = []
    for group, group_frame in scores.groupby(group_col, dropna=False):
        data = group_frame.copy()
        data["time"] = pd.to_numeric(data["time"], errors="coerce")
        data["event"] = pd.to_numeric(data["event"], errors="coerce")
        complete = data.dropna(subset=["time", "event"])
        n = len(complete)
        events = int(complete["event"].sum()) if n else 0
        if n < min_n or events < min_events:
            rows.append(
                {
                    group_col: group,
                    "score": "all",
                    "method": "not_run_underpowered",
                    "n": n,
                    "events": events,
                    "warning": f"Needs at least {min_n} samples and {min_events} events.",
                }
            )
            continue
        for score in available_score_columns(complete):
            data = complete[["time", "event", score]].dropna()
            if len(data) < min_n or data["event"].sum() < min_events or data[score].nunique() < 2:
                continue
            median = data[score].median()
            high = data[data[score] >= median]
            low = data[data[score] < median]
            if high.empty or low.empty:
                continue
            high_event_fraction = float(high["event"].mean())
            low_event_fraction = float(low["event"].mean())
            relative_event_rate = (high_event_fraction + 1e-9) / (low_event_fraction + 1e-9)
            rows.append(
                {
                    group_col: group,
                    "score": score,
                    "method": "median_split_event_rate_screen",
                    "n": len(data),
                    "events": int(data["event"].sum()),
                    "high_group_event_fraction": high_event_fraction,
                    "low_group_event_fraction": low_event_fraction,
                    "relative_event_rate": relative_event_rate,
                    "high_group_median_time": float(high["time"].median()),
                    "low_group_median_time": float(low["time"].median()),
                    "warning": "",
                }
            )
    return pd.DataFrame(rows)


def covariate_adjusted_event_screen(
    scores: pd.DataFrame,
    group_col: str = "cancer_group",
    min_n: int = 40,
    min_events: int = 8,
) -> pd.DataFrame:
    if group_col not in scores.columns or "event" not in scores.columns:
        return pd.DataFrame()
    frame = scores.copy()
    frame["event"] = pd.to_numeric(frame["event"], errors="coerce")
    frame["stage_simplified"] = (
        frame["ajcc_pathologic_tumor_stage"].map(simplify_stage)
        if "ajcc_pathologic_tumor_stage" in frame.columns
        else "unknown"
    )
    frame["grade_simplified"] = (
        frame["histological_grade"].map(simplify_grade) if "histological_grade" in frame.columns else "unknown"
    )
    if "is_metastatic" in frame.columns:
        frame["metastasis_simplified"] = frame["is_metastatic"].map(lambda value: "metastatic" if str(value) == "1.0" or value == 1 else "not_metastatic_or_unknown")
    else:
        frame["metastasis_simplified"] = "unknown"
    frame["treatment_outcome_simplified"] = (
        frame["treatment_outcome_first_course"].map(simplify_treatment_outcome)
        if "treatment_outcome_first_course" in frame.columns
        else "unknown"
    )
    frame["residual_tumor_simplified"] = (
        frame["residual_tumor"].map(simplify_residual_tumor) if "residual_tumor" in frame.columns else "unknown"
    )

    strata_cols = [
        "stage_simplified",
        "grade_simplified",
        "metastasis_simplified",
        "treatment_outcome_simplified",
        "residual_tumor_simplified",
    ]
    rows = []
    for group, group_frame in frame.groupby(group_col, dropna=False):
        complete = group_frame.dropna(subset=["event"])
        if len(complete) < min_n or complete["event"].sum() < min_events:
            rows.append(
                {
                    group_col: group,
                    "score": "all",
                    "method": "not_run_underpowered_covariate_screen",
                    "n": len(complete),
                    "events": int(complete["event"].sum()) if not complete.empty else 0,
                    "covariates": ",".join(strata_cols),
                    "warning": f"Needs at least {min_n} samples and {min_events} events.",
                }
            )
            continue
        for score in available_score_columns(complete):
            data = complete[[score, "event", *strata_cols]].dropna(subset=[score, "event"])
            if data[score].nunique() < 2:
                continue
            median = data[score].median()
            data = data.copy()
            data["score_high"] = data[score] >= median
            strata_rows = []
            for strata, part in data.groupby(strata_cols, dropna=False):
                high = part[part["score_high"]]
                low = part[~part["score_high"]]
                if len(high) < 2 or len(low) < 2:
                    continue
                strata_rows.append(
                    {
                        "strata": strata,
                        "n": len(part),
                        "high_events": high["event"].sum(),
                        "high_n": len(high),
                        "low_events": low["event"].sum(),
                        "low_n": len(low),
                    }
                )
            if not strata_rows:
                continue
            high_events = sum(row["high_events"] for row in strata_rows)
            high_n = sum(row["high_n"] for row in strata_rows)
            low_events = sum(row["low_events"] for row in strata_rows)
            low_n = sum(row["low_n"] for row in strata_rows)
            rows.append(
                {
                    group_col: group,
                    "score": score,
                    "method": "covariate_stratified_median_event_rate_screen",
                    "n": int(high_n + low_n),
                    "events": int(high_events + low_events),
                    "strata_used": len(strata_rows),
                    "covariates": ",".join(strata_cols),
                    "high_group_event_fraction": float(high_events / high_n) if high_n else pd.NA,
                    "low_group_event_fraction": float(low_events / low_n) if low_n else pd.NA,
                    "stratified_relative_event_rate": float((high_events / high_n + 1e-9) / (low_events / low_n + 1e-9))
                    if high_n and low_n
                    else pd.NA,
                    "warning": "screen_only_needs_full_multivariable_cox_validation",
                }
            )
    return pd.DataFrame(rows)


def run_multivariable_cox_models(
    scores: pd.DataFrame,
    group_col: str = "cancer_group",
    min_n: int = 60,
    min_events: int = 10,
    covariates: list[str] | None = None,
) -> pd.DataFrame:
    try:
        from lifelines import CoxPHFitter
    except ImportError as exc:
        return _cox_unavailable_rows(scores, group_col, f"lifelines_not_installed: {exc}")

    if group_col not in scores.columns or "time" not in scores.columns or "event" not in scores.columns:
        return pd.DataFrame()

    covariates = covariates or [
        "age_at_initial_pathologic_diagnosis",
        "gender",
        "stage_simplified",
        "grade_simplified",
        "metastasis_simplified",
        "treatment_outcome_simplified",
        "residual_tumor_simplified",
    ]
    frame = _clinical_model_frame(scores)
    rows: list[dict[str, Any]] = []
    for group, group_frame in frame.groupby(group_col, dropna=False):
        base = group_frame.copy()
        base["time"] = pd.to_numeric(base["time"], errors="coerce")
        base["event"] = pd.to_numeric(base["event"], errors="coerce")
        base = base.dropna(subset=["time", "event"])
        if len(base) < min_n or base["event"].sum() < min_events:
            rows.append(
                {
                    group_col: group,
                    "score": "all",
                    "method": "cox_not_run_underpowered",
                    "n": len(base),
                    "events": int(base["event"].sum()) if not base.empty else 0,
                    "warning": f"Needs at least {min_n} samples and {min_events} events.",
                }
            )
            continue
        for score in available_score_columns(base):
            model_data = _cox_design_matrix(base, score, covariates)
            if model_data.empty or model_data[score].nunique() < 2:
                rows.append(
                    {
                        group_col: group,
                        "score": score,
                        "method": "cox_not_run_no_valid_design",
                        "n": len(model_data),
                        "events": int(model_data["event"].sum()) if "event" in model_data.columns and not model_data.empty else 0,
                        "warning": "No valid Cox design matrix after covariate encoding.",
                    }
                )
                continue
            try:
                cph = CoxPHFitter(penalizer=0.05)
                cph.fit(model_data, duration_col="time", event_col="event")
                summary = cph.summary.loc[score]
                rows.append(
                    {
                        group_col: group,
                        "score": score,
                        "method": "multivariable_cox",
                        "n": len(model_data),
                        "events": int(model_data["event"].sum()),
                        "hazard_ratio": float(summary["exp(coef)"]),
                        "coef": float(summary["coef"]),
                        "p": float(summary["p"]),
                        "concordance": float(cph.concordance_index_),
                        "covariates": ",".join([col for col in model_data.columns if col not in {"time", "event", score}]),
                        "warning": "",
                    }
                )
            except Exception as exc:
                rows.append(
                    {
                        group_col: group,
                        "score": score,
                        "method": "cox_failed",
                        "n": len(model_data),
                        "events": int(model_data["event"].sum()) if "event" in model_data.columns else 0,
                        "warning": f"{type(exc).__name__}: {exc}",
                    }
                )
    return pd.DataFrame(rows)


def association_summary(
    scores: pd.DataFrame,
    group_col: str = "cancer_group",
    category_cols: list[str] | None = None,
) -> pd.DataFrame:
    category_cols = category_cols or ["ajcc_pathologic_tumor_stage", "clinical_stage", "histological_grade", "is_metastatic"]
    rows = []
    score_cols = available_score_columns(scores)
    for category_col in category_cols:
        if category_col not in scores.columns:
            continue
        for (group, category), part in scores.dropna(subset=[category_col]).groupby([group_col, category_col], dropna=False):
            row = {group_col: group, "clinical_feature": category_col, "feature_level": category, "sample_count": len(part)}
            for score_col in score_cols:
                row[f"{score_col}_mean"] = part[score_col].mean()
            rows.append(row)
    return pd.DataFrame(rows)


def clinical_warnings(group_summary: pd.DataFrame, group_col: str = "cancer_group") -> pd.DataFrame:
    rows = []
    if group_summary.empty:
        return pd.DataFrame()
    for _, row in group_summary.iterrows():
        warnings = []
        if row.get("sample_count", 0) < 30:
            warnings.append("underpowered_sample_count")
        if row.get("survival_events", 0) < 5:
            warnings.append("underpowered_survival_events")
        stage_fraction = row.get("stage_available_fraction")
        if pd.notna(stage_fraction) and stage_fraction < 0.5:
            warnings.append("limited_stage_annotation")
        grade_fraction = row.get("grade_available_fraction")
        if pd.notna(grade_fraction) and grade_fraction < 0.5:
            warnings.append("limited_grade_annotation")
        stromal_fraction = row.get("stromal_warning_fraction")
        if pd.notna(stromal_fraction) and stromal_fraction > 0.35:
            warnings.append("high_stromal_inflation_risk")
        if not warnings:
            warnings.append("usable_with_standard_research_caution")
        rows.append({group_col: row[group_col], "warnings": ";".join(warnings)})
    return pd.DataFrame(rows)


def write_clinical_report(
    group_summary: pd.DataFrame,
    survival: pd.DataFrame,
    covariate_screen: pd.DataFrame,
    cox_models: pd.DataFrame,
    associations: pd.DataFrame,
    warnings: pd.DataFrame,
    out_path: str | Path,
) -> Path:
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    survival_display = survival.copy()
    if "p" in survival_display.columns:
        survival_display = survival_display.sort_values("p", na_position="last")
    assoc_display = associations.sort_values("sample_count", ascending=False).head(40) if not associations.empty else associations
    lines = [
        "# Pan-Cancer EMT Clinical Layer",
        "",
        "This layer links EMT states to survival, stage, grade, and metastasis annotations where TCGA metadata support the comparison.",
        "",
        "## Disease-Group Clinical Readiness",
        "",
        table_to_markdown(group_summary),
        "",
        "## Clinical Warnings",
        "",
        table_to_markdown(warnings),
        "",
        "## Survival Screens",
        "",
        table_to_markdown(survival_display.head(50)) if not survival_display.empty else "No survival screen rows were generated.",
        "",
        "## Covariate-Aware Clinical Screen",
        "",
        table_to_markdown(covariate_screen.head(50)) if not covariate_screen.empty else "No covariate-aware screen rows were generated.",
        "",
        "## Full Multivariable Cox Models",
        "",
        table_to_markdown(_sort_model_table(cox_models).head(80)) if not cox_models.empty else "No Cox model rows were generated.",
        "",
        "## Stage, Grade, and Metastasis Associations",
        "",
        table_to_markdown(assoc_display) if not assoc_display.empty else "No stage, grade, or metastasis association rows were available.",
        "",
        "## Interpretation Boundary",
        "",
        "These are association screens, not treatment rules. Any clinical use needs cancer-specific modeling, covariates, independent validation, and pathology review.",
    ]
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


def _clinical_model_frame(scores: pd.DataFrame) -> pd.DataFrame:
    frame = scores.copy()
    frame["stage_simplified"] = (
        frame["ajcc_pathologic_tumor_stage"].map(simplify_stage)
        if "ajcc_pathologic_tumor_stage" in frame.columns
        else "unknown"
    )
    frame["grade_simplified"] = (
        frame["histological_grade"].map(simplify_grade) if "histological_grade" in frame.columns else "unknown"
    )
    if "is_metastatic" in frame.columns:
        frame["metastasis_simplified"] = frame["is_metastatic"].map(
            lambda value: "metastatic" if str(value) == "1.0" or value == 1 else "not_metastatic_or_unknown"
        )
    else:
        frame["metastasis_simplified"] = "unknown"
    frame["treatment_outcome_simplified"] = (
        frame["treatment_outcome_first_course"].map(simplify_treatment_outcome)
        if "treatment_outcome_first_course" in frame.columns
        else "unknown"
    )
    frame["residual_tumor_simplified"] = (
        frame["residual_tumor"].map(simplify_residual_tumor) if "residual_tumor" in frame.columns else "unknown"
    )
    return frame


def _cox_design_matrix(frame: pd.DataFrame, score: str, covariates: list[str]) -> pd.DataFrame:
    cols = ["time", "event", score, *[col for col in covariates if col in frame.columns]]
    data = frame[cols].copy()
    data["time"] = pd.to_numeric(data["time"], errors="coerce")
    data["event"] = pd.to_numeric(data["event"], errors="coerce")
    data[score] = pd.to_numeric(data[score], errors="coerce")
    data = data.dropna(subset=["time", "event", score])
    if data.empty:
        return data
    numeric_covs = []
    categorical_covs = []
    for covariate in [col for col in covariates if col in data.columns]:
        if covariate == score:
            continue
        if pd.api.types.is_numeric_dtype(data[covariate]):
            data[covariate] = pd.to_numeric(data[covariate], errors="coerce")
            numeric_covs.append(covariate)
        else:
            categorical_covs.append(covariate)
    for col in [score, *numeric_covs]:
        sd = data[col].std()
        if pd.notna(sd) and sd > 0:
            data[col] = (data[col] - data[col].mean()) / sd
    encoded = pd.get_dummies(data[["time", "event", score, *numeric_covs, *categorical_covs]], columns=categorical_covs, drop_first=True, dtype=float)
    keep = ["time", "event"]
    for col in encoded.columns:
        if col in keep:
            continue
        if encoded[col].nunique(dropna=True) > 1:
            keep.append(col)
    if score not in keep:
        keep.append(score)
    return encoded[keep].dropna()


def _cox_unavailable_rows(scores: pd.DataFrame, group_col: str, warning: str) -> pd.DataFrame:
    if group_col not in scores.columns:
        return pd.DataFrame([{"score": "all", "method": "cox_not_run_dependency_missing", "warning": warning}])
    rows = []
    for group, part in scores.groupby(group_col, dropna=False):
        rows.append(
            {
                group_col: group,
                "score": "all",
                "method": "cox_not_run_dependency_missing",
                "n": len(part),
                "events": int(pd.to_numeric(part.get("event", pd.Series(dtype=float)), errors="coerce").sum()),
                "warning": warning,
            }
        )
    return pd.DataFrame(rows)


def _sort_model_table(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return frame
    if "p" in frame.columns:
        return frame.sort_values("p", na_position="last")
    return frame
