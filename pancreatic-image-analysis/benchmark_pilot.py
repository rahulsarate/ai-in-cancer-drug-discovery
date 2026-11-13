"""Bounded local CPU timings on saved pilot inputs; excludes WSI tiling and downloads."""
from pathlib import Path
from datetime import datetime,timezone
import csv
import hashlib
import json
import platform
from time import perf_counter
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from threadpoolctl import threadpool_limits
from pipeline import extract,FEATURES

ROOT=Path(__file__).resolve().parent; OUT=ROOT/'outputs/real_pilot'
def rows(name):
    with (OUT/name).open(encoding='utf-8') as f:return list(csv.DictReader(f))

def main():
    tile_rows=rows('tile_manifest.csv'); feature_rows=rows('patient_features.csv'); patient_rows=rows('patient_manifest.csv')
    paths=[ROOT/t['tile_path'] for t in tile_rows]
    X=np.array([[float(row[k]) for k in FEATURES] for row in feature_rows])
    assert [x['patient_id'] for x in feature_rows]==[p['patient_id'] for p in patient_rows]
    y=np.array([float(p['exploratory_bulk_emt_score']) for p in patient_rows]); groups=np.array([p['site_id'] for p in patient_rows])
    folds=list(LeaveOneGroupOut().split(X,y,groups))
    def cv():
        result=np.zeros(len(y))
        for train,test in folds:
            model=make_pipeline(StandardScaler(),Ridge(alpha=10))
            model.fit(X[train],y[train]); result[test]=model.predict(X[test])
        return result
    for path in paths[:16]: extract(path)
    feature_times=[]
    for _ in range(3):
        start=perf_counter()
        for path in paths: extract(path)
        feature_times.append(perf_counter()-start)
    training_times=[]
    with threadpool_limits(limits=1):
        prediction=cv()
        for _ in range(50):
            start=perf_counter();cv();training_times.append(perf_counter()-start)
    metrics=json.loads((OUT/'pilot_results.json').read_text())
    assert np.isclose(np.abs(prediction-y).mean(),metrics['exploratory_emt']['model_mae'])
    image_bytes=sum(p.stat().st_size for p in paths)
    raw_bytes=metrics['primary_endpoints']['verified_raw_bytes']
    results={'recorded_at_utc':datetime.now(timezone.utc).isoformat(),
        'scope':'Local warm-cache CPU microbenchmark; existing PNG decode/resize/features and saved-feature 3-fold fit/predict only',
        'hardware':{'cpu':'Intel Core i5-9300H @ 2.40 GHz','physical_cores':4,'logical_processors':8,'installed_memory_bytes':17013329920},
        'environment':{'python':platform.python_version(),'os':platform.system(),'gpu_used_for_these_steps':False,'BLAS_threads_model_timing':1},
        'feature_extraction':{'tiles_per_pass':len(paths),'passes':3,'seconds_per_pass':feature_times,
            'median_seconds':float(np.median(feature_times)),'tiles_per_second_median':float(len(paths)/np.median(feature_times)),
            'median_ms_per_tile':float(np.median(feature_times)/len(paths)*1000)},
        'three_site_fold_fit_predict':{'patients':len(y),'features':len(FEATURES),'repeats':50,
            'median_ms':float(np.median(training_times)*1000),'p95_ms':float(np.quantile(training_times,.95)*1000),
            'excludes_imports':True,'same_MAE_reproduced':True},
        'storage':{'source_slide_and_rna_bytes':raw_bytes,'retained_png_tiles_bytes':image_bytes,
            'tile_bytes_fraction_of_source_plus_rna':image_bytes/raw_bytes,
            'caution':'Different content sets and representations; not a lossless compression ratio. Source-plus-RNA includes data omitted by sampled tiles.'},
        'not_measured':['Full WSI-to-report wall time','Download throughput','Peak RAM','Clinical turnaround time','Cost per clinical case','Energy consumption'],
        'limitations':['Single workstation, three image passes and 50 tiny regression runs; not an independent performance benchmark.',
            'Warm caches and background workload affect latency; throughput is not a production service guarantee.',
            'Microbenchmark does not include native WSI reads, ICC conversion, annotation, RNA parsing, reports or human review.'],
        'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (OUT/'efficiency_benchmark.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
    print(json.dumps(results,indent=2))

if __name__=='__main__':main()
