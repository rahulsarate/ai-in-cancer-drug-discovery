from __future__ import annotations

import argparse
import re
import ssl
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import Request, urlopen

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
THREE_CA_URL = "https://www.weizmann.ac.il/sites/3CA/"
TISCH_DOCS_URL = "https://tisch.compbio.cn/documentation"
HTAN_ACCESS_URL = "https://data.humantumoratlas.org/data-access"


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[dict[str, str]] = []
        self._current: dict[str, str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        href = dict(attrs).get("href")
        if href:
            self._current = {"href": href, "text": ""}

    def handle_data(self, data: str) -> None:
        if self._current is not None:
            self._current["text"] += data

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._current is not None:
            self.links.append(self._current)
            self._current = None


def fetch_text(url: str) -> str:
    request = Request(url, headers={"User-Agent": "Mozilla/5.0 EMT-State-Atlas/0.1"})
    try:
        with urlopen(request, timeout=60) as response:
            return response.read().decode("utf-8", errors="replace")
    except Exception:
        with urlopen(request, timeout=60, context=ssl._create_unverified_context()) as response:
            return response.read().decode("utf-8", errors="replace")


def three_ca_links() -> pd.DataFrame:
    parser = LinkParser()
    parser.feed(fetch_text(THREE_CA_URL))
    rows = []
    for link in parser.links:
        text = " ".join(link["text"].split())
        href = urljoin(THREE_CA_URL, link["href"])
        if not text:
            continue
        if "studies" in text or "cells" in text or "dropbox" in href:
            rows.append(
                {
                    "source": "3CA",
                    "portal_section": re.sub(r"\s+", " ", text),
                    "url": href,
                    "download_status": "direct_link_or_category_page_found",
                    "next_action": "Open/download selected cancer category, then import expression and metadata with build_emt_annotated_single_cell_layer.py.",
                }
            )
    return pd.DataFrame(rows)


def static_portal_requirements() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "source": "TISCH2",
                "portal_section": "Documentation/download page",
                "url": TISCH_DOCS_URL,
                "download_status": "portal_export_required",
                "next_action": "Download cell-type averaged expression, metadata, or dataset-level expression from TISCH2 selected dataset pages.",
            },
            {
                "source": "HTAN",
                "portal_section": "Data access",
                "url": HTAN_ACCESS_URL,
                "download_status": "selected_file_credentials_required",
                "next_action": "Use HTAN Download selected files and Synapse/Gen3 credentials, then import Level 3/4 annotated files.",
            },
        ]
    )


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Build public portal manifest for TISCH2, 3CA, and HTAN annotated single-cell exports.")
    p.add_argument("--out", default="data/processed/pan_cancer_emt_state_atlas/annotated_single_cell/external_portal_download_manifest.tsv")
    return p


def main() -> None:
    args = parser().parse_args()
    frames = [three_ca_links(), static_portal_requirements()]
    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    pd.concat(frames, ignore_index=True).to_csv(out, sep="\t", index=False)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
