from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel
import uvicorn
import io
import pandas as pd
import joblib
import json
import os
import shutil

# Import from refactored processing module
from services.processing import process_data, smart_merge
from services.report_generator import generate_report
from services.api_sync import sync_all_official_data
from services.rag_agent import SatarkAgent

app = FastAPI(title="Aadhaar Satark API")

# Setup CORS
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DistrictReportRequest(BaseModel):
    state: str
    district: str
    expected_updates: int
    actual_updates: int
    pending_updates: int
    gap_percentage: float
    status: str

@app.get("/health")
def health_check():
    """Simple health check endpoint."""
    return {"status": "ok"}

# Globals for Persistence
TRAINED_MODEL = None
GLOBAL_ENROL_DF = None
GLOBAL_BIO_DF = None
GLOBAL_DEMO_DF = None
AGENT = None

DATA_DIR = "data"
ENROL_PATH = os.path.join(DATA_DIR, "master_enrolment.pkl")
BIO_PATH = os.path.join(DATA_DIR, "master_biometric.pkl")
DEMO_PATH = os.path.join(DATA_DIR, "master_demographic.pkl")
MODEL_PATH = "models/isolation_forest.joblib"
INITIAL_DATA_PATH = "data/initial_data.json"

@app.on_event("startup")
async def load_artifacts():
    global TRAINED_MODEL, GLOBAL_ENROL_DF, GLOBAL_BIO_DF, GLOBAL_DEMO_DF, AGENT
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        
        # 1. Load Model
        if os.path.exists(MODEL_PATH):
            print(f"🧠 Loading Trained Model from {MODEL_PATH}...")
            TRAINED_MODEL = joblib.load(MODEL_PATH)
            
        # 2. Load Master Datasets (if they exist)
        if os.path.exists(ENROL_PATH):
            print(f"📂 Loading Enrolment Master from {ENROL_PATH}...")
            try:
                GLOBAL_ENROL_DF = pd.read_pickle(ENROL_PATH)
            except Exception as e:
                print(f"⚠️ Error loading Enrolment Master: {e}")
                
        if os.path.exists(BIO_PATH):
            print(f"📂 Loading Biometric Master from {BIO_PATH}...")
            try:
                GLOBAL_BIO_DF = pd.read_pickle(BIO_PATH)
            except Exception as e:
                print(f"⚠️ Error loading Biometric Master: {e}")

        if os.path.exists(DEMO_PATH):
            print(f"📂 Loading Demographic Master from {DEMO_PATH}...")
            try:
                GLOBAL_DEMO_DF = pd.read_pickle(DEMO_PATH)
            except Exception as e:
                print(f"⚠️ Error loading Demographic Master: {e}")
            
        # 3. Initialize RAG Agent
        print("🤖 Initializing RAG Agent...")
        AGENT = SatarkAgent("data/knowledge_base.txt", GLOBAL_ENROL_DF, GLOBAL_BIO_DF, GLOBAL_DEMO_DF)
        
        print("✅ System Initialization Complete. Persistence Layer Active.")
                
    except Exception as e:
        print(f"⚠️ Warning: Failed to load artifacts: {e}")

def save_state():
    """Helper to save current global DFs to disk"""
    try:
        if GLOBAL_ENROL_DF is not None:
            GLOBAL_ENROL_DF.to_pickle(ENROL_PATH)
        if GLOBAL_BIO_DF is not None:
            GLOBAL_BIO_DF.to_pickle(BIO_PATH)
        if GLOBAL_DEMO_DF is not None:
            GLOBAL_DEMO_DF.to_pickle(DEMO_PATH)
        print("💾 State saved successfully.")
    except Exception as e:
        print(f"❌ Error Saving State: {e}")

@app.get("/initial-data")
async def get_initial_data():
    """
    Returns the processed analysis. 
    If Global DFs are loaded, calculate fresh from them.
    Else fall back to initial_data.json.
    """
    # Priority: Real-time Global Data > Static JSON
    if GLOBAL_ENROL_DF is not None and GLOBAL_BIO_DF is not None:
        try:
            print("🚀 Generating fresh insights from Persistent Store...")
            result = process_data(
                GLOBAL_ENROL_DF, 
                GLOBAL_BIO_DF, 
                demographic_data=GLOBAL_DEMO_DF,
                model=TRAINED_MODEL
            )
            if "model" in result: result.pop("model")
            
            # Add metadata
            result['dataset_info'] = {
                "enrolment_records": len(GLOBAL_ENROL_DF),
                "biometric_records": len(GLOBAL_BIO_DF),
                "source": "persistent_store"
            }
            return JSONResponse(content=result)
        except Exception as e:
            print(f"⚠️ generation error: {e}. Falling back to static file.")
            
    # Fallback
    if os.path.exists(INITIAL_DATA_PATH):
        with open(INITIAL_DATA_PATH, "r") as f:
            return JSONResponse(content=json.load(f))
            
    return {"error": "No data available. Please upload files or run training."}

@app.post("/sync-official")
async def sync_official():
    global GLOBAL_ENROL_DF, GLOBAL_BIO_DF
    
    # Initialize if None (Fallbacks to handle empty start)
    if GLOBAL_ENROL_DF is None: GLOBAL_ENROL_DF = pd.DataFrame()
    if GLOBAL_BIO_DF is None: GLOBAL_BIO_DF = pd.DataFrame()
    
    try:
        results = sync_all_official_data(GLOBAL_ENROL_DF, GLOBAL_BIO_DF)
        GLOBAL_ENROL_DF = results["enrolment"]
        GLOBAL_BIO_DF = results["biometric"]
        
        # Update Agent
        if AGENT:
             AGENT.update_data(GLOBAL_ENROL_DF, GLOBAL_BIO_DF, GLOBAL_DEMO_DF)
        
        save_state()
        
        return {
            "status": "success",
            "message": "Official Data Synced successfully",
            "enrolment_size": len(GLOBAL_ENROL_DF),
            "biometric_size": len(GLOBAL_BIO_DF)
        }
    except Exception as e:
        print(f"❌ Sync Error: {e}")
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")

@app.post("/upload")
async def upload_files(
    enrolment_file: UploadFile = File(None),
    biometric_file: UploadFile = File(None),
    demographic_file: UploadFile = File(None)
):
    global GLOBAL_ENROL_DF, GLOBAL_BIO_DF, GLOBAL_DEMO_DF
    import time
    start_time = time.time()
    try:
        # 1. Read Uploaded Files (Handle Partial Uploads)
        # Note: 'File' default is not None for File(...), so we check if provided
        
        updated = False
        
        if enrolment_file:
            print("📥 Processing Enrolment Update...")
            enrol_bytes = await enrolment_file.read()
            if len(enrol_bytes) > 0:
                new_enrol_df = pd.read_csv(io.BytesIO(enrol_bytes))
                GLOBAL_ENROL_DF = smart_merge(GLOBAL_ENROL_DF, new_enrol_df)
                updated = True
        
        if biometric_file:
             print("📥 Processing Biometric Update...")
             bio_bytes = await biometric_file.read()
             if len(bio_bytes) > 0:
                new_bio_df = pd.read_csv(io.BytesIO(bio_bytes))
                GLOBAL_BIO_DF = smart_merge(GLOBAL_BIO_DF, new_bio_df)
                updated = True
                
        if demographic_file:
             print("📥 Processing Demographic Update...")
             demo_bytes = await demographic_file.read()
             if len(demo_bytes) > 0:
                new_demo_df = pd.read_csv(io.BytesIO(demo_bytes))
                GLOBAL_DEMO_DF = smart_merge(GLOBAL_DEMO_DF, new_demo_df)
                updated = True

        if not updated:
            return JSONResponse({"message": "No valid files received or empty files."}, status_code=400)
        
        # 2. Save State (Persistence)
        save_state()
        
        # 3. Process (Run Analysis on Global Data)
        result = process_data(
            GLOBAL_ENROL_DF, 
            GLOBAL_BIO_DF, 
            demographic_data=GLOBAL_DEMO_DF,
            model=TRAINED_MODEL
        )
        
        if "model" in result:
            result.pop("model") 
        
        if "error" in result:
             raise HTTPException(status_code=400, detail=result["error"])
             
        # Latency
        end_time = time.time()
        result['processing_time_ms'] = round((end_time - start_time) * 1000, 2)
        
        # Update Agent
        if AGENT:
            AGENT.update_data(GLOBAL_ENROL_DF, GLOBAL_BIO_DF, GLOBAL_DEMO_DF)
        
        result['dataset_info'] = {
            "enrolment_records": len(GLOBAL_ENROL_DF) if GLOBAL_ENROL_DF is not None else 0,
            "biometric_records": len(GLOBAL_BIO_DF) if GLOBAL_BIO_DF is not None else 0,
             "source": "live_update"
        }
             
        return JSONResponse(content=result)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-report")
async def generate_pdf(report_request: DistrictReportRequest):
    try:
        data = report_request.dict()
        pdf_bytes = generate_report(data)
        
        headers = {
            'Content-Disposition': f'attachment; filename="Report_{data["district"]}.pdf"'
        }
        return Response(content=pdf_bytes, media_type="application/pdf", headers=headers)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ChatRequest(BaseModel):
    query: str

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """Chat with the RAG Agent"""
    if AGENT:
        return AGENT.query(request.query)
    return {"answer": "Agent is initializing, please wait..."}

if __name__ == "__main__":
    # Use port 8001 to avoid conflicts if 8000 is taken, or match user env
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
