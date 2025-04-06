from crewai import Task

def get_cbc_analysis_task(agent, pdf_tool, csv_tool):
    return Task(
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
        tools=[pdf_tool, csv_tool],
        agent=agent,
        human_input=False,
        async_execution=False
    )
