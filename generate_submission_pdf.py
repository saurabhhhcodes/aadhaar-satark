from fpdf import FPDF
import os

# Define Project Info
PROJECT_ID = "UIDAI_11479"
TEAM_NAME = "HackElite_Coders"
PROJECT_TITLE = "Aadhaar Satark: Integrated Command & Control Center"
REPO_URL = "https://github.com/saurabhhhcodes/aadhaar-satark"
DEPLOY_URL = "https://aadhaar-satark.onrender.com"

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 10)
        self.cell(0, 10, f'{TEAM_NAME} | ID: {PROJECT_ID}', 0, 0, 'R')
        self.ln(15)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', 0, 0, 'C')

    def chapter_title(self, label):
        self.set_font('Arial', 'B', 14)
        self.set_fill_color(240, 240, 240)
        self.cell(0, 10, label, 0, 1, 'L', 1)
        self.ln(4)

    def chapter_body(self, body):
        self.set_font('Arial', '', 11)
        self.multi_cell(0, 7, body)
        self.ln()

    def add_image_if_exists(self, path, w=170):
        if os.path.exists(path):
            self.image(path, x=10, w=w)
            self.ln(5)
        else:
            self.set_font('Arial', 'I', 10)
            self.cell(0, 10, f'[Image not found: {path}]', 0, 1)

def create_final_pdf():
    pdf = PDF()
    pdf.alias_nb_pages()
    
    # --- PAGE 1: TITLE & LINKS ---
    pdf.add_page()
    pdf.set_font('Arial', 'B', 24)
    pdf.cell(0, 20, PROJECT_TITLE, 0, 1, 'C')
    pdf.ln(10)
    
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f"Team Name: {TEAM_NAME}", 0, 1)
    pdf.cell(0, 10, f"Team ID: {PROJECT_ID}", 0, 1)
    
    # Hyperlinks
    pdf.set_text_color(0, 0, 255)
    pdf.set_font('Arial', 'U', 12)
    pdf.cell(0, 10, "Live Deployment (Render)", 0, 1, link=DEPLOY_URL)
    pdf.cell(0, 10, "GitHub Repository (Source Code)", 0, 1, link=REPO_URL)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(10)

    # --- SECTION 1: PROBLEM STATEMENT AND APPROACH ---
    pdf.chapter_title("1. Problem Statement and Approach")
    pdf.chapter_body(
        "Problem: Despite high Aadhaar generation, 'Last Mile Saturation' (Mandatory Biometric Updates for ages 5-18) "
        "remains a challenge. District Nodal Officers lack real-time visibility into these micro-gaps due to data silos.\n\n"
        "Approach: We built 'Aadhaar Satark', a Lakehouse-based Command Center. It ingests UIDAI datasets, "
        "calculates saturation gaps using a custom 'Efficiency Index', and uses Geospatial Heatmaps for visualization. "
        "A RAG-based AI Agent assists officers with policy queries, reducing decision latency."
    )

    # --- SECTION 2: DATASETS USED ---
    pdf.chapter_title("2. Datasets Used")
    pdf.chapter_body(
        "1. Aadhaar Enrolment Data (Static & API): Demographic breakdown (0-5, 5-18, >18).\n"
        "2. Biometric Update Data: Mandatory biometric update statistics.\n"
        "3. OGD India APIs: Real-time sync with Data.gov.in using API Key integration.\n"
        "4. Geospatial Coordinates: Lat/Lng mapping for 700+ districts."
    )

    # --- SECTION 3: METHODOLOGY ---
    pdf.chapter_title("3. Methodology")
    pdf.chapter_body(
        "A. Data Cleaning & Preprocessing:\n"
        "- Normalization: Standardized district names (e.g., 'Coochbehar' -> 'Cooch Behar') using fuzzy matching dictionaries.\n"
        "- Deduplication: 'Last-Write-Wins' policy based on (State, District, Date) composite keys.\n"
        "- Conversion: Handled type casting for numeric columns sourced from JSON APIs.\n\n"
        
        "B. Analytical Engine:\n"
        "- Gap Analysis: Calculated 'Pending Updates' = (Estimated Population 5-18) - (Actual Biometric Updates).\n"
        "- Anomaly Detection: Implemented Isolation Forest (SciKit-Learn) to flag statistical outliers in update trends.\n\n"
        
        "C. AI Integration:\n"
        "- RAG Pipeline: Vectorized UIDAI circulars into FAISS. The Gemini Pro LLM retrieves context to answer policy queries."
    )

    # --- SECTION 4: DATA ANALYSIS AND VISUALISATION ---
    pdf.add_page()
    pdf.chapter_title("4. Data Analysis and Visualisation")
    
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, "Finding 1: High-Deficit Zones (Red)", 0, 1)
    pdf.set_font('Arial', '', 11)
    pdf.multi_cell(0, 7, 
        "Our analysis revealed specific districts (e.g., Dima Hasao) with >50% update gaps. "
        "The heatmap below highlights these critical zones."
    )
    pdf.add_image_if_exists('assets/screenshots/map_interaction.png')
    
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, "Finding 2: AI-Driven Policy Support", 0, 1)
    pdf.set_font('Arial', '', 11)
    pdf.multi_cell(0, 7, "The AI Assistant correctly interprets 'update lag' penalties, replacing manual PDF searches.")
    pdf.add_image_if_exists('assets/screenshots/search_demo.png')

    pdf.add_page()
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, "Dashboard Overview & Critical Flags", 0, 1)
    pdf.add_image_if_exists('assets/screenshots/dashboard.png')
    pdf.ln(5)
    pdf.add_image_if_exists('assets/screenshots/critical_status.png')

    # --- SECTION 5: CODE FILES (EMBEDDED) ---
    pdf.add_page()
    pdf.chapter_title("5. Code Snippets (Core Logic)")
    pdf.set_font('Courier', '', 8)
    
    # Read backend/services/processing.py
    try:
        with open('backend/services/processing.py', 'r', encoding='utf-8') as f:
            code_content = f.read()
            # Normalize for FPDF (Latin-1 compatible)
            # Replace common non-ascii chars or strip them
            code_content = code_content.encode('latin-1', 'replace').decode('latin-1')
            
            # Truncate if too long to save standard page limit, but mostly keep it
            # We'll grab the first 300 lines or specific functions
            lines = code_content.split('\n')
            
            pdf.cell(0, 5, "File: backend/services/processing.py (Data Processing & Anomaly Detection)", 0, 1)
            pdf.ln(2)
            
            # Print Key Algorithm Functions
            for line in lines:
                # Basic filter to skip large maps for brevity if needed, but printing all is safer for strict rules
                if len(pdf.pages) > 24: # Safety break
                    pdf.cell(0, 5, "... (Code Truncated for PDF Limit) ...", 0, 1)
                    break
                pdf.cell(0, 4, line, 0, 1)
                
    except Exception as e:
        pdf.cell(0, 10, f"Error reading code file: {str(e)}", 0, 1)

    # Output
    pdf.output("Aadhaar_Satark_Submission.pdf", 'F')
    print("Final Strict PDF Generated Successfully!")

if __name__ == '__main__':
    create_final_pdf()
