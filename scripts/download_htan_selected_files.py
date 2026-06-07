from __future__ import annotations

import argparse
from pathlib import Path
import subprocess

import pandas as pd


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Download HTAN selected files after portal file IDs and credentials are configured.")
    p.add_argument("--manifest", default="data/processed/spatial_emt_niche_gnn_htan/htan_selected_file_manifest_template.tsv")
    p.add_argument("--out-dir", default="data/processed/spatial_emt_niche_gnn_htan")
    p.add_argument("--execute", action="store_true", help="Run download commands. Default writes a dry-run status table.")
    return p


def run(args: list[str], timeout: int = 300) -> tuple[bool, str]:
    try:
        result = subprocess.run(args, capture_output=True, text=True, check=False, timeout=timeout)
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}"
    return result.returncode == 0, (result.stdout + "\n" + result.stderr).strip()[:1000]


def download_row(row: pd.Series, execute: bool) -> dict[str, object]:
    synapse = str(row.get("synapse_id", "")).strip()
    gen3 = str(row.get("gen3_guid", "")).strip()
    target = Path(str(row.get("local_target_dir", "data/raw/spatial/htan/wustl_pdac/unknown")))
    result = row.to_dict()
    result["attempted"] = False
    result["success"] = False
    result["command"] = ""
    result["evidence"] = ""
    if not synapse and not gen3:
        result["evidence"] = "No Synapse ID or Gen3 GUID filled in."
        result["next_action"] = "Export selected file IDs from the HTAN portal."
        return result
    if synapse:
        command = [".venv-deconv/Scripts/synapse.exe", "get", synapse, "--downloadLocation", str(target)]
    else:
        command = [".venv-deconv/Scripts/gen3.exe", "drs-pull", "object", gen3, "--output-dir", str(target)]
    result["command"] = " ".join(command)
    if not execute:
        result["evidence"] = "dry_run"
        result["next_action"] = "Rerun with --execute after credentials are configured."
        return result
    target.mkdir(parents=True, exist_ok=True)
    ok, output = run(command)
    result["attempted"] = True
    result["success"] = ok
    result["evidence"] = output
    result["next_action"] = "Standardize downloaded files." if ok else "Check credentials/file access and rerun."
    return result


def main() -> None:
    args = parser().parse_args()
    manifest = Path(args.manifest)
    if not manifest.exists():
        raise SystemExit(f"Missing manifest: {manifest}")
    rows = pd.read_csv(manifest, sep="\t").fillna("")
    status = pd.DataFrame([download_row(row, args.execute) for _, row in rows.iterrows()])
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    status.to_csv(out / "htan_selected_file_download_status.tsv", sep="\t", index=False)
    print(f"Wrote {out / 'htan_selected_file_download_status.tsv'}")


if __name__ == "__main__":
    main()
