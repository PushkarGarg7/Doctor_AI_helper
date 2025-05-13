from crewai import Task
from tools import serper_tool
from agents import symptom_agent, question_agent, analysis_agent

symptom_task = Task(
    expected_output="A list of age- and gender-specific symptoms for the likely diseases: {diseases}.",
    description="Find symptoms for the likely diseases: {diseases}, considering age {age} and gender {gender}.",
    tools=[serper_tool],
    agent=symptom_agent,
)

questions_task = Task(
    description="List questions for a doctor to ask the patient based on age- and gender-specific symptoms of the likely diseases: {diseases}.",
    expected_output=(
        "A JSON object where the keys are disease names from {diseases}, "
        "and the values are lists of 5 diagnostic questions for each disease. No additional data."
    ),
    agent=question_agent,
    context=[symptom_task],
)

analysis_task = Task(
    description=(
        "Analyze doctor-patient question-answer pairs: {question_answers}, and provide probabilities for each of the likely diseases: {diseases}. "
        "Determine the certainty level (High, Medium, Low) for each disease based on the provided answers."
    ),
    expected_output=(
        "For each disease in {diseases}, based on the provided question-answer pairs: {question_answers}, "
        "provide probabilities and categorize them as High, Medium, or Low certainty levels."
    ),
    agent=analysis_agent,
    context=[symptom_task, questions_task],
)
