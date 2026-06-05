# EMT State Atlas Pipeline

## Goal

Build an interpretable, public-data atlas that scores EMT state, partial EMT, stromal contamination, immune context, CAF/TAM niche activity, hypoxia, ferroptosis vulnerability, and survival association.

## Pipeline steps

1. **Load expression matrix**
   - Accept TCGA/GDC/Xena bulk RNA-seq or summarized single-cell data.
   - Normalize upstream when possible; for first-pass scoring, use log-transformed TPM/RSEM-style values.

2. **Orient genes and samples**
   - The scorer detects whether genes are rows or columns by matching curated EMT/TME genes.

3. **Score signatures**
   - Z-score each gene across samples.
   - Average z-scored genes per signature.
   - EMT score = mesenchymal score - epithelial score.
   - Partial EMT score = minimum of epithelial and mesenchymal scores.
   - Stromal contamination risk = percentile rank of fibroblast/stromal signature.

4. **Merge metadata**
   - Add cancer type, stage, metastatic label, sample type, survival time, and event status.

5. **Survival association**
   - Run univariate Cox models for EMT score, partial EMT score, stromal score, immune score, and CAF/TAM niche score.

6. **Single-cell validation**
   - Compare predicted states against CancerSEA/TISCH2 malignant-cell annotations.
   - Confirm that bulk EMT signals are not dominated by CAF/fibroblast expression.

## Expected outputs

- `emt_scores.tsv`: sample-level EMT/TME/vulnerability scores.
- `survival.tsv`: hazard ratio, p-value, and concordance for selected scores.
- Future notebooks: cancer-type plots, Kaplan-Meier curves, spatial niche maps, and target-ranker evidence tables.

## Pros

- Transparent and easy to explain to clinicians/scientists.
- Works with public data.
- Useful as a benchmark before deep learning.
- Directly feeds target prioritization.

## Cons

- Signature scoring is simpler than full state-space modeling.
- Bulk RNA-seq can confuse tumor-cell EMT with stromal content.
- Survival associations are not causal.
- Needs external validation before clinical interpretation.

