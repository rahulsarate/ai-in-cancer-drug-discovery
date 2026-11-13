"""Read-only evidence dashboard for the real public-data pilot."""
from pathlib import Path
import json
import streamlit as st

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'outputs/real_pilot'
st.set_page_config(page_title='TCGA pancreatic pilot evidence',layout='wide')
st.title('TCGA-PAAD: real-data technical pilot')
st.warning('Research feasibility only. Tissue tiles are not expert tumor annotations. Bulk RNA composite is not a validated EMT assay. No clinical staging or treatment selection.')
path=OUT/'pilot_results.json'
if not path.exists():
    st.info('Run acquire_pilot.py and run_real_pilot.py first.'); st.stop()
r=json.loads(path.read_text())
endpoint=r['primary_endpoints']; e=r['exploratory_emt']
cols=st.columns(3)
cols[0].metric('Real evaluable patients',endpoint['evaluable_patients'])
cols[1].metric('Extracted tissue tiles',endpoint['retained_tiles'])
cols[2].metric('Verified source files',endpoint['verified_raw_files'])
st.caption('NCI GDC / TCGA Research Network. Patient-level image/RNA pairing; same tissue block not established.')
st.subheader('Real image examples')
st.image(str(OUT/'real_image_gallery.png'),caption='Real TCGA tissue tiles. Unreviewed for tumor, artifacts and EMT phenotype.')
st.subheader('Exploratory site-held-out evaluation')
st.write(f"Image model MAE: {e['model_mae']:.3f}; training-mean baseline MAE: {e['baseline_mae']:.3f} score units.")
if e['model_mae']>=e['baseline_mae']: st.info('The image model did not improve on the mean baseline. No predictive benefit is demonstrated.')
elif e['mae_improvement_over_mean_percentile_95'][0]<=0:
    st.info('The point estimate favors the image model, but the descriptive interval includes no improvement. A predictive advantage is not established.')
st.image(str(OUT/'exploratory_results.png'))
st.write(e['evaluation']); st.caption(e['method'])
st.subheader('Stage reference labels, not stage predictions')
st.json({'stage_counts':r['stage_counts_exact'],'staging_editions':r['staging_editions'],'model_status':r['stage_model']})
st.subheader('Audit and limitations')
st.json(r)
for name in ['pilot_results.json','patient_manifest.csv','tile_manifest.csv','out_of_fold_predictions.csv']:
    st.download_button(f'Download {name}',(OUT/name).read_bytes(),name)
