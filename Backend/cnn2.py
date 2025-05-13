import numpy as np
import pandas as pd
import tensorflow as tf
from keras.applications.densenet import DenseNet121
from keras.layers import Dense, GlobalAveragePooling2D
from keras.models import Model
from tensorflow.keras.utils import load_img, img_to_array

# ------------------------
# CONSTANTS
# ------------------------
IMAGE_SIZE = (320, 320)

LABELS = [
    'Cardiomegaly', 'Emphysema', 'Effusion', 'Hernia', 'Infiltration', 
    'Mass', 'Nodule', 'Atelectasis', 'Pneumothorax', 'Pleural_Thickening', 
    'Pneumonia', 'Fibrosis', 'Edema', 'Consolidation'
]

THRESHOLDS = np.array([
    0.519135, 0.540763, 0.478758, 0.465557, 0.529498,
    0.474119, 0.481894, 0.509495, 0.480846, 0.45797,
    0.61158, 0.420276, 0.496351, 0.560865
])

DENSENET_PATH = "C:\\Abhinav\\Abhinav\\PEC\\Major Project\\Project\\densenet.hdf5"
WEIGHTS_PATH = "C:\\Abhinav\\Abhinav\\PEC\\Major Project\\Project\\pretrained_model.h5"

# ------------------------
# MODEL LOADING
# ------------------------

def load_densenet_model():
    base_model = DenseNet121(weights=DENSENET_PATH, include_top=False)
    x = GlobalAveragePooling2D()(base_model.output)
    predictions = Dense(len(LABELS), activation="sigmoid")(x)
    model = Model(inputs=base_model.input, outputs=predictions)
    model.load_weights(WEIGHTS_PATH)
    return model

# Load model once
model = load_densenet_model()

# ------------------------
# IMAGE PREDICTION
# ------------------------

def predict_disease_probabilities(img_path):
    """
    Loads an image and returns predicted probabilities from the model.
    
    Args:
        img_path (str): path to the image file
        
    Returns:
        np.ndarray: shape (1, 14) probability scores for each label
    """
    img = load_img(img_path, target_size=IMAGE_SIZE)
    img_array = img_to_array(img) / 255.0  # normalize
    img_array = np.expand_dims(img_array, axis=0)
    
    predicted_vals = model.predict(img_array)
    prob_array = np.array(predicted_vals).flatten()
    arr = prob_array.tolist()
    return arr

# ------------------------
# DISEASE FILTERING
# ------------------------

def get_diseases_above_threshold(prob_array):
    """
    Returns list of diseases with predicted prob > threshold
    
    Args:
        prob_array (np.ndarray): shape (1, 14)
    
    Returns:
        List[str]: disease names with prob > threshold
    """
    prob_array = np.array(prob_array).flatten()
    assert prob_array.shape[0] == len(THRESHOLDS), "Prediction size mismatch"
    
    return [LABELS[i] for i in range(len(LABELS)) if prob_array[i] > THRESHOLDS[i]]


if __name__ == "__main__":
    img_path = "C:\\Abhinav\\Abhinav\\PEC\\Major Project\\Project\\img5.png"
    
    probs = predict_disease_probabilities(img_path)
    print("Predicted Probabilities:\n", probs)
    
    positive_diseases = get_diseases_above_threshold(probs)
    print("Diseases above threshold:\n", positive_diseases)
