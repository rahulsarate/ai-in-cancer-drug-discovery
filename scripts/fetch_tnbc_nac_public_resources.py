from __future__ import annotations

import argparse
import csv
import gzip
import json
import re
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
NCBI_EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
USER_AGENT = "EMT-Metastasis-AI-TNBC-Digital-Twin/0.1"


@dataclass(frozen=True)
class GeoDataset:
    accession: str
    tier: str
    cancer_type: str
    tnbc_specific: str
    data_type: str
    timepoints: str
    therapy_context: str
    response_label: str
    planned_use: str
    notes: str

    @property
    def geo_url(self) -> str:
        return f"https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={self.accession}"

    @property
    def matrix_url(self) -> str:
        prefix = geo_series_prefix(self.accession)
        return (
            f"https://ftp.ncbi.nlm.nih.gov/geo/series/{prefix}/{self.accession}/matrix/"
            f"{self.accession}_series_matrix.txt.gz"
        )


GEO_SEED = [
    GeoDataset(
        accession="GSE18864",
        tier="A",
        cancer_type="TNBC",
        tnbc_specific="yes",
        data_type="expression array",
        timepoints="T0 pretreatment biopsy",
        therapy_context="neoadjuvant cisplatin monotherapy",
        response_label="Miller-Payne/pathologic response metadata expected",
        planned_use="small TNBC NAC pilot and response-label parsing",
        notes="Direct TNBC neoadjuvant cisplatin cohort; useful first smoke-test dataset.",
    ),
    GeoDataset(
        accession="GSE43816",
        tier="A",
        cancer_type="TNBC",
        tnbc_specific="yes",
        data_type="expression array",
        timepoints="T0 pretreatment biopsy",
        therapy_context="neoadjuvant chemotherapy",
        response_label="response metadata expected",
        planned_use="TNBC NAC response validation candidate",
        notes="Listed as response to neoadjuvant chemotherapy in triple-negative breast tumors.",
    ),
    GeoDataset(
        accession="GSE45898",
        tier="A",
        cancer_type="TNBC",
        tnbc_specific="yes",
        data_type="expression array",
        timepoints="T0 pretreatment biopsy",
        therapy_context="neoadjuvant chemotherapy",
        response_label="therapeutic response metadata expected",
        planned_use="TNBC NAC response validation candidate",
        notes="Gene expression analysis of therapeutic response in TNBC tumors.",
    ),
    GeoDataset(
        accession="GSE25066",
        tier="A",
        cancer_type="breast cancer",
        tnbc_specific="subset",
        data_type="expression array",
        timepoints="T0 pretreatment biopsy",
        therapy_context="neoadjuvant taxane-anthracycline chemotherapy",
        response_label="pCR/survival metadata expected",
        planned_use="large NAC cohort; subset to TNBC where receptor metadata supports it",
        notes="SuperSeries with discovery and validation cohorts.",
    ),
    GeoDataset(
        accession="GSE25055",
        tier="A",
        cancer_type="breast cancer",
        tnbc_specific="subset",
        data_type="expression array",
        timepoints="T0 pretreatment biopsy",
        therapy_context="neoadjuvant taxane-anthracycline chemotherapy",
        response_label="pCR/survival metadata expected",
        planned_use="GSE25066 discovery subseries",
        notes="SubSeries of GSE25066.",
    ),
    GeoDataset(
        accession="GSE25065",
        tier="A",
        cancer_type="breast cancer",
        tnbc_specific="subset",
        data_type="expression array",
        timepoints="T0 pretreatment biopsy",
        therapy_context="neoadjuvant taxane-anthracycline chemotherapy",
        response_label="pCR/survival metadata expected",
        planned_use="GSE25066 validation subseries",
        notes="SubSeries of GSE25066.",
    ),
    GeoDataset(
        accession="GSE43502",
        tier="B",
        cancer_type="TNBC",
        tnbc_specific="yes",
        data_type="expression array",
        timepoints="post-NAC residual/chemoresistant context",
        therapy_context="chemoresistant TNBC after neoadjuvant chemotherapy",
        response_label="prognostic/residual disease context",
        planned_use="residual-disease biology calibration",
        notes="Useful for resistant residual TNBC biology, not primary pCR training.",
    ),
    GeoDataset(
        accession="GSE164715",
        tier="B",
        cancer_type="TNBC",
        tnbc_specific="yes",
        data_type="single-cell or expression profiling",
        timepoints="residual disease / persistence context",
        therapy_context="chemotherapy persistence",
        response_label="residual disease context",
        planned_use="persister and non-genetic chemoresistance biology calibration",
        notes="Prioritize metadata now; large raw single-cell assets may need separate controlled download planning.",
    ),
    GeoDataset(
        accession="GSE163882",
        tier="A",
        cancer_type="breast cancer",
        tnbc_specific="subset",
        data_type="RNA-seq",
        timepoints="T0 pretreatment biopsy",
        therapy_context="neoadjuvant chemotherapy",
        response_label="pCR/no pCR metadata expected",
        planned_use="RNA-seq pCR classifier comparison if sample-level data are accessible",
        notes="Breast NAC expression classifier cohort.",
    ),
    GeoDataset(
        accession="GSE194040",
        tier="A",
        cancer_type="breast cancer",
        tnbc_specific="subset",
        data_type="mRNA/RPPA resource",
        timepoints="pretreatment",
        therapy_context="I-SPY2 neoadjuvant therapy",
        response_label="pCR/no pCR and treatment arm metadata expected",
        planned_use="modern I-SPY2 molecular response reference",
        notes="Metadata resource; large supplementary files should be reviewed before full download.",
    ),
]


LITERATURE_QUERIES = [
    "triple negative breast cancer neoadjuvant chemotherapy pathological complete response EMT",
    "triple negative breast cancer residual disease neoadjuvant chemotherapy epithelial mesenchymal transition",
    "TNBC neoadjuvant chemotherapy transcriptome response GSE25066",
    "digital twin oncology breast cancer neoadjuvant chemotherapy response",
    "single cell triple negative breast cancer residual disease chemotherapy persister",
]


def geo_series_prefix(accession: str) -> str:
    match = re.fullmatch(r"GSE(\d+)", accession.upper())
    if not match:
        raise ValueError(f"Unsupported GEO accession: {accession}")
    number = int(match.group(1))
    return f"GSE{number // 1000}nnn"


def request_bytes(url: str, timeout: int = 120) -> bytes:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=timeout) as response:
        return response.read()


def download(url: str, local: Path, force: bool = False, timeout: int = 120) -> tuple[str, int]:
    local.parent.mkdir(parents=True, exist_ok=True)
    if local.exists() and not force:
        return "exists", local.stat().st_size
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=timeout) as response, open(local, "wb") as handle:
        total = 0
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            handle.write(chunk)
            total += len(chunk)
    return "downloaded", total


def parse_geo_matrix_metadata(matrix_path: Path) -> dict[str, object]:
    opener = gzip.open if matrix_path.suffix == ".gz" else open
    series_title = ""
    series_summary = []
    sample_ids: list[str] = []
    characteristics: dict[str, list[str]] = {}

    with opener(matrix_path, "rt", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if line.startswith("!series_matrix_table_begin"):
                break
            row = next(csv.reader([line], delimiter="\t"))
            key = row[0] if row else ""
            values = [value.strip().strip('"') for value in row[1:]]
            if key == "!Series_title":
                series_title = values[0] if values else ""
            elif key == "!Series_summary":
                series_summary.extend(value for value in values if value)
            elif key == "!Sample_geo_accession":
                sample_ids = values
            elif key == "!Sample_characteristics_ch1":
                label = "characteristics"
                if values and ":" in values[0]:
                    label = values[0].split(":", 1)[0].strip().lower().replace(" ", "_")
                characteristics.setdefault(label, []).extend(values)

    return {
        "series_title": series_title,
        "series_summary": " ".join(series_summary),
        "sample_count": len(sample_ids),
        "sample_ids_preview": ";".join(sample_ids[:8]),
        "characteristic_keys": ";".join(sorted(characteristics)),
    }


def fetch_pubmed(query: str, retmax: int, timeout: int) -> list[dict[str, str]]:
    search_url = f"{NCBI_EUTILS}/esearch.fcgi?{urlencode({'db': 'pubmed', 'term': query, 'retmax': retmax, 'retmode': 'json', 'sort': 'relevance'})}"
    search = json.loads(request_bytes(search_url, timeout=timeout).decode("utf-8"))
    ids = search.get("esearchresult", {}).get("idlist", [])
    if not ids:
        return []
    time.sleep(0.34)
    summary_url = f"{NCBI_EUTILS}/esummary.fcgi?{urlencode({'db': 'pubmed', 'id': ','.join(ids), 'retmode': 'json'})}"
    summary = json.loads(request_bytes(summary_url, timeout=timeout).decode("utf-8"))
    rows = []
    for pmid in summary.get("result", {}).get("uids", []):
        item = summary.get("result", {}).get(pmid, {})
        rows.append(
            {
                "query": query,
                "pmid": pmid,
                "title": item.get("title", ""),
                "journal": item.get("fulljournalname", ""),
                "pubdate": item.get("pubdate", ""),
                "doi": next((aid.get("value", "") for aid in item.get("articleids", []) if aid.get("idtype") == "doi"), ""),
                "source_url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            }
        )
    return rows


def fetch_pubmed_abstracts(pmids: list[str], out_xml: Path, timeout: int) -> None:
    if not pmids:
        return
    out_xml.parent.mkdir(parents=True, exist_ok=True)
    url = f"{NCBI_EUTILS}/efetch.fcgi?{urlencode({'db': 'pubmed', 'id': ','.join(pmids), 'retmode': 'xml'})}"
    out_xml.write_bytes(request_bytes(url, timeout=timeout))


def write_geo_seed(out_path: Path) -> pd.DataFrame:
    rows = []
    for item in GEO_SEED:
        rows.append(
            {
                "dataset_id": item.accession,
                "source": "GEO",
                "cancer_type": item.cancer_type,
                "tnbc_specific": item.tnbc_specific,
                "data_type": item.data_type,
                "timepoints": item.timepoints,
                "therapy_context": item.therapy_context,
                "response_label": item.response_label,
                "access_status": "public",
                "planned_use": item.planned_use,
                "tier": item.tier,
                "geo_url": item.geo_url,
                "matrix_url": item.matrix_url,
                "notes": item.notes,
            }
        )
    df = pd.DataFrame(rows)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, sep="\t", index=False)
    return df


def download_geo_matrices(accessions: set[str], raw_dir: Path, force: bool, timeout: int) -> pd.DataFrame:
    rows = []
    by_accession = {item.accession: item for item in GEO_SEED}
    for accession in sorted(accessions):
        item = by_accession[accession]
        local = raw_dir / "geo" / accession / f"{accession}_series_matrix.txt.gz"
        row = {
            "dataset_id": accession,
            "matrix_url": item.matrix_url,
            "local_path": str(local.relative_to(ROOT)),
            "download_status": "",
            "bytes": 0,
            "error": "",
        }
        try:
            status, size = download(item.matrix_url, local, force=force, timeout=timeout)
            row["download_status"] = status
            row["bytes"] = size
            row.update(parse_geo_matrix_metadata(local))
        except (HTTPError, URLError, TimeoutError, OSError, csv.Error) as exc:
            row["download_status"] = "failed"
            row["error"] = str(exc)
        rows.append(row)
    return pd.DataFrame(rows)


def write_literature(raw_dir: Path, processed_dir: Path, retmax: int, timeout: int) -> pd.DataFrame:
    rows = []
    for query in LITERATURE_QUERIES:
        rows.extend(fetch_pubmed(query, retmax=retmax, timeout=timeout))
        time.sleep(0.34)
    df = pd.DataFrame(rows).drop_duplicates(subset=["pmid"]).sort_values(["pubdate", "title"], ascending=[False, True])
    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(processed_dir / "tnbc_nac_literature_seed.tsv", sep="\t", index=False)
    fetch_pubmed_abstracts(df["pmid"].head(50).astype(str).tolist(), raw_dir / "literature" / "pubmed_tnbc_nac_seed.xml", timeout)
    return df


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Fetch TNBC NAC public dataset and literature seed resources.")
    p.add_argument("--raw-dir", default="data/raw/tnbc_nac")
    p.add_argument("--processed-dir", default="data/processed/tnbc_digital_twin")
    p.add_argument("--docs-dir", default="docs/tnbc_digital_twin_emt_plasticity")
    p.add_argument("--download-geo", action="store_true", help="Download GEO series matrix files for selected accessions.")
    p.add_argument("--accession", action="append", help="GEO accession to download. Can be repeated. Defaults to priority small/medium cohorts.")
    p.add_argument("--all-geo", action="store_true", help="Download every seeded GEO matrix file.")
    p.add_argument("--force", action="store_true")
    p.add_argument("--pubmed-retmax", type=int, default=12)
    p.add_argument("--timeout", type=int, default=180)
    return p


def main() -> None:
    args = parser().parse_args()
    raw_dir = ROOT / args.raw_dir
    processed_dir = ROOT / args.processed_dir
    docs_dir = ROOT / args.docs_dir
    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)
    docs_dir.mkdir(parents=True, exist_ok=True)

    dataset_seed = write_geo_seed(docs_dir / "dataset_inventory_seed.tsv")
    dataset_seed.to_csv(processed_dir / "tnbc_nac_dataset_inventory_seed.tsv", sep="\t", index=False)

    literature = write_literature(raw_dir, processed_dir, retmax=args.pubmed_retmax, timeout=args.timeout)

    geo_audit = pd.DataFrame()
    if args.download_geo:
        if args.all_geo:
            accessions = {item.accession for item in GEO_SEED}
        elif args.accession:
            accessions = {item.upper() for item in args.accession}
        else:
            accessions = {"GSE18864", "GSE43816", "GSE45898", "GSE25065"}
        known = {item.accession for item in GEO_SEED}
        unknown = sorted(accessions - known)
        if unknown:
            raise SystemExit(f"Unknown seeded accessions: {', '.join(unknown)}")
        geo_audit = download_geo_matrices(accessions, raw_dir, force=args.force, timeout=args.timeout)
        geo_audit.to_csv(processed_dir / "tnbc_nac_geo_download_audit.tsv", sep="\t", index=False)

    report = {
        "dataset_seed_count": int(dataset_seed.shape[0]),
        "literature_seed_count": int(literature.shape[0]),
        "geo_download_attempt_count": int(geo_audit.shape[0]),
        "geo_download_success_count": int((geo_audit.get("download_status", pd.Series(dtype=str)) != "failed").sum()) if not geo_audit.empty else 0,
    }
    (processed_dir / "tnbc_nac_resource_fetch_summary.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
