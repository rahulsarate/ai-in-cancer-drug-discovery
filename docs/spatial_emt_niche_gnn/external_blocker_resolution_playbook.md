# External Blocker Resolution Playbook

This playbook covers the three blockers that cannot be solved by code alone:
gated HuggingFace resources, HTAN/Synapse/Gen3 credentials, and expert
pathologist review.

## Current Local Readiness

The required local clients are installed.

| Area | Local status | Verification |
| --- | --- | --- |
| HuggingFace access checks | ready | `scripts/check_foundation_model_access.py` |
| HTAN CLI | ready | `.venv-deconv\Scripts\htan.exe config check` |
| Synapse client | ready | `.venv-deconv\Scripts\synapse.exe` |
| Gen3 client | ready | `.venv-deconv\Scripts\gen3.exe` |
| Pathologist queue | ready | `data/processed/spatial_emt_niche_gnn_pathology_review/pathologist_review_queue.tsv` |

## HEST, UNI, And CONCH

### Best Route

Use an institutional HuggingFace account and request/accept access terms for:

- `MahmoodLab/hest`
- `MahmoodLab/UNI2-h`
- `MahmoodLab/UNI`
- `MahmoodLab/CONCH`

Use a read-only or fine-grained token. Do not store it in the repo.

```powershell
$env:HF_TOKEN="hf_your_token_here"
.venv-deconv\Scripts\python.exe scripts\check_foundation_model_access.py
```

Expected unlock sequence:

1. Metadata visible, gated auto/manual access still pending.
2. Terms accepted and token configured.
3. Access check returns downloadable status.
4. Cache only cancer-relevant HEST metadata first.
5. Download small HEST cancer subset before full-scale image download.
6. Run UNI2/CONCH embeddings on selected review batches before whole-cohort runs.

### Why This Is The Best Route

The project does not need the entire gated ecosystem immediately. The highest
value first run is to embed the same high-priority spots already selected for
pathologist review, then compare foundation embeddings against:

- color/stain baseline features,
- histology-similarity edges,
- AI-selected review class,
- pathologist consensus labels.

This gives a biologically interpretable benchmark before spending time on
full-scale HEST ingestion.

## HTAN Assay Download

### Best Route

Use the HTAN portal to select exact file IDs, then download through Synapse or
Gen3 depending on file access type.

```powershell
.venv-deconv\Scripts\htan.exe config check
.venv-deconv\Scripts\synapse.exe login
```

For Gen3-controlled files, configure the portal-generated credentials/profile:

```powershell
.venv-deconv\Scripts\gen3.exe --help
```

Target workflow:

1. Open `https://data.humantumoratlas.org/explore`.
2. Filter for HTAN WUSTL, pancreatic cancer, spatial transcriptomics, and
   Level 3 or Level 4 files.
3. Export or copy the HTAN file IDs and Synapse/Gen3 download instructions.
4. Save the selected-file manifest under
   `data/raw/spatial/htan/wustl_pdac/manifest/`.
5. Download one open-access sample first.
6. Standardize into the existing expression/metadata format.
7. Add controlled files only after credentials, DUA, and institutional rules
   are clear.

### Backup Route

If HTAN file access is slow, use HTAN publications and GEO-linked companion
accessions as a bridge. This keeps validation moving while controlled portal
credentials are being approved.

## Pathologist Review

### Best Available Option

Use a small expert panel rather than a single reviewer.

| Role | Who | What they do | Minimum load |
| --- | --- | --- | --- |
| Lead reviewer | GI/thoracic/breast pathologist or translational pathology collaborator | Calibrates rubric, scores difficult cases, adjudicates disagreement | 100 to 150 spots |
| Second reviewer | pathology fellow, senior resident, or second attending | Independent overlap scoring | 80 to 120 spots |
| Scientific reviewer | cancer biologist or computational pathologist | Checks transcriptomic interpretation, not morphology truth | 50 to 100 spots |

Best sourcing order:

1. Academic collaborator or tumor-board contact.
2. Digital pathology platform/case-sharing route, such as PathPresenter.
3. Local QuPath review pack for offline scoring.
4. Paid expert network or targeted professional platform for a small blinded
   pilot, with credential verification.
5. Public/community review only for non-clinical feasibility feedback, never as
   final ground truth.

### Quality Control Design

Use the 600-item queue in three phases:

1. Calibration: 60 shared spots across all reviewers.
2. Primary review: 400 to 450 spots split by cohort and AI review class.
3. Adjudication: 80 to 120 spots with disagreement, low confidence, or high
   biological impact.

Report:

- percent agreement,
- class-specific agreement,
- confidence-weighted consensus,
- cases excluded as artifact,
- AI/pathologist mismatch categories.

## Decision Rules

| Blocker | If solved | If delayed |
| --- | --- | --- |
| HEST/UNI/CONCH | Run foundation embeddings on review queue first | Keep color/stain baseline and publish as reproducible comparator |
| HTAN | Add external WUSTL PDAC validation | Use GEO/10x validation while credentials process |
| Pathologist review | Move from weak-label biology to morphology-anchored validation | Keep claims explicitly weak-label and hypothesis-generating |

## Sources

- HuggingFace user access tokens: https://huggingface.co/docs/hub/main/security-tokens
- HuggingFace gated model access: https://huggingface.co/docs/hub/main/models-gated
- Synapse programmatic download: https://docs.synapse.org/synapse-docs/downloading-data-programmatically
- HTAN data portal: https://data.humantumoratlas.org/explore
- PathPresenter: https://www.pathpresenter.com/
- QuPath: https://github.com/qupath/qupath
