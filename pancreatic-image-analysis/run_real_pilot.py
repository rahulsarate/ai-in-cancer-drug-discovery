"""Evaluate technical feasibility and exploratory RNA associations on real TCGA data."""
from pathlib import Path
from collections import Counter
import csv
import hashlib
import json
import platform
from importlib.metadata import version
from concurrent.futures import ThreadPoolExecutor

import joblib
import numpy as np
import openslide
from PIL import Image, ImageDraw, ImageCms
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from scipy.stats import spearmanr

from acquire_pilot import md5
from pipeline import extract, FEATURES

ROOT=Path(__file__).resolve().parent
DATA=ROOT/'data/real_pilot'
OUT=ROOT/'outputs/real_pilot'

def write_csv(path,rows):
    rows=list(rows)
    if not rows: return
    with Path(path).open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

def rna_score(path,config):
    wanted=set(config['epithelial_genes']+config['mesenchymal_genes']); values={}
    with Path(path).open(encoding='utf-8') as f:
        reader=csv.DictReader((line for line in f if not line.startswith('#')),delimiter='\t')
        for row in reader:
            gene=row.get('gene_name')
            if gene not in wanted: continue
            if gene in values: raise ValueError(f'Duplicate signature symbol {gene}')
            v=float(row['tpm_unstranded'])
            if not np.isfinite(v) or v<0: raise ValueError('Invalid TPM')
            values[gene]=v
    if set(values)!=wanted: raise ValueError(f'Missing signature genes: {wanted-set(values)}')
    score=float(np.mean([np.log2(values[g]+1) for g in config['mesenchymal_genes']])-np.mean([np.log2(values[g]+1) for g in config['epithelial_genes']]))
    return score,values

def tissue_fraction(rgb):
    a=np.asarray(rgb,dtype=float)/255
    return float(((a.min(axis=2)<.85)&((a.max(axis=2)-a.min(axis=2))>.05)).mean())

def tile_slide(path,pid,config):
    output=DATA/'tiles_srgb'/pid; output.mkdir(parents=True,exist_ok=True)
    thumbs=DATA/'thumbnails_srgb'; thumbs.mkdir(exist_ok=True)
    with openslide.OpenSlide(str(path)) as slide:
        source_profile=slide.color_profile
        srgb=ImageCms.createProfile('sRGB')
        rgb_transform=ImageCms.buildTransform(source_profile,srgb,'RGB','RGB') if source_profile else None
        rgba_transform=ImageCms.buildTransform(source_profile,srgb,'RGBA','RGBA') if source_profile else None
        mx=float(slide.properties.get('openslide.mpp-x','nan')); my=float(slide.properties.get('openslide.mpp-y','nan'))
        if not np.isfinite(mx) or not np.isfinite(my) or not .1<=mx<=2 or not .1<=my<=2:
            raise ValueError('Missing or unsupported physical resolution; no silent MPP assumption')
        if abs(mx-my)/max(mx,my)>.05: raise ValueError('Anisotropic slide resolution needs a separate resampling protocol')
        W,H=slide.dimensions; px=config['tile_pixels']; physical=px*config['target_mpp']
        span_x=int(round(physical/mx)); span_y=int(round(physical/my))
        thumb=slide.get_thumbnail((1600,1600)).convert('RGB')
        if rgb_transform: thumb=ImageCms.applyTransform(thumb,rgb_transform)
        # Pixel data are now sRGB; do not propagate large scanner ICC payloads into PNGs.
        thumb.info.clear(); thumb.save(thumbs/f'{pid}.png')
        candidates=[]
        for y in range(0,H-span_y+1,span_y):
            for x in range(0,W-span_x+1,span_x):
                region=thumb.crop((int(x/W*thumb.width),int(y/H*thumb.height),max(int((x+span_x)/W*thumb.width),int(x/W*thumb.width)+1),max(int((y+span_y)/H*thumb.height),int(y/H*thumb.height)+1)))
                if tissue_fraction(region)>=.4: candidates.append((x,y))
        # Stable per-patient seed; no selection based on stage or RNA target.
        seed=config['seed']+int(hashlib.sha256(pid.encode()).hexdigest()[:8],16)
        rng=np.random.default_rng(seed); rng.shuffle(candidates)
        rows=[]; features=[]
        for x,y in candidates[:500]:
            image=slide.read_region((x,y),0,(span_x,span_y))
            if rgba_transform: image=ImageCms.applyTransform(image,rgba_transform)
            image=image.convert('RGB').resize((px,px),Image.Resampling.LANCZOS)
            image.info.clear()
            fraction=tissue_fraction(image)
            if fraction<.4: continue
            dest=output/f'{pid}_x{x}_y{y}.png'; image.save(dest)
            try: feature=extract(dest)
            except ValueError as exc:
                if 'Insufficient colored tissue' in str(exc): continue
                raise
            features.append(feature)
            rows.append({'patient_id':pid,'tile_path':str(dest.relative_to(ROOT)),
                         'x_level0':x,'y_level0':y,'span_x_level0':span_x,'span_y_level0':span_y,
                         'output_pixels':px,'nominal_target_mpp':config['target_mpp'],
                         'tissue_fraction':fraction,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),
                         'review_status':'unreviewed_tissue_not_tumor_annotation'})
            if len(rows)==config['max_tiles_per_patient']: break
        if len(rows)<8: raise ValueError(f'Only {len(rows)} eligible tiles; require at least 8 for technical aggregation')
        return np.mean(features,axis=0),rows,{'native_mpp_x':mx,'native_mpp_y':my,'width_level0':W,'height_level0':H,'candidate_grid_tiles':len(candidates),'retained_tiles':len(rows),
            'color_policy':'source ICC to sRGB' if source_profile else 'source ICC absent; native RGB assumed; expert review needed'}

def bootstrap(y,pred,base,seed,reps):
    rng=np.random.default_rng(seed); mae=[]; improvement=[]
    for _ in range(reps):
        ix=rng.integers(0,len(y),len(y)); model_error=np.abs(y[ix]-pred[ix]).mean(); base_error=np.abs(y[ix]-base[ix]).mean()
        mae.append(model_error); improvement.append(base_error-model_error)
    return {'model_mae_percentile_95':np.quantile(mae,[.025,.975]).tolist(),
            'mae_improvement_over_mean_percentile_95':np.quantile(improvement,[.025,.975]).tolist(),
            'method':'Descriptive patient bootstrap of fixed out-of-fold predictions; not nested refitting; ignores site-cluster uncertainty',
            'replicates':reps}

def gallery(patients,tiles):
    sample=patients[:12]; sheet=Image.new('RGB',(1440,1032),'#f4f6f5'); draw=ImageDraw.Draw(sheet)
    for i,p in enumerate(sample):
        pid=p['patient_id']; row=next(t for t in tiles if t['patient_id']==pid)
        with Image.open(ROOT/row['tile_path']) as im: im=im.convert('RGB').resize((220,220))
        x=(i%4)*360+15; y=(i//4)*344+15
        sheet.paste(im,(x,y)); draw.text((x,y+230),pid,fill='#102c40')
        draw.text((x,y+252),'Real TCGA tissue tile | unreviewed',fill='#526675')
        draw.text((x,y+274),'No tumor or EMT annotation implied',fill='#526675')
    sheet.save(OUT/'real_image_gallery.png')

def plots(y,pred,base,patients):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axs=plt.subplots(1,2,figsize=(11,4),layout='constrained')
    colors={'HZ':'#087E83','FB':'#B27520','HV':'#74629D'}
    for site in sorted({p['site_id'] for p in patients}):
        ix=np.array([p['site_id']==site for p in patients]); axs[0].scatter(y[ix],pred[ix],label=f'{site} (n={ix.sum()})',color=colors.get(site,'gray'))
    lim=[min(y.min(),pred.min())-.2,max(y.max(),pred.max())+.2]
    axs[0].plot(lim,lim,'--',color='gray'); axs[0].set(xlabel='Observed exploratory bulk RNA score',ylabel='Site-held-out image prediction',title='Exploratory association, not a validated EMT assay')
    axs[0].legend(fontsize=8)
    axs[1].bar(['Image Ridge','Training-mean baseline'],[np.abs(y-pred).mean(),np.abs(y-base).mean()],color=['#087E83','#526675'])
    axs[1].set(ylabel='Mean absolute error (score units)',title='Lower error is better')
    fig.savefig(OUT/'exploratory_results.png',dpi=180); plt.close(fig)

def process_patient(p,config):
        pid=p['patient_id']
        try:
            for kind in ['slide','rna']:
                path=DATA/('slides' if kind=='slide' else 'rna')/p[kind]['file_name']
                if path.stat().st_size!=p[kind]['file_size'] or md5(path)!=p[kind]['md5sum']: raise ValueError('Raw file checksum failed')
            score,genes=rna_score(DATA/'rna'/p['rna']['file_name'],config)
            features,tiles,qc=tile_slide(DATA/'slides'/p['slide']['file_name'],pid,config)
            diag=p['diagnosis']; sample=p['rna_sample']
            patient={'patient_id':pid,'site_id':p['site_id'],'stage_exact':diag.get('ajcc_pathologic_stage','Unknown'),
                'staging_edition':diag.get('ajcc_staging_system_edition','Unknown'),'primary_diagnosis':diag['primary_diagnosis'],
                'morphology':diag['morphology'],'prior_treatment':diag['prior_treatment'],
                'slide_file_id':p['slide']['file_id'],'rna_file_id':p['rna']['file_id'],
                'rna_sample_id':sample['submitter_id'],'exploratory_bulk_emt_score':score,
                'pairing_level':p['pairing_level'],'expert_pathology_review':'not_performed',**qc}
            feature_row={'patient_id':pid,**dict(zip(FEATURES,map(float,features)))}
            gene_row={'patient_id':pid,**genes}
            print(f'Processed {pid}: {len(tiles)} tiles, RNA score {score:.3f}',flush=True)
            return patient,feature_row,tiles,gene_row,None
        except Exception as e:
            print(f'Excluded {pid}: {e}',flush=True)
            return None,None,[],None,{'patient_id':pid,'reason':str(e)}

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    plan=json.loads((DATA/'cohort_plan.json').read_text()); config=plan['config']
    patients=[]; all_tiles=[]; feature_rows=[]; gene_rows=[]; exclusions=[]
    receipt=json.loads((DATA/'download_receipts.json').read_text())
    if receipt['errors'] or len(receipt['receipts'])!=2*len(plan['patients']): raise ValueError('Complete verified download receipts required')
    # Independent OpenSlide handles; map preserves the frozen cohort order.
    with ThreadPoolExecutor(max_workers=3) as pool:
        for patient,feature_row,tiles,gene_row,error in pool.map(lambda p:process_patient(p,config),plan['patients']):
            if error:
                exclusions.append(error); continue
            patients.append(patient); feature_rows.append(feature_row); all_tiles.extend(tiles); gene_rows.append(gene_row)
    write_csv(OUT/'patient_manifest.csv',patients); write_csv(OUT/'tile_manifest.csv',all_tiles)
    write_csv(OUT/'patient_features.csv',feature_rows); write_csv(OUT/'signature_tpm.csv',gene_rows)
    (OUT/'processing_exclusions.json').write_text(json.dumps(exclusions,indent=2))
    if len(patients)<12: raise ValueError('Too few evaluable patients for exploratory analysis; retain feasibility outputs only')
    # Independent patient objects; a single aggregated feature vector each.
    if len({p['patient_id'] for p in patients})!=len(patients): raise ValueError('Duplicate patient')
    seen={}
    for tile in all_tiles:
        owner=seen.setdefault(tile['sha256'],tile['patient_id'])
        if owner!=tile['patient_id']: raise ValueError('Cross-patient duplicate derived tile')
    X=np.array([[f[k] for k in FEATURES] for f in feature_rows]); y=np.array([p['exploratory_bulk_emt_score'] for p in patients])
    groups=np.array([p['site_id'] for p in patients]); pred=np.full(len(y),np.nan); base=pred.copy(); folds=[]
    if len(set(groups))<3: raise ValueError('At least three contributing sites required by this pilot analysis')
    for train,test in LeaveOneGroupOut().split(X,y,groups):
        model=make_pipeline(StandardScaler(),Ridge(alpha=config['model']['alpha']))
        model.fit(X[train],y[train]); pred[test]=model.predict(X[test])
        baseline=DummyRegressor(strategy='mean').fit(X[train],y[train]); base[test]=baseline.predict(X[test])
        folds.append({'held_out_site':str(groups[test][0]),'train_patients':[patients[i]['patient_id'] for i in train],
            'test_patients':[patients[i]['patient_id'] for i in test],
            'model_mae':float(mean_absolute_error(y[test],pred[test])),'baseline_mae':float(mean_absolute_error(y[test],base[test]))})
    predictions=[{'patient_id':p['patient_id'],'held_out_site':p['site_id'],'observed_bulk_composite':float(y[i]),
                  'image_prediction':float(pred[i]),'training_mean_prediction':float(base[i])} for i,p in enumerate(patients)]
    write_csv(OUT/'out_of_fold_predictions.csv',predictions)
    stage_counts=Counter(p['stage_exact'] for p in patients)
    broad=Counter()
    for stage,count in stage_counts.items():
        token=stage.removeprefix('Stage ')
        for s in ['IV','III','II','I']:
            if token.startswith(s): broad[s]+=count; break
    report={'protocol_version':config['protocol_version'],'research_only':True,'real_public_data':True,
            'analysis_type':'retrospective technical feasibility with exploratory biological association',
            'primary_endpoints':{'selected_patients':len(plan['patients']),'verified_raw_files':len(receipt['receipts']),
                'verified_raw_bytes':sum(r['bytes'] for r in receipt['receipts']),
                'evaluable_patients':len(patients),'exclusions':exclusions,'retained_tiles':len(all_tiles),
                'same_patient_RNA_linkage':len(patients),'same_block_spatial_match_established':False,
                'expert_tumor_review_performed':False},
            'technical_gates':{'all_raw_files_verified':all(r['md5_verified'] for r in receipt['receipts']),
                'at_least_22_evaluable_patients':len(patients)>=22,
                'all_patients_have_at_least_8_tiles':all(p['retained_tiles']>=8 for p in patients),
                'cross_patient_exact_tile_duplicates':0},
            'sites':dict(Counter(groups)),'stage_counts_exact':dict(stage_counts),'stage_counts_broad':dict(broad),
            'staging_editions':dict(Counter(p['staging_edition'] for p in patients)),
            'stage_model':{'status':'NOT_TRAINED','reason':'Four-stage minimum gate not satisfied' if min(broad.get(s,0) for s in ['I','II','III','IV'])<10 else 'Separate registered development study required'},
            'exploratory_emt':{'definition':config['emt_score'],'not_validated_EMT_assay':True,'progression_assessed':False,
                'n':len(y),'model':'StandardScaler + Ridge(alpha=10); fixed configuration',
                'evaluation':'Leave-one-contributing-site-out; held-out sites remain part of TCGA, not independent external validation',
                'model_mae':float(mean_absolute_error(y,pred)),'baseline_mae':float(mean_absolute_error(y,base)),
                'mae_improvement_over_baseline':float(mean_absolute_error(y,base)-mean_absolute_error(y,pred)),
                'model_rmse':float(np.sqrt(mean_squared_error(y,pred))),'model_r2':float(r2_score(y,pred)),
                'spearman_r':float(spearmanr(y,pred).statistic),'folds':folds,**bootstrap(y,pred,base,config['seed'],config['bootstrap_replicates'])},
            'provenance':{'cohort_plan_sha256':hashlib.sha256((DATA/'cohort_plan.json').read_bytes()).hexdigest(),
                'analysis_code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'python':platform.python_version(),
                'package_versions':{name:version(name) for name in ['numpy','Pillow','scikit-learn','scipy','openslide-python','openslide-bin','requests','matplotlib']},
                'acknowledgement':'Results are based on data generated by the TCGA Research Network: https://www.cancer.gov/tcga'},
            'limitations':['Convenience selection by file size; not a representative clinical cohort.',
                'Unreviewed tissue tiles; no pathologist-confirmed tumor regions.',
                'Bulk RNA composite can reflect stromal contamination; not a clinical EMT endpoint.',
                'RNA and WSI matched by patient, not verified same block; no longitudinal progression.',
                'Tiny site groups and internal source; no external clinical validation.',
                'No cancer diagnosis, clinical stage inference, drug response or treatment recommendation.']}
    (OUT/'pilot_results.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    (OUT/'environment_versions.txt').write_text('\n'.join(f'{k}=={v}' for k,v in report['provenance']['package_versions'].items())+'\n')
    gallery(patients,all_tiles); plots(y,pred,base,patients)
    # Deliberately no inference model release: feasibility evidence is not a clinical artifact.
    print(json.dumps({'patients':len(y),'tiles':len(all_tiles),'stage':report['stage_model'],'EMT_MAE':report['exploratory_emt']['model_mae'],'baseline_MAE':report['exploratory_emt']['baseline_mae']},indent=2),flush=True)

if __name__=='__main__': main()
