import csv
import json
import sys
from pathlib import Path
import numpy as np
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from acquire_pilot import primary_diagnosis,select_cohort
from run_real_pilot import rna_score,bootstrap

def test_primary_label_ignores_metastatic_diagnosis():
    a={'diagnosis_is_primary_disease':False,'ajcc_pathologic_stage':'Stage IV'}
    b={'diagnosis_is_primary_disease':True,'ajcc_pathologic_stage':'Stage II'}
    assert primary_diagnosis({'diagnoses':[a,b]})==b
    assert primary_diagnosis({'diagnoses':[b,b]}) is None

def test_selection_requires_primary_diagnostic_and_primary_rna():
    case={'case_id':'case1','submitter_id':'TCGA-AA-0001',
          'diagnoses':[{'diagnosis_is_primary_disease':True,'morphology':'8500/3',
                        'tissue_or_organ_of_origin':'Pancreas, NOS','prior_treatment':'No'}],
          'samples':[{'sample_type':'Primary Tumor','submitter_id':'TCGA-AA-0001-01A'}]}
    common={'cases':[case],'access':'open','file_size':100,'md5sum':'example'}
    slide={**common,'file_id':'slide1','file_name':'TCGA-AA-0001-01Z-00-DX1.svs','data_type':'Slide Image'}
    rna={**common,'file_id':'rna1','file_name':'rna.tsv','data_type':'Gene Expression Quantification',
         'analysis':{'workflow_type':'STAR - Counts'}}
    config={'patients':1,'max_download_gb':.001,'rna_sample_type':'Primary Tumor','morphology':'8500/3','prior_treatment':'No','selection':'test'}
    selected,flow=select_cohort([slide,rna],config)
    assert selected[0]['patient_id']=='TCGA-AA-0001'
    assert flow['planned_bytes']==200
    slide['file_name']='TCGA-AA-0001-11A-01-TS1.svs'
    with pytest.raises(ValueError,match='Insufficient'): select_cohort([slide,rna],config)

def test_rna_composite_uses_defined_genes_and_rejects_missing(tmp_path):
    path=tmp_path/'rna.tsv'; config={'mesenchymal_genes':['VIM'],'epithelial_genes':['CDH1']}
    path.write_text('# comment\ngene_id\tgene_name\ttpm_unstranded\nENSG1\tVIM\t7\nENSG2\tCDH1\t1\n')
    score,genes=rna_score(path,config)
    assert score==pytest.approx(2.0)
    config['epithelial_genes'].append('EPCAM')
    with pytest.raises(ValueError,match='Missing'): rna_score(path,config)

def test_bootstrap_preserves_paired_baseline_comparison():
    y=np.array([0.,1.,2.,3.]); pred=y.copy(); base=np.zeros(4)
    r=bootstrap(y,pred,base,42,100)
    assert r['model_mae_percentile_95']==[0.,0.]
    assert r['mae_improvement_over_mean_percentile_95'][0]>=0

def test_real_outputs_have_site_disjoint_folds_if_available():
    path=Path(__file__).resolve().parents[1]/'outputs/real_pilot/pilot_results.json'
    if not path.exists(): pytest.skip('Real pilot not yet processed')
    r=json.loads(path.read_text()); seen=[]
    for fold in r['exploratory_emt']['folds']:
        assert not set(fold['train_patients'])&set(fold['test_patients'])
        assert all(pid.split('-')[1]==fold['held_out_site'] for pid in fold['test_patients'])
        assert all(pid.split('-')[1]!=fold['held_out_site'] for pid in fold['train_patients'])
        seen+=fold['test_patients']
    assert len(seen)==len(set(seen))==r['primary_endpoints']['evaluable_patients']
    assert r['real_public_data'] and r['stage_model']['status']=='NOT_TRAINED'

def test_frozen_real_cohort_has_unique_source_files_if_available():
    path=Path(__file__).resolve().parents[1]/'data/real_pilot/cohort_plan.json'
    if not path.exists(): pytest.skip('Real cohort plan not present')
    patients=json.loads(path.read_text())['patients']
    assert len({p['patient_id'] for p in patients})==len(patients)
    for kind in ['slide','rna']:
        assert len({p[kind]['file_id'] for p in patients})==len(patients)
        assert len({p[kind]['md5sum'] for p in patients})==len(patients)
    for p in patients:
        assert p['slide']['file_name'].startswith(p['patient_id']+'-01Z-')
        assert p['rna_sample']['submitter_id'].startswith(p['patient_id']+'-01')
