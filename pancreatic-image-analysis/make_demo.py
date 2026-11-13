"""Generate artificial colored textures to test plumbing, never medical performance."""
import csv
from pathlib import Path
import numpy as np
from PIL import Image

def make_demo(root='data/demo'):
    root=Path(root); root.mkdir(parents=True,exist_ok=True)
    rng=np.random.default_rng(42); rows=[]
    for stage in range(4):
        for patient in range(20):
            pid=f'DEMO_{stage}_{patient:03d}'
            score=float(rng.uniform())
            for tile in range(2):
                # Deliberate artificial correlations; no biological meaning.
                a=rng.normal(0,18,(96,96,3))+np.array([165+stage*12,85+score*60,160-stage*10])
                name=f'{pid}_{tile}.png'
                Image.fromarray(a.clip(0,255).astype('uint8')).save(root/name)
                rows.append([pid,name,['I','II','III','IV'][stage],score,'SYNTHETIC_DEMO','DEMO_SITE'])
    with (root/'manifest.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f); w.writerow(['patient_id','image_path','stage','emt_score','emt_assay','site_id']); w.writerows(rows)
    return root/'manifest.csv'

if __name__=='__main__': print(make_demo())
