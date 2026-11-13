import csv
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import joblib
import numpy as np
import pytest
from PIL import Image
from make_demo import make_demo
from pipeline import extract,read_manifest,train,predict
from context import treatment_context

def test_end_to_end_patient_splits(tmp_path):
    manifest=make_demo(tmp_path/'data')
    report=train(manifest,tmp_path/'out')
    splits=[set(report['splits'][k]) for k in ['train','validation','test']]
    assert len(set.union(*splits))==80
    assert all(not splits[i]&splits[j] for i,j in [(0,1),(0,2),(1,2)])
    model=joblib.load(tmp_path/'out/model.joblib')
    result=predict(model,[next(manifest.parent.glob('*.png'))])
    assert result['synthetic_model']
    assert 0<=result['emt_assay_association']<=1
    assert sum(result['stage_votes'].values())==pytest.approx(1)
    assert report['test']['patients']==16

def test_blank_rejected(tmp_path):
    p=tmp_path/'blank.png'; Image.new('RGB',(64,64),'white').save(p)
    with pytest.raises(ValueError,match='tissue'): extract(p)

def test_cross_patient_duplicate_rejected(tmp_path):
    manifest=make_demo(tmp_path)
    rows=list(csv.DictReader(manifest.open()))
    rows[2]['image_path']=rows[0]['image_path']
    with manifest.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    with pytest.raises(ValueError,match='multiple patients'): read_manifest(manifest)

def test_context_unknown_and_invalid():
    assert treatment_context('Unknown')['clinician_entered_status']=='Unknown'
    with pytest.raises(ValueError): treatment_context('II')
