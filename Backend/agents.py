from crewai import Agent
from tools import serper_tool

from dotenv import load_dotenv

load_dotenv()

import os
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_MODEL_NAME"] = "gpt-4-0125-preview"

symptom_agent = Agent(
    role="symptom finder",
    goal="Find symptoms for the likely diseases: {diseases} based on age {age} and gender {gender}.",
    backstory="This agent specializes in extracting age- and gender-specific symptoms from official medical sources.",
    verbose=True,
    tools=[serper_tool],
    allow_delegation=True
)

question_agent = Agent(
    role="question generator",
    goal="Generate questions for a doctor based on symptoms of the likely diseases: {diseases}, considering age {age} and gender {gender}.",
    backstory="This agent generates diagnostic questions tailored to age and gender, to help doctors confirm diseases.",
    verbose=True,
)

analysis_agent = Agent(
    role="disease analyzer",
    goal="Analyze question-answer pairs to determine probabilities and certainty levels for the likely diseases: {diseases}.",
    backstory=(
        "This agent specializes in processing doctor-patient interactions. "
        "It evaluates the provided question-answer pairs to assign probabilities for each disease and categorize certainty levels as High, Medium, or Low."
    ),
    verbose=True,
    allow_delegation=False,
)