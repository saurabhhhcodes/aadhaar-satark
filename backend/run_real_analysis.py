import os
import pandas as pd
import json
from services.processing import process_data

# Paths to the real datasets
BASE_DIR = "/home/saurabh/aadhaar-satark/UIDAIHackathonDataSets"
ENROL_DIR = os.path.join(BASE_DIR, "api_data_aadhar_enrolment")
BIO_DIR = os.path.join(BASE_DIR, "api_data_aadhar_biometric")

def load_and_merge_csvs(directory):
    all_files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.csv')]
    print(f"Loading {len(all_files)} files from {directory}...")
    df_list = []
    for f in all_files:
        print(f" - Reading {os.path.basename(f)} ({os.path.getsize(f)/1024/1024:.2f} MB)")
        df = pd.read_csv(f)
        df_list.append(df)
    
    if not df_list:
        return pd.DataFrame()
    return pd.concat(df_list, ignore_index=True)

import joblib

# ... (Previous imports)

def main():
    print("🚀 Starting Comprehensive Real Data Analysis & Training...")
    
    # ... (Loading data code same as before)
    enrol_df = load_and_merge_csvs(ENROL_DIR)
    bio_df = load_and_merge_csvs(BIO_DIR)
    
    # NEW: Load Demographic Data
    DEMO_DIR = os.path.join(BASE_DIR, "api_data_aadhar_demographic")
    demo_df = load_and_merge_csvs(DEMO_DIR)
    
    print("🧠 Training AI Model on 2.8M Records (Enrolment + Biometric + Demographic)...")
    result = process_data(enrol_df, bio_df, demo_df) # No model passed = Training Mode
    
    # Separate Model and Data
    model = result.pop('model')
    
    # Save Artifacts
    data_path = "data/initial_data.json"
    model_path = "models/isolation_forest.joblib"
    
    print(f"💾 Persisting Data to {data_path}...")
    with open(data_path, "w") as f:
        json.dump(result, f, indent=2)
        
    # NEW: Save Master Datasets for API Persistence
    print("💾 Saving Master Datasets for Stateful API...")
    enrol_df.to_pickle("data/master_enrolment.pkl")
    bio_df.to_pickle("data/master_biometric.pkl")
    # demo_df.to_pickle("data/master_demographic.pkl") # Optional if needed
        
    print(f"💾 Persisting Model to {model_path}...")
    joblib.dump(model, model_path)
    
    print("\n✅ SYSTEM INITIALIZED SUCCESSFULLY")


if __name__ == "__main__":
    main()
