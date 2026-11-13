"""Patient-level, interpretable H&E image research baseline. No clinical claims."""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import platform

import joblib
import numpy as np
import sklearn
from PIL import Image, ImageOps
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import accuracy_score, balanced_accuracy_score, confusion_matrix, mean_absolute_error
from sklearn.model_selection import train_test_split

STAGES = ['I', 'II', 'III', 'IV']
FEATURES = [f'{channel}_{stat}' for channel in ['R','G','B'] for stat in ['mean','std','q10','q50','q90']] + ['tissue_fraction','edge_x','edge_y']

def extract(path):
    """Fixed RGB summary baseline; not a cell segmentation or EMT assay."""
    with Image.open(path) as im:
        if im.format not in {'PNG','JPEG','TIFF'}:
            raise ValueError('Use PNG, JPEG or single-frame TIFF pathology tiles.')
        if getattr(im, 'n_frames', 1) != 1:
            raise ValueError('Export whole-slide/multiframe images into reviewed tiles first.')
        if min(im.size) < 32:
            raise ValueError('Image must be at least 32 x 32 pixels.')
        a = np.asarray(ImageOps.exif_transpose(im).convert('RGB').resize((128,128)), dtype=float)/255
    tissue = (a.min(axis=2)<0.85) & (a.max(axis=2)-a.min(axis=2)>0.05)
    if tissue.mean()<0.05:
        raise ValueError('Insufficient colored tissue; pathologist review required.')
    pixels = a[tissue]
    f=[]
    for c in range(3):
        x=pixels[:,c]
        f.extend([x.mean(),x.std(),*np.quantile(x,[.1,.5,.9])])
    f.extend([tissue.mean(),np.abs(np.diff(a,axis=0)).mean(),np.abs(np.diff(a,axis=1)).mean()])
    return np.array(f)

def read_manifest(path):
    path=Path(path).resolve()
    with path.open(newline='',encoding='utf-8') as f:
        reader=csv.DictReader(f)
        required={'patient_id','image_path','stage','emt_score','emt_assay','site_id'}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError(f'Manifest needs {sorted(required)}')
        rows=list(reader)
    if not rows:
        raise ValueError('Empty manifest')
    patients={}; hashes={}
    for row in rows:
        if any(not row[k].strip() for k in required):
            raise ValueError('Required values cannot be blank')
        if row['stage'] not in STAGES:
            raise ValueError('Stage must be I, II, III or IV; unknown stage is not eligible for training.')
        score=float(row['emt_score'])
        if not np.isfinite(score) or not 0<=score<=1:
            raise ValueError('EMT target must be a finite assay-derived value in [0,1].')
        image=(path.parent/row['image_path']).resolve()
        digest=hashlib.sha256(image.read_bytes()).hexdigest()
        owner=hashes.setdefault(digest,row['patient_id'])
        if owner!=row['patient_id']:
            raise ValueError('Identical image assigned to multiple patients; potential leakage.')
        record=patients.setdefault(row['patient_id'],{'stage':row['stage'],'emt_score':score,'site_id':row['site_id'],'emt_assay':row['emt_assay'],'images':{}})
        if any(record[k]!=v for k,v in [('stage',row['stage']),('emt_score',score),('site_id',row['site_id']),('emt_assay',row['emt_assay'])]):
            raise ValueError('Inconsistent patient labels/site/assay')
        record['images'][digest]=image
    ids=sorted(patients)
    X=np.stack([np.mean([extract(p) for p in patients[i]['images'].values()],axis=0) for i in ids])
    return ids,X,np.array([patients[i]['stage'] for i in ids]),np.array([patients[i]['emt_score'] for i in ids]),patients

def metrics(clf,reg,X,y,z):
    pred=clf.predict(X)
    return {'patients':len(y),'stage_accuracy':float(accuracy_score(y,pred)),
            'stage_balanced_accuracy':float(balanced_accuracy_score(y,pred)),
            'stage_confusion_matrix':confusion_matrix(y,pred,labels=STAGES).tolist(),
            'stage_class_order':STAGES,'emt_mae':float(mean_absolute_error(z,reg.predict(X)))}

def train(manifest,out,seed=42):
    ids,X,y,z,patients=read_manifest(manifest)
    counts={s:int((y==s).sum()) for s in STAGES}
    if min(counts.values())<10:
        raise ValueError('Need >=10 independent patients in each stage for this smoke-test split; real validation needs a power calculation.')
    assays={p['emt_assay'] for p in patients.values()}
    if len(assays)!=1:
        raise ValueError('Use one harmonized EMT assay/score definition per model.')
    indices=np.arange(len(ids))
    tr,hold=train_test_split(indices,test_size=.4,stratify=y,random_state=seed)
    va,te=train_test_split(hold,test_size=.5,stratify=y[hold],random_state=seed)
    # Fixed hyperparameters: validation is reported, never used to fit or tune this baseline.
    clf=RandomForestClassifier(n_estimators=120,min_samples_leaf=2,class_weight='balanced',random_state=seed,n_jobs=-1)
    reg=RandomForestRegressor(n_estimators=120,min_samples_leaf=2,random_state=seed,n_jobs=-1)
    clf.fit(X[tr],y[tr]); reg.fit(X[tr],z[tr])
    synthetic=all(p['emt_assay']=='SYNTHETIC_DEMO' for p in patients.values())
    artifact={'classifier':clf,'regressor':reg,'features':FEATURES,'synthetic':synthetic,'emt_assay':next(iter(assays)),
              'feature_min':X[tr].min(axis=0),'feature_max':X[tr].max(axis=0),'seed':seed,'schema_version':1}
    out=Path(out); out.mkdir(parents=True,exist_ok=True)
    joblib.dump(artifact,out/'model.joblib')
    report={'research_only':True,'synthetic':synthetic,'seed':seed,'versions':{'python':platform.python_version(),'sklearn':sklearn.__version__},
            'manifest_sha256':hashlib.sha256(Path(manifest).read_bytes()).hexdigest(),
            'validation':metrics(clf,reg,X[va],y[va],z[va]),'test':metrics(clf,reg,X[te],y[te],z[te]),
            'splits':{name:[ids[i] for i in ix] for name,ix in [('train',tr),('validation',va),('test',te)]},
            'limitations':['Internal split only; no external clinical validation.','Random-forest votes are not calibrated probabilities.','EMT is a cross-sectional assay-associated estimate, not progression.']}
    (out/'metrics.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    return report

def predict(artifact,images):
    if artifact.get('schema_version')!=1 or artifact.get('features')!=FEATURES:
        raise ValueError('Unsupported model schema/features')
    if not images:
        raise ValueError('Provide at least one tile from one patient.')
    x=np.mean([extract(p) for p in images],axis=0)[None,:]
    outside=bool(((x[0]<artifact['feature_min']) | (x[0]>artifact['feature_max'])).any())
    votes=artifact['classifier'].predict_proba(x)[0]
    return {'research_only':True,'synthetic_model':artifact['synthetic'],
            'stage_association':str(artifact['classifier'].classes_[votes.argmax()]),
            'stage_votes':dict(zip(artifact['classifier'].classes_,map(float,votes))),
            'emt_assay_association':float(artifact['regressor'].predict(x)[0]),'emt_assay':artifact['emt_assay'],
            'outside_training_feature_range':outside,'clinical_stage':'Not determined by this model',
            'emt_progression':'Not determined: requires longitudinal matched assays',
            'interpretation':'Synthetic software demonstration only' if artifact['synthetic'] else 'Unvalidated research estimate; requires pathology and clinical review'}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    t=sub.add_parser('train'); t.add_argument('--manifest',required=True); t.add_argument('--out',default='outputs'); t.add_argument('--seed',type=int,default=42)
    p=sub.add_parser('predict'); p.add_argument('--model',required=True); p.add_argument('--images',nargs='+',required=True); p.add_argument('--out',default='outputs/prediction.json')
    args=parser.parse_args()
    if args.command=='train':
        print(json.dumps(train(args.manifest,args.out,args.seed),indent=2))
    else:
        # Pickle-based artifacts must come from your own trusted training run.
        result=predict(joblib.load(args.model),args.images)
        Path(args.out).parent.mkdir(parents=True,exist_ok=True)
        Path(args.out).write_text(json.dumps(result,indent=2),encoding='utf-8')
        print(json.dumps(result,indent=2))

if __name__=='__main__': main()
