from crewai import Crew,Process
from agents import symptom_agent, question_agent
from tasks import symptom_task, questions_task


# Forming the tech-focused crew with some enhanced configurations
crew = Crew(
  agents=[symptom_agent, question_agent],
  tasks=[symptom_task, questions_task],
  process=Process.sequential,  # Optional: Sequential task execution is default
  memory=True,
  cache=True,
  max_rpm=100,
  share_crew=True
)

# Define the top 3 diseases, and add age and gender
top_diseases = [
    "Atelectasis",
    "Consolidation",
    "Pneumonia"
]
age = 45  # Example age
gender = "male"  # Example gender

# Start the task execution process with the defined top 3 diseases, age, and gender
result = crew.kickoff(inputs={
    'diseases': ", ".join(top_diseases),  # Join the top diseases into a single string
    'age': age,
    'gender': gender
})

print(result)
