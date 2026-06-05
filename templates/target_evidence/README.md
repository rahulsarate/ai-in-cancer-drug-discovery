# Target Evidence Templates

These templates define the minimum target-level extract format expected by `scripts/build_target_evidence.py`.

Every file should include a `target` column with HGNC gene symbols. Extra columns are allowed and kept for human review, but the v1 evidence builder counts rows or reads target columns only.

Recommended workflow:

1. Download the public source dataset locally under `data/raw/`.
2. Create a small target-level extract using these templates.
3. Pass the extract path to `scripts/build_target_evidence.py`.
4. Review `input_availability.tsv`, `missing_evidence_count`, and target evidence cards.

