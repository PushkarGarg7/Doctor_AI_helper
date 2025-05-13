import openai
import pandas as pd

# Load rules CSV
csv_df = pd.read_csv("CBC_All_Conditions_Filtered.csv")

# Load extracted CBC values from PDF (already parsed in your system)
cbc_values = "Hemoglobin: 12.5 g/dL (Low), RBC Count: 5.2 mill/cumm, PCV: 57.5% (High), MCV: 87.75 fL, MCH: 27.2 pg, MCHC: 32.8 g/dL, RDW: 13.6%, WBC Count: 9000/cumm, Neutrophils: 60%, Lymphocytes: 31%, Eosinophils: 1%, Monocytes: 7%, Basophils: 1%, Platelet Count: 450000/cumm (High)"

# Top diseases and probabilities

# Build the user prompt
csv_summary = "Elevated white blood cell (WBC) count, known as leukocytosis, indicates infection or inflammation and is commonly observed in lung diseases such as pneumonia, lung cancer, and granulomatous infections. Neutrophilia, or an increase in neutrophils, suggests bacterial infection or inflammation, often seen in lung infections and nodule formation. Lymphopenia, characterized by a low lymphocyte count, is associated with advanced lung cancer and reflects disease progression and immune suppression. Anemia, indicated by reduced red blood cells or hemoglobin, is frequently found in lung cancer patients due to chronic disease, blood loss, or bone marrow suppression. Thrombocytosis, or elevated platelet count, acts as a paraneoplastic marker in lung cancer and points to systemic inflammation, while thrombocytopenia (low platelet count) may occur in advanced lung cancer, especially with bone marrow involvement or disseminated intravascular coagulation (DIC).An elevated red cell distribution width (RDW) reflects variation in RBC size and is linked to poor prognosis in lung cancer and severe COPD. Polycythemia, or increased red blood cell count, occurs due to chronic hypoxia and is typical in COPD and emphysema as the body compensates for low oxygen levels. Altered hemoglobin levels affect oxygen-carrying capacity and are commonly seen in COPD and lung cancer. Elevated hematocrit indicates increased RBC volume and is also seen in chronic lung diseases due to hypoxia. A high neutrophil-to-lymphocyte ratio (NLR) serves as an inflammatory marker and is significantly elevated in asthma, COPD, and lung infections, correlating with disease severity. Monocytosis, or elevated monocyte count, appears in chronic inflammatory lung conditions like tuberculosis. Lymphocytosis, or increased lymphocytes, may point to chronic infections such as TB or pertussis. Neutropenia, a reduction in neutrophils, is observed in viral lung infections or due to drug-induced immunosuppression.Additionally, elevated ESR (erythrocyte sedimentation rate) is a nonspecific marker of inflammation and is raised in TB, pneumonia, and chronic lung disease exacerbations. High CRP (C-reactive protein) levels indicate acute-phase inflammation and are common in pneumonia, TB, and COPD flare-ups. Bandemia, or the presence of immature neutrophils, is seen in severe bacterial pneumonia. Eosinophilia, or increased eosinophils, is a key indicator in allergic asthma and eosinophilic lung diseases, while eosinopenia (low eosinophils) may occur in severe infections or with corticosteroid use. Lastly, basophilia, though rare, can be present in allergic pulmonary reactions."

cbc_summary = "\n".join([f"{k}: {v}" for k, v in cbc_values.items()])
disease_summary = ", ".join([f"{k} with probability ({v:.3f})" for k, v in top_diseases.items()])

user_prompt = f"""
You are a clinical assistant analyzing CBC reports.
Here are the patient's CBC values:
{cbc_summary}

Below are the known symptom inference rules from medical literature:
{csv_summary}

Analyze these CBC values against the inference rules. Then, based on the following diseases and their probabilities:
{disease_summary}

Output a JSON object with:
1. extracted_CBC_parameters – the values above.
2. highlighted_abnormalities – only the ones outside normal range.
3. potential_medical_conditions – inferred conditions from symptoms.
4. top_disease_likelihoods – for each top disease, explain its relevance based on CBC symptoms, or return 'No inference by CBC for this disease.'
"""

# System prompt
system_prompt = "You are a helpful medical assistant that returns structured analysis in JSON format."

# Send to OpenAI API
response = openai.ChatCompletion.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ],
    temperature=0.2
)

# Extract and display result
output = response["choices"][0]["message"]["content"]
print(output)
