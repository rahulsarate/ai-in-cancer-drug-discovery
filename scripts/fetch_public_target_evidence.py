from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

import pandas as pd

from metastasis_target_ranker.ranking import starter_targets


ROOT = Path(__file__).resolve().parents[1]
DGIDB_ENDPOINT = "https://dgidb.org/api/graphql"
CHEMBL_BASE = "https://www.ebi.ac.uk/chembl/api/data"
OPEN_TARGETS_ENDPOINT = "https://api.platform.opentargets.org/api/v4/graphql"


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Fetch small public target evidence extracts from APIs.")
    p.add_argument("--out-dir", default="data/raw/api_evidence")
    p.add_argument("--limit", type=int, default=0, help="Optional number of targets for quick tests.")
    p.add_argument("--timeout", type=int, default=30)
    return p


def post_json(url: str, payload: dict, timeout: int) -> dict | None:
    data = json.dumps(payload).encode("utf-8")
    request = Request(url, data=data, headers={"Content-Type": "application/json", "Accept": "application/json"})
    try:
        with urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        return {"error": str(exc)}


def get_json(url: str, timeout: int) -> dict | None:
    request = Request(url, headers={"Accept": "application/json"})
    try:
        with urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        return {"error": str(exc)}


def fetch_dgidb(targets: list[str], timeout: int) -> pd.DataFrame:
    query = """
    query GeneInteractions($genes: [String!]!) {
      genes(names: $genes) {
        nodes {
          name
          interactions {
            drug { name conceptId }
            interactionScore
            interactionTypes { type directionality }
            sources { sourceDbName }
            publications { pmid }
          }
        }
      }
    }
    """
    payload = {"query": query, "variables": {"genes": targets}}
    result = post_json(DGIDB_ENDPOINT, payload, timeout) or {}
    rows = []
    for node in result.get("data", {}).get("genes", {}).get("nodes", []) or []:
        target = node.get("name")
        for interaction in node.get("interactions", []) or []:
            rows.append(
                {
                    "target": target,
                    "drug_name": (interaction.get("drug") or {}).get("name"),
                    "interaction_type": ";".join(
                        item.get("type", "") for item in interaction.get("interactionTypes", []) or []
                    ),
                    "interaction_score": interaction.get("interactionScore"),
                    "source_db": ";".join(item.get("sourceDbName", "") for item in interaction.get("sources", []) or []),
                    "pmids": ";".join(str(item.get("pmid", "")) for item in interaction.get("publications", []) or []),
                    "source_url": "https://www.dgidb.org/",
                    "notes": "",
                }
            )
    if not rows and result.get("error"):
        rows.append({"target": "", "drug_name": "", "interaction_type": "", "source_db": "", "source_url": DGIDB_ENDPOINT, "notes": result["error"]})
    return pd.DataFrame(rows)


def fetch_chembl(targets: list[str], timeout: int) -> pd.DataFrame:
    rows = []
    for target in targets:
        lookup_url = f"{CHEMBL_BASE}/target.json?pref_name__icontains={quote(target)}&limit=10"
        lookup = get_json(lookup_url, timeout) or {}
        candidates = lookup.get("targets", []) or []
        if not candidates:
            lookup_url = f"{CHEMBL_BASE}/target/search.json?q={quote(target)}&limit=10"
            lookup = get_json(lookup_url, timeout) or {}
            candidates = lookup.get("targets", []) or []

        ranked_candidates = sorted(candidates, key=lambda item: chembl_target_rank(target, item))
        for item in ranked_candidates[:3]:
            chembl_target_id = item.get("target_chembl_id")
            pref_name = item.get("pref_name")
            if not chembl_target_id:
                continue
            activity_url = f"{CHEMBL_BASE}/activity.json?target_chembl_id={quote(chembl_target_id)}&limit=25"
            activity = get_json(activity_url, timeout) or {}
            for act in activity.get("activities", []) or []:
                rows.append(
                    {
                        "target": target,
                        "compound_name": act.get("molecule_pref_name") or act.get("molecule_chembl_id"),
                        "chembl_id": act.get("molecule_chembl_id"),
                        "target_chembl_id": chembl_target_id,
                        "target_pref_name": pref_name,
                        "activity_type": act.get("standard_type"),
                        "activity_value": act.get("standard_value"),
                        "activity_units": act.get("standard_units"),
                        "source_url": "https://www.ebi.ac.uk/chembl/",
                        "notes": "",
                    }
                )
    return pd.DataFrame(rows)


def chembl_target_rank(gene: str, item: dict) -> tuple[int, str]:
    gene = gene.upper()
    target_type = str(item.get("target_type", "")).upper()
    organism = str(item.get("organism", "")).lower()
    synonyms = []
    for component in item.get("target_components", []) or []:
        for synonym in component.get("target_component_synonyms", []) or []:
            synonyms.append(str(synonym.get("component_synonym", "")).upper())
    exact = gene in synonyms or str(item.get("pref_name", "")).upper() == gene
    single_protein = "SINGLE PROTEIN" in target_type
    human = organism == "homo sapiens"
    return (0 if exact else 1, 0 if single_protein else 1, 0 if human else 1, str(item.get("pref_name", "")))


def fetch_open_targets_placeholder(targets: list[str], timeout: int) -> pd.DataFrame:
    """Fetch target search hits for audit-ready Open Targets extracts.

    The v1 ranker only needs target-level rows. These rows confirm that the API
    can resolve each target symbol; deeper disease-specific extracts can be
    added after choosing exact EFO disease/metastasis terms.
    """
    query = """
    query Search($queryString: String!) {
      search(queryString: $queryString, entityNames: ["target"], page: {index: 0, size: 3}) {
        hits {
          id
          name
          entity
          description
        }
      }
    }
    """
    rows = []
    for target in targets:
        result = post_json(OPEN_TARGETS_ENDPOINT, {"query": query, "variables": {"queryString": target}}, timeout) or {}
        hits = result.get("data", {}).get("search", {}).get("hits", []) or []
        for hit in hits:
            rows.append(
                {
                    "target": target,
                    "disease_or_trait": "cancer/metastasis review needed",
                    "evidence_type": "open_targets_symbol_resolution",
                    "score": "",
                    "open_targets_id": hit.get("id"),
                    "open_targets_name": hit.get("name"),
                    "source_url": "https://platform.opentargets.org/",
                    "notes": hit.get("description", ""),
                }
            )
    return pd.DataFrame(rows)


def main() -> None:
    args = parser().parse_args()
    out = ROOT / args.out_dir
    out.mkdir(parents=True, exist_ok=True)

    targets = starter_targets()["target"].astype(str).str.upper().tolist()
    if args.limit:
        targets = targets[: args.limit]

    tables = {
        "dgidb_interactions.tsv": fetch_dgidb(targets, args.timeout),
        "chembl_target_compounds.tsv": fetch_chembl(targets, args.timeout),
        "open_targets_emt_metastasis.tsv": fetch_open_targets_placeholder(targets, args.timeout),
    }
    for filename, table in tables.items():
        table.to_csv(out / filename, sep="\t", index=False)
        print(f"Wrote {out / filename} ({len(table)} rows)")


if __name__ == "__main__":
    main()
