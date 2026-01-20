#!/usr/bin/env python3
"""
Train Isolation Forest Model for Anomaly Detection
This script runs during Docker build to ensure the model is ready for production.
"""
import pandas as pd
import joblib
import os
from sklearn.ensemble import IsolationForest

def train_isolation_forest():
    """Train the Isolation Forest model using master datasets."""
    print("🧠 Starting Model Training...")
    
    # Paths
    enrol_path = "data/master_enrolment.pkl"
    bio_path = "data/master_biometric.pkl"
    model_output = "models/isolation_forest.joblib"
    
    # Ensure directories exist
    os.makedirs("models", exist_ok=True)
    
    # Load datasets
    if not os.path.exists(enrol_path) or not os.path.exists(bio_path):
        print("❌ Master datasets not found. Cannot train model.")
        print(f"   Expected: {enrol_path}, {bio_path}")
        return False
    
    print(f"📂 Loading datasets from {enrol_path} and {bio_path}...")
    enrol_df = pd.read_pickle(enrol_path)
    bio_df = pd.read_pickle(bio_path)
    
    print(f"   Enrolment records: {len(enrol_df)}")
    print(f"   Biometric records: {len(bio_df)}")
    
    # Use process_data to get metrics (it handles all the merging and calculations)
    print("🔄 Processing data and calculating metrics...")
    from services.processing import process_data
    
    # Process data without a model (will train internally, but we'll extract features)
    result = process_data(enrol_df, bio_df, demographic_data=None, model=None)
    
    if not result or 'districts' not in result:
        print("❌ Data processing failed.")
        return False
    
    districts = result['districts']
    print(f"   Processed districts: {len(districts)}")
    
    # Extract features for training
    # IMPORTANT: Must match the 3 features used in production (processing.py line ~269)
    training_data = []
    for d in districts:
        training_data.append([
            d.get('pending_updates', 0),
            d.get('gap_percentage', 0),
            d.get('demo_updates', 0)  # Third feature for demographic data
        ])
    
    training_df = pd.DataFrame(training_data, columns=['pending_updates', 'gap_percentage', 'demo_updates'])
    
    if len(training_df) < 10:
        print("❌ Insufficient data for training (need at least 10 samples).")
        return False
    
    print(f"   Training samples: {len(training_df)}")
    print(f"   Features: {list(training_df.columns)}")
    
    # Train Isolation Forest
    print("🤖 Training Isolation Forest (contamination=0.1)...")
    model = IsolationForest(
        contamination=0.1,  # Expect 10% anomalies
        random_state=42,
        n_estimators=100
    )
    model.fit(training_df)
    
    # Save model
    joblib.dump(model, model_output)
    print(f"✅ Model saved to {model_output}")
    
    # Quick validation
    predictions = model.predict(training_df)
    anomaly_count = (predictions == -1).sum()
    print(f"   Detected {anomaly_count} anomalies in training data ({anomaly_count/len(training_df)*100:.1f}%)")
    
    return True

if __name__ == "__main__":
    success = train_isolation_forest()
    if not success:
        print("⚠️  Model training failed, but continuing build...")
        # Don't exit with error code to allow build to continue
        # The app will handle missing model gracefully
    else:
        print("🎉 Model training complete!")

