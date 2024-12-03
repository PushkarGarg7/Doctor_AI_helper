import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from keras.applications.mobilenet import MobileNet
from keras.layers import GlobalAveragePooling2D, Dense, Dropout
from keras.models import Sequential

# Define labels
all_labels = ['Atelectasis', 'Cardiomegaly', 'Consolidation', 'Edema', 'Effusion',
              'Emphysema', 'Fibrosis', 'Hernia', 'Infiltration', 'Mass', 
              'Nodule', 'Pleural_Thickening', 'Pneumonia', 'Pneumothorax']

# Function to create the model
def make_model():
    base_mobilenet_model = MobileNet(input_shape=(512, 512, 1), include_top=False, weights=None)
    model = Sequential([
        base_mobilenet_model,
        GlobalAveragePooling2D(),
        Dropout(0.5),
        Dense(512),
        Dropout(0.5),
        Dense(len(all_labels), activation='sigmoid')
    ])
    return model

# Function to load model with weights
def load_model(weights_path):
    model = make_model()
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.001), 
                  loss='binary_crossentropy', 
                  metrics=[tf.keras.metrics.AUC(multi_label=True)])
    model.load_weights(weights_path)
    return model

# Function to preprocess the image
def preprocess_image(image_path):
    IMG_SIZE = (512, 512)
    img = load_img(image_path, target_size=IMG_SIZE, color_mode='grayscale')
    img_array = img_to_array(img)
    img_array = (img_array - np.mean(img_array)) / (np.std(img_array) + 1e-7)
    img_array = np.expand_dims(img_array, axis=0)
    return img_array

# Function to predict probabilities
def predict(model, image_path):
    img_array = preprocess_image(image_path)
    predicted_probs = model.predict(img_array)
    # print(predicted_probs)
    return predicted_probs
