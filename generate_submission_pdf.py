from fpdf import FPDF
import os

class PDF(FPDF):
    def header(self):
        # Logo
        # self.image('assets/logo.png', 10, 8, 33) 
        self.set_font('Arial', 'B', 15)
        self.cell(80)
        self.cell(30, 10, 'Aadhaar Satark - Final Report', 0, 0, 'C')
        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, 'Page ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')

def create_pdf():
    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font('Arial', '', 12)

    # Title
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Project Submission: Aadhaar Satark', 0, 1)
    pdf.ln(5)

    # Content
    pdf.set_font('Arial', '', 12)
    intro_text = (
        "Team: HackElite_Coders\n"
        "Date: 20-Jan-2026\n\n"
        "1. Problem Statement:\n"
        "District officers lack real-time, actionable intelligence to close enrolment gaps.\n\n"
        "2. Our Solution:\n"
        "We unified Geospatial Analytics with Generative AI to create a Command Center."
    )
    pdf.multi_cell(0, 10, intro_text)
    pdf.ln(5)

    # Dashboard Image
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, '3. Dashboard Visualization', 0, 1)
    
    if os.path.exists('assets/screenshots/dashboard.png'):
        pdf.image('assets/screenshots/dashboard.png', x=10, w=190)
    else:
        pdf.cell(0, 10, '[Dashboard Image Missing]', 0, 1)

    pdf.add_page()
    
    # AI Chat Image
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, '4. AI Agent Interface', 0, 1)

    if os.path.exists('assets/screenshots/chat.png'):
        pdf.image('assets/screenshots/chat.png', x=10, w=190)
    else:
        pdf.cell(0, 10, '[Chat Image Missing]', 0, 1)
        
    pdf.ln(10)
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 10, "The AI Agent (shown above) allows natural language queries on the dataset.")

    pdf.output("Aadhaar_Satark_Submission.pdf", 'F')
    print("PDF Generated Successfully: Aadhaar_Satark_Submission.pdf")

if __name__ == '__main__':
    create_pdf()
