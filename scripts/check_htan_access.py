from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import sys

import pandas as pd


OUT = Path("data/processed/spatial_emt_niche_gnn_htan")
DECONV_PYTHON = Path(".venv-deconv/Scripts/python.exe")
HTAN_EXE = Path(".venv-deconv/Scripts/htan.exe")
R46 = Path("C:/Program Files/R/R-4.6.0/bin/Rscript.exe")


def run(args: list[str], timeout: int = 60) -> tuple[bool, str]:
    try:
        result = subprocess.run(args, check=False, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return False, f"timeout_after_{timeout}s"
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}"
    output = (result.stdout + "\n" + result.stderr).strip()
    return result.returncode == 0, output[:800]


def check_synapse(python_exe: Path | str) -> dict[str, object]:
    code = (
        "import json, synapseclient\n"
        "status={'synapseclient_version': synapseclient.__version__}\n"
        "syn=synapseclient.Synapse()\n"
        "try:\n"
        "    syn.login(silent=True); profile=syn.getUserProfile(); "
        "    status.update({'logged_in': True, 'owner_id': profile.get('ownerId','')})\n"
        "except Exception as exc:\n"
        "    status.update({'logged_in': False, 'error': type(exc).__name__ + ': ' + str(exc)[:250]})\n"
        "print(json.dumps(status))"
    )
    ok, output = run([str(python_exe), "-c", code], timeout=90)
    return {
        "resource": "Synapse client and login",
        "tool": "synapseclient",
        "available": ok and "synapseclient_version" in output,
        "authenticated": '"logged_in": true' in output.lower(),
        "evidence": output,
        "next_action": (
            "Use HTAN portal selected-file Synapse IDs and download with synapseclient."
            if '"logged_in": true' in output.lower()
            else "Run `synapse login` or set Synapse credentials, then rerun this check."
        ),
    }


def check_gen3() -> dict[str, object]:
    gen3 = shutil.which("gen3-client") or shutil.which("gen3-client.exe")
    cred = os.environ.get("GEN3_CREDENTIALS_JSON", "")
    return {
        "resource": "Gen3 client and credentials",
        "tool": "gen3-client",
        "available": bool(gen3),
        "authenticated": bool(cred and Path(cred).exists()),
        "evidence": gen3 or "gen3-client not found on PATH",
        "next_action": (
            "Configure HTAN/CRDC profile and run the portal-generated gen3-client command."
            if gen3 and cred
            else "Install Gen3 client and configure the portal-generated profile only for controlled/CRDC files."
        ),
    }


def check_htan_cli() -> dict[str, object]:
    htan_exe = HTAN_EXE if HTAN_EXE.exists() else shutil.which("htan")
    if not htan_exe:
        return {
            "resource": "HTAN CLI",
            "tool": "htan",
            "available": False,
            "authenticated": False,
            "evidence": "htan command not found",
            "next_action": "Install with `.venv-deconv\\Scripts\\python.exe -m pip install htan`.",
        }
    ok, output = run([str(htan_exe), "config", "check"], timeout=60)
    return {
        "resource": "HTAN CLI",
        "tool": "htan",
        "available": ok,
        "authenticated": '"configured": true' in output.lower(),
        "evidence": output,
        "next_action": "Configure HTAN portal/Synapse/Gen3 credentials after selected HTAN files are known.",
    }


def main() -> None:
    python_exe = DECONV_PYTHON if DECONV_PYTHON.exists() else Path(sys.executable)
    rows = [
        check_htan_cli(),
        check_synapse(python_exe),
        check_gen3(),
        {
            "resource": "HTAN WUSTL PDAC target manifest",
            "tool": "local manifest",
            "available": Path("data/processed/spatial_emt_niche_gnn_htan/htan_wustl_pdac_manifest.tsv").exists(),
            "authenticated": False,
            "evidence": "data/processed/spatial_emt_niche_gnn_htan/htan_wustl_pdac_manifest.tsv",
            "next_action": "Select one open-access Level 3/4 spatial assay file in the HTAN portal and use its Synapse/Gen3 instructions.",
        },
    ]
    OUT.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT / "htan_access_status.tsv", sep="\t", index=False)
    print(f"Wrote {OUT / 'htan_access_status.tsv'}")


if __name__ == "__main__":
    main()
