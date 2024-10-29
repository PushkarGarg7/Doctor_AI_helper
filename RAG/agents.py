from crewai import Agent
from tools import serper_tool

from dotenv import load_dotenv

load_dotenv()

import os
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_MODEL_NAME"]="gpt-4-0125-preview"

symptom_agent = Agent(
    role="symptom finder",
    goal="find symptoms for the top 3 diseases: {diseases}",
    backstory="This agent specializes in extracting symptoms from official medical sources.",
    verbose=True,
    tools=[serper_tool],
    allow_delegation=True
)

question_agent = Agent(
    role="question generator",
    goal="generate questions for a doctor based on symptoms of {diseases}",
    backstory="This agent generates diagnostic questions to help doctors confirm diseases.",
    verbose=True,
)