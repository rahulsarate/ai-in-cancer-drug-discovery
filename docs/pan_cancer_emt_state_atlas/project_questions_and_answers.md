# Pan-Cancer EMT State Atlas: Questions and Answers

## What is this project?

The Pan-Cancer EMT State Atlas is a research website that explains where tumor cohorts sit on the epithelial, hybrid EMT, mesenchymal, stromal-dominant, immune-inflamed, and hypoxic EMT landscape.

It combines bulk tumor expression, clinical associations, annotated single-cell data, spatial EMT niches, pathology review tasks, and target hypotheses in one evidence browser.

## What can I learn from one sample?

Open the Samples tab and search by sample ID. The sample view reports the consensus EMT state, confidence, partial EMT score, stromal contamination risk, hypoxia context, and a plain-language state explanation.

## What does hybrid E/M mean?

Hybrid E/M means the sample has both epithelial and mesenchymal features. It is often biologically important because plastic tumor cells may retain epithelial growth properties while gaining motility, invasion, therapy tolerance, or immune-remodeling behavior.

## How do I know whether EMT is tumor-intrinsic?

Use the Single-Cell tab. The atlas compares malignant cells with CAF/stromal and TAM/myeloid compartments. A strong malignant-cell signal is more supportive of tumor-intrinsic EMT; a CAF/stromal-enriched signal is flagged as possible stromal mimicry.

## What does a stromal warning mean?

A stromal warning means fibroblast, CAF, ECM, or related context may explain part of the bulk EMT signal. It does not mean the sample is unusable. It means the result should be interpreted with cell-type and spatial validation.

## Which cancers are covered?

The requested disease groups are covered: head and neck, breast, colon/intestine, pancreatic, brain, prostate, ovarian, skin, lung, oesophageal, and blood tumors.

The public 3CA annotated single-cell layer currently covers 10 disease groups and 32,626 cells across real cohorts from breast, colorectal, blood, brain, head and neck, lung, ovarian, pancreatic, prostate, and skin cancer.

## What are the most useful website views?

- Overview: see cohort size, confidence, state distribution, combined EMT pressure, stromal-mimicry caution, and real single-cell coverage.
- Disease Groups: compare cancer groups and warnings.
- Samples: search and download sample-level cards.
- Clinical: inspect survival screens, covariate availability, and model warnings.
- Single-Cell: separate malignant, CAF/stromal, and TAM/myeloid EMT-like signals.
- Spatial: review EMT niches and pathology priorities.
- Targets: inspect target families, lineage evidence, and validation ideas.
- Guide & Q&A: understand the atlas without reading the methods first.

## How should clinicians use it?

Use it to frame research questions, compare cohorts, identify possible tumor-intrinsic versus stromal EMT patterns, and select validation experiments or trial hypotheses. It is not a diagnostic tool, treatment recommendation, or replacement for pathology and clinical judgment.

## How should researchers use it?

Use the researcher mode and downloadable tables to reproduce state comparisons, inspect annotated compartments, check cohort warnings, trace evidence sources, and design validation assays.

## What do the target cards mean?

Target cards are ranked hypotheses that combine EMT context with dependency, druggability, compound availability, lineage evidence, and literature support where available. They are prioritization aids, not evidence that a treatment will work in a patient.

## What should I validate next?

The most useful next checks are usually:

1. Confirm malignant-cell EMT with CNV or an orthogonal tumor-cell marker panel.
2. Check CAF/TAM adjacency and hypoxia at the spatial or pathology level.
3. Test the leading target in invasion, organoid, perturbation, or combination assays.
4. Reproduce the finding in an independent cohort.

## Why are confidence and warnings shown everywhere?

EMT is a mixed biological program and bulk tissue contains multiple cell types. Confidence and warnings prevent a visually impressive score from being mistaken for a definitive biological or clinical conclusion.

## What are the current limitations?

TISCH2 and HTAN imports still depend on selected portal exports or credentials. Expert pathology labels still require human review. Clinical associations remain research screens and may be underpowered for some disease groups.

## What does research-only mean?

It means the atlas is designed to generate interpretable, testable hypotheses. It has not been validated for diagnosis, prognosis, treatment selection, or regulatory use.
