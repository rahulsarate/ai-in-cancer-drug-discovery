# EMT Atlas Pathology Review Handoff

## Purpose

This packet is for expert pathology review of computational EMT spatial-niche hypotheses. It is not a diagnostic sign-out workflow.

## Files for Review

| File | Use |
| --- | --- |
| `data/processed/pan_cancer_emt_state_atlas/pathology/pathology_review_queue.tsv` | Ranked spatial cohorts and review focus labels. |
| `data/processed/pan_cancer_emt_state_atlas/pathology/pathology_review_checklist.tsv` | Feature definitions and marker/context expectations. |
| `data/processed/pan_cancer_emt_state_atlas/pathology/pathology_label_template.tsv` | Region-level labels to be completed by reviewers. |

## Requested Labels

For each region in the template, fill:

- `reviewer_id`
- `invasive_edge_label`
- `caf_stromal_interface_label`
- `tam_neighborhood_label`
- `hypoxia_necrosis_label`
- `tumor_intrinsic_emt_label`
- `confidence_0_3`
- `notes`

Accepted positive values are `yes`, `true`, `present`, `positive`, or `1`. Negative values can be `no`, `false`, `absent`, `negative`, or `0`.

## Review Boundary

The computational labels are hypotheses. Reviewer labels should be based on H&E morphology, tumor-stroma architecture, and available marker/spatial context. A returned label file can be merged with:

```powershell
$env:PYTHONPATH='src'
python scripts\build_emt_pathology_review_queue.py --labels path\to\returned_pathology_labels.tsv
```

## Minimum Practical Review

Start with the highest-priority cohorts in the queue. The current template contains 80 region rows across the spatial review queue.
