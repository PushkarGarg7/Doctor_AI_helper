from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import numpy as np
from flask_cors import CORS
from dotenv import load_dotenv
from pymongo.server_api import ServerApi
from pymongo import MongoClient
from crew import Crew, Process, symptom_agent, question_agent, symptom_task, questions_task, analysis_agent, analysis_task
from cnn import load_model, predict
import bcrypt
import json
import re
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
import random

app = Flask(__name__)
load_dotenv()
CORS(app)  # Enable CORS for the Flask app
mongo_uri = os.getenv('MONGO_URI')
client = MongoClient(mongo_uri, server_api=ServerApi('1'))
users_collection = client.myapp.users
TEMP_DIR = './temp'
os.makedirs(TEMP_DIR, exist_ok=True)


aws_access_key_id=os.getenv('AWS_ACCESS_KEY')
aws_secret_access_key=os.getenv('AWS_SECRET_KEY')
region_name=os.getenv('REGION_NAME')
# BUCKET_NAME = os.getenv('BUCKET_NAME')

from io import BytesIO
from PyPDF2 import PdfReader
import boto3
from botocore.exceptions import NoCredentialsError
import uuid
s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id,
                         aws_secret_access_key=aws_secret_access_key,
                         region_name=region_name)

BUCKET_NAME = os.getenv('BUCKET_NAME')

MODEL_WEIGHTS_PATH = "C:\Abhinav\Abhinav\PEC\Major Project\model_weights.weights.h5"
model = load_model(MODEL_WEIGHTS_PATH)

def format_predictions_to_dict(predictions, labels):
    predictions = predictions.flatten()
    
    formatted_predictions = {label: round(prob, 3) for label, prob in zip(labels, predictions)}
    print(formatted_predictions)
    # Convert formatted predictions (values) to numpy array
    # formatted_predictions_array = np.array(list(formatted_predictions.values()))
    
    return formatted_predictions


@app.route('/cnn', methods=['POST'])
def CnnCall():
    if 'file' not in request.files:
        return jsonify({'error': 'No image file found in the request'}), 400

    # Save the uploaded file
    image_file = request.files['file']
    all_labels = np.array(['Atelectasis', 'Cardiomegaly', 'Consolidation', 'Edema', 'Effusion', 'Emphysema', 'Fibrosis', 'Hernia', 'Infiltration', 'Mass', 'Nodule', 'Pleural_Thickening', 'Pneumonia', 'Pneumothorax'])
    image_filename = image_file.filename
    image_path = os.path.join(TEMP_DIR, image_filename)
    
    try:
        image_file.save(image_path)
    except Exception as e:
        return jsonify({'error': f"Failed to save the image. {str(e)}"}), 500
    try:
        # Get predictions
        predictions = predict(model, image_path)
        # print("-----")
        # print(predictions, "HeLLO")
        formatted_predictions = format_predictions_to_dict(predictions, all_labels)
        for key in formatted_predictions:
            # formatted_predictions[key] = float(formatted_predictions[key])
            formatted_predictions[key] = float(round(formatted_predictions[key], 3))
        response = {"predictions": formatted_predictions}
        return jsonify(response), 201
    except:
        return jsonify({"error": "Server Error"}), 500

@app.route('/rag1', methods=['POST'])
def rag1():
    try:
        # Get data from request
        data = request.json
        age = data.get('age')
        gender = data.get('gender')
        top_probabilities = data.get('top_probabilities')

        if not all([age, gender, top_probabilities]):
            return jsonify({"error": "Missing required fields"}), 400
      
        print(top_probabilities)
        # Process the data (replace with actual logic for RAG model)
        task_result = executeCrewTasks(top_probabilities, age,gender)
        print(type(task_result))
        print(task_result)
        raw_json_string = task_result.raw  # Ensure 'raw' is the correct field
    
        # Remove unnecessary backticks or code block markers if present
        if raw_json_string.startswith("```json") and raw_json_string.endswith("```"):
            raw_json_string = raw_json_string[7:-3].strip()  # Remove ```json and ```

        # Parse the JSON string into a Python dictionary
        parsed_data = json.loads(raw_json_string)
        
        # Convert to JSON response (if using Flask, for example)
        return jsonify(parsed_data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def generate_pdf(name, age, height, gender, weight, raw_json_string, top_diseases, xray_image_path="../img1.png"):
    pdf_path = "Preliminary_Report.pdf"
    pdf = SimpleDocTemplate(pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    normal_style = styles['Normal']
    heading_style = styles['Heading2']
    
    # Title
    title = Paragraph("Preliminary Report", title_style)
    spacer = Spacer(1, 12)

    # Patient Info Table
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

    # X-ray Image
    xray_image = Image(xray_image_path, width=3 * inch, height=3 * inch)
    xray_image.hAlign = 'CENTER'

    # Diseases and Probabilities Table
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

    # Insights from Raw JSON String
    formatted_raw_json = clean_and_format_raw_json(raw_json_string)
    print('------------')
    print(formatted_raw_json)
    raw_json_paragraphs = []
    for paragraph in formatted_raw_json.split("<BR/>"):
        raw_json_paragraphs.append(Paragraph(paragraph.strip(), normal_style))
        raw_json_paragraphs.append(Spacer(1, 6))  # Add space between paragraphs

    # Assemble Elements
    elements = [
        title,
        spacer,
        patient_table,
        Spacer(1, 12),
        xray_image,
        Spacer(1, 24),
        Paragraph("Diseases and Probabilities", heading_style),
        Spacer(1, 6),
        disease_table,
        Spacer(1, 24),
        Paragraph("Analysis Insights", heading_style),
        Spacer(1, 6),
    ] + raw_json_paragraphs  # Add JSON paragraphs with spacers

    pdf.build(elements)
    print(f"PDF generated: {pdf_path}")
    return pdf_path


def get_pdf_link(local_pdf_path):
    unique_filename = f"{uuid.uuid4()}.pdf"  # Use a unique filename for the S3 upload
    print("Uploading PDF to S3...")

    try:
        # Open the locally saved PDF file and upload it to S3
        with open(local_pdf_path, 'rb') as pdf_file:
            s3.upload_fileobj(pdf_file, BUCKET_NAME, unique_filename, ExtraArgs={'ContentType': 'application/pdf'})

        # Construct the file URL
        file_url = f"https://{BUCKET_NAME}.s3.{s3.meta.region_name}.amazonaws.com/{unique_filename}"
        print("PDF successfully uploaded to S3 at:", file_url)

        return file_url

    except NoCredentialsError:
        return jsonify({'error': 'Credentials not available'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500



import re

def clean_and_format_raw_json(raw_json_string):
    import re

    # Remove asterisks (*) and other unwanted symbols
    cleaned_text = raw_json_string.replace('\n', '<BR/>\n')
    cleaned_text = re.sub(r"[*\-]", "", cleaned_text)  # Remove asterisks and dashes
    cleaned_text = re.sub(r"\s{2,}", " ", cleaned_text)  # Remove extra spaces
    cleaned_text = cleaned_text.strip()  # Remove leading and trailing spaces

    # Replace newlines with <br /> tags for proper HTML formatting

    return cleaned_text





@app.route('/rag2', methods=['POST'])
def rag2():
    try:
        # Parse input JSON
        data = request.json
        top_diseases = data.get('top_diseases')
        question_answers = data.get('question_answers')
        name = data.get('name')
        age = data.get('age')
        gender = data.get('gender')
        height = data.get('height')
        weight = data.get('weight')
        imagePath = data.get('image_path')
        
        
        # Validate inputs
        if not isinstance(top_diseases, list) or not isinstance(question_answers, dict):
            return jsonify({"error": "Invalid input format"}), 400

        # Call the function with provided data
        task_result = executeCrewTasks2(top_diseases, question_answers)
        
        # Extract raw_json_string from task_result
        raw_json_string = task_result.raw 

#         # Generate PDF with all required data
#         raw_json_string = '''Fibrosis:
# - Probability: 0.384
# - Symptoms Analysis:
#   - Sudden episodes of shortness of breath without physical activity: Common in fibrosis.
#   - Increased difficulty breathing when lying down: Indicative of lung issues, including fibrosis.
#   - Dry cough: Often associated with fibrotic changes in the lungs.       
#   - Chest discomfort with deep breathing: Seen in fibrosis due to stiff lung tissue.
#   - No changes in skin or lip color: Lack of this symptom does not rule out fibrosis.
# - Certainty Level: Medium
#   - Reasoning: The presence of classic symptoms such as dry cough, difficulty breathing during rest, and discomfort with deep breathing align with fibrosis. However, the absence of other significant symptoms like cyanosis (bluish skin or lips) prevents a high certainty designation.

# Edema:
# - Probability: 0.218
# - Symptoms Analysis:
#   - Difficulty breathing and cough: While present, these symptoms are less specific to edema without the context of other systemic signs.
#   - Absence of skin or lip color change: Lack of cyanosis could be seen in early stages of edema but is not definitive.
# - Certainty Level: Low
#   - Reasoning: Given that pulmonary edema is typically characterized by acute symptoms like frothy pink sputum and very rapid onset of breathlessness often related to heart failure, the documented symptoms do not strongly suggest edema as the primary diagnosis without further cardiac symptoms or findings.

# Infiltration:
# - Probability: 0.199
# - Symptoms Analysis:
#   - Dry cough and difficulty breathing: These symptoms are common in various respiratory conditions, including infiltration.
#   - No sputum production indicative of infection: Infiltration can be due to various causes, including infections, but clear sputum is not a direct indicator.
#   - Wheezing and localized chest pain: Potential indicators of localized lung issues, including infiltration.
# - Certainty Level: Low
#   - Reasoning: The symptoms presented could suggest lung infiltration, especially when considering the occasional wheezing and localized chest pain. However, given the broad nature of these symptoms and their association with various pulmonary conditions, a low certainty level is most appropriate without further imaging or diagnostics specific to infiltration patterns on chest X-ray or CT.

# *Summary and Recommendations:*
# - *Fibrosis* is the most probable diagnosis given the symptom profile, meriting a *Medium certainty level*. Further diagnostic tests, such as high-resolution CT scans or lung function tests, would be crucial to confirm the presence and extent of fibrotic changes.
# - *Edema* has a *Low certainty level* due to the lack of specific symptoms directly pointing towards pulmonary edema, such as orthopnea or paroxysmal nocturnal dyspnea, that would significantly elevate its probability. Cardiac evaluation may also be necessary due to its relationship with heart conditions.
# - *Infiltration* is assigned a *Low certainty level* since, while some symptoms align, there's insufficient specificity in the symptomatology provided to confidently diagnose without additional evidence from imaging studies.

# This refined analysis is crucial for guiding further diagnostic workups and ensuring accurate diagnosis and management for the patient.'''
        print(raw_json_string)
        raw_json_string = clean_and_format_raw_json(raw_json_string)
        local_pdf_link = generate_pdf(name, age, height, gender, weight, raw_json_string, top_diseases, imagePath)
        
        # Get the URL of the PDF from S3
        pdf_link = get_pdf_link(local_pdf_link)
        
        return jsonify({"pdf_link": pdf_link}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



# Forming the tech-focused crew with some enhanced configurations
crew_1 = Crew(
  agents=[symptom_agent, question_agent],
  tasks=[symptom_task, questions_task],
  process=Process.sequential,  # Optional: Sequential task execution is default
  memory=True,
  cache=True,
  max_rpm=100,
  share_crew=True
)

crew_2 = Crew(
  agents=[analysis_agent],
  tasks=[analysis_task],
  process=Process.sequential,  # Optional: Sequential task execution is default
  memory=True,
  cache=True,
  max_rpm=100,
  share_crew=True
)

def executeCrewTasks(top_diseases, age, gender):
    diseases_dict = {list(disease_dict.keys())[0]: list(disease_dict.values())[0] for disease_dict in top_diseases}

    # Start the task execution process
    result = crew_1.kickoff(inputs={
        'diseases': diseases_dict,  # Send diseases as a dictionary
        'age': age,
        'gender': gender
    })
    return result


def executeCrewTasks2(top_diseases, question_answer):
    # data = request.json
    # top_diseases = data.get("diseases", ["Atelectasis", "Consolidation", "Pneumonia"])
    # age = data.get("age", 45)
    # gender = data.get("gender", "male")
    print(top_diseases, question_answer)
    # Start the task execution process
    diseases_str = ", ".join([f"{list(d.keys())[0]}: {list(d.values())[0]}" for d in top_diseases])

    # Call crew_2.kickoff
    result = crew_2.kickoff(inputs={
        'diseases': diseases_str,
        'question_answers': question_answer
    })


    return result

# Configure upload folder and allowed extensions
# UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure the upload directory exists

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_image():
    # Check for file part in the request
    print(request)
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    age = request.form.get('age')
    gender = request.form.get('gender')

    # If no file is selected
    if file.filename == '':
        return jsonify({"error": "No file selected for uploading"}), 400

    # Validate file type and save if valid
    if file and allowed_file(file.filename):

        # Generate disease probabilities and get questions for top 3 diseases
        probabilities_data = generate_disease_probabilities()
        print(probabilities_data["disease_probabilities"])
        top_diseases = probabilities_data["top_3_diseases"]
        # task_result = executeCrewTasks(top_diseases, age,gender)
        # print(task_result)
        response = {
            "disease_data": probabilities_data,
            # "task_result": task_result  # Add result from execute_tasks
        }
        
        return jsonify(response), 201
    else:
        return jsonify({"error": "File type not allowed"}), 400
    
    

# User login
@app.route("/login", methods=['POST'])
def loginUser():
    data = request.json
    required_fields = ['email', 'password']
    
    for field in required_fields:
        if not data.get(field):
            return jsonify({"msg": f"'{field}' is required"}), 400

    # Find the user by email
    user = users_collection.find_one({'email': data['email']})
    
    if user and bcrypt.checkpw(data['password'].encode('utf-8'), user['password'].encode('utf-8')):
        return jsonify({
            "msg": "Login successful",
            "user": {
                "name": user['name'],
                "email": user['email'],
            }
        }), 200

    return jsonify({"msg": "Invalid email or password"}), 401
    
    
@app.route("/register", methods=['POST'])
def createUser():
    data = request.json
    
    # Check if all required fields are present
    required_fields = ['name', 'email', 'password']
    for field in required_fields:
        if not data.get(field):  # Check if field is missing or empty
            return jsonify({"msg": f"'{field}' is required"}), 400
    
    # Check if the user already exists by email
    if users_collection.find_one({'email': data['email']}):
        return jsonify({"msg": "User already exists"}), 400
    
    # Hash the password
    hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
    
    # Insert new user into the database
    users_collection.insert_one({
        'name': data['name'],
        'email': data['email'],
        'password': hashed_password.decode('utf-8'),
    })
    
    return jsonify({"msg": "User created successfully"}), 201


if __name__ == '__main__':
    app.run(debug=True)
