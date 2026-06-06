# Pathologist Review SOP

## Review Principles

1. Score morphology without using transcriptomic values first.
2. Mark artifact/acellular regions before assigning biological labels.
3. Use 0-3 scores for EMT-like morphology, stroma, hypoxia/necrosis, immune
   richness, and vessel richness.
4. Use `mixed_ambiguous` when a spot/region cannot separate tumor from stroma.
5. Use `needs_second_review` when morphology is plausible but uncertain.

## Minimum Quality Bar

- Calibration set: all reviewers score the same 60 cases.
- High-impact classes: at least two reviewers for tumor EMT, invasive edge, and
  stromal-inflated EMT.
- Adjudication: lead pathologist resolves cases with disagreement, low
  confidence, or model/pathology mismatch.

## Consensus Rule

Use confidence-weighted agreement. If reviewers disagree between tumor EMT and
stromal-rich/CAF-rich, keep the case as `mixed_ambiguous` unless the lead
pathologist adjudicates it.
