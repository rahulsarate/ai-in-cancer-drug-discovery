from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
CALIBRATED_PARAM_NAMES = ["aEH", "aHE", "aHM", "aEP", "aHP", "aPH", "kE", "kH", "kM", "kP"]


ARCHETYPES = {
    "chemo_sensitive_epithelial": {
        "initial": {"E": 0.72, "H": 0.17, "M": 0.06, "P": 0.05},
        "rates": {"rE": 0.050, "rH": 0.030, "rM": 0.022, "rP": 0.006},
        "kill": {"kE": 0.130, "kH": 0.060, "kM": 0.025, "kP": 0.010},
        "transitions": {"aEH": 0.010, "aHE": 0.018, "aHM": 0.006, "aEP": 0.004, "aHP": 0.003, "aPH": 0.004},
        "persister_layers": {"tumor": 0.20, "stress": 0.15, "niche": 0.10},
    },
    "plastic_residual_risk": {
        "initial": {"E": 0.40, "H": 0.34, "M": 0.14, "P": 0.12},
        "rates": {"rE": 0.042, "rH": 0.037, "rM": 0.026, "rP": 0.008},
        "kill": {"kE": 0.105, "kH": 0.038, "kM": 0.017, "kP": 0.006},
        "transitions": {"aEH": 0.026, "aHE": 0.006, "aHM": 0.018, "aEP": 0.010, "aHP": 0.012, "aPH": 0.007},
        "persister_layers": {"tumor": 0.55, "stress": 0.45, "niche": 0.35},
    },
    "mesenchymal_persister_high": {
        "initial": {"E": 0.24, "H": 0.30, "M": 0.26, "P": 0.20},
        "rates": {"rE": 0.035, "rH": 0.033, "rM": 0.030, "rP": 0.010},
        "kill": {"kE": 0.095, "kH": 0.028, "kM": 0.012, "kP": 0.004},
        "transitions": {"aEH": 0.030, "aHE": 0.004, "aHM": 0.024, "aEP": 0.012, "aHP": 0.016, "aPH": 0.010},
        "persister_layers": {"tumor": 0.85, "stress": 0.75, "niche": 0.60},
    },
}


def load_calibrated_params(path: Path | None) -> dict[str, float] | None:
    if path is None or not path.exists():
        return None
    df = pd.read_csv(path, sep="\t")
    if df.empty:
        return None
    row = df.iloc[0]
    return {name: float(row[name]) for name in CALIBRATED_PARAM_NAMES if name in row}


def scale_calibrated_params(params: dict[str, float], days: int) -> tuple[dict[str, float], dict[str, float]]:
    interval = max(float(days), 1.0)
    transitions = {name: params[name] / interval for name in ["aEH", "aHE", "aHM", "aEP", "aHP", "aPH"] if name in params}
    kill = {name: params[name] / interval for name in ["kE", "kH", "kM", "kP"] if name in params}
    return transitions, kill


def blend_dicts(base: dict[str, float], calibrated: dict[str, float], weight: float) -> dict[str, float]:
    out = dict(base)
    for key, value in calibrated.items():
        out[key] = (1.0 - weight) * out.get(key, value) + weight * value
    return out


def apply_persister_layers(
    rates: dict[str, float],
    kill: dict[str, float],
    transitions: dict[str, float],
    layers: dict[str, float],
) -> tuple[dict[str, float], dict[str, float], dict[str, float]]:
    rates = dict(rates)
    kill = dict(kill)
    transitions = dict(transitions)
    tumor = float(layers.get("tumor", 0.0))
    stress = float(layers.get("stress", 0.0))
    niche = float(layers.get("niche", 0.0))
    induction = 1.0 + 0.25 * tumor + 0.18 * stress + 0.12 * niche
    transitions["aEP"] *= induction
    transitions["aHP"] *= induction
    transitions["aPH"] *= max(0.35, 1.0 - 0.18 * stress)
    rates["rP"] *= 1.0 + 0.12 * tumor + 0.08 * niche
    kill["kP"] *= max(0.25, 1.0 - 0.30 * stress - 0.12 * niche)
    kill["kH"] *= max(0.45, 1.0 - 0.10 * tumor)
    return rates, kill, transitions


def step(state: np.ndarray, rates: dict[str, float], kill: dict[str, float], transitions: dict[str, float], therapy_on: bool, dt: float) -> np.ndarray:
    E, H, M, P = state
    total = max(float(state.sum()), 1e-12)
    carrying = max(0.0, 1.0 - total)
    therapy = 1.0 if therapy_on else 0.0

    dE = rates["rE"] * E * carrying - therapy * kill["kE"] * E - transitions["aEH"] * E + transitions["aHE"] * H - transitions["aEP"] * E
    dH = (
        rates["rH"] * H * carrying
        - therapy * kill["kH"] * H
        + transitions["aEH"] * E
        - transitions["aHE"] * H
        - transitions["aHM"] * H
        - transitions["aHP"] * H
        + transitions["aPH"] * P
    )
    dM = rates["rM"] * M * carrying - therapy * kill["kM"] * M + transitions["aHM"] * H
    dP = rates["rP"] * P * carrying - therapy * kill["kP"] * P + transitions["aEP"] * E + transitions["aHP"] * H - transitions["aPH"] * P
    next_state = state + dt * np.array([dE, dH, dM, dP])
    return np.clip(next_state, 0.0, None)


def simulate(
    archetype: str,
    days: int,
    dt: float,
    cycle_days: int,
    calibrated_params: dict[str, float] | None = None,
    calibrated_weight: float = 0.0,
    parameter_set: str = "baseline",
) -> pd.DataFrame:
    config = ARCHETYPES[archetype]
    state = np.array([config["initial"][key] for key in ["E", "H", "M", "P"]], dtype=float)
    rates = dict(config["rates"])
    kill = dict(config["kill"])
    transitions = dict(config["transitions"])
    if calibrated_params:
        calibrated_transitions, calibrated_kill = scale_calibrated_params(calibrated_params, days)
        transitions = blend_dicts(transitions, calibrated_transitions, calibrated_weight)
        kill = blend_dicts(kill, calibrated_kill, calibrated_weight)
    rates, kill, transitions = apply_persister_layers(rates, kill, transitions, config.get("persister_layers", {}))
    rows = []
    for day in np.arange(0, days + dt, dt):
        total = float(state.sum())
        fractions = state / total if total > 0 else np.zeros_like(state)
        therapy_on = int(day // cycle_days) < int(days // cycle_days)
        rows.append(
            {
                "archetype": archetype,
                "parameter_set": parameter_set,
                "day": round(float(day), 3),
                "cycle": int(day // cycle_days) + 1,
                "therapy_on": therapy_on,
                "tumor_burden": total,
                "E": state[0],
                "H": state[1],
                "M": state[2],
                "P": state[3],
                "epithelial_fraction_estimate": fractions[0],
                "hybrid_fraction_estimate": fractions[1],
                "mesenchymal_fraction_estimate": fractions[2],
                "persister_fraction_estimate": fractions[3],
                "plasticity_index": fractions[1] + fractions[3],
                "resistant_fraction": fractions[1] + fractions[2] + fractions[3],
                "tumor_persister_layer": config.get("persister_layers", {}).get("tumor", 0.0),
                "stress_tolerance_layer": config.get("persister_layers", {}).get("stress", 0.0),
                "persister_niche_layer": config.get("persister_layers", {}).get("niche", 0.0),
            }
        )
        state = step(state, rates, kill, transitions, therapy_on=therapy_on, dt=dt)
    return pd.DataFrame(rows)


def summarize(sim: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for archetype, group in sim.groupby("archetype"):
        first = group.iloc[0]
        last = group.iloc[-1]
        rows.append(
            {
                "archetype": archetype,
                "initial_tumor_burden": first["tumor_burden"],
                "final_tumor_burden": last["tumor_burden"],
                "tumor_burden_ratio": last["tumor_burden"] / max(first["tumor_burden"], 1e-12),
                "initial_resistant_fraction": first["resistant_fraction"],
                "final_resistant_fraction": last["resistant_fraction"],
                "emt_shift_delta": (last["hybrid_fraction_estimate"] + last["mesenchymal_fraction_estimate"]) - (first["hybrid_fraction_estimate"] + first["mesenchymal_fraction_estimate"]),
                "persister_delta": last["persister_fraction_estimate"] - first["persister_fraction_estimate"],
                "therapy_selection_pressure": last["resistant_fraction"] - first["resistant_fraction"],
                "residual_disease_probability_proxy": min(0.99, max(0.01, 0.15 + 0.55 * last["tumor_burden"] + 0.30 * last["resistant_fraction"])),
            }
        )
    return pd.DataFrame(rows)


def simulate_uncertainty(
    days: int,
    dt: float,
    cycle_days: int,
    calibrated_params: dict[str, float],
    samples: int,
    seed: int,
    calibrated_weight: float,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    frames = []
    final_rows = []
    for run in range(samples):
        sampled = {
            key: max(0.0001, value * float(rng.lognormal(mean=0.0, sigma=0.22)))
            for key, value in calibrated_params.items()
        }
        for archetype in ARCHETYPES:
            sim = simulate(
                archetype,
                days=days,
                dt=dt,
                cycle_days=cycle_days,
                calibrated_params=sampled,
                calibrated_weight=calibrated_weight,
                parameter_set="calibrated_uncertainty",
            )
            sim["simulation_id"] = run
            frames.append(sim)
            final = sim.iloc[-1].to_dict()
            final["simulation_id"] = run
            final_rows.append(final)
    uncertainty = pd.concat(frames, ignore_index=True)
    final = pd.DataFrame(final_rows)
    metrics = [
        "tumor_burden",
        "epithelial_fraction_estimate",
        "hybrid_fraction_estimate",
        "mesenchymal_fraction_estimate",
        "persister_fraction_estimate",
        "plasticity_index",
        "resistant_fraction",
    ]
    bands = (
        uncertainty.groupby(["archetype", "day"])[metrics]
        .quantile([0.025, 0.5, 0.975])
        .unstack()
        .reset_index()
    )
    bands.columns = [
        "_".join(str(part) for part in col if str(part) != "")
        if isinstance(col, tuple)
        else str(col)
        for col in bands.columns
    ]
    return bands, final


def save_uncertainty_plot(bands: pd.DataFrame, out_path: Path) -> None:
    if bands.empty:
        return
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5), constrained_layout=True)
    for archetype, group in bands.groupby("archetype"):
        group = group.sort_values("day")
        x = group["day"].to_numpy(dtype=float)
        for ax, metric, label in [
            (axes[0], "tumor_burden", "Tumor burden"),
            (axes[1], "persister_fraction_estimate", "Persister fraction"),
        ]:
            median = group[f"{metric}_0.5"].to_numpy(dtype=float)
            low = group[f"{metric}_0.025"].to_numpy(dtype=float)
            high = group[f"{metric}_0.975"].to_numpy(dtype=float)
            ax.plot(x, median, label=archetype.replace("_", " "))
            ax.fill_between(x, low, high, alpha=0.15)
            ax.set_title(label)
            ax.set_xlabel("Day")
    axes[0].set_ylabel("Simulated value")
    axes[1].legend(frameon=False, fontsize=8)
    fig.suptitle("Calibrated transition-prior uncertainty bands", fontsize=13)
    fig.savefig(out_path, dpi=180)
    plt.close(fig)


def write_simulation_report(summary: pd.DataFrame, calibrated_summary: pd.DataFrame, final_uncertainty: pd.DataFrame, image_path: Path | None, out_path: Path) -> None:
    lines = [
        "# TNBC EMT Digital-Twin Therapy Simulation",
        "",
        "## Purpose",
        "",
        "Simulate four EMT/plasticity compartments under neoadjuvant chemotherapy using the original archetypes plus `GSE43816` calibrated transition-rate priors.",
        "",
        "## Baseline Archetype Summary",
        "",
        summary.to_markdown(index=False),
        "",
    ]
    if not calibrated_summary.empty:
        lines.extend(
            [
                "## Calibrated-Prior Summary",
                "",
                calibrated_summary.to_markdown(index=False),
                "",
            ]
        )
    if not final_uncertainty.empty:
        metrics = ["tumor_burden", "persister_fraction_estimate", "plasticity_index", "resistant_fraction"]
        rows = []
        for archetype, group in final_uncertainty.groupby("archetype"):
            row = {"archetype": archetype}
            for metric in metrics:
                row[f"{metric}_median"] = float(group[metric].median())
                row[f"{metric}_q025"] = float(group[metric].quantile(0.025))
                row[f"{metric}_q975"] = float(group[metric].quantile(0.975))
            rows.append(row)
        lines.extend(
            [
                "## Final-State Uncertainty",
                "",
                pd.DataFrame(rows).to_markdown(index=False),
                "",
            ]
        )
    if image_path is not None:
        lines.extend(["## Plot", "", f"![Calibrated uncertainty]({image_path.as_posix()})", ""])
    lines.extend(
        [
            "## Interpretation",
            "",
            "- Calibrated parameters are used as priors, not fixed clinical constants.",
            "- Refined persister layers reduce persister kill and increase therapy-induced entry into the `P` compartment.",
            "- The uncertainty band reflects parameter perturbation around the sparse 7-patient `GSE43816` calibration.",
        ]
    )
    out_path.write_text("\n".join(lines), encoding="utf-8")


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Simulate a four-state TNBC EMT plasticity digital twin.")
    p.add_argument("--out-dir", default="data/processed/tnbc_digital_twin")
    p.add_argument("--days", type=int, default=126, help="Six 21-day NAC cycles by default.")
    p.add_argument("--dt", type=float, default=0.25)
    p.add_argument("--cycle-days", type=int, default=21)
    p.add_argument("--calibration-params", default="data/processed/tnbc_digital_twin/transition_calibration/gse43816_calibrated_transition_parameters.tsv")
    p.add_argument("--calibrated-weight", type=float, default=0.65)
    p.add_argument("--uncertainty-samples", type=int, default=250)
    p.add_argument("--seed", type=int, default=1729)
    p.add_argument("--docs-dir", default="docs/tnbc_digital_twin_emt_plasticity")
    return p


def main() -> None:
    args = parser().parse_args()
    out_dir = ROOT / args.out_dir
    asset_dir = ROOT / args.docs_dir / "assets" / "therapy_simulation"
    out_dir.mkdir(parents=True, exist_ok=True)
    asset_dir.mkdir(parents=True, exist_ok=True)
    calibrated_params = load_calibrated_params(ROOT / args.calibration_params)
    frames = [simulate(name, days=args.days, dt=args.dt, cycle_days=args.cycle_days) for name in ARCHETYPES]
    sim = pd.concat(frames, ignore_index=True)
    summary = summarize(sim)
    calibrated = pd.DataFrame()
    calibrated_summary = pd.DataFrame()
    bands = pd.DataFrame()
    final_uncertainty = pd.DataFrame()
    image_path = None
    if calibrated_params:
        calibrated_frames = [
            simulate(
                name,
                days=args.days,
                dt=args.dt,
                cycle_days=args.cycle_days,
                calibrated_params=calibrated_params,
                calibrated_weight=args.calibrated_weight,
                parameter_set="gse43816_calibrated_prior",
            )
            for name in ARCHETYPES
        ]
        calibrated = pd.concat(calibrated_frames, ignore_index=True)
        calibrated_summary = summarize(calibrated)
        if args.uncertainty_samples > 0:
            bands, final_uncertainty = simulate_uncertainty(
                days=args.days,
                dt=args.dt,
                cycle_days=args.cycle_days,
                calibrated_params=calibrated_params,
                samples=args.uncertainty_samples,
                seed=args.seed,
                calibrated_weight=args.calibrated_weight,
            )
            image_path = asset_dir / "tnbc_calibrated_simulation_uncertainty.png"
            save_uncertainty_plot(bands, image_path)
    sim.to_csv(out_dir / "tnbc_digital_twin_synthetic_trajectories.tsv", sep="\t", index=False)
    summary.to_csv(out_dir / "tnbc_digital_twin_synthetic_summary.tsv", sep="\t", index=False)
    if not calibrated.empty:
        calibrated.to_csv(out_dir / "tnbc_digital_twin_calibrated_prior_trajectories.tsv", sep="\t", index=False)
        calibrated_summary.to_csv(out_dir / "tnbc_digital_twin_calibrated_prior_summary.tsv", sep="\t", index=False)
    if not bands.empty:
        bands.to_csv(out_dir / "tnbc_digital_twin_calibrated_uncertainty_bands.tsv", sep="\t", index=False)
        final_uncertainty.to_csv(out_dir / "tnbc_digital_twin_calibrated_uncertainty_final_states.tsv", sep="\t", index=False)
    (out_dir / "tnbc_digital_twin_archetype_parameters.json").write_text(json.dumps(ARCHETYPES, indent=2), encoding="utf-8")
    write_simulation_report(summary, calibrated_summary, final_uncertainty, image_path, out_dir / "tnbc_digital_twin_therapy_simulation_report.md")
    print(summary.to_string(index=False))
    if not calibrated_summary.empty:
        print(calibrated_summary.to_string(index=False))


if __name__ == "__main__":
    main()
