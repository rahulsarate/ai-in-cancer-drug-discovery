from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Create a lightweight morphology embedding baseline from H&E tile features.")
    p.add_argument("--features", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--components", type=int, default=4)
    return p


def main() -> None:
    args = parser().parse_args()
    features = pd.read_csv(args.features, sep="\t")
    cols = [col for col in features.columns if col != "spot_id"]
    x = features[cols].apply(pd.to_numeric, errors="coerce").fillna(features[cols].median(numeric_only=True)).to_numpy(dtype=float)
    x = (x - x.mean(axis=0)) / np.where(x.std(axis=0) == 0, 1.0, x.std(axis=0))
    _, _, vt = np.linalg.svd(x, full_matrices=False)
    k = min(args.components, vt.shape[0])
    z = x @ vt[:k].T
    out = pd.DataFrame({"spot_id": features["spot_id"].astype(str)})
    for idx in range(k):
        out[f"morphology_embedding_{idx + 1}"] = z[:, idx]
    path = Path(args.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(path, sep="\t", index=False)
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
