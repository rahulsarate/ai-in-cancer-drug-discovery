from __future__ import annotations

from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import pandas as pd


HEST_METADATA_URL = "https://huggingface.co/datasets/MahmoodLab/hest/resolve/main/HEST_v1_1_0.csv"


def main() -> None:
    status = {
        "resource": "HEST_v1_1_0.csv",
        "url": HEST_METADATA_URL,
        "accessible": False,
        "http_status": "",
        "note": "",
    }
    try:
        request = Request(HEST_METADATA_URL, method="HEAD", headers={"User-Agent": "spatial-emt-niche-gnn/0.1"})
        with urlopen(request, timeout=30) as response:
            status["accessible"] = 200 <= response.status < 300
            status["http_status"] = response.status
    except HTTPError as exc:
        status["http_status"] = exc.code
        status["note"] = "HEST HuggingFace dataset appears gated or requires authentication." if exc.code in {401, 403} else str(exc)
    except (URLError, TimeoutError) as exc:
        status["note"] = str(exc)
    out = Path("data/processed/spatial_emt_niche_gnn_blockers")
    out.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([status]).to_csv(out / "hest_access_status.tsv", sep="\t", index=False)
    print(f"Wrote {out / 'hest_access_status.tsv'}")


if __name__ == "__main__":
    main()
