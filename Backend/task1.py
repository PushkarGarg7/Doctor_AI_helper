from crewai import Task
from tool1 import csv_tool, pdf_tool
from agent1 import cbc_analysis_agent

from crewai import Task

cbc_analysis_task = Task(
    description=(
        "Extract blood parameters from the provided CBC report (PDF) and analyze them "
        "against predefined medical reference values from the CSV dataset. "
        "Identify abnormalities in blood test results and infer potential conditions."
    ),
    expected_output=(
        "A structured JSON object containing the extracted CBC parameters, "
        "highlighted abnormalities, and a list of potential medical conditions inferred "
        "from the reference dataset."
    ),
    tools=[pdf_tool, csv_tool],  # Replace with actual tool instances
    agent=cbc_analysis_agent,
    human_input=False,  # Fully automated analysis without human intervention
    async_execution=False  # Execute synchronously for real-time inference
)
