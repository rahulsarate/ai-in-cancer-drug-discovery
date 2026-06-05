from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.request import Request, urlopen

import pandas as pd

from emt_state_atlas.signatures import SIGNATURES


ROOT = Path(__file__).resolve().parents[1]
L1000FWD_URL = "https://maayanlab.cloud/l1000fwd/"


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Query L1000FWD for EMT-reversing perturbations and map them to target genes.")
    p.add_argument("--dgidb", default="data/raw/api_evidence/dgidb_interactions.tsv")
    p.add_argument("--chembl", default="data/raw/api_evidence/chembl_target_compounds.tsv")
    p.add_argument("--prism", default="data/raw/prism/prism_target_hits.tsv")
    p.add_argument("--raw-out", default="data/raw/lincs/l1000fwd_emt_reversal_signatures.tsv")
    p.add_argument("--out", default="data/raw/lincs/lincs_target_hits.tsv")
    p.add_argument("--top-n", type=int, default=50)
    return p


def post_json(path: str, payload: dict) -> dict:
    request = Request(
        L1000FWD_URL + path,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Accept": "application/json"},
    )
    with urlopen(request, timeout=120) as response:
        return json.loads(response.read().decode("utf-8"))


def get_json(path: str) -> dict:
    request = Request(L1000FWD_URL + path, headers={"Accept": "application/json"})
    with urlopen(request, timeout=120) as response:
        return json.loads(response.read().decode("utf-8"))


def read_optional(path: str) -> pd.DataFrame:
    local = ROOT / path
    if not local.exists():
        return pd.DataFrame()
    return pd.read_csv(local, sep="\t" if local.suffix.lower() != ".csv" else ",")


def normalize_name(value: str) -> str:
    return str(value).strip().upper().replace("-", "").replace("_", "").replace(" ", "")


def compound_target_map(*tables: pd.DataFrame) -> dict[str, set[str]]:
    mapping: dict[str, set[str]] = {}
    for table in tables:
        if table.empty or "target" not in table.columns:
            continue
        compound_cols = [col for col in ["compound_name", "drug_name", "perturbagen"] if col in table.columns]
        for _, row in table.iterrows():
            target = str(row.get("target", "")).upper()
            if not target:
                continue
            for col in compound_cols:
                name = row.get(col)
                if pd.notna(name):
                    mapping.setdefault(normalize_name(name), set()).add(target)
    return mapping


def main() -> None:
    args = parser().parse_args()
    up_genes = SIGNATURES["mesenchymal"][:50]
    down_genes = SIGNATURES["epithelial"][:50]
    result = post_json("sig_search", {"up_genes": up_genes, "down_genes": down_genes})
    top = get_json(f"result/topn/{result['result_id']}")

    raw_rows = []
    for direction in ["opposite", "similar"]:
        for hit in top.get(direction, [])[: args.top_n]:
            sig = get_json(f"sig/{hit['sig_id']}")
            raw_rows.append(
                {
                    "direction": direction,
                    "sig_id": hit["sig_id"],
                    "connectivity_score": hit.get("scores"),
                    "perturbagen": sig.get("pert_desc"),
                    "cell_id": sig.get("cell_id", ""),
                    "pert_id": sig.get("pert_id", ""),
                    "source_url": "https://maayanlab.cloud/l1000fwd/",
                }
            )

    raw = pd.DataFrame(raw_rows)
    raw_out = ROOT / args.raw_out
    raw_out.parent.mkdir(parents=True, exist_ok=True)
    raw.to_csv(raw_out, sep="\t", index=False)

    mapping = compound_target_map(read_optional(args.dgidb), read_optional(args.chembl), read_optional(args.prism))
    rows = []
    for _, row in raw[raw["direction"].eq("opposite")].iterrows():
        targets = mapping.get(normalize_name(row.get("perturbagen", "")), set())
        for target in targets:
            rows.append(
                {
                    "target": target,
                    "perturbagen": row.get("perturbagen"),
                    "signature_direction": "emt_reversal",
                    "connectivity_score": row.get("connectivity_score"),
                    "source_url": "https://maayanlab.cloud/l1000fwd/",
                    "notes": row.get("sig_id"),
                }
            )

    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).drop_duplicates().to_csv(out, sep="\t", index=False)
    print(f"Wrote {raw_out} ({len(raw)} signatures)")
    print(f"Wrote {out} ({len(rows)} mapped target hits)")


if __name__ == "__main__":
    main()
