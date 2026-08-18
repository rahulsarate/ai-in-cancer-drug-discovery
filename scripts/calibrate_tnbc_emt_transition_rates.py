from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import least_squares


ROOT = Path(__file__).resolve().parents[1]

STATES = ["E", "H", "M", "P"]
FRACTION_COLS = {
    "E": "epithelial_fraction_estimate",
    "H": "hybrid_fraction_estimate",
    "M": "mesenchymal_fraction_estimate",
    "P": "persister_fraction_estimate",
}
PARAMS = ["aEH", "aHE", "aHM", "aEP", "aHP", "aPH", "kE", "kH", "kM", "kP"]
PRIOR = {
    "aEH": 0.08,
    "aHE": 0.05,
    "aHM": 0.04,
    "aEP": 0.03,
    "aHP": 0.04,
    "aPH": 0.03,
    "kE": 0.40,
    "kH": 0.20,
    "kM": 0.10,
    "kP": 0.05,
}


def load_pairs(path: Path) -> pd.DataFrame:
    pairs = pd.read_csv(path, sep="\t")
    required = [f"before_{col}" for col in FRACTION_COLS.values()] + [f"after_{col}" for col in FRACTION_COLS.values()]
    missing = [col for col in required if col not in pairs.columns]
    if missing:
        raise SystemExit(f"Missing required paired fraction columns: {', '.join(missing)}")
    return pairs


def vector_from_row(row: pd.Series, prefix: str) -> np.ndarray:
    values = np.array([float(row[f"{prefix}_{FRACTION_COLS[state]}"]) for state in STATES], dtype=float)
    total = values.sum()
    return values / total if total > 0 else np.full(4, 0.25)


def simulate_fraction(initial: np.ndarray, params: dict[str, float], steps: int = 300) -> np.ndarray:
    state = initial.astype(float).copy()
    dt = 1.0 / steps
    for _ in range(steps):
        E, H, M, P = state
        dE = -params["kE"] * E - params["aEH"] * E - params["aEP"] * E + params["aHE"] * H
        dH = (
            -params["kH"] * H
            + params["aEH"] * E
            - params["aHE"] * H
            - params["aHM"] * H
            - params["aHP"] * H
            + params["aPH"] * P
        )
        dM = -params["kM"] * M + params["aHM"] * H
        dP = -params["kP"] * P + params["aEP"] * E + params["aHP"] * H - params["aPH"] * P
        state = np.clip(state + dt * np.array([dE, dH, dM, dP]), 1e-9, None)
    return state / state.sum()


def unpack(x: np.ndarray) -> dict[str, float]:
    return {name: float(value) for name, value in zip(PARAMS, x)}


def objective(x: np.ndarray, initials: np.ndarray, observed: np.ndarray, regularization: float) -> np.ndarray:
    params = unpack(x)
    residuals = []
    for init, obs in zip(initials, observed):
        pred = simulate_fraction(init, params)
        residuals.extend(pred - obs)
    prior_vector = np.array([PRIOR[name] for name in PARAMS], dtype=float)
    residuals.extend(regularization * (np.log1p(x) - np.log1p(prior_vector)))
    return np.array(residuals)


def transition_matrix(params: dict[str, float]) -> pd.DataFrame:
    rows = []
    for source in STATES:
        out = {target: 0.0 for target in STATES}
        if source == "E":
            total = params["aEH"] + params["aEP"]
            out["H"] = params["aEH"] / max(total, 1e-12)
            out["P"] = params["aEP"] / max(total, 1e-12)
        elif source == "H":
            total = params["aHE"] + params["aHM"] + params["aHP"]
            out["E"] = params["aHE"] / max(total, 1e-12)
            out["M"] = params["aHM"] / max(total, 1e-12)
            out["P"] = params["aHP"] / max(total, 1e-12)
        elif source == "P":
            out["H"] = 1.0
        out["source_state"] = source
        rows.append(out)
    return pd.DataFrame(rows)[["source_state"] + STATES]


def save_transition_heatmap(matrix: pd.DataFrame, out_path: Path) -> None:
    values = matrix[STATES].to_numpy(dtype=float)
    fig, ax = plt.subplots(figsize=(5.5, 4.5), constrained_layout=True)
    im = ax.imshow(values, cmap="YlGnBu", vmin=0, vmax=max(1.0, float(np.nanmax(values))))
    ax.set_xticks(range(len(STATES)), STATES)
    ax.set_yticks(range(len(STATES)), matrix["source_state"])
    ax.set_xlabel("Target state")
    ax.set_ylabel("Source state")
    ax.set_title("Calibrated transition allocation")
    for i in range(values.shape[0]):
        for j in range(values.shape[1]):
            ax.text(j, i, f"{values[i, j]:.2f}", ha="center", va="center", fontsize=9)
    fig.colorbar(im, ax=ax, label="Allocation among outgoing transitions")
    fig.savefig(out_path, dpi=180)
    plt.close(fig)


def save_observed_predicted_plot(predictions: pd.DataFrame, out_path: Path) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(8, 7), constrained_layout=True)
    for ax, state in zip(axes.ravel(), STATES):
        ax.scatter(predictions[f"observed_{state}"], predictions[f"predicted_{state}"], color="#4c78a8", s=45)
        lim = [0, max(predictions[f"observed_{state}"].max(), predictions[f"predicted_{state}"].max(), 0.01)]
        ax.plot(lim, lim, color="#777777", linewidth=1)
        ax.set_xlim(lim)
        ax.set_ylim(lim)
        ax.set_title(state)
        ax.set_xlabel("Observed after")
        ax.set_ylabel("Predicted after")
    fig.suptitle("GSE43816 E/H/M/P calibration fit", fontsize=13)
    fig.savefig(out_path, dpi=180)
    plt.close(fig)


def write_report(params: dict[str, float], fit_summary: dict[str, float], matrix: pd.DataFrame, predictions: pd.DataFrame, image_paths: dict[str, Path], out_path: Path) -> None:
    param_table = pd.DataFrame({"parameter": list(params), "value": list(params.values()), "prior": [PRIOR[name] for name in params]})
    lines = [
        "# GSE43816 E/H/M/P Transition Calibration",
        "",
        "## Purpose",
        "",
        "Fit a small regularized transition model that maps pretreatment E/H/M/P fractions to post-NAC fractions in the 7 paired `GSE43816` TNBC patients.",
        "",
        "## Fit Summary",
        "",
        pd.DataFrame([fit_summary]).to_markdown(index=False),
        "",
        "## Calibrated Parameters",
        "",
        param_table.to_markdown(index=False),
        "",
        "## Transition Allocation",
        "",
        matrix.to_markdown(index=False),
        "",
        "## Visual Checks",
        "",
        f"![Transition heatmap]({image_paths['transition_heatmap'].as_posix()})",
        "",
        f"![Observed predicted states]({image_paths['observed_predicted'].as_posix()})",
        "",
        "## Interpretation",
        "",
        "- This is a cohort-level calibration from only 7 paired patients.",
        "- Parameters should be used as priors for simulation, not final clinical constants.",
        "- Because tumor burden is unavailable, this fit targets normalized state fractions, not absolute tumor shrinkage.",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Calibrate E/H/M/P transition rates from GSE43816 paired TNBC NAC samples.")
    p.add_argument("--pairs", default="data/processed/tnbc_digital_twin/gse43816_longitudinal/gse43816_paired_shift_wide.tsv")
    p.add_argument("--out-dir", default="data/processed/tnbc_digital_twin/transition_calibration")
    p.add_argument("--docs-dir", default="docs/tnbc_digital_twin_emt_plasticity")
    p.add_argument("--regularization", type=float, default=0.12)
    return p


def main() -> None:
    args = parser().parse_args()
    out_dir = ROOT / args.out_dir
    asset_dir = ROOT / args.docs_dir / "assets" / "transition_calibration"
    out_dir.mkdir(parents=True, exist_ok=True)
    asset_dir.mkdir(parents=True, exist_ok=True)

    pairs = load_pairs(ROOT / args.pairs)
    initials = np.vstack([vector_from_row(row, "before") for _, row in pairs.iterrows()])
    observed = np.vstack([vector_from_row(row, "after") for _, row in pairs.iterrows()])
    x0 = np.array([PRIOR[name] for name in PARAMS], dtype=float)
    result = least_squares(
        objective,
        x0=x0,
        bounds=(np.full(len(PARAMS), 0.001), np.full(len(PARAMS), 2.0)),
        args=(initials, observed, args.regularization),
        max_nfev=4000,
    )
    params = unpack(result.x)
    predicted = np.vstack([simulate_fraction(init, params) for init in initials])
    rmse = float(np.sqrt(np.mean((predicted - observed) ** 2)))
    fit_summary = {
        "paired_patients": int(pairs.shape[0]),
        "state_fraction_rmse": rmse,
        "optimizer_success": bool(result.success),
        "optimizer_cost": float(result.cost),
    }

    prediction_rows = []
    for i, patient_id in enumerate(pairs["patient_pair_id"].astype(str)):
        row = {"patient_pair_id": patient_id}
        for j, state in enumerate(STATES):
            row[f"before_{state}"] = initials[i, j]
            row[f"observed_{state}"] = observed[i, j]
            row[f"predicted_{state}"] = predicted[i, j]
            row[f"residual_{state}"] = predicted[i, j] - observed[i, j]
        prediction_rows.append(row)
    predictions = pd.DataFrame(prediction_rows)
    matrix = transition_matrix(params)

    pd.DataFrame([params]).to_csv(out_dir / "gse43816_calibrated_transition_parameters.tsv", sep="\t", index=False)
    predictions.to_csv(out_dir / "gse43816_transition_fit_predictions.tsv", sep="\t", index=False)
    matrix.to_csv(out_dir / "gse43816_transition_allocation_matrix.tsv", sep="\t", index=False)
    (out_dir / "gse43816_transition_fit_summary.json").write_text(json.dumps(fit_summary, indent=2), encoding="utf-8")

    image_paths = {
        "transition_heatmap": asset_dir / "gse43816_transition_allocation_heatmap.png",
        "observed_predicted": asset_dir / "gse43816_transition_observed_predicted.png",
    }
    save_transition_heatmap(matrix, image_paths["transition_heatmap"])
    save_observed_predicted_plot(predictions, image_paths["observed_predicted"])
    write_report(params, fit_summary, matrix, predictions, image_paths, out_dir / "gse43816_transition_calibration_report.md")
    print(json.dumps(fit_summary, indent=2))
    print(pd.DataFrame([params]).to_string(index=False))


if __name__ == "__main__":
    main()
