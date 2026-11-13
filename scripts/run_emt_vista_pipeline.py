from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import yaml


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Run the complete EMT-ViSTA MVP workflow.")
    p.add_argument("--config", default="configs/emt_virtual_spatial_staining.yml")
    p.add_argument("--backend", choices=["handcrafted", "resnet50", "phikon_v2", "h_optimus_0"])
    p.add_argument("--max-spots-per-dataset", type=int)
    return p


def run(command: list[str]) -> None:
    print("+", " ".join(command), flush=True)
    subprocess.run(command, check=True)


def main() -> None:
    args = parser().parse_args()
    config = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    out_dir = Path(config["output_dir"])
    backend = args.backend or config["image"]["backend"]
    python = sys.executable
    pairs = out_dir / "virtual_stain_training_pairs.tsv"
    embeddings = out_dir / f"pathology_embeddings_{backend}.tsv"
    model_dir = out_dir / backend

    run([python, "scripts/09_build_virtual_stain_training_pairs.py", "--config", args.config, "--out-dir", str(out_dir)])
    command = [
        python,
        "scripts/10_extract_pathology_embeddings.py",
        "--pairs",
        str(pairs),
        "--out-dir",
        str(out_dir),
        "--backend",
        backend,
        "--tile-px",
        str(config["image"]["tile_px"]),
        "--context-px",
        str(config["image"]["context_px"]),
        "--batch-size",
        str(config["image"]["batch_size"]),
    ]
    if args.max_spots_per_dataset:
        command.extend(["--max-spots-per-dataset", str(args.max_spots_per_dataset)])
    run(command)
    common = [
        "--pairs",
        str(pairs),
        "--embeddings",
        str(embeddings),
        "--out-dir",
        str(model_dir),
        "--alpha",
        str(config["model"]["alpha"]),
        "--models",
        str(config["model"]["n_models"]),
        "--components",
        str(config["model"]["max_components"]),
    ]
    run([python, "scripts/11_train_virtual_stain_baselines.py", *common])
    run(
        [
            python,
            "scripts/12_train_emt_vista_multitask.py",
            *common,
            "--k-neighbors",
            str(config["model"]["k_neighbors"]),
        ]
    )
    run(
        [
            python,
            "scripts/15_export_virtual_stain_maps.py",
            "--predictions",
            str(model_dir / "emt_vista_predictions.tsv"),
            "--out-dir",
            str(model_dir / "maps"),
        ]
    )
    run(
        [
            python,
            "scripts/16_generate_emt_vista_paper_figures.py",
            "--metrics",
            str(model_dir / "emt_vista_metrics.tsv"),
            "--predictions",
            str(model_dir / "emt_vista_predictions.tsv"),
            "--pairs",
            str(pairs),
            "--out-dir",
            str(model_dir / "paper"),
        ]
    )


if __name__ == "__main__":
    main()
