from crewai import Task
from tools import serper_tool
from agents import symptom_agent, question_agent

symptom_task = Task(
    expected_output="a list of symptoms for {diseases}",
    description="Find symptoms for the top 3 diseases provided.",
    tools=[serper_tool],
    agent=symptom_agent,
)

questions_task = Task(
    description="List questions for a doctor to ask the patient based on the symptoms of {diseases}.",
    expected_output="A list of diagnostic questions to confirm which disease the patient might have, based on the symptoms.",
    agent=question_agent,
    context=[symptom_task],
)

