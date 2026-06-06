# Pathologist Review Template

## Purpose

This template converts weak spatial EMT niche labels into reviewable pathology
regions. It is designed for spot-level or region-level review by a pathologist
or trained translational scientist.

## Regions To Annotate

| Region class | What to mark | Why it matters |
| --- | --- | --- |
| Tumor-rich epithelial | Tumor glands/nests with epithelial morphology | Controls against stromal EMT inflation |
| Invasive edge | Tumor-stroma interface, budding, infiltrative fronts | Candidate partial EMT niche |
| Stroma-rich/CAF-rich | Dense desmoplastic or fibromuscular stroma | Separates CAF signal from malignant EMT |
| Necrosis/hypoxia | Necrotic, poorly perfused, or hypoxic-looking areas | Validates hypoxia-gradient edges |
| Immune-rich/TAM-rich | Dense immune/macrophage infiltrates | Validates CAF/TAM and CSF1-SPP1 circuits |
| Vessel/angiogenic | Vessel-rich regions or endothelial structures | Validates angiogenesis and VEGFA-KDR signal |
| Artifact/acellular | Tissue folds, tears, acellular matrix, low-quality regions | Exclusion and QC |

## Minimum Review Fields

| Field | Description |
| --- | --- |
| sample_id | Spatial sample or slide identifier |
| region_id | Unique pathologist region label |
| region_class | One of the classes above |
| confidence | low, medium, or high |
| spot_ids | Optional comma-separated spot IDs if spot mapping is available |
| notes | Free text notes |

## Suggested Review Order

1. Review H&E without transcriptomic scores.
2. Mark artifact/acellular regions first.
3. Mark tumor-rich, stroma-rich, invasive-edge, necrosis/hypoxia, immune-rich, and vessel-rich regions.
4. Overlay EMT niche scores and check whether high-scoring regions agree with morphology.
5. Flag mismatches as either stromal contamination risk, false negative tumor EMT, or ambiguous mixed spot.

## Interpretation Rule

Pathologist regions should not be treated as ground truth for EMT biology by
themselves. They are validation anchors that help separate tumor-cell EMT,
partial EMT, stromal admixture, hypoxia, and immune/CAF niche effects.
