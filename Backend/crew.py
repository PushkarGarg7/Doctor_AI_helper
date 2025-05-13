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
