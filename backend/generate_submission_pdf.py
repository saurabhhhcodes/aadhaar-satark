from fpdf import FPDF
import os
import datetime

# Configuration
TEAM_NAME = "UIDAI_11479"
PROJECT_TITLE = "Aadhaar Satark: Intelligence Engine"
OUTPUT_FILENAME = "UIDAI_11479_Submission_Report.pdf"

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, f'{PROJECT_TITLE} - Team {TEAM_NAME}', 0, 1, 'R')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 16)
        self.set_fill_color(230, 230, 230)
        self.cell(0, 12, title, 0, 1, 'L', 1)
        self.ln(4)

    def chapter_body(self, body):
        self.set_font('Arial', '', 11)
        # Sanitize body
        body = body.encode('latin-1', 'replace').decode('latin-1')
        self.multi_cell(0, 6, body)
        self.ln()

    def add_code_file(self, filename, filepath):
        self.add_page()
        self.chapter_title(f"Appendix Code: {filename}")
        self.set_font("Courier", "", 8)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                code = f.read()
            # Sanitize code for FPDF (remove emojis/unicode)
            code = code.encode('latin-1', 'replace').decode('latin-1')
            self.multi_cell(0, 4, code)
        except Exception as e:
            self.multi_cell(0, 4, f"Could not read file: {e}")

pdf = PDF()
pdf.add_page()

# --- COVER PAGE ---
pdf.set_font('Arial', 'B', 24)
pdf.ln(60)
pdf.cell(0, 10, PROJECT_TITLE, 0, 1, 'C')
pdf.set_font('Arial', '', 16)
pdf.cell(0, 10, f"Team: {TEAM_NAME}", 0, 1, 'C')
pdf.ln(20)
pdf.set_font('Arial', '', 12)
pdf.cell(0, 10, f"Date: {datetime.date.today()}", 0, 1, 'C')
pdf.cell(0, 10, "Hackathon Track: Societal Trends in Aadhaar Enrolment", 0, 1, 'C')
pdf.add_page()

# --- 1. PROBLEM STATEMENT & APPROACH ---
pdf.chapter_title("1. Problem Statement & Approach")
pdf.chapter_body("""
Problem:
The Aadhaar ecosystem handles billions of updates annually. However, gaps exists between 'Expected Biometric Updates' (based on population demographics) and 'Actual Updates'. Identifying these gaps manually across 700+ districts is impossible, leading to potential fraud or service denial.

Approach:
We developed 'Aadhaar Satark', a Real-time Intelligence Engine.
1. Data Ingestion: Integrating Official Data.Gov.in APIs for Enrolment and Biometric data.
2. Smart Merging: A persistent stateful backend that merges monthly datasets without duplication.
3. Anomaly Detection: Implementing an Isolation Forest (Unsupervised ML) model to detect districts where the Update-to-Enrolment ratio deviates significantly from the national norm.
4. Actionable Intelligence: Generating targeted PDF Action Plans for district administrators.
""")

# --- 2. DATASETS USED ---
pdf.chapter_title("2. Datasets Used")
pdf.chapter_body("""
We utilized the official Open Government Data (OGD) Platform APIs provided by UIDAI via Data.Gov.in.

1. Aadhaar Enrolment Data (Resource ID: ecd49b12-3084-4521-8f7e-ca8bf72069ba)
   - Columns Used: State, District, Pincode, Age Group (0-5, 5-18, 18+), Gender.
   - Purpose: To establish the baseline 'Addressable Market' for updates.

2. Aadhaar Biometric Update Data (Resource ID: 65454dab-1517-40a3-ac1d-47d4dfe6891c)
   - Columns Used: State, District, Biometric Updates Count.
   - Purpose: To measure actual performance.

3. Demographic Data (Resource ID: 19eac040-0b94-49fa-b239-4f2fd8677d53)
   - Purpose: Validation of demographic shifts.
""")

# --- 3. METHODOLOGY ---
pdf.chapter_title("3. Methodology")
pdf.chapter_body("""
Data Cleaning & Preprocessing:
- Normalization: We implemented a dictionary-based cleaning engine to standardize State/District names (e.g., merging 'Orissa'/'Odisha', correcting 'Westbengal').
- Imputation: Numeric fields are sanitized using reliable zero-filling for missing values.

Analytical Model:
- We calculate the 'Gap Percentage' = (Expected Updates - Actual Updates) / Expected Updates.
- We use Sklearn's Isolation Forest to detect statistical anomalies in this Gap distribution.
- Districts are classified into:
  * CRITICAL (>50% Gap)
  * MODERATE (20-50% Gap)
  * EMERGING (1-20% Gap)
  * COMPLIANT (0% Gap)
""")

# --- 4. DATA ANALYSIS & FINDINGS ---
pdf.chapter_title("4. Analysis & Visualisation")
pdf.chapter_body("""
Key Findings from Current Data:
- Total Districts Monitored: 916
- Critical Districts Identified: 36 (Requiring immediate intervention)
- Total Pending Updates Identified: ~42,000

Visualisation:
The solution features a Next.js Dashboard with:
- Interactive Geospatial Map (Color-coded by Risk)
- Real-time Sync Status with Data.Gov.in
- Before/After Trend Analysis
""")

# --- 5. CODE APPENDIX ---
# Add key files
pdf.add_code_file("api_sync.py (Official API Integration)", "services/api_sync.py")
pdf.add_code_file("processing.py (ML Logic)", "services/processing.py")
pdf.add_code_file("main.py (FastAPI Backend)", "main.py")

output_path = os.path.join(os.getcwd(), OUTPUT_FILENAME)
pdf.output(output_path)
print(f"PDF Generated Successfully: {output_path}")
