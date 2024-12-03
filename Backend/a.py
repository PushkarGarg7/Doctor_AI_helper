import json
from flask import jsonify

# Original data
raw_data = {
    "Edema": [
    "Have you noticed any recent swelling in your legs, arms, or other parts of your body?",
    "Does the swollen area remain indented after pressing it for a few seconds?",
    "Is there any stretched, shiny, or discolored skin near the swollen areas?",
    "Have you experienced any increase in abdominal size or bloating?",
    "Are there periods when the swelling decreases, and if so, when does this typically occur?"
  ],
  "Infiltration": [
    "Have you been experiencing any breathlessness or difficulty breathing?",
    "Do you notice any pain, swelling, or discoloration in specific areas of your body?",
    "Have you had any recent episodes of coughing, and if so, can you describe the nature (dry, with phlegm) of the cough?",
    "Are there any environmental factors that worsen your breathlessness or pain?",
    "Have you experienced any unexplained weight loss or fever recently?"
  ],
  "Nodule Mass": [
    "Have you noticed any lumps or masses on your body, particularly in the neck, or elsewhere?",
    "Are the noticed lumps causing any pain or discomfort?",
    "Have you experienced any changes in voice or difficulty swallowing if the mass is near your throat?",
    "If the nodule mass is external, has there been any change in the size or appearance of the mass?",
    "Have you had any recent imaging tests (like X-rays or CT scans) that have shown unknown masses?"
  ]
}

# Output cleaned and formatted data
print(jsonify(raw_data))
