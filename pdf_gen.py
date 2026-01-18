from fpdf import FPDF
import datetime
import os

# Helper to remove characters that crash the PDF generator
def clean_text(text):
    if isinstance(text, str):
        return text.encode('latin-1', 'ignore').decode('latin-1')
    return str(text)

class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'Battery Health AI Diagnostics', 0, 1, 'C')
        self.ln(5)
        self.set_draw_color(0, 80, 180) # Blue line
        self.line(10, 25, 200, 25)
        self.ln(10)

def create_pdf(inputs, results):
    pdf = PDFReport()
    pdf.add_page()
    
    # 1. Timestamp
    pdf.set_font("Arial", "I", 10)
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    pdf.cell(0, 10, f"Generated: {now}", 0, 1, 'R')
    
    # 2. Input Section
    pdf.set_font("Arial", "B", 12)
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(0, 10, "  Input Parameters", 0, 1, 'L', fill=True)
    pdf.ln(2)
    
    pdf.set_font("Arial", "", 12)
    # Use clean_text to prevent crashes
    pdf.cell(50, 10, clean_text(f"Voltage: {inputs['voltage']} V"))
    pdf.cell(50, 10, clean_text(f"Current: {inputs['current']} A"))
    pdf.ln(8)
    pdf.cell(50, 10, clean_text(f"Temp: {inputs['temperature']} C"))
    pdf.cell(50, 10, clean_text(f"Cycles: {inputs['cycle']}"))
    pdf.ln(15)
    
    # 3. Results Section
    pdf.set_font("Arial", "B", 12)
    pdf.set_fill_color(200, 240, 255) # Light blue
    pdf.cell(0, 10, "  AI Analysis Results", 0, 1, 'L', fill=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, clean_text(f"Health Condition: {results['condition']}"), 0, 1)
    
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, clean_text(f"Health Score: {results['health_score']}%"), 0, 1)
    pdf.cell(0, 10, clean_text(f"Remaining Useful Life (RUL): {results['rul']} cycles"), 0, 1)
    pdf.cell(0, 10, clean_text(f"Estimated Repair Cost: ${results['cost']}"), 0, 1)
    pdf.ln(5)
    
    pdf.set_text_color(100, 100, 100)
    # Multi_cell handles long text wrapping
    pdf.multi_cell(0, 8, clean_text(f"Recommendation: {results['recommendation']}"))
    
    # SAVE using absolute path to avoid "File Not Found" errors
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "report.pdf")
    pdf.output(file_path)
    return file_path