from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import numpy as np
from flask_cors import CORS
from dotenv import load_dotenv
from pymongo.server_api import ServerApi
from pymongo import MongoClient
from crew import Crew, Process, symptom_agent, question_agent, symptom_task, questions_task
import bcrypt

app = Flask(__name__)
load_dotenv()
CORS(app)  # Enable CORS for the Flask app
mongo_uri = os.getenv('MONGO_URI')
client = MongoClient(mongo_uri, server_api=ServerApi('1'))

@app.route('/')
def home():
    return "Hello, Flask!"

# Full list of diseases
diseases = [
    "Atelectasis", "Consolidation", "Infiltration", "Pneumothorax", "Edema", "Emphysema",
    "Fibrosis", "Effusion", "Pneumonia", "Pleural_thickening", "Cardiomegaly", "Nodule Mass", "Hernia"
]

users_collection = client.myapp.users


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

def generate_disease_probabilities():

    # Step 1: Randomly select three diseases for higher probabilities
    selected_indices = np.random.choice(len(diseases), 3, replace=False)
    selected_probabilities = np.random.uniform(0.2, 0.4, 3)
    selected_probabilities /= selected_probabilities.sum()  # Normalize to sum to 1 within selected range
    selected_probabilities *= 0.8  # Scale to make the sum of these three around 0.8

    # Step 2: Assign these high probabilities to the selected diseases
    probabilities = np.zeros(len(diseases))
    for i, idx in enumerate(selected_indices):
        probabilities[idx] = selected_probabilities[i]

    # Step 3: Calculate remaining probability for other diseases
    remaining_prob = 1 - probabilities[selected_indices].sum()
    remaining_indices = [i for i in range(len(diseases)) if i not in selected_indices]

    # Step 4: Distribute remaining probability across other diseases with low but non-zero values
    remaining_probabilities = np.random.uniform(0.01, 0.05, len(remaining_indices))
    remaining_probabilities /= remaining_probabilities.sum()  # Normalize to sum to 1
    remaining_probabilities *= remaining_prob  # Scale to the remaining probability

    # Step 5: Assign these lower probabilities to the remaining diseases
    for i, idx in enumerate(remaining_indices):
        probabilities[idx] = remaining_probabilities[i]

    # Step 6: Trim probabilities to 3 decimal places and create dictionary
    probabilities = np.round(probabilities, 3)
    disease_probabilities = dict(zip(diseases, probabilities))

    
    # Get the top 3 diseases with the highest probabilities
    top_3_diseases = sorted(disease_probabilities, key=disease_probabilities.get, reverse=True)[:3]
    
    # Prepare questions for the top 3 diseases if available in the questions dictionary
    questions = {disease: disease_questions.get(disease, ["No specific questions available"]) for disease in top_3_diseases}
    
    return {
        "disease_probabilities" : disease_probabilities,
        "top_3_diseases" : top_3_diseases,
        "questions" : questions
    }

crew = Crew(
    agents=[symptom_agent, question_agent],
    tasks=[symptom_task, questions_task],
    process=Process.sequential,
    memory=True,
    cache=True,
    max_rpm=100,
    share_crew=True
)

def executeCrewTasks(top_diseases, age, gender):
    # data = request.json
    # top_diseases = data.get("diseases", ["Atelectasis", "Consolidation", "Pneumonia"])
    # age = data.get("age", 45)
    # gender = data.get("gender", "male")

    # Start the task execution process
    result = crew.kickoff(inputs={
        'diseases': ", ".join(top_diseases),
        'age': age,
        'gender': gender
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

        top_diseases = probabilities_data["disease_probabilities"]
        # task_result = executeCrewTasks(top_diseases, age,gender)
        
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
