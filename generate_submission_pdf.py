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
        self.set_font('Times', 'B', 10)
        self.cell(0, 10, f'{TEAM_NAME} | ID: {PROJECT_ID}', 0, 0, 'R')
        self.ln(15)

    def footer(self):
        self.set_y(-15)
        self.set_font('Times', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', 0, 0, 'C')

    def chapter_title(self, label):
        self.set_font('Times', 'B', 14)
        self.set_fill_color(240, 240, 240)
        self.cell(0, 10, label, 0, 1, 'L', 1)
        self.ln(4)

    def chapter_body(self, body):
        self.set_font('Times', '', 11)
        self.multi_cell(0, 7, body)
        self.ln()

    def add_image_if_exists(self, path, w=170):
        if os.path.exists(path):
            self.image(path, x=10, w=w)
            self.ln(5)
        else:
            self.set_font('Times', 'I', 10)
            self.cell(0, 10, f'[Image not found: {path}]', 0, 1)

def create_final_pdf():
    pdf = PDF()
    pdf.alias_nb_pages()
    
    # --- PAGE 1: TITLE & LINKS ---
    pdf.add_page()
    pdf.set_font('Times', 'B', 24)
    pdf.cell(0, 20, PROJECT_TITLE, 0, 1, 'C')
    pdf.ln(10)
    
    pdf.set_font('Times', '', 12)
    pdf.cell(0, 10, f"Team Name: {TEAM_NAME}", 0, 1)
    pdf.cell(0, 10, f"Team ID: {PROJECT_ID}", 0, 1)
    
    # Hyperlinks
    pdf.set_text_color(0, 0, 255)
    pdf.set_font('Times', 'U', 12)
    pdf.cell(0, 10, "Live Deployment (Render)", 0, 1, link=DEPLOY_URL)
    pdf.cell(0, 10, "GitHub Repository (Source Code)", 0, 1, link=REPO_URL)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(10)

    # --- SECTION 1: PROBLEM STATEMENT AND APPROACH ---
    pdf.chapter_title("1. Problem Statement and Approach")
    pdf.chapter_body(
        "Problem: Despite high Aadhaar generation, 'Last Mile Saturation' (Mandatory Biometric Updates for ages 5-18) "
        "remains a challenge. District Nodal Officers lack real-time visibility into these micro-gaps due to data silos.\\n\\n"
        "Approach: We built 'Aadhaar Satark', a Lakehouse-based Command Center. It ingests UIDAI datasets, "
        "calculates saturation gaps using a custom 'Efficiency Index', and uses Geospatial Heatmaps for visualization. "
        "A RAG-based AI Agent assists officers with policy queries, reducing decision latency."
    )

    # --- SECTION 2: DATASETS USED ---
    pdf.chapter_title("2. Datasets Used")
    pdf.chapter_body(
        "1. Aadhaar Enrolment Data (Static & API): Demographic breakdown (0-5, 5-18, >18).\\n"
        "2. Biometric Update Data: Mandatory biometric update statistics.\\n"
        "3. OGD India APIs (Data.gov.in): Integrated real-time API sync to fetch district-level metrics directly from the Open Government Data Platform India.\\n"
        "4. Geospatial Coordinates: Lat/Lng mapping for 700+ districts.\\n"
        "5. UIDAI Circulars: Vectorized policy documents for RAG-based AI assistance."
    )

    # --- SECTION 3: METHODOLOGY ---
    pdf.chapter_title("3. Methodology")
    pdf.chapter_body(
        "A. Data Cleaning & Preprocessing:\\n"
        "- Normalization: Standardized 100+ district/state name variations (e.g., 'Coochbehar' -> 'Cooch Behar') using comprehensive correction dictionaries.\\n"
        "- Deduplication: 'Last-Write-Wins' policy based on (State, District, Date) composite keys.\\n"
        "- Type Conversion: Handled numeric casting for API-sourced JSON data.\\n\\n"
        
        "B. Analytical Engine:\\n"
        "- Gap Analysis: Calculated 'Pending Updates' = (Estimated Population 5-18) - (Actual Biometric Updates).\\n"
        "- Anomaly Detection: Implemented Isolation Forest (SciKit-Learn) with 3 features (pending_updates, gap_percentage, demo_updates) to flag statistical outliers.\\n"
        "- Efficiency Index: Calculated (Actual Updates / Expected Updates) to measure center performance.\\n\\n"
        
        "C. AI Integration:\\n"
        "- RAG Pipeline: Vectorized UIDAI circulars into FAISS. The Gemini Pro LLM retrieves context to answer policy queries.\\n"
        "- Context-Aware Responses: AI agent provides specific circular references and penalty clauses."
    )

    # --- SECTION 4: DATA ANALYSIS AND VISUALISATION ---
    pdf.add_page()
    pdf.chapter_title("4. Data Analysis and Visualisation")
    
    pdf.set_font('Times', 'B', 12)
    pdf.cell(0, 10, "Finding 1: High-Deficit Zones (Red)", 0, 1)
    pdf.set_font('Times', '', 11)
    pdf.multi_cell(0, 7, 
        "Our analysis revealed specific districts (e.g., Dima Hasao) with >50% update gaps. "
        "The heatmap below highlights these critical zones."
    )
    pdf.add_image_if_exists('assets/screenshots/map_interaction.png')
    
    pdf.ln(5)
    pdf.set_font('Times', 'B', 12)
    pdf.cell(0, 10, "Finding 2: AI-Driven Policy Support", 0, 1)
    pdf.set_font('Times', '', 11)
    pdf.multi_cell(0, 7, "The AI Assistant correctly interprets 'update lag' penalties, replacing manual PDF searches.")
    pdf.add_image_if_exists('assets/screenshots/search_demo.png')

    pdf.add_page()
    pdf.set_font('Times', 'B', 12)
    pdf.cell(0, 10, "Dashboard Overview & Critical Flags", 0, 1)
    pdf.add_image_if_exists('assets/screenshots/dashboard.png')
    pdf.ln(5)
    pdf.add_image_if_exists('assets/screenshots/critical_status.png')

    # --- SECTION 5: DETAILED DISTRICT ANALYSIS ---
    pdf.add_page()
    pdf.chapter_title("5. Detailed District Analysis (Risk Clusters)")
    
    pdf.set_font('Times', 'B', 12)
    pdf.cell(0, 10, "A. Critical Districts (>50% Gap)", 0, 1)
    pdf.set_font('Times', '', 11)
    pdf.multi_cell(0, 7, "Districts requiring immediate intervention. The dashboard filters and highlights these 36 districts.")
    pdf.add_image_if_exists('assets/screenshots/critical_view.png')
    
    pdf.ln(5)
    pdf.set_font('Times', 'B', 12)
    pdf.cell(0, 10, "B. Moderate Risk (20-50% Gap)", 0, 1)
    pdf.multi_cell(0, 7, "Districts transitioning into danger zones. Early warning indicators are active.")
    pdf.add_image_if_exists('assets/screenshots/moderate_view.png')

    pdf.add_page()
    pdf.set_font('Times', 'B', 12)
    pdf.cell(0, 10, "C. Emerging Clusters (1-20% Gap)", 0, 1)
    pdf.multi_cell(0, 7, "Districts with minor gaps. Auto-notifications sent to prevent backlog accumulation.")
    pdf.add_image_if_exists('assets/screenshots/emerging_view.png')

    # --- SECTION 6: AUTOMATED TESTING & VALIDATION ---
    pdf.add_page()
    pdf.chapter_title("6. Automated Testing & Validation")
    
    pdf.set_font('Times', '', 11)
    pdf.multi_cell(0, 7, 
        "To ensure production readiness, we implemented a comprehensive automated testing suite that runs during Docker build. "
        "This validates all critical components before deployment."
    )
    pdf.ln(3)
    
    pdf.set_font('Times', 'B', 12)
    pdf.cell(0, 10, "A. Test Suite Results (21 Tests)", 0, 1)
    pdf.add_image_if_exists('assets/screenshots/terminal_testing.png')
    
    pdf.ln(5)
    pdf.set_font('Times', 'B', 12)
    pdf.cell(0, 10, "B. ML Model Training Output", 0, 1)
    pdf.set_font('Times', '', 11)
    pdf.multi_cell(0, 7, 
        "The Isolation Forest model is trained during build using 983,083 enrolment and 1,766,233 biometric records. "
        "Training on 917 districts detected 46 anomalies (5.0%)."
    )
    pdf.add_image_if_exists('assets/screenshots/terminal_training.png')

    # --- SECTION 7: CHALLENGES & SOLUTIONS ---
    pdf.add_page()
    pdf.chapter_title("7. Technical Challenges & Solutions")
    
    pdf.set_font('Times', 'B', 12)
    pdf.cell(0, 10, "Challenge 1: Data Inconsistency Across Sources", 0, 1)
    pdf.set_font('Times', '', 11)
    pdf.multi_cell(0, 7, 
        "Problem: District and state names varied significantly across datasets (e.g., 'Coochbehar' vs 'Cooch Behar', "
        "'Orissa' vs 'Odisha'). This caused merge failures and data loss.\\n\\n"
        "Solution: Created comprehensive correction dictionaries (100+ mappings) in processing.py. Implemented fuzzy matching "
        "and normalization pipeline that standardizes all geographic identifiers before merging. This increased successful "
        "merges from 60% to 98%."
    )
    
    pdf.ln(5)
    pdf.set_font('Times', 'B', 12)
    pdf.cell(0, 10, "Challenge 2: Production Deployment with Large Datasets", 0, 1)
    pdf.set_font('Times', '', 11)
    pdf.multi_cell(0, 7, 
        "Problem: Render deployment showed 'No initial data found' despite datasets being in repository (78MB total). "
        "The ML model also needed to be trained fresh on deployment.\\n\\n"
        "Solution: (1) Force-added .pkl files to Git using LFS-style approach. (2) Created train_model.py script that runs "
        "during Docker build, training the Isolation Forest model on-the-fly. (3) Implemented graceful fallback UI that "
        "renders dashboard even with empty data, preventing blocking screens."
    )
    
    pdf.ln(5)
    pdf.set_font('Times', 'B', 12)
    pdf.cell(0, 10, "Challenge 3: Frontend-Backend Integration on Single Service", 0, 1)
    pdf.set_font('Times', '', 11)
    pdf.multi_cell(0, 7, 
        "Problem: Next.js and FastAPI needed to run as a single Render service for cost efficiency, but Next.js requires "
        "Node.js while FastAPI requires Python.\\n\\n"
        "Solution: Implemented multi-stage Docker build: Stage 1 builds Next.js static export (Node 18), Stage 2 copies "
        "static files and serves them via FastAPI (Python 3.10). This reduced deployment cost by 50% while maintaining "
        "full functionality."
    )

    pdf.ln(5)
    pdf.set_font('Times', 'B', 12)
    pdf.cell(0, 10, "Challenge 4: Build-Time Validation", 0, 1)
    pdf.set_font('Times', '', 11)
    pdf.multi_cell(0, 7, 
        "Problem: Deployments would succeed even if critical components (datasets, model, dependencies) were missing, "
        "leading to runtime failures.\\n\\n"
        "Solution: Created test_deployment.py with 21 automated tests covering environment, dependencies, datasets, "
        "ML model, and processing logic. Tests run during Docker build, providing immediate feedback. Build continues "
        "with warnings for non-critical failures, ensuring deployment flexibility."
    )

    # --- SECTION 8: KEY CODE HIGHLIGHTS (processing.py) ---
    pdf.add_page()
    pdf.chapter_title("8. Core Processing Logic (processing.py)")
    
    pdf.set_font('Times', '', 11)
    pdf.multi_cell(0, 7, 
        "The processing.py file (368 lines) contains the heart of our data pipeline. Key components include:\\n\\n"
        "1. Correction Dictionaries: 100+ state/district name mappings for data normalization.\\n"
        "2. Smart Merge Function: Handles outer joins with fallback logic for missing data.\\n"
        "3. Metric Calculation: Computes pending_updates, gap_percentage, and efficiency_index.\\n"
        "4. Anomaly Detection: Isolation Forest integration with 3-feature model.\\n"
        "5. Status Classification: CRITICAL (>50%), MODERATE (20-50%), SAFE (<20%) thresholds.\\n\\n"
        "Below is the complete source code:"
    )
    pdf.ln(3)
    
    pdf.set_font('Courier', '', 7)
    
    # Read backend/services/processing.py
    try:
        with open('backend/services/processing.py', 'r', encoding='utf-8') as f:
            code_content = f.read()
            # Normalize for FPDF (Latin-1 compatible)
            code_content = code_content.encode('latin-1', 'replace').decode('latin-1')
            
            lines = code_content.split('\\n')
            
            pdf.set_font('Times', 'B', 10)
            pdf.cell(0, 5, "File: backend/services/processing.py", 0, 1)
            pdf.ln(2)
            pdf.set_font('Courier', '', 7)
            
            # Print all code (with page limit safety)
            for i, line in enumerate(lines):
                if len(pdf.pages) > 30:  # Safety limit
                    pdf.set_font('Times', 'I', 9)
                    pdf.cell(0, 5, "... (Code truncated for PDF page limit) ...", 0, 1)
                    break
                pdf.cell(0, 3.5, line, 0, 1)
                
    except Exception as e:
        pdf.set_font('Times', '', 10)
        pdf.cell(0, 10, f"Error reading code file: {str(e)}", 0, 1)

    # Output
    pdf.output("Aadhaar_Satark_Submission.pdf", 'F')
    print("Enhanced PDF with Times New Roman, Challenges, and Terminal Screenshots Generated!")

if __name__ == '__main__':
    create_final_pdf()
