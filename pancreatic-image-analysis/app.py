from pathlib import Path
from tempfile import TemporaryDirectory
import joblib
import streamlit as st
from pipeline import predict
from context import TOPICS,treatment_context

st.set_page_config(page_title='Pancreatic image research',layout='wide')
st.title('Pancreatic cancer image research workbench')
st.info('This is the original demonstration workbench. For the real TCGA pilot results, run: streamlit run pilot_app.py')
st.warning('Research prototype. No validated diagnosis, clinical staging, EMT progression measurement or treatment selection.')
st.write('Upload H&E tiles from ONE patient. CT, MRI, whole slides and photographs require separate pipelines.')
model=Path(__file__).parent/'outputs/model.joblib'
files=st.file_uploader('Pathology tiles',type=['png','jpg','jpeg','tif','tiff'],accept_multiple_files=True)
if st.button('Analyze research features',disabled=not files):
    if not model.exists(): st.error('Run the training command first.')
    else:
        try:
            artifact=joblib.load(model)  # Fixed local path: only use artifacts you trained/trust.
            if artifact['synthetic']: st.error('SYNTHETIC DEMO MODEL: outputs have no medical meaning.')
            with TemporaryDirectory() as temp:
                paths=[]
                for i,f in enumerate(files):
                    if f.size>20*1024*1024: raise ValueError('Maximum tile file size: 20 MB')
                    path=Path(temp)/f'tile_{i}{Path(f.name).suffix}'
                    path.write_bytes(f.getvalue()); paths.append(path)
                result=predict(artifact,paths)
            st.json(result)
            import json
            st.download_button('Download research report',json.dumps(result,indent=2),'research_report.json')
        except Exception as e: st.error(str(e))
st.subheader('Clinical discussion context')
status=st.selectbox('Clinician-confirmed resectability (independent of image model)',list(TOPICS))
st.json(treatment_context(status))
