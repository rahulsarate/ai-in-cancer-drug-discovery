from __future__ import annotations

import argparse
import re
import ssl
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin
from urllib.request import Request, urlopen

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://www.weizmann.ac.il/sites/3CA/"
CATEGORIES = {
    "head-and-neck": "Head and Neck Cancer",
    "breast": "Breast Cancer",
    "colorectal": "Colon / Intestine Cancer",
    "pancreas": "Pancreatic Cancer",
    "brain": "Brain Tumors",
    "prostate": "Prostate Cancer",
    "ovarian": "Ovarian Cancer",
    "skin": "Skin Cancer",
    "lung": "Lung Cancer",
    "hematologic": "Blood Tumors",
}


class ThreeCaTableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.rows: list[list[dict[str, str]]] = []
        self._row: list[dict[str, str]] | None = None
        self._cell: dict[str, str] | None = None
        self._link: dict[str, str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = {key: value or "" for key, value in attrs}
        if tag == "tr":
            self._row = []
        elif tag == "td" and self._row is not None:
            self._cell = {"text": "", "hrefs": ""}
        elif tag == "a" and self._cell is not None:
            self._link = {"href": attrs_dict.get("href", ""), "text": ""}

    def handle_data(self, data: str) -> None:
        if self._cell is not None:
            self._cell["text"] += data
        if self._link is not None:
            self._link["text"] += data

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._link is not None and self._cell is not None:
            hrefs = [href for href in self._cell.get("hrefs", "").split(" ") if href]
            if self._link.get("href"):
                hrefs.append(self._link["href"])
            self._cell["hrefs"] = " ".join(hrefs)
            self._link = None
        elif tag == "td" and self._cell is not None and self._row is not None:
            self._cell["text"] = " ".join(self._cell["text"].split())
            self._row.append(self._cell)
            self._cell = None
        elif tag == "tr" and self._row is not None:
            if self._row:
                self.rows.append(self._row)
            self._row = None


def fetch_text(url: str) -> str:
    request = Request(url, headers={"User-Agent": "Mozilla/5.0 EMT-State-Atlas/0.1"})
    try:
        with urlopen(request, timeout=60) as response:
            return response.read().decode("utf-8", errors="replace")
    except Exception:
        with urlopen(request, timeout=60, context=ssl._create_unverified_context()) as response:
            return response.read().decode("utf-8", errors="replace")


def clean_url(url: str, base_url: str) -> str:
    if not url:
        return ""
    return unquote(urljoin(base_url, url).replace("&amp;", "&"))


def slug(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", text).strip("_")


def parse_category(category: str, cancer_group: str) -> pd.DataFrame:
    url = urljoin(BASE_URL, category)
    parser = ThreeCaTableParser()
    parser.feed(fetch_text(url))
    rows = []
    for cells in parser.rows:
        if len(cells) < 9:
            continue
        title = cells[0]["text"]
        if not title or title.lower().startswith("all "):
            continue
        data_url = clean_url(cells[1].get("hrefs", "").split(" ")[0] if cells[1].get("hrefs") else "", url)
        metadata_url = clean_url(cells[2].get("hrefs", "").split(" ")[0] if cells[2].get("hrefs") else "", url)
        rows.append(
            {
                "source": "3CA",
                "category": category,
                "cancer_group": cancer_group,
                "dataset_title": title,
                "dataset_name": slug(title.replace(" et al. ", "").replace(" ", "")) + f"_{category}",
                "disease": cells[5]["text"],
                "technology": cells[6]["text"],
                "samples": pd.to_numeric(cells[7]["text"], errors="coerce"),
                "cells": pd.to_numeric(cells[8]["text"], errors="coerce"),
                "data_url": data_url,
                "metadata_url": metadata_url,
                "category_url": url,
                "download_status": "ready" if data_url and metadata_url else "missing_data_or_metadata_link",
            }
        )
    return pd.DataFrame(rows)


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Build dataset-level manifest for public 3CA expression and metadata downloads.")
    p.add_argument("--out", default="data/processed/pan_cancer_emt_state_atlas/annotated_single_cell/3ca_dataset_manifest.tsv")
    return p


def main() -> None:
    args = parser().parse_args()
    frames = [parse_category(category, group) for category, group in CATEGORIES.items()]
    manifest = pd.concat(frames, ignore_index=True).sort_values(["cancer_group", "cells", "dataset_title"])
    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    manifest.to_csv(out, sep="\t", index=False)
    print(f"Wrote {out} with {len(manifest)} datasets")


if __name__ == "__main__":
    main()
