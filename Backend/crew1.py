from crewai import Crew,Process
from agent1 import cbc_analysis_agent
from task1 import cbc_analysis_task

cbc_analysis_crew = Crew(
    agents=[cbc_analysis_agent],  # List of agents
    tasks=[cbc_analysis_task],  # List of tasks
    process=Process.sequential,  # Tasks are executed in a defined order
    verbose=True,  # Enable detailed execution logs
    memory=True,  # Maintain context for multi-step analysis
    cache=True,  # Cache tool execution results for efficiency
    full_output=True,  # Return the full output, including all task results
    output_log_file="cbc_analysis_logs.json"  # Save logs in JSON format
)

if __name__ == "__main__":
  result = cbc_analysis_crew.kickoff()
  print(result)

