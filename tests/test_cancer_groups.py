from __future__ import annotations

import pandas as pd

from emt_state_atlas.cancer_groups import REQUESTED_CANCER_GROUPS, add_cancer_groups, requested_group_table


def test_requested_cancer_groups_cover_user_focus_areas():
    table = requested_group_table()

    assert set(REQUESTED_CANCER_GROUPS).issubset(set(table["cancer_group"]))
    assert table["tcga_codes"].str.len().gt(0).all()


def test_add_cancer_groups_maps_core_tcga_codes():
    frame = pd.DataFrame({"cancer_type": ["HNSC", "BRCA", "COAD", "PAAD", "GBM", "PRAD", "OV", "SKCM", "LUAD", "ESCA", "LAML"]})
    mapped = add_cancer_groups(frame)

    assert mapped.loc[0, "cancer_group"] == "Head and Neck Cancer"
    assert mapped.loc[1, "cancer_group"] == "Breast Cancer"
    assert mapped.loc[2, "cancer_group"] == "Colon / Intestine Cancer"
    assert mapped.loc[3, "cancer_group"] == "Pancreatic Cancer"
    assert mapped.loc[4, "cancer_group"] == "Brain Tumors"
    assert mapped.loc[5, "cancer_group"] == "Prostate Cancer"
    assert mapped.loc[6, "cancer_group"] == "Ovarian Cancer"
    assert mapped.loc[7, "cancer_group"] == "Skin Cancer"
    assert mapped.loc[8, "cancer_group"] == "Lung Cancer"
    assert mapped.loc[9, "cancer_group"] == "Oesophageal Cancer"
    assert mapped.loc[10, "cancer_group"] == "Blood Tumors"
