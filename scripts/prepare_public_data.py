"""Create local data folders and print source-specific download guidance.

Large public cancer resources change release names and are often hundreds of MB
to many GB. This script keeps downloads explicit and reproducible.
"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    for folder in ["data/raw", "data/processed", "data/interim", "data/manifests"]:
        (ROOT / folder).mkdir(parents=True, exist_ok=True)

    print("Public data folders are ready.\n")
    print("Recommended first downloads:")
    print("1. TCGA pan-cancer expression + phenotype from UCSC Xena or GDC.")
    print("2. CancerSEA functional state signatures for single-cell benchmarking.")
    print("3. TISCH2/HTAN datasets for immune and stromal context.")
    print("4. DepMap CRISPR gene effect and model metadata.")
    print("5. PRISM secondary dose-response and treatment metadata.")
    print("6. LINCS/CLUE L1000 perturbation signatures for drug reversal.")
    print("7. Open Targets, ChEMBL, and DGIdb evidence tables for target ranker.\n")

    print("Official source links:")
    print("- tcga_xena: https://xena.ucsc.edu/")
    print("- gdc: https://portal.gdc.cancer.gov/")
    print("- cancersea: http://biocc.hrbmu.edu.cn/CancerSEA/")
    print("- tisch2: https://tisch.compbio.cn/")
    print("- htan: https://humantumoratlas.org/")
    print("- depmap: https://depmap.org/portal/")
    print("- prism: https://depmap.org/repurposing/")
    print("- lincs_clue: https://clue.io/lincs")
    print("- open_targets: https://platform.opentargets.org/")
    print("- chembl: https://www.ebi.ac.uk/chembl/")
    print("- dgidb: https://www.dgidb.org/")


if __name__ == "__main__":
    main()
