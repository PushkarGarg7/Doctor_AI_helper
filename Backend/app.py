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



def generate_pdf(name, height, gender, weight, raw_json_string):
    # Convert the raw_json_string into a list of points (this depends on the structure of raw_json_string)
    points = []
    try:
        points = [f"{key}: {value}" for key, value in raw_json_string.items()]
    except AttributeError:
        points = [str(raw_json_string)]
    
    # Create an in-memory PDF buffer
    pdf = SimpleDocTemplate("outputwdef.pdf", pagesize=letter)

    # Set styles
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    normal_style = styles['Normal']
    heading_style = styles['Heading2']

    # Header with name, height, weight, and gender
    title = Paragraph(f"Patient Information: {name}", title_style)
    user_info_text = Paragraph(
        f"<b>Name:</b> {name} &nbsp;&nbsp;&nbsp; <b>Height:</b> {height} cm &nbsp;&nbsp;&nbsp; <b>Weight:</b> {weight} kg &nbsp;&nbsp;&nbsp; <b>Gender:</b> {gender}",
        normal_style
    )

    # Create a table for the user details
    info_data = [["Name:", name], ["Height:", f"{height} cm"], ["Weight:", f"{weight} kg"], ["Gender:", gender]]
    info_table = Table(info_data, colWidths=[70, 200])
    info_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                                   ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                   ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                   ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                   ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                   ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                                   ('GRID', (0, 0), (-1, -1), 1, colors.black)]))

    # Create a section for the raw_json_string data points
    points_heading = Paragraph("Key Points from Analysis", heading_style)
    points_paragraph = Paragraph("<br />".join(points), normal_style)

    # Add all elements to the PDF
    elements = [
        title,
        Spacer(1, 10),
        user_info_text,
        Spacer(1, 20),
        info_table,
        Spacer(1, 20),
        points_heading,
        Spacer(1, 10),
        points_paragraph
    ]

    # Build the PDF in memory
    pdf.build(elements)
    print("pdf generated successfully!")
    base_path = os.path.dirname(__file__)  # This gives the current directory of the script
    file_path = os.path.join(base_path, "outputwdef.pdf")
    print(file_path)
    return file_path



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



@app.route('/rag2', methods=['POST'])
def rag2():
    try:
        # Parse input JSON
        
        data = request.json
        top_diseases = data.get('top_diseases')
        question_answers = data.get('question_answers')
        name = data.get("name")
        age = data.get("age")
        height = data.get("height")
        weight = data.get("weight")
        gender = data.get("gender")
        
        # Validate inputs
        if not isinstance(top_diseases, list) or not isinstance(question_answers, dict):
            return jsonify({"error": "Invalid input format"}), 400

        # Call the function with provided data
        task_result = executeCrewTasks2(top_diseases, question_answers)
        
        # Extract raw_json_string from task_result
        raw_json_string = task_result.raw 

        # Generate PDF with all required data
        local_pdf_link = generate_pdf(name, height, gender, weight, raw_json_string)
        
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
