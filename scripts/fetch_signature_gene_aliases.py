from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import pandas as pd

from emt_state_atlas.signatures import SIGNATURES


ROOT = Path(__file__).resolve().parents[1]
MYGENE_ENDPOINT = "https://mygene.info/v3/query"


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Fetch Entrez aliases for EMT signature genes from MyGene.info.")
    p.add_argument("--out", default="data/raw/gene_aliases/signature_gene_aliases.tsv")
    p.add_argument("--timeout", type=int, default=30)
    return p


def query_symbol(symbol: str, timeout: int) -> dict:
    params = urlencode(
        {
            "q": f"symbol:{symbol}",
            "species": "human",
            "fields": "symbol,entrezgene,ensembl.gene,name",
            "size": 3,
        }
    )
    request = Request(f"{MYGENE_ENDPOINT}?{params}", headers={"Accept": "application/json"})
    with urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> None:
    args = parser().parse_args()
    genes = sorted({gene.upper() for gene_list in SIGNATURES.values() for gene in gene_list})
    rows = []
    for symbol in genes:
        try:
            result = query_symbol(symbol, args.timeout)
        except Exception as exc:
            rows.append({"symbol": symbol, "alias": "", "alias_type": "error", "notes": str(exc)})
            continue
        hits = result.get("hits", [])
        if not hits:
            rows.append({"symbol": symbol, "alias": "", "alias_type": "missing", "notes": ""})
            continue
        best = hits[0]
        entrez = best.get("entrezgene")
        if entrez:
            rows.append({"symbol": symbol, "alias": str(entrez), "alias_type": "entrezgene", "notes": best.get("name", "")})
        ensembl = best.get("ensembl", {})
        if isinstance(ensembl, list):
            for item in ensembl:
                if item.get("gene"):
                    rows.append({"symbol": symbol, "alias": item["gene"], "alias_type": "ensembl_gene", "notes": best.get("name", "")})
        elif isinstance(ensembl, dict) and ensembl.get("gene"):
            rows.append({"symbol": symbol, "alias": ensembl["gene"], "alias_type": "ensembl_gene", "notes": best.get("name", "")})

    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out, sep="\t", index=False)
    print(f"Wrote {out} ({len(rows)} aliases)")


if __name__ == "__main__":
    main()

