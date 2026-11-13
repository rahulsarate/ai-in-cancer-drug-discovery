# TNBC EMT Digital Twin: Project Questions and Answers

## Purpose and Scope

### What is this project?

This is a reproducible research prototype that represents triple-negative breast cancer (TNBC) during neoadjuvant chemotherapy as a changing mixture of epithelial (E), hybrid (H), mesenchymal (M), and drug-tolerant persister (P) programs. It integrates public transcriptomic cohorts, longitudinal evidence, external validation, single-cell review, and reporting safeguards. It is not a clinical decision-support device.

### Why focus on TNBC during neoadjuvant chemotherapy?

Residual TNBC after neoadjuvant chemotherapy is clinically important because it identifies a population with ongoing relapse risk. Response labels alone do not explain how a tumor may have survived therapy. The project is designed to expose possible therapy-tolerant biological states rather than only classify a binary outcome.

### What do E, H, M, and P mean?

- **E, epithelial-like:** a comparatively chemo-sensitive program.
- **H, hybrid:** a transitional epithelial-mesenchymal program associated with plasticity.
- **M, mesenchymal-like:** a resistance-associated program.
- **P, persister:** a drug-tolerant survival program.

These are score-derived research representations. They are not histopathology diagnoses and do not identify an individual patient's tumor state with clinical certainty.

## Evidence and Validation

### What is the principal external validation result?

In the independent GSE163882 RNA-seq TPM cohort (n=90), the combined feature model with external quantile-to-internal calibration achieved AUROC 0.649, AUPRC 0.714, accuracy 0.656, and Brier score 0.232. The bootstrap AUROC interval was 0.521 to 0.728. This is modest exploratory discrimination with material uncertainty, not evidence for clinical deployment.

### Why does the project show multiple calibration methods?

The training and independent cohorts use different assay platforms. Raw scores can be shifted for technical reasons. The project therefore reports raw, internal-percentile, external-z-score-to-internal, and external-quantile-to-internal results separately. This makes cross-platform limitations visible rather than hiding them behind a pooled metric.

### What did the longitudinal GSE43816 analysis contribute?

The analysis measured paired pre/post-NAC shifts in seven samples, including EMT, partial EMT, hypoxia, and persister-related features. The observed within-patient changes calibrated transition priors used in the therapy simulator. Seven pairs provide hypothesis-generating longitudinal evidence; they do not define a universal trajectory for future patients.

### What did the GSE43502 recurrence-axis analysis contribute?

The residual chemoresistant cohort was used to compare recurrence versus no-recurrence groups. AXL/TAM and hypoxia showed positive recurrence-minus-no-recurrence mean differences with bootstrap support. These are mechanistic leads for follow-up, not validated recurrence biomarkers.

### What did the GSE164715 single-cell layer contribute?

The workflow applied species filtering, persister scoring, targeted malignant/stromal/endothelial/immune annotation, and marker-direction validation. All 11 targeted marker-direction checks passed. Ambiguous compartments are retained in the output and must remain qualified in any publication-level claim.

### Why were response labels curated?

Public TNBC NAC metadata can mix broad good-response language with pathology evidence of residual disease. The project created a locked sensitivity analysis that conservatively recoded flagged GSE25055 and GSE25065 rows, and it reports curated results separately from original-label results.

## Novelty and Comparison

### What is novel about this work?

The novelty is an integrated, governed TNBC NAC workflow. It joins an E/H/M/P state representation, paired transition priors, separate tumor/stress/niche persister layers, response-label curation, platform-aware validation, single-cell ambiguity review, and clinician-style reporting boundaries in one reproducible package.

### How does this compare with standard pCR or residual-disease studies?

Standard studies establish why pCR and residual cancer burden matter. This project uses those endpoints but asks a different question: which therapy-tolerant biological states may be selected or enriched under therapy? It does not replace the clinical endpoint literature.

### How does it compare with EMT or drug-tolerant persister reviews?

Those reviews establish the biological rationale for plasticity and tolerance. This project turns the ideas into an executable TNBC NAC workflow with public cohorts, scoring, validation, curation, and explicit output limits.

### How does it compare with MRI-based TNBC digital twins?

MRI-based twins are often designed around tumor volume and treatment-response dynamics. This project focuses on transcriptomic EMT plasticity, persister programs, and microenvironment context. A future multimodal model could combine the strengths of both.

## Clinical Use and Limits

### Can a clinician use this to choose therapy today?

No. This research prototype must not be used to select, withhold, sequence, or recommend treatment. It does not produce validated individual pCR, recurrence, or survival predictions and it cannot replace pathology, imaging, molecular tumor-board review, or clinical guidelines.

### What is the responsible clinician-facing use?

It can frame research questions. For example, a clinician-scientist may ask whether a residual-disease program appears more consistent with plasticity, mesenchymal resistance, persister biology, or a microenvironmental niche, then decide what orthogonal pathology, molecular, or clinical-trial evidence would be needed to study that question.

### Why is uncertainty so prominent?

The user should see the same safeguards as the developer: cohort size, confidence intervals, label curation sensitivity, platform effects, and ambiguous single-cell compartments. This is necessary to prevent the portal from looking more clinically certain than the evidence allows.

### Can I upload an individual patient sample?

No. The project portal intentionally has no patient upload or individual-level prediction feature. It is a cohort-level research communication tool.

### What would be needed before clinical translation?

A defined intended use, prospective multi-site validation, protocol-matched assay and normalization procedures, pathology-reviewed outcomes, calibration monitoring, usability studies, fairness and privacy governance, a model-update policy, and any applicable regulatory review.

## Research Next Steps

### What is the most valuable next experiment?

A prospective TNBC NAC cohort with pre-treatment, on-treatment, and residual-disease biopsies; matched pathology-reviewed response/RCB and outcomes; and a standardized transcriptomic assay. Spatial proteogenomics would further resolve whether persister and niche signals arise in malignant, stromal, endothelial, or immune compartments.

### Which hypotheses are ready for testing?

The highest-value leads are whether AXL/TAM, hypoxia, YAP/TAZ, partial EMT, and refined persister signals are reproducibly associated with residual disease or recurrence after preregistered calibration, and whether their trajectories align with imaging dynamics under therapy.

### How can the work be reproduced?

Use the project configuration in `configs/tnbc_digital_twin.yml` and run:

```bash
python scripts/run_tnbc_digital_twin_pipeline.py --skip-existing
```

The frozen release under `docs/tnbc_digital_twin_emt_plasticity/frozen_releases/tnbc_digital_twin_freeze_2026-06-15/` contains the locked reports, tables, figures, and release documentation.
