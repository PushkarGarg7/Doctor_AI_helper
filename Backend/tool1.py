from crewai_tools import CSVSearchTool, PDFSearchTool

def get_tools(csv_path, pdf_path):
    csv_tool = CSVSearchTool(csv=csv_path)
    pdf_tool = PDFSearchTool(pdf=pdf_path)
    return csv_tool, pdf_tool
