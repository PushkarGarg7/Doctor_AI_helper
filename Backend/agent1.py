from crewai import Agent
from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_MODEL_NAME"] = "gpt-4-0125-preview"

def get_cbc_analysis_agent(pdf_tool, csv_tool):
    return Agent(
        role="CBC Report Analyzer",
        goal=(
            "Extract and analyze blood parameters from the CBC report provided as a PDF. "
            "Compare the extracted values against predefined thresholds and conditions "
            "from the reference CSV file. Infer potential medical conditions based on "
            "correlations found in the data."
        ),
        backstory=(
            "This agent is an expert in hematology and blood analysis. It specializes in "
            "identifying abnormalities in blood test results and correlating them with "
            "known medical conditions. With a deep understanding of diagnostic criteria, "
            "it provides precise inferences to assist healthcare professionals."
        ),
        tools=[pdf_tool, csv_tool],
        verbose=True,
        allow_delegation=False,
        max_iter=10,
        allow_code_execution=False,
    )
