from crewai import Task
    
# def get_cbc_analysis_task2(agent, pdf_tool, csv_tool, top_diseases):
#     return Task(
#         description=(
#             "Extract blood parameters from the provided CBC report (PDF) and analyze them "
#             "against predefined medical reference values and disease-specific inference rules from the CSV dataset. "
#             "Identify abnormalities in blood test results and infer potential conditions. "
#             f"Based on the inference rules in the CSV, provide explanations for the likelihood of the following diseases: "
#             f"{', '.join([f'{disease} with probablity ({prob:.3f})' for disease, prob in top_diseases.items()])}. If no rule is available in the CSV for a disease, explicitly mention "
#             # "'No inference by CBC for this disease.'"
#             "If no exact rule is found that links a disease to the identified conditions, still generate a plausible explanation "
#             "based on similar rules, overlapping symptoms, or general CBC interpretation heuristics."
#         ),
#         expected_output=(
#             "A structured JSON object with the following keys:\n\n"
#             "1. extracted_CBC_parameters - Extracted CBC values from the PDF.\n"
#             "2. highlighted_abnormalities - Parameters that fall outside the normal range.\n"
#             "3. potential_medical_conditions - General conditions inferred from abnormal values.\n"
#             "4. top_disease_likelihoods - A dictionary with each of the top 3 diseases and a text-based explanation of their likelihood, "
#             "based on how the inferred potential_medical_conditions match with the inference rules from the CSV. "
#             # "If no rule is found that links a disease to the identified conditions, the value should be "
#             # "'No inference by CBC for this disease.'"
#             "If no exact rule is found that links a disease to the identified conditions, still generate a plausible explanation "
#             "based on similar rules, overlapping symptoms, or general CBC interpretation heuristics."
#         ),
#         tools=[pdf_tool, csv_tool],
#         agent=agent,
#         human_input=False,
#         async_execution=False
#     )


def get_cbc_analysis_task(agent, pdf_tool, csv_tool, top_diseases):
    return Task(
        description=(
            "Extract blood parameters from the provided CBC report (PDF) and analyze them "
            "against predefined medical reference values and disease-specific inference rules from the CSV dataset. "
            "Identify abnormalities in blood test results and infer potential conditions. "
            f"Based on the inference rules in the CSV, provide explanations for the likelihood of the following diseases: "
            f"{', '.join([f'{disease} with probability ({prob:.3f})' for disease, prob in top_diseases.items()])}. "
            "If no rule is available in the CSV for a disease, explicitly mention "
            "'No inference by CBC for this disease.' "
            # "If no exact rule is found that links a disease to the identified conditions, still generate a plausible explanation "
            # "based on similar rules, overlapping symptoms, or general CBC interpretation heuristics."
        ),
        expected_output=(
            "A structured JSON object with the following keys:\n\n"
            "1. extracted_CBC_parameters - Extracted CBC values from the PDF.\n"
            "2. highlighted_abnormalities - Parameters that fall outside the normal range.\n"
            "3. potential_medical_conditions - General conditions inferred from abnormal values.\n"
            "4. top_disease_likelihoods - A dictionary with each of the likely diseases and a text-based explanation of their likelihood, "
            "based on how the inferred potential_medical_conditions match with the inference rules from the CSV. "
            "If no rule is found that links a disease to the identified conditions, the value should be "
            "'No inference by CBC for this disease.'"
            "Output must be a valid JSON object only. Do not include any explanatory text, headers, or formatting outside the JSON."
        ),
        tools=[pdf_tool, csv_tool],
        agent=agent,
        human_input=False,
        async_execution=False
    )