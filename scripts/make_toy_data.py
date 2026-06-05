from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    rng = np.random.default_rng(7)
    samples = [f"S{i:03d}" for i in range(1, 31)]
    genes = [
        "CDH1", "EPCAM", "KRT8", "KRT18", "VIM", "FN1", "ZEB1", "SNAI1",
        "COL1A1", "FAP", "PTPRC", "CD8A", "NKG7", "CD68", "SPP1", "HIF1A",
        "CA9", "GPX4", "SLC7A11", "ACSL4", "AXL", "TGFBR1", "TEAD1",
    ]
    expr = pd.DataFrame(rng.normal(5, 1, size=(len(samples), len(genes))), index=samples, columns=genes)
    expr.loc[samples[10:20], ["VIM", "FN1", "ZEB1", "SNAI1", "AXL"]] += 3
    expr.loc[samples[20:30], ["COL1A1", "FAP", "PTPRC", "CD8A", "SPP1"]] += 2
    expr.insert(0, "sample_id", samples)

    metadata = pd.DataFrame(
        {
            "sample_id": samples,
            "cancer_type": ["toy"] * len(samples),
            "time": rng.integers(100, 2000, size=len(samples)),
            "event": rng.integers(0, 2, size=len(samples)),
        }
    )

    raw = ROOT / "data" / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    expr.to_csv(raw / "toy_expression.tsv", sep="\t", index=False)
    metadata.to_csv(raw / "toy_metadata.tsv", sep="\t", index=False)
    print(f"Wrote {raw / 'toy_expression.tsv'}")
    print(f"Wrote {raw / 'toy_metadata.tsv'}")


if __name__ == "__main__":
    main()

