from crewai import Task
from tools import serper_tool
from agents import symptom_agent, question_agent

symptom_task = Task(
    expected_output="a list of age- and gender-specific symptoms for {diseases}",
    description="Find symptoms for the top 3 diseases provided, considering age {age} and gender {gender}.",
    tools=[serper_tool],
    agent=symptom_agent,
)

questions_task = Task(
    description="List questions for a doctor to ask the patient based on age- and gender-specific symptoms of {diseases}.",
    expected_output="A list of diagnostic questions to confirm which disease the patient might have, based on age and gender.",
    agent=question_agent,
    context=[symptom_task],
)


