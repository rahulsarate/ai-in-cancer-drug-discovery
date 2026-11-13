"""Generate an evidence-based resources, efficiency and accuracy PDF."""
from pathlib import Path
import json
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader

ROOT=Path(__file__).resolve().parent; RES=ROOT/'outputs/real_pilot'
r=json.loads((RES/'pilot_results.json').read_text()); b=json.loads((RES/'efficiency_benchmark.json').read_text())
v=json.loads((RES/'software_inventory.json').read_text()); e=r['exploratory_emt']; ep=r['primary_endpoints']
OUT=ROOT.parent/'output/pdf/pancreatic_project_resources_efficiency_accuracy.pdf'
OUT.parent.mkdir(parents=True,exist_ok=True)
for n,f in [('Body','arial.ttf'),('Bold','arialbd.ttf')]:pdfmetrics.registerFont(TTFont(n,str(Path('C:/Windows/Fonts')/f)))
W,H=A4; LEFT=45; CW=W-90
NAVY='#102C40'; TEAL='#087E83'; INK='#173244'; MUTED='#526675'; BG='#F4F6F5'; AMBER='#9C6116'
c=canvas.Canvas(str(OUT),pagesize=A4); c.setTitle('Pancreatic Image Project: Resources, Efficiency and Accuracy'); c.setAuthor('Pancreatic Image Analysis Project')
page=0

def txt(s,x,y,w,size=10.5,color=INK,bold=False,maxh=700):
    p=Paragraph(str(s),ParagraphStyle('p',fontName='Bold' if bold else 'Body',fontSize=size,leading=size*1.39,textColor=HexColor(color)))
    _,h=p.wrap(w,maxh)
    if h>maxh+.1:raise ValueError(f'Page {page} overflow: {s[:80]} ({h}>{maxh})')
    p.drawOn(c,x,y-h);return h

def box(x,y,w,h,color):
    c.setFillColor(HexColor(color));c.roundRect(x,y,w,h,8,fill=1,stroke=0)

def start(label,title,sub=''):
    global page
    page+=1;c.setFillColor(HexColor(BG));c.rect(0,0,W,H,fill=1,stroke=0)
    c.setFillColor(HexColor(TEAL));c.rect(0,H-8,W,8,fill=1,stroke=0)
    txt(label.upper(),LEFT,H-35,CW,9,TEAL,True)
    used=txt(title,LEFT,H-59,CW,24,NAVY,True,maxh=80)
    y=H-59-used-12
    if sub:y-=txt(sub,LEFT,y,CW,10,MUTED,maxh=45)+15
    c.setStrokeColor(HexColor('#D7E0E3'));c.line(LEFT,43,W-LEFT,43)
    txt('TCGA-PAAD TECHNICAL PILOT | RESEARCH ONLY | 13 NOVEMBER 2026',LEFT,31,CW-30,7,MUTED)
    txt(f'{page:02d}',W-LEFT-20,32,20,9,TEAL,True)
    return y

def heading(s,y):
    return y-txt(s,LEFT,y,CW,14,TEAL,True,maxh=45)-9

def para(s,y,size=10.5):
    return y-txt(s,LEFT,y,CW,size,maxh=y-65)-13

def callout(title,body,y,height=104):
    box(LEFT,y-height,CW,height,'#E1EFED')
    txt(title,LEFT+15,y-14,CW-30,12,TEAL,True,maxh=34)
    txt(body,LEFT+15,y-42,CW-30,10.5,maxh=height-52)
    return y-height-18

def table(headers,rows,y,widths=None,size=9.5):
    widths=widths or [CW/len(headers)]*len(headers)
    for i,row in enumerate([headers]+rows):
        heights=[]
        for s,w in zip(row,widths):
            p=Paragraph(str(s),ParagraphStyle('cell',fontName='Bold' if i==0 else 'Body',fontSize=size,leading=size*1.35))
            heights.append(p.wrap(w-18,700)[1])
        rh=max(heights)+20
        if y-rh<65:raise ValueError(f'Page {page}: table beyond footer')
        x=LEFT
        for j,(s,w) in enumerate(zip(row,widths)):
            c.setFillColor(HexColor(NAVY if i==0 else ('#FFFFFF' if i%2 else '#EAF0F1')));c.rect(x,y-rh,w-2,rh-2,fill=1,stroke=0)
            txt(s,x+9,y-10,w-18,size,'#FFFFFF' if i==0 else INK,i==0,maxh=rh-17)
            x+=w
        y-=rh
    return y-17

# 1
y=start('Evidence brief','Resources, efficiency<br/>and accuracy','Pancreatic cancer image analysis | Real-data pilot evidence and resource rationale')
y=callout('Main conclusion','The workflow processed all 24 selected real patients. Its exploratory RNA-score prediction has not established an advantage over a simple baseline. Clinical diagnostic and staging accuracy remain unmeasured.',y,118)
y=table(['Evidence domain','Measured finding'],[
('Real dataset','24 TCGA-PAAD patients; 24 diagnostic SVS slides; 24 primary-tumor RNA files; 768 tissue tiles.'),
('Technical completion','48/48 source files verified; 24/24 patients processed; no final processing exclusions.'),
('Exploratory error',f"Image-model MAE {e['model_mae']:.3f}; mean-baseline MAE {e['baseline_mae']:.3f}. Lower error is better."),
('Clinical accuracy','No cancer-versus-benign test, four-stage classifier, EMT progression test or therapy-response study was performed.')],y,[125,CW-125])
y=heading('How to read this document',y)
y=para('Resources are grouped into actual data, software and interpretive/reporting references. Efficiency is reported only for measured technical steps. Accuracy is described using regression error and uncertainty, not an invented percentage of correct cancer diagnoses.',y)
y=para('All real-data results are separate from the earlier artificial-image demonstration. Its 100% synthetic stage result is not clinical evidence and is excluded from performance claims here.',y)
c.showPage()

# 2
y=start('01 / Data resources','What data were used, and why?','Actual source: NCI Genomic Data Commons (GDC), project TCGA-PAAD. [1-3]')
y=table(['Resource','How it was used','Why it matters / limitation'],[
('TCGA-PAAD diagnostic pathology','24 primary diagnostic 01Z/DX SVS files, one per selected patient.','Provides real H&E morphology and scanner metadata. Tissue regions remain unreviewed for tumor content.'),
('GDC clinical metadata','Primary diagnosis, morphology 8500/3, prior treatment, exact pathological stage and staging edition.','Prevents treating every pancreatic-project case as eligible PDAC. Stage labels are references, not model predictions.'),
('GDC STAR-Counts RNA files','24 primary-tumor files; unstranded TPM for 13 prespecified genes.','Provides an independent expression-based exploratory target. Bulk RNA can contain stromal signal.'),
('GDC API and file metadata','Query response, file UUIDs, sizes, MD5 values, patient/sample links.','Makes acquisition reproducible and detects file corruption or ambiguous linkage.')],y,[112,183,CW-295],9.2)
y=heading('How the 24 patients were chosen',y)
y=para('The metadata audit identified 142 eligible unique patients. The pilot used the smallest eligible slide per patient and selected 24 by file size under a 4-GB cap. This is a resource-bounded convenience sample, not a random, consecutive or clinically representative cohort.',y)
y=callout('Pairing is by patient','The slide and RNA record belong to the same patient and primary-tumor category. Matching to the exact tissue block, spatial region or equivalent collection time was not established.',y,103)
c.showPage()

# 3
y=start('02 / Image and model software','Which tools performed the analysis?','Versions below describe the recorded pilot environment, not the newest available releases.')
y=table(['Tool / version','Actual role','Why it is important'],[
(f"Python {r['provenance']['python']}",'Scripts, configuration, manifests and reproducible execution.','A common implementation language connecting acquisition, image processing and analysis.'),
(f"OpenSlide Python {v['openslide-python']}<br/>OpenSlide bin {v['openslide-bin']}",'Read SVS regions, level-0 coordinates, MPP and source color profiles.','Reads large slides region by region and preserves physical-scale provenance. [4]'),
(f"Pillow {v['Pillow']}",'Resize images, apply ICC-to-sRGB conversion and save PNGs.','Produces consistent readable exports. Color management corrected an oversized-profile export problem; this is not stain normalization.'),
(f"NumPy {v['numpy']}",'Tissue masks, RGB summaries, gene-score calculations and patient means.','Makes the 18-feature baseline and score formula explicit and reproducible.'),
(f"scikit-learn {v['scikit-learn']}",'StandardScaler, Ridge(alpha=10), site-held-out folds and training-mean baseline.','Fits a simple auditable baseline; training-only scaling reduces leakage. Regularization does not establish biological validity. [5]')],y,[125,182,CW-307],9.2)
y=para('No GPU, pathology foundation-model encoder, deep neural network, tumor segmentation model or cell-level EMT detector was used in the real pilot. The earlier random-forest synthetic model was not reused.',y)
c.showPage()

# 4
y=start('03 / Supporting resources','Tools for evaluation, review and reporting','Software checks verify implementation behavior; they do not establish clinical performance.')
y=table(['Resource','Role and importance'],[
(f"Requests {v['requests']}",'Downloads GDC metadata/files over HTTPS. Size and MD5 verification provide integrity checks.'),
(f"SciPy {v['scipy']}",'Calculates Spearman rank correlation. This detects a different aspect of association than absolute error.'),
(f"Matplotlib {v['matplotlib']}",'Plots out-of-fold predictions and baseline comparisons so weak performance is visible.'),
(f"Streamlit {v['streamlit']}",'Local read-only pilot dashboard, real image gallery, provenance and downloadable reports. It is not a validated clinical viewer.'),
(f"pytest {v['pytest']}",'Ten automated tests passed in the completed pilot; they cover data/label handling, leakage checks and workflow behavior.'),
(f"threadpoolctl {v['threadpoolctl']}",'Limits model benchmark BLAS execution to one thread, making the small timing experiment easier to describe.'),
('ReportLab + Poppler','Generate PDF artifacts and render pages for visual review. These support communication and quality checking, not predictive accuracy.')],y,[139,CW-139],9.5)
y=para(f"Joblib {v['joblib']} is a dependency and was used for the earlier synthetic artifacts. The real pilot did not release a fitted clinical inference model; it saves auditable out-of-fold results instead.",y)
c.showPage()

# 5
y=start('04 / Scientific and reporting references','Why the external references matter','These are methodological or educational resources, not training datasets.')
y=table(['Reference','Importance to this project','What it does not establish'],[
('EMT consensus: Yang et al., 2020 [6]','Frames EMT as heterogeneous and context dependent; supports caution about single markers and state versus progression.','It does not validate the project\'s chosen 13-gene bulk composite.'),
('TRIPOD+AI, 2024 [7]','Informs transparent reporting of cohort selection, predictors, outcomes, evaluation, uncertainty and limitations.','A reporting crosswalk is not certification, full compliance or clinical validation.'),
('NCI pancreatic treatment PDQ [8]','Supplies educational resectability/treatment discussion context for the separate clinical-context panel.','It does not make image-based treatment selection valid. No regimen or response model was trained.'),
('NCI TCGA acknowledgement [3]','Documents appropriate credit to the TCGA Research Network and the origin of the public data.','Open access is not a claim of endorsement or unrestricted use of every TCGA dataset.')],y,[123,190,CW-313],9.2)
y=heading('Resources considered but not used as pilot data',y)
y=para('CPTAC-PDA/TCIA was considered during dataset discovery, but no CPTAC slides or molecular files were used in the measured 24-patient pilot. CT/MRI, prospective hospital cases and new wet-lab assays were not included. This distinction prevents a resource list from overstating the evidence base.',y)
c.showPage()

# 6
y=start('05 / Measured efficiency','How efficiently did the workflow run?','Completion rates describe technical feasibility. They are not diagnostic accuracy.')
f=b['feature_extraction']; m=b['three_site_fold_fit_predict']; st=b['storage']
y=table(['Efficiency measure','Result','Interpretation'],[
('File integrity','48/48 verified (100%).','Every planned source file matched the repository size and MD5.'),
('Patient processing','24/24 evaluable (100%).','All selected cases passed the final technical processing path; no expert tumor approval is implied.'),
('Tile yield','768 total; 32 per patient.','Sampling was capped at 32. This is not tissue-QC sensitivity or full-slide coverage.'),
('Saved-PNG features',f"Median {f['median_seconds']:.3f} s / 768 tiles; {f['tiles_per_second_median']:.1f} tiles/s.",'Three passes, existing 256-pixel PNGs, local cached-file conditions; excludes native SVS tiling.'),
('Three-fold model fit + predict',f"Median {m['median_ms']:.2f} ms; P95 {m['p95_ms']:.2f} ms.",'50 repeats on the saved 24 x 18 feature matrix; one BLAS thread; imports excluded.'),
('Storage',f"Source SVS + RNA: {st['source_slide_and_rna_bytes']/1e9:.3f} GB. Retained tiles: {st['retained_png_tiles_bytes']/1e6:.1f} MB.",'Different content sets: sampled tiles omit almost all source pixels and all RNA. This is not a lossless compression ratio.')],y,[122,163,CW-285],9.1)
y=para('Benchmark hardware: Intel Core i5-9300H at 2.40 GHz, four physical cores/eight logical processors; approximately 15.8 GiB installed RAM; Windows and Python 3.14.3. No GPU was used for the timed steps. The image passes took '+', '.join(f'{x:.3f} s' for x in f['seconds_per_pass'])+'.',y,9.5)
y=callout('Not measured','Full-slide-to-report latency, acquisition throughput, peak RAM, clinical turnaround time, energy and cost per case were not recorded. The microbenchmark cannot support a production speed or cost-saving claim.',y,100)
c.showPage()

# 7
y=start('06 / Predictive accuracy','What accuracy can actually be reported?','The real model predicts a continuous exploratory RNA score, so regression metrics are appropriate. [5]')
improvement=(e['baseline_mae']-e['model_mae'])/e['baseline_mae']*100
y=table(['Metric','Measured value','Meaning'],[
('Mean absolute error (MAE)',f"{e['model_mae']:.4f}",'Average absolute difference between the observed bulk composite and its out-of-fold image prediction; score units.'),
('Mean-baseline MAE',f"{e['baseline_mae']:.4f}",'Predicts the training-fold mean for every held-out patient. A necessary comparator for any image model.'),
('Relative MAE reduction',f'{improvement:.2f}% (point estimate)','(Baseline MAE - model MAE) / baseline MAE x 100. This is an error reduction, not cancer-diagnosis accuracy.'),
('RMSE',f"{e['model_rmse']:.4f}",'Penalizes large prediction errors more strongly than MAE.'),
('R-squared',f"{e['model_r2']:.4f}",'Compared with the overall observed-target mean, squared error is reduced modestly. This is not percent correct.'),
('Spearman correlation',f"{e['spearman_r']:.4f}",'Near-zero rank association; the pilot does not reliably preserve the ordering of patients by the score.')],y,[122,102,CW-224],9.5)
y=heading('What the model was predicting',y)
y=para('Target = mean log2(TPM + 1) of VIM, FN1, CDH2, ZEB1, ZEB2, SNAI1, SNAI2, TWIST1 minus the corresponding mean of CDH1, EPCAM, KRT8, KRT18, KRT19. This prespecified contrast is unbounded; it is not a validated EMT assay, a percentage, or a measure of longitudinal progression.',y)
c.showPage()

# 8
y=start('07 / Uncertainty and site variation','Is the apparent improvement convincing?','Evaluation held out one TCGA tissue-source-site code at a time; it is still internal evaluation.')
maeci=e['model_mae_percentile_95']; dci=e['mae_improvement_over_mean_percentile_95']
y=callout('Predictive advantage is not established',f"Image-model MAE: {e['model_mae']:.3f}, with a descriptive interval of {maeci[0]:.3f} to {maeci[1]:.3f}. Baseline-minus-model MAE difference: {e['mae_improvement_over_baseline']:.3f}, interval {dci[0]:.3f} to {dci[1]:.3f}. The difference interval includes zero.",y,130)
folds=[]
for fold in e['folds']:
    folds.append((fold['held_out_site'],str(len(fold['test_patients'])),f"{fold['model_mae']:.3f}",f"{fold['baseline_mae']:.3f}"))
y=table(['Held-out site','Patients','Image MAE','Mean MAE'],folds,y,[139,75,145,CW-359],10)
y=para('The image model had lower error in the FB and HZ folds, but higher error in the two-patient HV fold. Site groups contain 6, 2 and 16 patients. Tissue-source-site codes do not necessarily identify scanners or individual hospitals.',y)
y=para('Intervals use 2,000 patient resamples of fixed out-of-fold predictions. They omit model refitting and site-cluster uncertainty. They are descriptive conditional intervals, not definitive evidence of generalization to another institution.',y)
y=para('Small size, convenience sampling, unreviewed tumor content, bulk stromal confounding and unverified block matching limit interpretation. There is no independent external cohort and no clinical calibration or decision threshold.',y)
c.showPage()

# 9
y=start('08 / Clinical limits and next evidence','Why a clinical accuracy percentage is unavailable','A technically successful pilot is a starting point for validation, not a clinical diagnostic product.')
y=table(['Clinical question','Current evidence status','What is needed next'],[
('Cancer versus benign','Not evaluated: cohort contains selected pancreatic ductal-carcinoma cases, not a diagnostic control population.','Expert diagnostic ground truth and appropriate benign/mimic cases.'),
('Full cancer stage','No model trained. Broad stages: I=2, II=21, III=1, IV=0.','Clinically appropriate multimodal staging evidence and an adequately sized cohort across the intended population.'),
('Malignant-cell EMT','Only an exploratory bulk expression contrast was predicted.','Tumor-region annotation, cell-aware/spatial assay validation and matched tissue blocks.'),
('EMT progression','Not assessed; no longitudinal model or matched trajectory study.','Paired timepoints, repeatable assays and controls for sampling/batch effects.'),
('Treatment response','Not evaluated; no treatment-outcome prediction study.','Defined treatment exposure, outcomes, follow-up and an appropriate prospective or causal study.')],y,[115,197,CW-312],9.2)
y=callout('Why an apparently high stage accuracy could mislead','Always guessing stage II would match 21/24 reference labels (87.5%) in this sample. This is a hypothetical class-imbalance illustration, not a trained or evaluated classifier. Sensitivity, specificity, AUC and clinical stage accuracy are therefore not reported.',y,118)
c.showPage()

# 10
y=start('09 / References and audit trail','Where every resource and number comes from','Primary references and local evidence were checked on 13 November 2026.')
refs=[
('[1] NCI GDC API: search and retrieval','https://docs.gdc.cancer.gov/API/Users_Guide/Search_and_Retrieval/'),
('[2] GDC mRNA pipeline: STAR quantification and TPM','https://docs.gdc.cancer.gov/Data/Bioinformatics_Pipelines/Expression_mRNA_Pipeline/'),
('[3] NCI: citing TCGA','https://www.cancer.gov/ccg/research/genome-sequencing/tcga/using-tcga-data/citing'),
('[4] OpenSlide Python: region reading, MPP and color profiles','https://openslide.org/api/python/'),
('[5] scikit-learn: regression metrics and model evaluation','https://scikit-learn.org/stable/modules/model_evaluation.html'),
('[6] Yang et al. EMT research consensus, 2020','https://www.nature.com/articles/s41580-020-0237-9'),
('[7] Collins et al. TRIPOD+AI, BMJ 2024;385:e078378','https://www.bmj.com/content/385/bmj-2023-078378'),
('[8] NCI pancreatic cancer treatment PDQ, professional version','https://www.cancer.gov/types/pancreatic/hp/pancreatic-treatment-pdq')]
for label,url in refs:
    y-=txt(label,LEFT,y,CW,9.4,NAVY,True,maxh=32)+3
    y-=txt(f'<link href="{url}" color="{TEAL}">{url}</link>',LEFT,y,CW,8.1,TEAL,maxh=32)+11
y=heading('Local evidence and reproducibility',y)
y=para('Performance: outputs/real_pilot/pilot_results.json and out_of_fold_predictions.csv. Timings: efficiency_benchmark.json, generated by benchmark_pilot.py. Versions: software_inventory.json and environment_versions.txt. Traceability: cohort_plan.json, download_receipts.json, patient_manifest.csv and tile_manifest.csv. These are under the pancreatic-image-analysis project directory.',y,9.1)
y=para('The timing rerun reproduced the saved exploratory MAE. Ten automated tests and a real-dashboard smoke check passed during the pilot; these are software checks, not clinical accuracy estimates. Review PILOT_PROTOCOL.md and PILOT_REPORTING_CHECKLIST.md for prespecified rules and outstanding work.',y,9.1)
y=para('Results are based on data generated by the TCGA Research Network: https://www.cancer.gov/tcga. No endorsement, ethics approval, clinical certification or treatment benefit is claimed.',y,9.1)
c.showPage();c.save();print(OUT)
