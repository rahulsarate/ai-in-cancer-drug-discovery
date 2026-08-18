# Persister-State Refinement From GSE164715 scRNA

## Purpose

This note refines the digital twin's `P` drug-tolerant persister state using the first targeted single-cell import from `GSE164715`.

The import uses selected PDX samples:

- `HBCx95_chemonaive`
- `HBCx95_persister`
- `HBCx95_residual`
- `HBCx95_resistant`
- `HBCx95_recurrent`
- `HBCx39_chemonaive`
- `HBCx39_persister`
- `HBCx172_chemonaive`
- `HBCx172_persister`

The current import is signature-targeted rather than full transcriptome clustering. It is designed to refine the digital twin while keeping the pipeline lightweight.

## Import Scale

- Cells scored: 66,515.
- Samples imported: 9.
- Target genes detected: 154.
- Data source: `GSE164715_RAW.tar`.

## Human/Mouse Filtering Update

The PDX matrices contain both human (`hg19`) and mouse (`mm10`) features. A species-aware filtering pass was therefore added before final `P`-state interpretation.

Human-dominant filtering result:

- Total cells inspected: 66,515.
- Human-dominant cells retained: 26,730.
- `HBCx95_persister` is mostly mouse-dominant: 541 human-dominant cells versus 14,722 mouse-dominant cells.
- `HBCx39_persister` is mostly human-dominant: 2,421 human-dominant cells.
- `HBCx172_persister` contains a smaller human-dominant compartment: 461 human-dominant cells.

This changes the interpretation of the first import: large vascular/niche signals in the mixed import are likely host/niche enriched and should not be treated as malignant persister identity.

## Key Finding

Before species filtering, the strongest persister-minus-chemonaive targeted gene increases in `HBCx95` included:

- `FLT1`
- `CDH5`
- `PECAM1`
- `CXCL12`
- `KDR`
- `ESAM`
- `ENG`
- `RAMP2`
- `APOE`
- `SPARC`

This is biologically informative but needs careful interpretation. Several of these genes are vascular, endothelial, stromal, or niche-associated. They may indicate a persister-supportive microenvironment or residual niche signal rather than pure malignant-cell persister identity.

After human-dominant filtering, the top persister-associated targeted genes shift toward a more tumor/stress-like set:

- `FTL`
- `FTH1`
- `GPX4`
- `KRT14`
- `KRT19`
- `TAGLN`
- `YAP1`
- `SMAD2`
- `HIF1A`
- `BNIP3`
- `LAMC2`
- `S100A4`

## Candidate Tumor/Persister Markers To Prioritize

The following genes are better candidates for the tumor-cell persister refinement layer because they connect more directly to EMT, stress tolerance, immune evasion, or plasticity:

| Candidate | Rationale |
| --- | --- |
| `NOTCH1` | Plasticity and cell-state switching. |
| `WWTR1` | TAZ/YAP-axis mechanotransduction and therapy tolerance. |
| `YAP1` | Adaptive survival and EMT-associated resistance. |
| `TGFB1` | EMT and persister-supportive signaling. |
| `HMOX1` | Oxidative stress tolerance. |
| `GAS6` | AXL/TAM-axis support. |
| `ZEB1` | EMT plasticity and non-genetic resistance. |
| `CD274` | Immune-evasive residual state. |
| `SPARC` | ECM/stress-associated residual tumor niche. |
| `TJP1` | Hybrid epithelial/plastic state marker candidate. |
| `FTH1` / `FTL` | Iron/stress-response and ferroptosis-resistance context. |
| `KRT14` | Basal/persister-like TNBC state in some models. |
| `KRT19` | Epithelial/plastic residual tumor-state signal. |
| `TAGLN` | Stress/contractile mesenchymal program; interpret with stromal caution. |
| `SMAD2` | TGF-beta pathway relay. |
| `HIF1A` / `BNIP3` | Hypoxia/stress adaptation. |
| `LAMC2` / `S100A4` | EMT/invasion-associated residual-state signal. |

## Niche/Contamination Markers To Track Separately

These should not be automatically added to the tumor persister score without malignant-cell filtering:

- `FLT1`
- `CDH5`
- `PECAM1`
- `KDR`
- `ESAM`
- `ENG`
- `RAMP2`
- `CXCL12`

Recommended use:

- Keep these as a **persister-niche / vascular-survival axis**.
- Do not merge them directly into the `P` tumor-cell state until full scRNA cell-type filtering is complete.
- In PDX data, mouse-dominant cells should be treated as host/niche context, not malignant persister cells.

## Recommended Digital-Twin Update

Do not replace the current `P` state yet. Instead, split persister evidence into three layers:

1. **Tumor-cell persister score**
   - `ALDH1A1`, `PROM1`, `CD44`, `NOTCH1`, `YAP1`, `WWTR1`, `ZEB1`, `HMOX1`, `GAS6`, `TGFB1`, `CD274`, `KRT14`, `KRT19`, `SMAD2`, `LAMC2`, `S100A4`.

2. **Stress/ferroptosis-tolerance score**
   - `FTH1`, `FTL`, `HMOX1`, `SLC7A11`, `GPX4`, `NFE2L2`, `HIF1A`, `BNIP3`.

3. **Persister-niche score**
   - `FLT1`, `CDH5`, `PECAM1`, `KDR`, `ESAM`, `ENG`, `CXCL12`, `RAMP2`, `SPARC`.

## Next Analysis Needed

The first species-aware filter, production scoring-config update, and targeted malignant/endothelial/stromal/immune annotation are now complete. The next refinement tasks are:

1. Rank persister markers within human-dominant malignant-like cells only.
2. Compare human-dominant persister axes with `GSE43502` recurrence-associated residual samples.
3. Use mouse-dominant and mixed cells as host/niche context for a separate residual-niche module.
4. Validate the targeted annotation with fuller marker panels before publication-grade claims.
5. Keep uncertainty and cohort-relative percentile reporting in all clinician-facing summaries.

## Bottom Line

`GSE164715` confirms that persister biology is not a single clean EMT score. The digital twin should treat persister risk as a combination of **tumor-cell plasticity**, **stress tolerance**, and **supportive residual niche signals**.
