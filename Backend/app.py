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

app = Flask(__name__)
load_dotenv()
CORS(app)  # Enable CORS for the Flask app
mongo_uri = os.getenv('MONGO_URI')
client = MongoClient(mongo_uri, server_api=ServerApi('1'))
users_collection = client.myapp.users
TEMP_DIR = './temp'
os.makedirs(TEMP_DIR, exist_ok=True)

# Full list of diseases
diseases = [
    "Atelectasis", "Consolidation", "Infiltration", "Pneumothorax", "Edema", "Emphysema",
    "Fibrosis", "Effusion", "Pneumonia", "Pleural_thickening", "Cardiomegaly", "Nodule Mass", "Hernia"
]


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


# Questions associated with each disease
disease_questions = {
    "Atelectasis": [
        "Are you experiencing a sudden onset of difficulty breathing or shortness of breath?",
        "Do you have a cough that produces mucus?",
        "Are you experiencing wheezing without a history of asthma?"
    ],
    "Consolidation": [
        "Have you coughed up blood or blood-stained mucus recently?",
        "Are you experiencing unexplained weight loss or night sweats?",
        "Have you had a fever, and how high has it been?"
    ],
    "Infiltration": [
        "Do you feel a tightness in your chest or discomfort when breathing deeply?",
        "Are you coughing up yellow or green mucus?",
        "Have you noticed any recent fatigue or low energy levels?"
    ],
    "Pneumothorax": [
        "Do you have sudden, sharp chest pain on one side of your chest?",
        "Are you experiencing shortness of breath that worsens with activity?",
        "Have you recently had a chest injury or trauma?"
    ],
    "Edema": [
        "Are you experiencing swelling in your legs, ankles, or feet?",
        "Do you have difficulty breathing when lying down or at night?",
        "Have you noticed sudden weight gain or bloating?"
    ],
    "Emphysema": [
        "Do you have a chronic cough that produces mucus, particularly in the morning?",
        "Are you experiencing a wheezing or whistling sound when breathing?",
        "Have you noticed shortness of breath, especially during physical activities?"
    ],
    "Fibrosis": [
        "Are you experiencing a persistent dry cough?",
        "Do you feel short of breath even when at rest?",
        "Have you noticed fatigue or muscle and joint aches?"
    ],
    "Effusion": [
        "Do you have chest pain that worsens with deep breaths or coughs?",
        "Are you experiencing difficulty breathing while lying down?",
        "Have you had a recent infection or surgery in your chest area?"
    ],
    "Pneumonia": [
        "Do you have a high fever, and if so, how high has it been?",
        "Have you experienced confusion or changes in mental awareness?",
        "Is your cough dry or are you coughing up phlegm? What color is the phlegm?"
    ],
    "Pleural_thickening": [
        "Do you have a persistent dry cough that doesn’t improve?",
        "Are you experiencing any chest pain or discomfort?",
        "Have you had exposure to asbestos or other chemicals in the past?"
    ],
    "Cardiomegaly": [
        "Do you experience swelling in your legs or abdomen?",
        "Are you frequently short of breath, especially during physical activities?",
        "Have you noticed an irregular heartbeat or palpitations?"
    ],
    "Nodule Mass": [
        "Do you have unexplained chest pain or discomfort?",
        "Have you noticed any hoarseness or changes in your voice?",
        "Do you feel short of breath with minimal activity?"
    ],
    "Hernia": [
        "Do you have a bulge or lump in your abdomen or groin area?",
        "Are you experiencing discomfort when bending over or lifting?",
        "Have you noticed pain in your chest after heavy meals?"
    ]
}

MODEL_WEIGHTS_PATH = r'C:\Users\Gaurav\Downloads\multi_disease_model.h5'
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
            formatted_predictions[key] = float(formatted_predictions[key])
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
        # task_result = {
        #     "Effusion": [
        #         "Have you experienced shortness of breath or difficulty breathing, particularly when lying down?",
        #         "Are you experiencing any chest pain, and does it worsen with coughing or taking deep breaths?",
        #         "Do you feel a sense of fullness in your abdomen, or have you noticed swelling in your legs or feet?",
        #         "Have you noticed any decrease in mobility or discomfort in a specific area of your body?",
        #         "Have there been any recent infections or injuries that might have led to fluid accumulation?"
        #     ],
        #     "Edema": [
        #         "Where is the swelling located, and how long have you noticed it?",
        #         "Does the swollen area leave an indentation when pressed and then retains its shape?",
        #         "Is the skin over the swollen area appearing stretched, shiny, or discolored?",
        #         "Have you experienced an increase in abdominal size or problems with mobility?",
        #         "Are there any associated symptoms, such as shortness of breath or weight gain?"
        #     ],
        #     "Hernia": [
        #         "Can you describe the exact location and size of any lump or bulge you have noticed?",
        #         "Does this bulge become more noticeable when you stand, cough, or lift heavy objects?",
        #         "Do you experience pain or discomfort in the bulge area, especially when bending over or lifting?",
        #         "Is the bulge reducible, meaning, can you or your doctor push it back in?",
        #         "Have you had any previous surgeries in the area where the bulge is located?"
        #     ]
        #     }
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


def generate_pdf(raw_json_string):
    return

def get_pdf_link(pdf):
    unique_filename = f"{uuid.uuid4()}"

    try:
        # Upload file to S3
        pdf.seek(0)
        s3.upload_fileobj(pdf, BUCKET_NAME, unique_filename, ExtraArgs={'ContentType': 'application/pdf'})
        
        # Construct the file URL
        file_url = f"https://{BUCKET_NAME}.s3.{s3.meta.region_name}.amazonaws.com/{unique_filename}"
        
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
        # print(top_diseases)
        # print("-------")
        # print(question_answers)
        # Validate inputs
        if not isinstance(top_diseases, list) or not isinstance(question_answers, dict):
            return jsonify({"error": "Invalid input format"}), 400
        print(2)
        # Call the function with provided data
        task_result = executeCrewTasks2(top_diseases, question_answers)
        print(3)
        print(task_result)
        raw_json_string = task_result.raw 

        pdf = generate_pdf(raw_json_string)

        pdf_link = get_pdf_link(pdf)

        return jsonify(pdf_link), 200
        # print("--------")
        # print(type(raw_json_string))
        # print(raw_json_string) # Ensure 'raw' is the correct field



        # # Parse the JSON string into a Python dictionary
        # parsed_data = json.loads(raw_json_string)
        # print("-------")
        # print(parsed_data)
        
        # # Convert to JSON response (if using Flask, for example)
        # return jsonify(parsed_data), 200
        # return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# def generate_disease_probabilities():

#     # Step 1: Randomly select three diseases for higher probabilities
#     selected_indices = np.random.choice(len(diseases), 3, replace=False)
#     selected_probabilities = np.random.uniform(0.2, 0.4, 3)
#     selected_probabilities /= selected_probabilities.sum()  # Normalize to sum to 1 within selected range
#     selected_probabilities *= 0.8  # Scale to make the sum of these three around 0.8

#     # Step 2: Assign these high probabilities to the selected diseases
#     probabilities = np.zeros(len(diseases))
#     for i, idx in enumerate(selected_indices):
#         probabilities[idx] = selected_probabilities[i]

#     # Step 3: Calculate remaining probability for other diseases
#     remaining_prob = 1 - probabilities[selected_indices].sum()
#     remaining_indices = [i for i in range(len(diseases)) if i not in selected_indices]

#     # Step 4: Distribute remaining probability across other diseases with low but non-zero values
#     remaining_probabilities = np.random.uniform(0.01, 0.05, len(remaining_indices))
#     remaining_probabilities /= remaining_probabilities.sum()  # Normalize to sum to 1
#     remaining_probabilities *= remaining_prob  # Scale to the remaining probability

#     # Step 5: Assign these lower probabilities to the remaining diseases
#     for i, idx in enumerate(remaining_indices):
#         probabilities[idx] = remaining_probabilities[i]

#     # Step 6: Trim probabilities to 3 decimal places and create dictionary
#     probabilities = np.round(probabilities, 3)
#     disease_probabilities = dict(zip(diseases, probabilities))

    
#     # Get the top 3 diseases with the highest probabilities
#     top_3_diseases = sorted(disease_probabilities, key=disease_probabilities.get, reverse=True)[:3]
    
#     # Prepare questions for the top 3 diseases if available in the questions dictionary
#     questions = {disease: disease_questions.get(disease, ["No specific questions available"]) for disease in top_3_diseases}
    
#     return {
#         "disease_probabilities" : disease_probabilities,
#         "top_3_diseases" : top_3_diseases,
#         "questions" : questions
#     }

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
