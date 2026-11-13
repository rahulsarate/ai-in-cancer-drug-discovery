"""Package code, real derived tiles, audit files and the pilot presentation; omit large raw files."""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT=Path(__file__).resolve().parent
target=ROOT.parent/'deliverables/pancreatic-real-data-pilot-v1.zip'
target.parent.mkdir(parents=True,exist_ok=True)
files=[]
for pattern in ['*.py','*.txt','*.json','README.md','.gitignore']:
    files.extend(ROOT.glob(pattern))
for directory in ['docs','tests','outputs/real_pilot','data/real_pilot/tiles_srgb','data/real_pilot/thumbnails_srgb']:
    files.extend(p for p in (ROOT/directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
for name in ['gdc_inventory.json','cohort_plan.json','download_receipts.json']:
    files.append(ROOT/'data/real_pilot'/name)
files.append(ROOT/'data/manifest_template.csv')
files=sorted(set(files))
pdf=ROOT.parent/'output/pdf/pancreatic_cancer_real_data_pilot.pdf'
if not pdf.exists(): raise FileNotFoundError('Generate and review the real-data PDF first.')
entries={(Path(ROOT.name)/p.relative_to(ROOT)).as_posix():p for p in files}
entries[f'{ROOT.name}/presentation/{pdf.name}']=pdf
manifest={'scope':'Code, real derived tissue tiles and thumbnails, audit metadata, reports and presentation. Raw SVS/RNA files omitted; acquire_pilot.py reproduces them.',
          'files':[{'path':name,'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()} for name,path in entries.items()]}
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=5) as z:
    for name,path in entries.items(): z.write(path,name)
    z.writestr(f'{ROOT.name}/DELIVERY_MANIFEST.json',json.dumps(manifest,indent=2))
with zipfile.ZipFile(target) as z:
    assert z.testzip() is None
    assert len([n for n in z.namelist() if '/tiles_srgb/' in n and n.endswith('.png')])==768
    assert not any(n.endswith(('.svs','.joblib')) for n in z.namelist())
print(target)
print(f'Files: {len(entries)+1}; size: {target.stat().st_size/1e6:.1f} MB')
