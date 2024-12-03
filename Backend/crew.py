from crewai import Crew,Process
from agents import symptom_agent, question_agent, analysis_agent
from tasks import symptom_task, questions_task, analysis_task


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

if __name__ == "__main__":

  # Define the top 3 diseases, and add age and gender
  top_diseases = [
      "Atelectasis: 40%/100%",
      "Consolidation: 30%/100%",
      "Pneumonia: 70%/100%"
  ]
  age = 45  # Example age
  gender = "male"  # Example gender
  question_answers = {
  "Atelectasis": [
    {
      "question": "Have you experienced sudden episodes of shortness of breath without engaging in physical activity?",
      "answer": "Yes, occasionally during rest."
    },
    {
      "question": "Do you notice an increase in difficulty breathing when lying down or during physical exertion?",
      "answer": "Yes, especially when lying flat."
    },
    {
      "question": "Have you been coughing more frequently, and if so, is it a dry cough or accompanied by mucus?",
      "answer": "Yes, it’s a dry cough."
    },
    {
      "question": "Are you experiencing chest pain or discomfort that worsens with coughing or deep breathing?",
      "answer": "Yes, there is discomfort with deep breathing."
    },
    {
      "question": "Have you noticed any changes in your skin or lip color, such as them turning bluish, indicating possible oxygen deprivation?",
      "answer": "No, I haven’t noticed any such changes."
    }
  ],
  "Consolidation (Lung)": [
    {
      "question": "When coughing, do you expel thick green or bloody sputum?",
      "answer": "No, the sputum is clear."
    },
    {
      "question": "Have you noticed any changes in the sound of your breathing, such as it becoming noisier or more unusual than before?",
      "answer": "Yes, there is occasional wheezing."
    },
    {
      "question": "Are you experiencing flu-like symptoms, including fever and a general feeling of malaise, especially in the initial stages?",
      "answer": "Yes, I had mild fever and fatigue initially."
    },
    {
      "question": "Does your chest pain intensify with deep breaths or coughing, and is it localized to a particular area?",
      "answer": "Yes, the pain is localized to the right side."
    },
    {
      "question": "Have you recently experienced a dry cough that has progressively worsened, independent of a common cold or allergies?",
      "answer": "Yes, it’s been persistent for two weeks."
    }
  ],
  "Pneumonia": [
    {
      "question": "Have you been experiencing a persistent cough that produces phlegm or mucus? If yes, what color is the phlegm?",
      "answer": "Yes, the phlegm is yellowish."
    },
    {
      "question": "Do you have a fever accompanied by chills, making you feel excessively cold then overheated?",
      "answer": "Yes, the chills are frequent, especially at night."
    },
    {
      "question": "Are you experiencing sharp or stabbing chest pain that increases with breathing or coughing?",
      "answer": "Yes, it feels sharp and worsens with coughing."
    },
    {
      "question": "Have you felt a marked decrease in your appetite or experienced unintentional weight loss recently?",
      "answer": "Yes, my appetite has decreased significantly."
    },
    {
      "question": "Have you noticed a significant increase in your fatigue levels, making daily activities more challenging?",
      "answer": "Yes, I feel exhausted even after light activity."
    }
  ]
}


  # Start the task execution process with the defined top 3 diseases, age, and gender
  result = crew_1.kickoff(inputs={
      'diseases': ", ".join(top_diseases),  # Join the top diseases into a single string
      'age': age,
      'gender': gender
  })
  result = crew_2.kickoff(inputs={
      'diseases': ", ".join(top_diseases),  # Join the top diseases into a single string
      'question_answers': question_answers
  })

  print(result)
