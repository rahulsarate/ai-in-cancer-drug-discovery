"""Acquire a bounded open-access GDC pilot, retaining inventory and file checksums."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from collections import Counter
import argparse
import hashlib
import json
import time
import requests

ROOT=Path(__file__).resolve().parent
DATA=ROOT/'data/real_pilot'
API='https://api.gdc.cancer.gov'

def md5(path):
    h=hashlib.md5()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''): h.update(block)
    return h.hexdigest()

def primary_diagnosis(case):
    ds=[d for d in case.get('diagnoses',[]) if d.get('diagnosis_is_primary_disease') is True]
    return ds[0] if len(ds)==1 else None

def select_cohort(hits,config):
    rna={}
    for item in hits:
        if item['data_type']!='Gene Expression Quantification' or item.get('access')!='open': continue
        if item.get('analysis',{}).get('workflow_type')!='STAR - Counts': continue
        if len(item.get('cases',[]))!=1: continue
        for case in item['cases']:
            samples=case.get('samples',[])
            # Only unambiguous, file-linked primary tumor samples.
            if len(samples)!=1 or samples[0].get('sample_type')!=config['rna_sample_type']: continue
            pid=case['submitter_id']
            rna.setdefault(pid,[]).append(item)
    candidates=[]; seen=set(); exclusions=Counter()
    slides=sorted([h for h in hits if h['data_type']=='Slide Image'],key=lambda h:(h['file_size'],h['file_id']))
    for slide in slides:
        if '-DX' not in slide['file_name'] or '-01Z-' not in slide['file_name']:
            exclusions['not_primary_diagnostic_slide']+=1; continue
        if slide.get('access')!='open' or len(slide.get('cases',[]))!=1:
            exclusions['access_or_case_ambiguity']+=1; continue
        case=slide['cases'][0]; pid=case['submitter_id']; diag=primary_diagnosis(case)
        if not diag or diag.get('morphology')!=config['morphology'] or 'pancrea' not in diag.get('tissue_or_organ_of_origin','').lower():
            exclusions['not_unambiguous_pancreatic_ductal_primary']+=1; continue
        if diag.get('prior_treatment')!=config['prior_treatment']:
            exclusions['prior_treatment_not_confirmed_no']+=1; continue
        if pid not in rna:
            exclusions['no_unambiguous_primary_tumor_STAR_file']+=1; continue
        if pid in seen:
            exclusions['additional_slide_same_patient']+=1; continue
        seen.add(pid)
        # RNA replicates chosen lexicographically by stable UUID, never by endpoint.
        expr=sorted(rna[pid],key=lambda h:h['file_id'])[0]
        candidates.append({'patient_id':pid,'case_id':case['case_id'],'site_id':pid.split('-')[1],
            'diagnosis':diag,'slide':{k:slide[k] for k in ['file_id','file_name','file_size','md5sum','access']},
            'rna':{k:expr[k] for k in ['file_id','file_name','file_size','md5sum','access']},
            'rna_sample':expr['cases'][0]['samples'][0],
            'pairing_level':'same_patient_primary_tumor; exact block and spatial match not established',
            'expert_review_status':'not_reviewed'})
    selected=candidates[:config['patients']]
    if len(selected)<config['patients']: raise ValueError('Insufficient eligible patients')
    size=sum(p[k]['file_size'] for p in selected for k in ['slide','rna'])
    if size>config['max_download_gb']*1e9: raise ValueError(f'Planned {size/1e9:.2f} GB exceeds configured cap')
    return selected,{'inventory_files':len(hits),'slide_files':len(slides),'eligible_unique_patients':len(candidates),
        'selected_patients':len(selected),'not_selected_due_to_cap':len(candidates)-len(selected),
        'sequential_slide_exclusion_counts':dict(exclusions),'planned_bytes':size,
        'selection_bias':config['selection']}

def download(item,folder):
    folder.mkdir(parents=True,exist_ok=True)
    path=folder/item['file_name']
    url=f"{API}/data/{item['file_id']}"
    if path.exists() and path.stat().st_size==item['file_size'] and md5(path)==item['md5sum']:
        return {'file_id':item['file_id'],'relative_path':str(path.relative_to(DATA)),
                'bytes':path.stat().st_size,'md5_verified':True,'url':url,'cached':True}
    part=path.with_suffix(path.suffix+'.part')
    for attempt in range(3):
        try:
            with requests.get(url,stream=True,timeout=(30,120)) as response:
                response.raise_for_status()
                with part.open('wb') as f:
                    for chunk in response.iter_content(1024*1024):
                        if chunk: f.write(chunk)
            if part.stat().st_size!=item['file_size'] or md5(part)!=item['md5sum']:
                raise ValueError(f"Size or MD5 mismatch for {item['file_id']}")
            part.replace(path)
            return {'file_id':item['file_id'],'relative_path':str(path.relative_to(DATA)),
                    'bytes':path.stat().st_size,'md5_verified':True,'url':url,'cached':False}
        except Exception:
            if attempt==2: raise
            time.sleep(2**attempt)

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--refresh',action='store_true'); parser.add_argument('--workers',type=int,default=4)
    args=parser.parse_args()
    config=json.loads((ROOT/'pilot_config.json').read_text())
    DATA.mkdir(parents=True,exist_ok=True); inv=DATA/'gdc_inventory.json'
    if args.refresh or not inv.exists():
        filt={'op':'and','content':[{'op':'in','content':{'field':'cases.project.project_id','value':[config['project']]}},
            {'op':'in','content':{'field':'data_type','value':['Slide Image','Gene Expression Quantification']}}]}
        r=requests.get(API+'/files',params={'filters':json.dumps(filt),'expand':'cases.diagnoses,cases.samples',
            'fields':'file_id,file_name,file_size,md5sum,access,data_type,analysis.workflow_type,cases.case_id,cases.submitter_id',
            'size':2000},timeout=120); r.raise_for_status(); payload=r.json()
        if payload['data']['pagination']['total']>len(payload['data']['hits']): raise ValueError('Inventory pagination needed')
        inv.write_text(json.dumps(payload,indent=2),encoding='utf-8')
    selected,flow=select_cohort(json.loads(inv.read_text())['data']['hits'],config)
    plan={'config':config,'flow':flow,'patients':selected,'planned_at_utc':datetime.now(timezone.utc).isoformat(),
          'inventory_sha256':hashlib.sha256(inv.read_bytes()).hexdigest()}
    # Plan saved before downloads, image inspection or model evaluation.
    plan_path=DATA/'cohort_plan.json'
    if plan_path.exists():
        prior=json.loads(plan_path.read_text())
        if prior['patients']!=selected or prior['config']!=config:
            raise ValueError('Existing pilot plan differs. Version the protocol and output directory rather than overwrite.')
    else: plan_path.write_text(json.dumps(plan,indent=2),encoding='utf-8')
    print(f"Selected {len(selected)} patients; planned {flow['planned_bytes']/1e9:.2f} GB",flush=True)
    receipts=[]; errors=[]
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures={pool.submit(download,p[k],DATA/('slides' if k=='slide' else 'rna')):(p['patient_id'],k) for p in selected for k in ['slide','rna']}
        for future in as_completed(futures):
            pid,kind=futures[future]
            try:
                receipt=future.result(); receipt.update(patient_id=pid,kind=kind); receipts.append(receipt)
                print(f"Verified {pid} {kind}: {receipt['bytes']/1e6:.1f} MB",flush=True)
            except Exception as e:
                errors.append({'patient_id':pid,'kind':kind,'error':str(e)}); print(f'FAILED {pid} {kind}: {e}',flush=True)
            (DATA/'download_receipts.json').write_text(json.dumps({'receipts':receipts,'errors':errors},indent=2),encoding='utf-8')
    if errors: raise RuntimeError(f'{len(errors)} downloads failed; rerun to reuse verified files')
    print('All pilot files verified.',flush=True)

if __name__=='__main__': main()
