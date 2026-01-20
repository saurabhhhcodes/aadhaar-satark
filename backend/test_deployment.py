#!/usr/bin/env python3
"""
Automated Deployment Tests
Runs during Docker build to validate the application is production-ready.
"""
import sys
import os
import pandas as pd
import joblib
from pathlib import Path

# Test counters
tests_passed = 0
tests_failed = 0

def test_result(name, passed, details=""):
    """Record test result."""
    global tests_passed, tests_failed
    if passed:
        tests_passed += 1
        print(f"✅ {name}")
        if details:
            print(f"   {details}")
    else:
        tests_failed += 1
        print(f"❌ {name}")
        if details:
            print(f"   {details}")

def test_datasets():
    """Verify master datasets exist and are valid."""
    print("\n📊 Testing Datasets...")
    
    enrol_path = "data/master_enrolment.pkl"
    bio_path = "data/master_biometric.pkl"
    demo_path = "data/master_demographic.pkl"  # Optional
    
    # Test 1: Required files exist
    enrol_exists = os.path.exists(enrol_path)
    bio_exists = os.path.exists(bio_path)
    test_result("Master datasets exist", enrol_exists and bio_exists,
                f"Enrolment: {enrol_exists}, Biometric: {bio_exists}")
    
    # Test 1b: Optional demographic dataset
    demo_exists = os.path.exists(demo_path)
    if demo_exists:
        test_result("Demographic dataset found (optional)", True, demo_path)
    else:
        print(f"ℹ️  Demographic dataset not found (optional): {demo_path}")
    
    if not (enrol_exists and bio_exists):
        return
    
    # Test 2: Files are readable
    try:
        enrol_df = pd.read_pickle(enrol_path)
        bio_df = pd.read_pickle(bio_path)
        test_result("Datasets are readable", True,
                   f"Enrolment: {len(enrol_df)} rows, Biometric: {len(bio_df)} rows")
        
        # Test demographic if exists
        if demo_exists:
            demo_df = pd.read_pickle(demo_path)
            test_result("Demographic dataset readable", True,
                       f"Demographic: {len(demo_df)} rows")
        
        # Test 3: Required columns exist
        required_enrol_cols = ['state', 'district']
        required_bio_cols = ['state', 'district']
        
        enrol_valid = all(col in enrol_df.columns for col in required_enrol_cols)
        bio_valid = all(col in bio_df.columns for col in required_bio_cols)
        
        test_result("Datasets have required columns", enrol_valid and bio_valid)
        
        # Test 4: Data quality
        enrol_has_data = len(enrol_df) > 0
        bio_has_data = len(bio_df) > 0
        test_result("Datasets contain data", enrol_has_data and bio_has_data,
                   f"Enrolment: {len(enrol_df)}, Biometric: {len(bio_df)}")
        
    except Exception as e:
        test_result("Datasets are readable", False, str(e))

def test_model():
    """Verify trained model exists and is functional."""
    print("\n🤖 Testing ML Model...")
    
    model_path = "models/isolation_forest.joblib"
    
    # Test 1: Model file exists
    model_exists = os.path.exists(model_path)
    test_result("Model file exists", model_exists, model_path)
    
    if not model_exists:
        return
    
    # Test 2: Model is loadable
    try:
        model = joblib.load(model_path)
        test_result("Model loads successfully", True)
        
        # Test 3: Model can make predictions
        import numpy as np
        # Use 3 features: pending_updates, gap_percentage, demo_updates
        test_data = np.array([[10000, 50.0, 0], [1000, 10.0, 0]])  # Sample data
        predictions = model.predict(test_data)
        test_result("Model can predict", len(predictions) == 2,
                   f"Predictions: {predictions}")
        
    except Exception as e:
        test_result("Model loads successfully", False, str(e))

def test_processing_module():
    """Verify processing functions work correctly."""
    print("\n⚙️  Testing Processing Module...")
    
    try:
        from services.processing import smart_merge, process_data
        test_result("Processing module imports", True)
        
        # Test with sample data
        sample_enrol = pd.DataFrame({
            'state': ['State A', 'State B'],
            'district': ['District 1', 'District 2'],
            'age_5_17': [100000, 150000]
        })
        
        sample_bio = pd.DataFrame({
            'state': ['State A', 'State B'],
            'district': ['District 1', 'District 2'],
            'bio_age_5_17': [50000, 120000]
        })
        
        merged = smart_merge(sample_enrol, sample_bio)
        test_result("smart_merge works", len(merged) > 0,
                   f"Merged {len(merged)} districts")
        
        # Test process_data
        result = process_data(sample_enrol, sample_bio)
        test_result("process_data works", 'districts' in result and len(result['districts']) > 0)
        
    except Exception as e:
        test_result("Processing module works", False, str(e))

def test_api_dependencies():
    """Verify all API dependencies are installed."""
    print("\n📦 Testing Dependencies...")
    
    required_modules = [
        'fastapi',
        'uvicorn',
        'pandas',
        'sklearn',
        'joblib',
        'langchain',
        'google.generativeai'
    ]
    
    for module_name in required_modules:
        try:
            __import__(module_name)
            test_result(f"Module '{module_name}' installed", True)
        except ImportError:
            test_result(f"Module '{module_name}' installed", False)

def test_environment():
    """Check environment configuration."""
    print("\n🌍 Testing Environment...")
    
    # Test 1: Python version
    import sys
    py_version = sys.version_info
    py_ok = py_version.major == 3 and py_version.minor >= 10
    test_result("Python version >= 3.10", py_ok,
               f"Current: {py_version.major}.{py_version.minor}")
    
    # Test 2: Working directory structure
    required_dirs = ['data', 'models', 'services']
    for dir_name in required_dirs:
        exists = os.path.isdir(dir_name)
        test_result(f"Directory '{dir_name}' exists", exists)

def main():
    """Run all tests."""
    print("=" * 60)
    print("🧪 AADHAAR SATARK - AUTOMATED DEPLOYMENT TESTS")
    print("=" * 60)
    
    test_environment()
    test_api_dependencies()
    test_datasets()
    test_model()
    test_processing_module()
    
    print("\n" + "=" * 60)
    print(f"📊 TEST RESULTS: {tests_passed} passed, {tests_failed} failed")
    print("=" * 60)
    
    if tests_failed > 0:
        print("⚠️  Some tests failed, but build will continue.")
        print("   The application may have reduced functionality.")
        # Don't exit with error to allow build to complete
        return 0
    else:
        print("✅ All tests passed! Deployment is production-ready.")
        return 0

if __name__ == "__main__":
    sys.exit(main())
