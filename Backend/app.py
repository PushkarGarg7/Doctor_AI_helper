from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import numpy as np
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for the Flask app

@app.route('/')
def home():
    return "Hello, Flask!"

# Full list of diseases
diseases = [
    "Atelectasis", "Consolidation", "Infiltration", "Pneumothorax", "Edema", "Emphysema",
    "Fibrosis", "Effusion", "Pneumonia", "Pleural_thickening", "Cardiomegaly", "Nodule Mass", "Hernia"
]

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
    "Pneumonia": [
        "Do you have a high fever, and if so, how high has it been?",
        "Have you experienced confusion or changes in mental awareness?",
        "Is your cough dry or are you coughing up phlegm? What color is the phlegm?"
    ],
    # Add similar question lists for other diseases if needed
}

def generate_disease_probabilities():
    # Generate random probabilities for all 13 diseases and normalize to sum to 1
    probabilities = np.random.rand(len(diseases))
    probabilities /= probabilities.sum()
    
    # Create a dictionary of diseases and their probabilities
    disease_probabilities = dict(zip(diseases, probabilities))
    
    # Get the top 3 diseases with the highest probabilities
    top_3_diseases = sorted(disease_probabilities, key=disease_probabilities.get, reverse=True)[:3]
    
    # Prepare questions for the top 3 diseases if available in the questions dictionary
    questions = {disease: disease_questions.get(disease, ["No specific questions available"]) for disease in top_3_diseases}
    
    return {
        "disease_probabilities": disease_probabilities,
        "top_3_diseases": top_3_diseases,
        "questions": questions
    }

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
        # filename = secure_filename(file.filename)
        # file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        # file.save(file_path)

        # Generate disease probabilities and get questions for top 3 diseases
        probabilities_data = generate_disease_probabilities()
        # print(probabilities_data)
        response = {
            "disease_data": probabilities_data,
        }
        
        return jsonify(response), 201
    else:
        return jsonify({"error": "File type not allowed"}), 400

if __name__ == '__main__':
    app.run(debug=True)
