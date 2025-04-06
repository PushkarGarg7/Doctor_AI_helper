from crewai_tools import CSVSearchTool, PDFSearchTool

csv_tool = CSVSearchTool(csv='C:\PythonPersonal\MajorProject\Doctor_AI_helper\Backend\CBC_All_Conditions_Filtered.csv')
pdf_tool = PDFSearchTool(pdf='C:\PythonPersonal\MajorProject\Doctor_AI_helper\Backend\SampleCBC.pdf')
