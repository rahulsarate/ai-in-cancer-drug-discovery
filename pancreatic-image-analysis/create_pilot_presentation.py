"""Presentation of measured real-data pilot results, with actual TCGA image examples."""
from pathlib import Path
import csv
import json
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader

ROOT=Path(__file__).resolve().parent
DATA=ROOT/'data/real_pilot'; RESULTS=ROOT/'outputs/real_pilot'
OUT=ROOT.parent/'output/pdf/pancreatic_cancer_real_data_pilot.pdf'
OUT.parent.mkdir(parents=True,exist_ok=True)
r=json.loads((RESULTS/'pilot_results.json').read_text())
plan=json.loads((DATA/'cohort_plan.json').read_text())
patients=list(csv.DictReader((RESULTS/'patient_manifest.csv').open(encoding='utf-8')))
tiles=list(csv.DictReader((RESULTS/'tile_manifest.csv').open(encoding='utf-8')))
e=r['exploratory_emt']; ep=r['primary_endpoints']; f=plan['flow']
for name,file in [('Body','arial.ttf'),('Bold','arialbd.ttf')]:
    pdfmetrics.registerFont(TTFont(name,str(Path('C:/Windows/Fonts')/file)))
W,H=960,540; BG='#F4F6F5'; NAVY='#102C40'; TEAL='#087E83'; INK='#173244'; MUTED='#526675'; AMBER='#9C6116'
c=canvas.Canvas(str(OUT),pagesize=(W,H)); c.setTitle('Pancreatic Cancer | Real TCGA Data Technical Pilot'); c.setAuthor('Pancreatic Image Analysis Project')
page=0

def box(x,y,w,h,color,radius=9):
    c.setFillColor(HexColor(color)); c.roundRect(x,y,w,h,radius,fill=1,stroke=0)

def txt(s,x,y,w,size=14,color=INK,bold=False,maxh=300):
    p=Paragraph(str(s),ParagraphStyle('p',fontName='Bold' if bold else 'Body',fontSize=size,leading=size*1.32,textColor=HexColor(color)))
    _,h=p.wrap(w,maxh)
    if h>maxh+.1: raise ValueError(f'Overflow page {page}: {s[:90]} ({h}>{maxh})')
    p.drawOn(c,x,y-h); return h

def start(section,title,sub='',source=''):
    global page
    page+=1; c.setFillColor(HexColor(BG)); c.rect(0,0,W,H,fill=1,stroke=0)
    c.setFillColor(HexColor(TEAL)); c.rect(0,531,W,9,fill=1,stroke=0)
    txt(section.upper(),40,506,880,10,TEAL,True)
    txt(title,40,477,880,27,NAVY,True,maxh=73)
    if sub: txt(sub,40,433,880,12,MUTED,maxh=36)
    c.setStrokeColor(HexColor('#D7E0E3')); c.line(40,43,920,43)
    txt('REAL TCGA-PAAD DATA  /  TECHNICAL PILOT v1  /  RESEARCH ONLY  /  13 NOV 2026',40,30,835,8,MUTED)
    txt(f'{page:02d}',884,31,35,10,TEAL,True)
    if source: txt(source,40,64,880,8,MUTED,maxh=20)

def cards(items,note=''):
    gap=18; width=(880-gap*(len(items)-1))/len(items)
    for i,(title,body) in enumerate(items):
        x=40+i*(width+gap); box(x,120,width,280,'#FFFFFF')
        txt(f'{i+1:02d}',x+17,381,width-34,12,TEAL,True)
        txt(title,x+17,350,width-34,18,NAVY,True,maxh=51)
        txt(body,x+17,285,width-34,13,maxh=151)
    if note: txt(note,40,100,880,11,TEAL,True,maxh=30)
    c.showPage()

def table(rows,headers=('Area','Measured result','Meaning'),widths=(180,320,380)):
    y=397
    for i,row in enumerate([headers]+rows):
        rh=36 if i==0 else 65; x=40
        for j,s in enumerate(row):
            box(x,y-rh,widths[j]-3,rh-3,NAVY if i==0 else '#FFFFFF',3)
            txt(s,x+10,y-9,widths[j]-23,11,'#FFFFFF' if i==0 else INK,i==0,maxh=rh-15)
            x+=widths[j]
        y-=rh
    c.showPage()

def pic(path,x,y,w,h):
    c.drawImage(ImageReader(str(path)),x,y,w,h,preserveAspectRatio=True,anchor='c',mask='auto')

start('Real-data pilot','Pancreatic cancer: from concept to real data','A bounded, auditable technical pilot using NCI GDC / TCGA-PAAD pathology and RNA-seq')
box(40,153,565,244,NAVY)
txt('Real images.<br/>Traceable labels.<br/>Explicit evidence limits.',65,369,510,31,'#FFFFFF',True,maxh=135)
txt('A research step toward a future multimodal clinical platform',65,220,500,15,'#D9EEEE',maxh=48)
txt(str(ep['evaluable_patients']),650,385,240,49,TEAL,True,maxh=75)
txt('real patients processed',650,316,240,17,NAVY,True)
txt(f"{ep['verified_raw_files']} verified source files<br/>{ep['retained_tiles']} retained tissue tiles<br/>{ep['verified_raw_bytes']/1e9:.2f} GB of source data",650,267,240,15,maxh=100)
txt('No validated clinical stage, EMT progression or treatment-response prediction is claimed.',40,112,880,12,AMBER,True)
c.showPage()

start('01 / What changed','The real-data pilot is separate from the synthetic demo','Demonstration metrics are not reused in this report.')
cards([
('Real source data','Actual diagnostic SVS slides and STAR-Counts gene-expression files downloaded from GDC.<br/><br/>Every raw file passed size and MD5 verification.'),
('Pilot-grade controls','Configuration and cohort plan saved before analysis.<br/><br/>Patient/site traceability, physical-resolution metadata, rejection logs and a fixed baseline comparison.'),
('Honest endpoints','Primary aim: acquisition, linkage and tiling feasibility.<br/><br/>Secondary aim: exploratory bulk RNA association. Stage and treatment claims remain outside the evidence.')])

start('02 / Database and eligibility','TCGA-PAAD: explicit selection rules','The project name alone is insufficient to establish histological eligibility.',source='Sources: GDC API [1,2]; NCI TCGA acknowledgement [3]. References on the final slide.')
cards([
('Clinical metadata','Unique primary pancreatic diagnosis; morphology 8500/3; prior treatment recorded as No.<br/><br/>Unrelated metastases and non-ductal histologies are not used as the primary label.'),
('Image + RNA records','Primary diagnostic 01Z/DX slide and primary-tumor STAR-Counts RNA file.<br/><br/>Join by patient. Exact tissue-block and spatial correspondence are not established.'),
('Bounded sampling','Smallest eligible slide per patient, then first 24 by size; 4-GB cap.<br/><br/>This convenience sample favors small images and certain source sites. It is not representative.')])

start('03 / Cohort flow','Track acquisition and processing denominators','The full inventory and sequential exclusions are preserved in the acquisition plan.')
table([
('Source inventory',f"{f['inventory_files']} queried files; {f['slide_files']} slide files.",'TCGA-PAAD slide-image and gene-expression file metadata.'),
('Eligible population',f"{f['eligible_unique_patients']} unique metadata-eligible patients.",'One eligible diagnostic slide and primary-tumor RNA record per patient.'),
('Pilot selection',f"{ep['selected_patients']} patients; {ep['verified_raw_files']} verified files.",'Selection by size for technical feasibility, not by stage or outcome.'),
('Processing',f"{ep['evaluable_patients']} evaluable patients; {len(ep['exclusions'])} processing exclusions.",f"{ep['retained_tiles']} tiles retained. Expert tumor review remains outstanding.")])

start('04 / Real whole-slide examples','Actual pancreatic diagnostic slide overviews','Overview images demonstrate real data acquisition; they are not tumor annotations.',source='Image source: TCGA Research Network, accessed through NCI GDC. Patient/file UUIDs are in the manifest.')
for i,p in enumerate(patients[:2]):
    x=40+i*450; box(x,106,430,292,'#FFFFFF')
    pic(DATA/'thumbnails_srgb'/f"{p['patient_id']}.png",x+15,154,400,228)
    txt(p['patient_id'],x+15,140,400,13,TEAL,True)
    txt(f"Native MPP {float(p['native_mpp_x']):.4f}; unreviewed tissue",x+15,120,400,10,MUTED)
c.showPage()

start('05 / Real image tiles','Tissue tiles at a documented physical scale','Nominal 1 micrometer per pixel; 256 x 256 pixels. Tumor content has not been expert-adjudicated.')
for i,p in enumerate(patients[:4]):
    tile=next(t for t in tiles if t['patient_id']==p['patient_id'])
    x=40+i*225; box(x,133,205,264,'#FFFFFF')
    pic(ROOT/tile['tile_path'],x+10,193,185,185)
    txt(p['patient_id'],x+10,179,185,11,TEAL,True)
    txt(f"x={tile['x_level0']}, y={tile['y_level0']}<br/>Tissue fraction {float(tile['tissue_fraction']):.0%}",x+10,160,185,10,MUTED,maxh=29)
txt('Representative acquisition examples from the first four selected patients; no EMT or malignant-cell annotation is implied.',40,103,880,11,AMBER,maxh=30)
c.showPage()

start('06 / Reference-label availability','The stage distribution does not support four-stage training','Stage values are database reference labels, not model predictions.')
b=r['stage_counts_broad']
table([
('Stage I',str(b.get('I',0))+' patients','Too few for a credible stage-I performance estimate.'),
('Stage II',str(b.get('II',0))+' patients','Dominant class; majority-class predictions can look deceptively accurate.'),
('Stages III / IV',f"{b.get('III',0)} / {b.get('IV',0)} patients",'Rare or absent advanced stages prevent four-stage evaluation.'),
('Model decision',r['stage_model']['status'],f"Exact labels and staging editions retained: {r['staging_editions']}. No retrospective relabeling to balance classes.")],headers=('Broad reference stage','Observed count / decision','Pilot implication'))

start('07 / Biological endpoint','A prespecified exploratory bulk RNA composite','This endpoint is neither a validated EMT assay nor a percentage of cells undergoing EMT.',source='Conceptual EMT limitations follow the TEMTIA consensus [4]. This specific composite is exploratory.')
cards([
('Mesenchymal panel','VIM, FN1, CDH2, ZEB1, ZEB2, SNAI1, SNAI2 and TWIST1.<br/><br/>Compute the mean of log2(TPM + 1) across these eight genes.'),
('Epithelial panel','CDH1, EPCAM, KRT8, KRT18 and KRT19.<br/><br/>Subtract their mean log2(TPM + 1) from the mesenchymal mean. All 13 genes must be present.'),
('Interpretation limits','Unbounded expression contrast, not a universal biological scale.<br/><br/>Bulk signal can reflect fibroblasts. Different tissue blocks can weaken image/RNA correspondence. No progression measurement.')])

start('08 / Evaluation design','Hold out contributing sites, not individual tiles','Internal site-grouped evaluation; not independent external clinical validation.')
site_text=', '.join(f'{k}: {v}' for k,v in sorted(r['sites'].items()))
cards([
('One row per patient','Average 18 fixed RGB summary features over retained tissue tiles.<br/><br/>No stage or RNA target enters image selection. No cross-patient duplicate tile hashes were detected.'),
('Fixed analysis','StandardScaler + Ridge(alpha=10), fitted within each training fold.<br/><br/>Leave one TCGA source-site code out at a time. Compare against the same training-fold mean.'),
('Limited uncertainty',f'Source-site groups: {site_text}.<br/><br/>Patient bootstrap intervals use fixed out-of-fold predictions. They omit model-refit and site-cluster uncertainty.')],
'Source-site codes identify tissue contributors; they do not necessarily identify scanning laboratories.')

start('09 / Measured results','Exploratory results from real data','Report the baseline comparison regardless of direction; do not tune after seeing the result.')
pic(RESULTS/'exploratory_results.png',40,130,880,268)
verdict='The image model did not improve on the mean baseline.' if e['model_mae']>=e['baseline_mae'] else 'The point estimate favors the image model; uncertainty and external replication remain necessary.'
if e['mae_improvement_over_mean_percentile_95'][0]<=0<=e['mae_improvement_over_mean_percentile_95'][1]:
    verdict='The descriptive interval includes no improvement; predictive advantage is not established.'
txt(verdict,40,109,880,13,AMBER,True,maxh=35)
c.showPage()

start('10 / Result interpretation','Quantify error without claiming clinical performance','All values below refer to an exploratory expression contrast, not stage accuracy.')
ci=e['model_mae_percentile_95']; delta=e['mae_improvement_over_mean_percentile_95']
table([
('Image prediction',f"MAE {e['model_mae']:.3f}; RMSE {e['model_rmse']:.3f}.",f'Descriptive MAE interval: {ci[0]:.3f} to {ci[1]:.3f} score units.'),
('Mean baseline',f"MAE {e['baseline_mae']:.3f}.",'Training-only mean fitted independently in every site-held-out fold.'),
('Paired improvement',f"Baseline MAE minus model MAE: {e['mae_improvement_over_baseline']:.3f}.",f'Descriptive interval: {delta[0]:.3f} to {delta[1]:.3f}. Includes zero; an advantage is not established.'),
('Association',f"R-squared {e['model_r2']:.3f}; Spearman r {e['spearman_r']:.3f}.",'Small sample; no clinical threshold, biological assay validation or causal interpretation.')])

start('11 / Technical pilot gates','Technical completion is distinct from clinical validity','Acceptance rules were specified in the pilot protocol before analysis.')
g=r['technical_gates']
table([
('Raw-file integrity','PASS' if g['all_raw_files_verified'] else 'FAIL',f"{ep['verified_raw_files']} source files checked against repository size and MD5."),
('Evaluable patients','PASS' if g['at_least_22_evaluable_patients'] else 'FAIL',f"{ep['evaluable_patients']}/24 processed; required at least 22. Resource-based feasibility target."),
('Image traceability','PASS' if g['all_patients_have_at_least_8_tiles'] else 'FAIL','At least eight tiles per patient; coordinates, MPP and hashes retained.'),
('Clinical readiness','NOT ESTABLISHED','No expert tumor adjudication, valid four-stage cohort, prospective evaluation or treatment-response evidence.')])

start('12 / Pilot reporting practice','Use transparent reporting, not a compliance label','Reporting crosswalk is informed by TRIPOD+AI; no certification or full compliance is asserted.',source='Reporting reference: TRIPOD+AI, BMJ 2024;385:e078378 [5].')
cards([
('Prespecified + auditable','Versioned configuration, selection plan and fixed endpoints.<br/><br/>Inventory, download receipts, code hash, sample linkage, exclusions and analysis files remain reviewable.'),
('Data separation','Patient aggregation and source-site folds prevent direct tile leakage.<br/><br/>Training-only scaling and mean baseline. No feature or hyperparameter tuning on held-out predictions.'),
('Open limitations','Convenience sampling and tiny site groups disclosed.<br/><br/>Expert review, local governance, patient involvement, external validation and clinical utility remain outstanding.')])

start('13 / What cannot be concluded','The pilot establishes a data pipeline, not a clinical platform','Avoid promoting a feasible acquisition workflow into unsupported medical claims.')
cards([
('Anatomical stage','A primary-tumor image lacks the complete metastatic and vascular assessment.<br/><br/>This cohort cannot estimate performance across all four stages. No stage classifier was trained.'),
('EMT progression','The bulk RNA composite may reflect stromal content and spatial mismatch.<br/><br/>Longitudinal matched assays and malignant-cell localization are needed to study progression.'),
('Therapeutic benefit','Treatment exposure, outcomes and a suitable causal or prospective study are absent.<br/><br/>The earlier therapeutic panel remains educational, based on clinician-confirmed status.')])

start('14 / Next pilot phase','Spend the next phase on labels and cohort quality','Recommended next work; not completed or funded by this technical pilot.')
table([
('Pathology review','Expert-check a pilot subset, then all retained tumor regions.','Record tumor/stroma fractions, artifacts, adequacy and interobserver agreement.'),
('Biological validation','Confirm malignant-cell EMT with spatial or multiplex evidence.','Audit tissue-block/timepoint match; assess assay reliability and stromal confounding.'),
('Model comparison','Expand with prespecified sample size and external center(s).','Compare clinical-only, stain/site-only and pathology-encoder baselines under locked evaluation.'),
('Decision gate','Proceed only if the new endpoint and model add reliable value.','Negative or uncertain results trigger endpoint/model revision, not stronger clinical language.')],headers=('Work package','Next deliverable','Decision purpose'))

start('15 / Long-term clinical platform','Advance only when each evidence gate is met','Illustrative planning horizons; no approval or deployment date is promised.')
table([
('0-6 months','Technical pilot + expert label review','Use this pipeline to establish cohort access, annotation quality and biological validity.'),
('6-18 months','Expanded retrospective / external study','Power the intended endpoint; lock the model; quantify subgroup errors and calibration.'),
('18-30 months','Prospective silent evaluation','Test hospital workflow, review time, mismatch handling, uncertainty and operational failure.'),
('30+ months','Defined-use clinical translation','Appropriate clinical-impact evidence, jurisdiction-specific review, security and lifecycle monitoring.')],headers=('Illustrative horizon','Evidence stage','Required next capability'))

start('16 / Reproducible project files','Every displayed result has a local evidence trail','Raw data remain outside the source-code archive; reproducible download scripts are included.')
table([
('Acquire','acquire_pilot.py; pilot_config.json','GDC inventory, fixed cohort plan and checksum-verified source downloads.'),
('Analyze','run_real_pilot.py; requirements-pilot.txt','SVS tiling, gene composite, site-grouped evaluation and environment snapshot.'),
('Review','pilot_app.py; outputs/real_pilot/','Real images, manifests, gene TPMs, OOF predictions, figures and pilot_results.json.'),
('Audit','docs/PILOT_PROTOCOL.md; reporting checklist','Scope, rules, acceptance gates, missing work and attribution. Local plan/code hashes in results.')],headers=('Purpose','Files','Evidence retained'))

start('17 / References and attribution','Data and reporting references','Sources checked 13 November 2026. No TCGA endorsement is implied.')
refs=[
('[1] GDC API search and retrieval','https://docs.gdc.cancer.gov/API/Users_Guide/Search_and_Retrieval/'),
('[2] GDC API file downloads','https://docs.gdc.cancer.gov/API/Users_Guide/Downloading_Files/'),
('[3] NCI: citing TCGA','https://www.cancer.gov/ccg/research/genome-sequencing/tcga/using-tcga-data/citing'),
('[4] Yang et al. EMT research consensus, 2020','https://www.nature.com/articles/s41580-020-0237-9'),
('[5] Collins et al. TRIPOD+AI, BMJ 2024;385:e078378','https://www.bmj.com/content/385/bmj-2023-078378')]
y=395
for title,url in refs:
    txt(title,40,y,880,12,NAVY,True,maxh=20)
    txt(f'<link href="{url}" color="{TEAL}">{url}</link>',40,y-21,880,9,TEAL,maxh=17)
    y-=51
box(40,79,880,53,'#E1EFED')
txt('Results are based on data generated by the TCGA Research Network: https://www.cancer.gov/tcga.<br/>Real-data values: pilot_results.json and manifests. Clinical efficacy and biological validity remain unestablished.',55,118,850,11,maxh=37)
c.showPage(); c.save(); print(OUT)
