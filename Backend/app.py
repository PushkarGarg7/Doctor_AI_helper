# === Core Imports and Flask Setup ===
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import numpy as np
from flask_cors import CORS
from dotenv import load_dotenv

# === MongoDB Setup ===
from pymongo.server_api import ServerApi
from pymongo import MongoClient

# === CrewAI Agents and Tasks ===
from crewai import Crew, Process
from crew import Crew, Process, symptom_agent, question_agent, symptom_task, questions_task, analysis_agent, analysis_task

# === CNN Model for Prediction ===
from cnn import load_model, predict
from cnn2 import predict_disease_probabilities, get_diseases_above_threshold

# === Utilities: Auth, JSON, Regex ===
import bcrypt
import json
import re

# === PDF Report Generation ===
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

# === Miscellaneous and OpenAI ===
import random
import openai

# === CBC Agent Tools and Tasks ===
from tool1 import get_tools
from agent1 import get_cbc_analysis_agent
from task1 import get_cbc_analysis_task, get_cbc_analysis_task2

# === Flask App and Config ===
app = Flask(__name__)
load_dotenv()
CORS(app)

# === MongoDB Connection ===
mongo_uri = os.getenv('MONGO_URI')
client = MongoClient(mongo_uri, server_api=ServerApi('1'))
users_collection = client.myapp.users

# === Temporary Directory Setup ===
TEMP_DIR = './temp'
os.makedirs(TEMP_DIR, exist_ok=True)

# === CBC Rules and Model Paths from .env ===
CBC_RULE_CSV_PATH = os.getenv('CBC_RULE_CSV_PATH')
MODEL_WEIGHTS_PATH = os.getenv('MODEL_WEIGHTS_PATH')

# === AWS S3 Configuration ===
aws_access_key_id = os.getenv('AWS_ACCESS_KEY')
aws_secret_access_key = os.getenv('AWS_SECRET_KEY')
region_name = os.getenv('REGION_NAME')

# === S3 Client Setup ===
from io import BytesIO
from PyPDF2 import PdfReader
import boto3
from botocore.exceptions import NoCredentialsError
import uuid
s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id,
                         aws_secret_access_key=aws_secret_access_key,
                         region_name=region_name)
BUCKET_NAME = os.getenv('BUCKET_NAME')

# === Load CNN Model ===
model = load_model(MODEL_WEIGHTS_PATH)

# === Global Variables for CBC Analysis State ===
cbc_Data = {}
global_cbc_storage = {}
global_disease_probablities = {}


# def openaiChatOutput2():
#     disease_probablities={"Infiltration" : 33.00,"Effusion": 15.80,"Atelectasis" : 9.30}
#     disease_summary = ", ".join([f"{k} with probability ({v:.3f})" for k, v in disease_probablities.items()])

#      # Load extracted CBC values from PDF (already parsed in your system)
#     cbc_values = "Hemoglobin: 12.5 g/dL (Low), RBC Count: 5.2 mill/cumm, PCV: 57.5% (High), MCV: 87.75 fL, MCH: 27.2 pg, MCHC: 32.8 g/dL, RDW: 13.6%, WBC Count: 9000/cumm, Neutrophils: 60%, Lymphocytes: 31%, Eosinophils: 1%, Monocytes: 7%, Basophils: 1%, Platelet Count: 450000/cumm (High)"

#     # Top diseases and probabilities

#     # Build the user prompt
#     csv_summary = "Elevated white blood cell (WBC) count, known as leukocytosis, indicates infection or inflammation and is commonly observed in lung diseases such as pneumonia, lung cancer, and granulomatous infections. Neutrophilia, or an increase in neutrophils, suggests bacterial infection or inflammation, often seen in lung infections and nodule formation. Lymphopenia, characterized by a low lymphocyte count, is associated with advanced lung cancer and reflects disease progression and immune suppression. Anemia, indicated by reduced red blood cells or hemoglobin, is frequently found in lung cancer patients due to chronic disease, blood loss, or bone marrow suppression. Thrombocytosis, or elevated platelet count, acts as a paraneoplastic marker in lung cancer and points to systemic inflammation, while thrombocytopenia (low platelet count) may occur in advanced lung cancer, especially with bone marrow involvement or disseminated intravascular coagulation (DIC).An elevated red cell distribution width (RDW) reflects variation in RBC size and is linked to poor prognosis in lung cancer and severe COPD. Polycythemia, or increased red blood cell count, occurs due to chronic hypoxia and is typical in COPD and emphysema as the body compensates for low oxygen levels. Altered hemoglobin levels affect oxygen-carrying capacity and are commonly seen in COPD and lung cancer. Elevated hematocrit indicates increased RBC volume and is also seen in chronic lung diseases due to hypoxia. A high neutrophil-to-lymphocyte ratio (NLR) serves as an inflammatory marker and is significantly elevated in asthma, COPD, and lung infections, correlating with disease severity. Monocytosis, or elevated monocyte count, appears in chronic inflammatory lung conditions like tuberculosis. Lymphocytosis, or increased lymphocytes, may point to chronic infections such as TB or pertussis. Neutropenia, a reduction in neutrophils, is observed in viral lung infections or due to drug-induced immunosuppression.Additionally, elevated ESR (erythrocyte sedimentation rate) is a nonspecific marker of inflammation and is raised in TB, pneumonia, and chronic lung disease exacerbations. High CRP (C-reactive protein) levels indicate acute-phase inflammation and are common in pneumonia, TB, and COPD flare-ups. Bandemia, or the presence of immature neutrophils, is seen in severe bacterial pneumonia. Eosinophilia, or increased eosinophils, is a key indicator in allergic asthma and eosinophilic lung diseases, while eosinopenia (low eosinophils) may occur in severe infections or with corticosteroid use. Lastly, basophilia, though rare, can be present in allergic pulmonary reactions."

#     disease_summary = ", ".join([f"{k} with probability ({v:.3f})" for k, v in global_disease_probablities.items()])

#     user_prompt = f"""
#     You are a clinical assistant analyzing CBC reports.
#     Here are the patient's CBC values:
#     {cbc_values}
#     Below are the known symptom inference rules from medical literature:
#     {csv_summary}
#     Analyze these CBC values against the inference rules. Then, based on the following diseases and their probabilities:
#     {disease_summary}

#     Output a JSON object with:
#     1. extracted_CBC_parameters – the values above.
#     2. highlighted_abnormalities – only the ones outside normal range.
#     3. potential_medical_conditions – inferred conditions from symptoms.
#     4. top_disease_likelihoods – for each top disease, explain its relevance based on CBC symptoms don't say no inference always write a reference from that cbc report'
#     """

#     # System prompt
#     system_prompt = "You are a helpful medical assistant that returns structured analysis in JSON format."

#     # Send to OpenAI API
#     response = openai.chat.completions.create(
#         model="gpt-4o",
#         messages=[
#             {"role": "system", "content": system_prompt},
#             {"role": "user", "content": user_prompt}
#         ],
#         temperature=0.5
#     )

#     # Extract and display result
#     output = response.choices[0].message.content
#     print(output)

#     raw_json_string = output
    
#     if raw_json_string.startswith("```json") and raw_json_string.endswith("```"):
#         raw_json_string = raw_json_string[7:-3].strip()  # Remove ```json and ```

#     # Parse the JSON string into a Python dictionary
#     parsed_data = json.loads(raw_json_string)
#     global_cbc_storage['new_cbc_data'] = parsed_data

#     print(parsed_data)
#     return parsed_data

# === Helper Function to Format CNN Predictions ===
def format_predictions_to_dict(predictions, labels):
    # predictions = predictions.flatten()  # Flatten the prediction array
    formatted_predictions = {label: round(prob, 3) for label, prob in zip(labels, predictions)}  # Create label-probability mapping
    print(formatted_predictions)  # Debug print
    return formatted_predictions

# === CNN Endpoint for X-ray Image Analysis ===
@app.route('/cnn2', methods=['POST'])
def CnnCall2():
    if 'file' not in request.files:
            return jsonify({'error': 'No image file found in the request'}), 400

        # Define possible disease labels and prepare image path
    image_file = request.files['file']
    image_filename = image_file.filename
    image_path = os.path.join(TEMP_DIR, image_filename)
    
    disease_labels = [
    'Cardiomegaly', 'Emphysema', 'Effusion', 'Hernia', 'Infiltration', 
    'Mass', 'Nodule', 'Atelectasis', 'Pneumothorax', 'Pleural_Thickening', 
    'Pneumonia', 'Fibrosis', 'Edema', 'Consolidation'
    ]

    try:
        image_file.save(image_path)  # Save uploaded image to temp directory
    except Exception as e:
        return jsonify({'error': f"Failed to save the image. {str(e)}"}), 500
    
    try:
        # Run CNN model to get predictions
        predicted_probs = predict_disease_probabilities(image_path)
        positive_diseases = get_diseases_above_threshold(predicted_probs)

        # Format predictions as a readable dictionary
        formatted_predictions = format_predictions_to_dict(predicted_probs, disease_labels)

        # Ensure all values are floats with 3 decimal precision
        for key in formatted_predictions:
            formatted_predictions[key] = float(round(formatted_predictions[key], 3))

        # Create response and extract top 3 predictions
        response = {"predictions": formatted_predictions, "positive_diseases" : positive_diseases}
        
        top_3_predictions = dict(sorted(
            formatted_predictions.items(),
            key=lambda item: item[1],
            reverse=True
        )[:3])

        # Save top diseases to global state for use in other modules
        global_disease_probablities["top_diseases"] = top_3_predictions

        return jsonify(response), 201

    except:
        # Fallback for unexpected server-side errors
        return jsonify({"error": "Server Error"}), 500


# === CNN Endpoint for X-ray Image Analysis ===
@app.route('/cnn', methods=['POST'])
def CnnCall():
    # Validate if image file is present in the request
    if 'file' not in request.files:
        return jsonify({'error': 'No image file found in the request'}), 400

    # Define possible disease labels and prepare image path
    image_file = request.files['file']
    all_labels = np.array([
        'Atelectasis', 'Cardiomegaly', 'Consolidation', 'Edema', 'Effusion',
        'Emphysema', 'Fibrosis', 'Hernia', 'Infiltration', 'Mass',
        'Nodule', 'Pleural_Thickening', 'Pneumonia', 'Pneumothorax'
    ])
    image_filename = image_file.filename
    image_path = os.path.join(TEMP_DIR, image_filename)

    try:
        image_file.save(image_path)  # Save uploaded image to temp directory
    except Exception as e:
        return jsonify({'error': f"Failed to save the image. {str(e)}"}), 500

    try:
        # Run CNN model to get predictions
        predictions = predict(model, image_path)

        # Format predictions as a readable dictionary
        formatted_predictions = format_predictions_to_dict(predictions, all_labels)

        # Ensure all values are floats with 3 decimal precision
        for key in formatted_predictions:
            formatted_predictions[key] = float(round(formatted_predictions[key], 3))

        # Create response and extract top 3 predictions
        response = {"predictions": formatted_predictions}
        top_3_predictions = dict(sorted(
            formatted_predictions.items(),
            key=lambda item: item[1],
            reverse=True
        )[:3])

        # Save top diseases to global state for use in other modules
        global_disease_probablities["top_diseases"] = top_3_predictions

        return jsonify(response), 201

    except:
        # Fallback for unexpected server-side errors
        return jsonify({"error": "Server Error"}), 500

# === Endpoint to Perform Agent based Reasoning on Top Disease Probabilities ===
@app.route('/rag1', methods=['POST'])
def rag1():
    try:
        # === Extract data from the POST request ===
        data = request.json
        age = data.get('age')
        gender = data.get('gender')
        top_probabilities = data.get('top_probabilities')

        # === Validate required fields ===
        if not all([age, gender, top_probabilities]):
            return jsonify({"error": "Missing required fields"}), 400

        print("I have these top Probablities")
        print(top_probabilities)

        # === Execute CrewAI task using disease probabilities, age, and gender ===
        task_result = executeCrewTasks(top_probabilities, age, gender)
        print(type(task_result))
        print(task_result)

        # === Clean up raw JSON response if wrapped in code block markers ===
        raw_json_string = task_result.raw
        if raw_json_string.startswith("```json") and raw_json_string.endswith("```"):
            raw_json_string = raw_json_string[7:-3].strip()

        # === Parse JSON string into dictionary ===
        parsed_data = json.loads(raw_json_string)

        # === Return the parsed result as a JSON response ===
        return jsonify(parsed_data), 200

    except Exception as e:
        # === Handle and return any unexpected errors ===
        return jsonify({"error": str(e)}), 500



# === Generates a structured medical PDF report with X-ray, CBC, and AI insights ===
def generate_pdf(name, age, height, gender, weight, raw_json_string, top_diseases, xray_image_path, cbc_data):
    pdf_path = "Preliminary_Report.pdf"
    pdf = SimpleDocTemplate(pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    normal_style = styles['Normal']
    heading_style = styles['Heading2']

    # === Report Title ===
    title = Paragraph("Preliminary Report", title_style)
    spacer = Spacer(1, 12)

    # === Patient Information Section ===
    patient_data = [
        ["Name:", name],
        ["Age:", f"{age} years"],
        ["Gender:", gender],
        ["Height:", f"{height} cm"],
        ["Weight:", f"{weight} kg"]
    ]
    patient_table = Table(patient_data, colWidths=[70, 200])
    patient_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    # === X-ray Image Display ===
    xray_image = Image(xray_image_path, width=3 * inch, height=3 * inch)
    xray_image.hAlign = 'CENTER'

    # === AI-Predicted Diseases with Probabilities Table ===
    disease_table_data = [["Disease", "Probability"]]
    for disease in top_diseases:
        for key, value in disease.items():
            disease_table_data.append([key, f"{value * 100:.2f}%"])

    disease_table = Table(disease_table_data, colWidths=[150, 150])
    disease_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    # === Insights from RAG/LLM JSON Response ===
    formatted_raw_json = clean_and_format_raw_json(raw_json_string)
    raw_json_paragraphs = []
    for paragraph in formatted_raw_json.split("<BR/>"):
        raw_json_paragraphs.append(Paragraph(paragraph.strip(), normal_style))
        raw_json_paragraphs.append(Spacer(1, 6))

    # === Assemble Report Sections ===
    elements = [
        title, spacer, patient_table, Spacer(1, 12), xray_image,
        Spacer(1, 24), Paragraph("Diseases and Probabilities", heading_style),
        Spacer(1, 6), disease_table, Spacer(1, 24),
        Paragraph("Analysis Insights", heading_style),
        Spacer(1, 6)
    ] + raw_json_paragraphs

    # === CBC Abnormalities Section ===
    elements.append(Spacer(1, 24))
    elements.append(Paragraph("Insights from CBC Data", heading_style))
    elements.append(Spacer(1, 6))

    cbc_abnormalities = cbc_data.get("highlighted_abnormalities", {})
    for key, value in cbc_abnormalities.items():
        elements.append(Paragraph(f"<b>{key}:</b> {value}", normal_style))
        elements.append(Spacer(1, 4))

    # === Inferred Conditions from CBC ===
    cbc_medical_conditions = cbc_data.get("potential_medical_conditions", [])
    if cbc_medical_conditions:
        elements.append(Spacer(1, 12))
        elements.append(Paragraph("<b>Observations of Medical Conditions :</b>", normal_style))
        for obs in cbc_medical_conditions:
            elements.append(Paragraph(f"• {obs}", normal_style))
            elements.append(Spacer(1, 4))

    # === Disease Likelihoods from CBC Rules ===
    top_disease_likelihoods = cbc_data.get("top_disease_likelihoods", {})
    if top_disease_likelihoods:
        elements.append(Spacer(1, 12))
        elements.append(Paragraph("<b>Observations of Disease Likelihood:</b>", normal_style))
        for disease, likelihood in top_disease_likelihoods.items():
            elements.append(Paragraph(f"• {disease}: {likelihood}", normal_style))
            elements.append(Spacer(1, 4))

    # === Build PDF Report ===
    pdf.build(elements)
    print(f"PDF generated: {pdf_path}")
    return pdf_path


# === Uploads the generated PDF to AWS S3 and returns the public URL ===
def get_pdf_link(local_pdf_path):
    unique_filename = f"{uuid.uuid4()}.pdf"
    print("Uploading PDF to S3...")

    try:
        with open(local_pdf_path, 'rb') as pdf_file:
            s3.upload_fileobj(pdf_file, BUCKET_NAME, unique_filename, ExtraArgs={'ContentType': 'application/pdf'})
        file_url = f"https://{BUCKET_NAME}.s3.{s3.meta.region_name}.amazonaws.com/{unique_filename}"
        print("PDF successfully uploaded to S3 at:", file_url)
        return file_url
    except NoCredentialsError:
        return jsonify({'error': 'Credentials not available'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# === Cleans and formats raw JSON response into paragraph-friendly HTML text ===
def clean_and_format_raw_json(raw_json_string):
    import re
    cleaned_text = raw_json_string.replace('\n', '<BR/>\n')
    cleaned_text = re.sub(r"[*\-]", "", cleaned_text)
    cleaned_text = re.sub(r"\s{2,}", " ", cleaned_text)
    return cleaned_text.strip()


# === Endpoint to process disease insights, perform RAG, and return diagnostic PDF link ===
@app.route('/rag2', methods=['POST'])
def rag2():
    try:
        # --- Extract incoming JSON fields ---
        data = request.json
        top_diseases = data.get('top_diseases')
        question_answers = data.get('question_answers')
        name = data.get('name')
        age = data.get('age')
        gender = data.get('gender')
        height = data.get('height')
        weight = data.get('weight')
        imagePath = data.get('image_path')
        
        # --- Validate essential input types ---
        if not isinstance(top_diseases, list) or not isinstance(question_answers, dict):
            return jsonify({"error": "Invalid input format"}), 400

        # --- Call CrewAI task executor for RAG-based analysis ---
        task_result = executeCrewTasks2(top_diseases, question_answers)

        # --- Extract and clean raw RAG response ---
        raw_json_string = task_result.raw 
        print(raw_json_string)
        raw_json_string = clean_and_format_raw_json(raw_json_string)

        # --- Retrieve globally stored CBC data ---
        CBC_Data = global_cbc_storage['cbc_data'] 
        print("-------")
        print(global_cbc_storage['cbc_data'])

        # --- Generate structured PDF report locally ---
        local_pdf_link = generate_pdf(name, age, height, gender, weight, raw_json_string, top_diseases, imagePath, cbc_data=CBC_Data)
        
        # --- Upload PDF to S3 and return public URL ---
        pdf_link = get_pdf_link(local_pdf_link)
        return jsonify({"pdf_link": pdf_link}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# === Crew 1: Handles initial question + symptom-based task processing ===
crew_1 = Crew(
  agents=[symptom_agent, question_agent],
  tasks=[symptom_task, questions_task],
  process=Process.sequential,  # Sequential execution of tasks
  memory=True,
  cache=True,
  max_rpm=100,
  share_crew=True
)

# === Crew 2: Focused on advanced analysis from previous inputs ===
crew_2 = Crew(
  agents=[analysis_agent],
  tasks=[analysis_task],
  process=Process.sequential,  # Sequential execution (default)
  memory=True,
  cache=True,
  max_rpm=100,
  share_crew=True
)

# === Executes CrewAI pipeline (crew_1) for symptom-based disease insight generation ===
def executeCrewTasks(top_diseases, age, gender):
    # Convert list of disease dictionaries to a single disease:probability dictionary
    diseases_dict = {list(disease_dict.keys())[0]: list(disease_dict.values())[0] for disease_dict in top_diseases}

    # Run the first Crew (symptom + question agents) with disease and patient data
    result = crew_1.kickoff(inputs={
        'diseases': diseases_dict,  # Diseases with their probabilities
        'age': age,
        'gender': gender
    })
    return result


# === Executes CrewAI pipeline (crew_2) for deeper analysis using question-answer context ===
def executeCrewTasks2(top_diseases, question_answer):
    # Convert top diseases into a readable string format: "Disease1: val1, Disease2: val2"
    diseases_str = ", ".join([f"{list(d.keys())[0]}: {list(d.values())[0]}" for d in top_diseases])

    # Run the second Crew (analysis agent) with disease summary and Q&A context
    result = crew_2.kickoff(inputs={
        'diseases': diseases_str,
        'question_answers': question_answer
    })
    return result


# === Helper to validate uploaded file extensions ===
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

        
# === Executes a CrewAI-based CBC (Complete Blood Count) Analysis Agent ===
def executeCBCAgent(pdf_path):
    # Load the CSV and PDF tools required for rule-based CBC interpretation
    csv_tool, pdf_tool = get_tools(CBC_RULE_CSV_PATH, pdf_path)

    # Get the top diseases from global probabilities for context-aware CBC interpretation
    top_diseases = global_disease_probablities["top_diseases"]

    # Instantiate CBC analysis agent and its associated task
    agent = get_cbc_analysis_agent(pdf_tool=pdf_tool, csv_tool=csv_tool)
    task = get_cbc_analysis_task2(agent=agent, pdf_tool=pdf_tool, csv_tool=csv_tool, top_diseases=top_diseases)

    # Create a Crew with the CBC agent and task, set to run sequentially with caching and memory
    crew = Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True,
        memory=True,
        cache=True,
        full_output=True
    )

    # Execute the crew pipeline and return result
    result = crew.kickoff()
    return result


# === Configuration for storing uploaded CBC PDF files ===
UPLOAD_FOLDER = 'CBC_Uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# === Flask route for uploading and analyzing CBC reports in PDF format ===
@app.route("/analyze-cbc", methods=["POST"])
def analyze_cbc():
    # --- Validate that a file is part of the request ---
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # --- Save the uploaded PDF file securely ---
    filename = secure_filename(file.filename)
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(pdf_path)

    try:
        # Run the CBC analysis using CrewAI agent
        task_result = executeCBCAgent(pdf_path)
        print(type(task_result))
        print(task_result)

        # Extract and clean raw JSON string output from the agent
        raw_json_string = task_result.raw
        if raw_json_string.startswith("```json") and raw_json_string.endswith("```"):
            raw_json_string = raw_json_string[7:-3].strip()

        # Convert raw JSON string into a Python dictionary
        parsed_data = json.loads(raw_json_string)
        global_cbc_storage['cbc_data'] = parsed_data  # Store in global state

        print(parsed_data)
        return jsonify(parsed_data), 200  # Return structured JSON response

    except Exception as e:
        return jsonify({'error': str(e)}), 500  # Handle and return any runtime errors



# === Endpoint: User Login ===
# Validates credentials against stored hashed passwords in MongoDB.
# Returns user details on successful login or error message on failure.
@app.route("/login", methods=['POST'])
def loginUser():
    data = request.json
    required_fields = ['email', 'password']
    
    # Ensure all required fields are present
    for field in required_fields:
        if not data.get(field):
            return jsonify({"msg": f"'{field}' is required"}), 400

    # Retrieve user record from the database by email
    user = users_collection.find_one({'email': data['email']})
    
    # Verify password using bcrypt hash comparison
    if user and bcrypt.checkpw(data['password'].encode('utf-8'), user['password'].encode('utf-8')):
        return jsonify({
            "msg": "Login successful",
            "user": {
                "name": user['name'],
                "email": user['email'],
            }
        }), 200

    # If credentials are invalid, return 401
    return jsonify({"msg": "Invalid email or password"}), 401


# === Endpoint: User Registration ===
# Registers a new user after validating inputs and hashing the password.
# Ensures email uniqueness before inserting the user into the database.
@app.route("/register", methods=['POST'])
def createUser():
    data = request.json
    
    # Ensure all required fields are present
    required_fields = ['name', 'email', 'password']
    for field in required_fields:
        if not data.get(field):
            return jsonify({"msg": f"'{field}' is required"}), 400

    # Check for duplicate email in the database
    if users_collection.find_one({'email': data['email']}):
        return jsonify({"msg": "User already exists"}), 400

    # Hash the password using bcrypt before storing
    hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
    
    # Insert user details into the collection
    users_collection.insert_one({
        'name': data['name'],
        'email': data['email'],
        'password': hashed_password.decode('utf-8'),
    })
    
    return jsonify({"msg": "User created successfully"}), 201


# === Application Entry Point ===
# Runs the Flask app in debug mode for development
if __name__ == '__main__':
    app.run(debug=True)
