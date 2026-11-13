"""Build the project concept and clinical translation presentation PDF."""
from pathlib import Path
import json
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT=Path(__file__).resolve().parent
OUT=ROOT.parent/'output/pdf/pancreatic_cancer_project_presentation.pdf'
OUT.parent.mkdir(parents=True,exist_ok=True)
for n,f in [('Body','arial.ttf'),('Bold','arialbd.ttf')]:
    pdfmetrics.registerFont(TTFont(n,str(Path('C:/Windows/Fonts')/f)))
W,H=960,540
NAVY='#102C40'; TEAL='#087E83'; BG='#F4F6F5'; INK='#173244'; MUTED='#526675'; GOLD='#B27520'
c=canvas.Canvas(str(OUT),pagesize=(W,H))
c.setTitle('Pancreatic Cancer Image Analysis | From Research Prototype to Clinical Platform')
c.setAuthor('Pancreatic Image Analysis Project')
page=0

def box(x,y,w,h,color,r=12):
    c.setFillColor(HexColor(color)); c.roundRect(x,y,w,h,r,fill=1,stroke=0)

def txt(s,x,y,w,size=15,color=INK,bold=False,maxh=300):
    style=ParagraphStyle('t',fontName='Bold' if bold else 'Body',fontSize=size,leading=size*1.35,textColor=HexColor(color))
    p=Paragraph(s,style); _,h=p.wrap(w,maxh)
    if h>maxh+0.1: raise ValueError(f'Text overflow ({h}>{maxh}): {s[:90]}')
    p.drawOn(c,x,y-h)
    return h

def start(section,title,sub='',source=''):
    global page
    page+=1
    c.setFillColor(HexColor(BG)); c.rect(0,0,W,H,fill=1,stroke=0)
    c.setFillColor(HexColor(TEAL)); c.rect(0,H-9,W,9,fill=1,stroke=0)
    txt(section.upper(),40,506,880,10,TEAL,True)
    txt(title,40,479,880,27,NAVY,True,maxh=74)
    if sub: txt(sub,40,433,880,12,MUTED,maxh=40)
    c.setStrokeColor(HexColor('#D7E0E3')); c.line(40,43,920,43)
    txt('PDAC IMAGE + EMT  /  PROJECT PRESENTATION  /  13 NOV 2026',40,30,660,8,MUTED)
    txt(f'{page:02d}',885,31,35,10,TEAL,True)
    if source: txt(source,40,64,880,8,MUTED,maxh=18)

def cards(items,note=''):
    n=len(items); gap=18; width=(880-gap*(n-1))/n
    for i,(label,body) in enumerate(items):
        x=40+i*(width+gap); box(x,118,width,282,'#FFFFFF')
        box(x+18,359,36,24,TEAL,5); txt(f'{i+1:02d}',x+25,377,28,10,'#FFFFFF',True)
        txt(label,x+18,343,width-36,18,NAVY,True,maxh=52)
        txt(body,x+18,280,width-36,13,maxh=150)
    if note: txt(note,40,100,880,11,TEAL,True,maxh=30)
    c.showPage()

def rows(data,widths=(180,335,365),headers=('Domain','Available now','Next development')):
    x0=40; y=397; rowh=65
    for i,row in enumerate([headers]+data):
        h=37 if i==0 else rowh
        x=x0
        for j,value in enumerate(row):
            box(x,y-h,widths[j]-3,h-3,NAVY if i==0 else '#FFFFFF',3)
            txt(value,x+10,y-9,widths[j]-23,11,'#FFFFFF' if i==0 else INK,i==0,maxh=h-15)
            x+=widths[j]
        y-=h
    c.showPage()

# 01
start('Project vision','Pancreatic cancer image analysis','A research foundation for a future multimodal clinical platform')
box(40,150,570,246,NAVY)
txt('Connect morphology,<br/>tumor biology and clinical context.',65,369,520,29,'#FFFFFF',True,maxh=125)
txt('H&E pathology images + matched EMT assays + independently confirmed stage',65,238,510,15,'#D9EEEE',maxh=60)
txt('TODAY',655,377,240,11,TEAL,True)
txt('Runnable research prototype',655,350,240,23,NAVY,True,maxh=75)
txt('LONG-TERM AIM',655,255,240,11,TEAL,True)
txt('Evidence-based support for multidisciplinary review',655,229,240,20,NAVY,True,maxh=90)
txt('Research only. No real patient cohort or clinically validated model is included.',40,112,880,12,GOLD,True)
c.showPage()

start('01 / Clinical idea','Three different questions, three evidence needs','Scope: pathologist-confirmed pancreatic ductal adenocarcinoma (PDAC).',source='Sources: NCI PDQ [1]; EMT consensus [2]. Full references on slide 20.')
cards([
('Cancer stage','How far has disease spread?<br/><br/>Full staging requires clinical, radiological and pathological information. A primary-tumor tile cannot establish whole-body extent.'),
('EMT phenotype','What epithelial/mesenchymal features are present?<br/><br/>Use matched, tumor-aware molecular or spatial assays. A cross-sectional prediction is not a measure of progression.'),
('Therapeutic context','What should the care team review?<br/><br/>Resectability, diagnosis, fitness, organ function, molecular findings and patient goals guide discussion.')])

start('02 / Product concept','Begin with an auditable research workbench','A narrower first product makes the scientific question testable.')
cards([
('Primary user','Pathology and translational research teams studying image associations with a predefined EMT assay.<br/><br/>The first use is retrospective feasibility analysis.'),
('Core hypothesis','Patient-level morphology may contain reproducible information associated with EMT labels and broad stage labels.<br/><br/>This remains an unproven hypothesis.'),
('Success definition','Reproducible external performance beyond simple clinical/site baselines, interpretable failures and acceptable workflow burden.<br/><br/>Clinical benefit needs a later study.')])

start('03 / What is built','A working baseline with explicit boundaries','Completed software versus proposed clinical-platform capabilities.')
rows([
('Images','Single-frame H&E tile QC and RGB summary features.','Whole-slide ingestion, annotations and validated tumor-region selection.'),
('Models','Patient-level stage classifier and EMT regressor.','Compare pathology encoders, multiple-instance learning and multimodal models.'),
('Interface','Local tile upload, JSON report and context panel.','Hospital integration, role-based review and controlled report sign-off.'),
('Evidence','Synthetic workflow, four tests and dashboard smoke check.','Real cohort, external validation and prospective clinical studies.')])

start('04 / Data design','Build a cohort before building a clinical claim','Labels must be independent of model outputs and aligned to the same specimen/timepoint.')
cards([
('Images + provenance','Reviewed H&E tumor tiles; patient, specimen and site identifiers.<br/><br/>Record stain, scanner, physical resolution, specimen type and pretreatment status.'),
('Clinical reference','Confirmed PDAC diagnosis; cTNM/pTNM basis and staging edition in the cohort database.<br/><br/>Keep treatment timing, procedure and resectability distinct.'),
('Biological reference','Matched EMT assay with prespecified normalization and tumor-cell localization.<br/><br/>Measure assay reliability and stromal contamination. Use one harmonized score definition.')],
'Current manifest: patient_id | image_path | stage | emt_score | emt_assay | site_id')

start('05 / Analysis workflow','From reviewed tiles to a patient-level research report','One specimen/timepoint per patient in the current implementation.')
steps=[('01','Reviewed tiles'),('02','QC + 18 features'),('03','Patient averaging'),('04','Two random forests')]
for i,(num,label) in enumerate(steps):
    x=40+i*225
    box(x,277,205,105,NAVY if i==3 else '#FFFFFF')
    txt(num,x+15,365,175,13,'#7ACAC4' if i==3 else TEAL,True)
    txt(label,x+15,332,175,17,'#FFFFFF' if i==3 else NAVY,True,maxh=50)
    if i<3: txt('>',x+208,332,17,18,TEAL,True)
box(40,126,880,117,'#E1EFED')
txt('Split by patient before fitting: 60% training / 20% validation / 20% test',60,224,835,18,TEAL,True)
txt('Outputs: stage-associated votes + EMT assay association + feature-range warning + JSON report.<br/>The model does not diagnose cancer, determine clinical stage or select therapy.',60,184,835,14,maxh=50)
c.showPage()

start('06 / Demonstration output','Software pipeline verified on artificial data','SYNTHETIC ONLY - no clinical or biological performance claim.')
metrics=json.loads((ROOT/'outputs/metrics.json').read_text())
cards([
('80 fictional patients','160 artificial texture tiles.<br/><br/>48 train / 16 validation / 16 test patients.<br/><br/>No real pancreatic tissue images are included.'),
('Held-out demo metrics',f"Stage balanced accuracy: <b>{metrics['test']['stage_balanced_accuracy']:.0%}</b><br/><br/>EMT MAE: <b>{metrics['test']['emt_mae']:.4f}</b> on the artificial 0-1 scale.<br/><br/>The generator deliberately encodes labels in color."),
('What this proves','Training, artifact saving, patient splitting, evaluation and inference can run end to end.<br/><br/>It does not show ability to stage cancer or measure EMT.')],
'Four automated tests passed; dashboard rendering and clinical-context interaction also passed.')

start('07 / Example patient report','Make every output traceable and qualified','Illustrative report from an in-training synthetic sample - not independent validation.')
pred=json.loads((ROOT/'outputs/prediction.json').read_text())
rows([
('Stage association',f"Class {pred['stage_association']}; vote fraction 0.9917.",'Uncalibrated forest vote; clinical stage remains undetermined.'),
('EMT association',f"{pred['emt_assay_association']:.4f}; assay: SYNTHETIC_DEMO.",'Artificial cross-sectional score; not a percentage of cells undergoing EMT.'),
('Progression','Reported as not determined.','Requires longitudinal matched samples and assay validation.'),
('Clinical context','Selected independently by clinician-confirmed resectability.','Educational discussion only; no image-driven prescription.')],headers=('Report field','Current demo value','Required interpretation'))

start('08 / Biological strategy','Validate EMT in malignant cells, not just tissue color','A future image model needs reliable molecular ground truth.',source='Source: Yang et al., EMT research consensus [2].')
cards([
('Define the endpoint','Prespecify the marker/signature panel, score mapping and assay repeatability.<br/><br/>EMT is heterogeneous and context dependent; a single marker is insufficient.'),
('Localize the signal','Distinguish malignant epithelial cells from fibroblasts and other stromal cells.<br/><br/>Use spatial, multiplex or single-cell evidence where feasible.'),
('Study change separately','Collect paired baseline, on-treatment and progression specimens.<br/><br/>Control batch and sampling effects; test longitudinal models before labeling change as progression.')])

start('09 / Therapeutic approach','Support an informed multidisciplinary discussion','Educational pathway categories; actual care remains patient-specific.',source='Source: NCI professional pancreatic cancer treatment summary [1].')
rows([
('Resectable','Surgical assessment and perioperative systemic therapy discussion.','Review stage, fitness, anatomy, pathology and patient preferences.'),
('Borderline resectable','Neoadjuvant therapy and reassessment discussion.','Multidisciplinary review determines the pathway.'),
('Locally advanced','Systemic therapy and selected local approaches.','Discuss response, symptoms and appropriate trials.'),
('Metastatic','Systemic and eligible biomarker-directed options; symptom care.','Molecular assessment, goals and trial eligibility inform review.')],headers=('Clinician-entered status','Discussion domain','Clinical review'))

start('10 / Platform vision','Proposed architecture for a clinical-grade service','Future architecture - these production services are not implemented today.')
layers=[
('Clinical systems','Pathology slides + annotations | radiology/PACS | EHR | molecular laboratory'),
('Governed data layer','Deidentification | identity linkage | consent/access rules | provenance | versioned labels'),
('Analysis services','Tile QC | image encoder/MIL | optional CT model | assay alignment | calibrated model outputs'),
('Review workspace','Evidence view | uncertainty/abstention | clinician review | signed report | audit trail'),
('Operations','Model registry | monitored deployment | drift review | incident response | controlled updates')]
for i,(title,body) in enumerate(layers):
    y=337-i*51
    box(40,y,880,44,NAVY if i==3 else '#FFFFFF',6)
    txt(title,55,y+31,180,12,'#FFFFFF' if i==3 else TEAL,True,maxh=30)
    txt(body,240,y+31,660,11,'#FFFFFF' if i==3 else INK,maxh=32)
txt('Integration candidates: DICOM/DICOMweb and HL7 FHIR, subject to hospital capabilities and local requirements.',40,95,880,11,MUTED,maxh=30)
c.showPage()

start('11 / Clinical workflow','Design around accountable human review','The research model supplies evidence; the clinical team owns interpretation.')
cards([
('Before analysis','Confirm diagnosis and intended use.<br/><br/>Verify patient/specimen match, timing, image suitability and assay provenance.<br/><br/>Reject unusable or unsupported inputs.'),
('At review','Display evidence provenance, uncertainty, quality failures and model version.<br/><br/>Separate image associations from confirmed clinical findings. Require reviewer sign-off.'),
('After review','Retain an auditable report and record corrections.<br/><br/>Monitor failures, workload and disagreement.<br/><br/>New model versions require controlled evaluation and release.')])

start('12 / Evidence roadmap','Move forward through evidence gates','Illustrative 36+ month plan; timing depends on cohort access, results and intended use.')
rows([
('0-6 months','Research foundation','Protocol, ethics/data agreements, assay definition, pilot cohort and QC. Gate: usable labels and repeatable assays.'),
('6-12 months','Retrospective development','Compare baseline/encoder models and confounder controls. Gate: reproducible patient-level benefit.'),
('12-24 months','External + silent study','Lock model; evaluate unseen centers and prospective workflow. Gate: prespecified performance and usable review.'),
('24-36+ months','Clinical translation','Impact study, deployment controls and applicable review. Gate: evidence and authorizations for the defined use.')],headers=('Planning horizon','Work package','Deliverable and decision gate'))

start('13 / Validation plan','Measure reliability before measuring adoption','Specify numerical acceptance criteria with clinicians and statisticians before the study.')
cards([
('Analytical performance','Independent patient/site/time splits; no test-driven normalization or tuning.<br/><br/>Classwise error, calibration, EMT error and patient-bootstrap uncertainty. Test against assay repeatability.'),
('Generalizability','Held-out institutions, scanners and specimen types.<br/><br/>Check shortcuts, subgroup uncertainty, missing labels, rejected cases and distribution shift. Compare clinical-only baselines.'),
('Clinical usefulness','Prospective silent evaluation first, then a suitable impact study.<br/><br/>Assess review time, errors, clinician interpretation and patient-relevant benefit. Stage agreement alone is insufficient.')])

start('14 / Development controls','Treat lifecycle management as part of the product','Exact obligations depend on jurisdiction, intended use and device classification.',source='Reference: FDA AI-enabled device lifecycle draft guidance, January 2025 [3]; draft, not a binding approval pathway.')
cards([
('Governance + security','Define purpose, access and retention with each partner.<br/><br/>Role-based access, encryption, audit trails, security testing and incident ownership.<br/><br/>Confirm local privacy obligations.'),
('Quality + safety','Maintain requirements, risk analysis, traceability and verified releases.<br/><br/>Specify abstention behavior, human factors, version history and rollback.<br/><br/>Research tooling is not clinical clearance.'),
('Regulatory planning','Obtain qualified advice early for each intended market.<br/><br/>Confirm study evidence and submission requirements; assess model-change controls.<br/><br/>No approval or timeline is assumed.')])

start('15 / Team and sustainability','A clinical partnership, supported by engineering','Staffing and resource categories are planning proposals, not committed funding.')
cards([
('Core partnership','Clinical lead: pancreatic oncology/surgery.<br/><br/>Pathology lead and molecular/EMT scientist.<br/><br/>Biostatistician, data steward and patient/public input.'),
('Build + operate','ML engineer, data engineer and platform engineer.<br/><br/>Annotation/QC capacity; product and clinical-integration support.<br/><br/>Quality, regulatory and security expertise as scope grows.'),
('Sustainable funding','Early: research grants and institutional partnerships.<br/><br/>Later: carefully scoped service contracts or licensed validated modules.<br/><br/>Budget data/assays, staff, compute, studies and maintenance.')])

start('16 / Key risks','Define stop conditions before expanding scope','A failed hypothesis is a useful outcome when the study can detect it.')
rows([
('Stain/site shortcuts','Model learns scanner or sampling procedure instead of biology.','Use external centers and confounder baselines; stop the claim if performance collapses.'),
('Weak EMT labels','Bulk stromal signals or noisy assays dominate the target.','Use malignant-cell evidence and repeatability checks; revise the endpoint if unreliable.'),
('Misinterpretation','Votes are mistaken for diagnosis, progression or treatment advice.','Review labels, uncertainty and human factors; block unsupported clinical outputs.'),
('Operational failure','Identity mismatch, drift or uncontrolled model updates.','Audit linkage, monitor failures, version deployments and provide rollback.')],headers=('Risk','Failure mode','Mitigation / decision'))

start('17 / First 90 days','Turn the concept into a credible study','Immediate deliverables for a hospital or research collaboration.')
cards([
('Days 1-30','Agree one intended research use and endpoint.<br/><br/>Appoint clinical/pathology leads; map data access and ethics requirements.<br/><br/>Freeze cohort and assay dictionaries.'),
('Days 31-60','Assemble a deidentified pilot and review tumor tiles.<br/><br/>Audit specimen timing, molecular pairing and duplicate identities.<br/><br/>Run baseline and inspect confounding.'),
('Days 61-90','Prepare pilot evidence and failure analysis.<br/><br/>Set sample-size and external-validation plans with a statistician.<br/><br/>Decide whether to expand, revise the endpoint or stop.')],
'Decision requested from collaborators: a clinical lead, a data/assay partner and support for the pilot study.')

start('18 / Project package','Reproducible starting point for collaborators','Implementation is available in the pancreatic-image-analysis project folder.')
rows([
('Run the prototype','README.md; run_demo.ps1; requirements.txt','Local setup and synthetic workflow; model artifacts remain research-only.'),
('Inspect the analysis','pipeline.py; make_demo.py; tests/test_pipeline.py','Feature extraction, training, inference and meaningful software checks.'),
('Review the product','app.py; context.py; outputs/*.json','Local dashboard, independent treatment context and traceable demo reports.'),
('Plan the study','docs/PROTOCOL.md; docs/MODEL_CARD.md','Research questions, limitations, validation gates and development scope.')],headers=('Purpose','Files','What collaborators can review'))

start('19 / References and provenance','Sources, evidence status and interpretation','Sources checked 13 November 2026. Project proposals are planning recommendations.')
refs=[
('[1] NCI. Pancreatic Cancer Treatment (PDQ), professional summary.','https://www.cancer.gov/types/pancreatic/hp/pancreatic-treatment-pdq'),
('[2] Yang et al. Guidelines and definitions for research on EMT. Nature Reviews Molecular Cell Biology, 2020.','https://www.nature.com/articles/s41580-020-0237-9'),
('[3] FDA. AI-enabled device software functions: lifecycle management and marketing submission recommendations. January 2025. DRAFT.','https://www.fda.gov/regulatory-information/search-fda-guidance-documents/artificial-intelligence-enabled-device-software-functions-lifecycle-management-and-marketing')]
y=391
for label,url in refs:
    used=txt(label,40,y,880,13,NAVY,True,maxh=42)
    used2=txt(f'<link href="{url}" color="{TEAL}">{url}</link>',40,y-used-8,880,10,TEAL,maxh=40)
    y-=used+used2+29
box(40,88,880,92,'#E1EFED')
txt('Local evidence',55,162,850,13,TEAL,True)
txt('Demo metrics and example values come from outputs/metrics.json and outputs/prediction.json. The example prediction uses an in-training artificial sample. Four automated tests and a dashboard smoke test passed. Clinical performance, utility and regulatory readiness remain unestablished.',55,137,850,11,maxh=48)
c.showPage()
c.save()
print(OUT)
