"""Educational discussion topics selected ONLY from clinician-entered status."""
SOURCE='https://www.cancer.gov/types/pancreatic/hp/pancreatic-treatment-pdq'
TOPICS={
    'Unknown':['Obtain multidisciplinary staging and resectability assessment before discussing a disease-specific pathway.'],
    'Resectable':['Discuss surgical assessment and perioperative systemic therapy with the pancreatic multidisciplinary team.'],
    'Borderline resectable':['Discuss neoadjuvant systemic therapy, possible radiation, and reassessment for surgery.'],
    'Locally advanced':['Discuss systemic therapy and selected local approaches after multidisciplinary review.'],
    'Metastatic':['Discuss systemic therapy, biomarker-directed options when eligible, symptom care, and clinical trials.'],
}

def treatment_context(status):
    if status not in TOPICS: raise ValueError('Unknown resectability category')
    return {'clinician_entered_status':status,'discussion_topics':TOPICS[status],
            'additional_review':['Histological diagnosis and disease extent','Performance status, organ function, comorbidities and patient goals',
                                 'Germline and tumor molecular testing as appropriate','Supportive care and clinical-trial eligibility'],
            'source':SOURCE,'source_reviewed':'2026-11-13',
            'scope':'Educational context, not a prescription. Image/EMT output is not used to choose treatment.'}
