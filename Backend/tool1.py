from crewai_tools import FileReadTool, PDFSearchTool

def get_tools(csv_path, pdf_path):
    csv_tool = FileReadTool(file_path=csv_path)
    pdf_tool = PDFSearchTool(pdf=pdf_path)
    return csv_tool, pdf_tool 