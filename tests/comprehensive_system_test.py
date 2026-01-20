import requests
import pandas as pd
import io
import time
import sys

BASE_URL = "http://localhost:8001"

def log(msg, status="INFO"):
    colors = {
        "INFO": "\033[94m", # Blue
        "SUCCESS": "\033[92m", # Green
        "ERROR": "\033[91m", # Red
        "WARN": "\033[93m", # Yellow
        "RESET": "\033[0m"
    }
    print(f"{colors.get(status, '')}[{status}] {msg}{colors['RESET']}")

def test_health():
    log("Testing /health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            log("Health check passed ✅", "SUCCESS")
            return True
        else:
            log(f"Health check failed: {response.status_code}", "ERROR")
            return False
    except Exception as e:
        log(f"Health check exception: {e}", "ERROR")
        return False

def test_initial_data():
    log("Testing /initial-data endpoint...")
    try:
        start = time.time()
        response = requests.get(f"{BASE_URL}/initial-data")
        duration = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            if 'districts' in data and len(data['districts']) > 0:
                log(f"Initial data loaded: {len(data['districts'])} districts in {duration:.2f}s ✅", "SUCCESS")
                log(f"Dataset Info: {data.get('dataset_info')}", "INFO")
                return data
            else:
                log("Initial data loaded but empty districts", "WARN")
                return None
        else:
            log(f"Initial data failed: {response.status_code}", "ERROR")
            return None
    except Exception as e:
        log(f"Initial data exception: {e}", "ERROR")
        return None

def test_official_sync():
    log("Testing /sync-official endpoint (Deep Sync)...")
    try:
        start = time.time()
        response = requests.post(f"{BASE_URL}/sync-official")
        duration = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            log(f"Sync successful in {duration:.2f}s ✅", "SUCCESS")
            log(f"Sync Result: {data.get('message')}", "SUCCESS")
            log(f"New Enrolment Size: {data.get('enrolment_size')}", "INFO")
            log(f"New Biometric Size: {data.get('biometric_size')}", "INFO")
            return True
        else:
            log(f"Sync failed: {response.status_code} - {response.text}", "ERROR")
            return False
    except Exception as e:
        log(f"Sync exception: {e}", "ERROR")
        return False

def test_upload_flow():
    log("Testing /upload endpoint with dummy data...")
    
    # Create dummy CSVs
    enrol_csv = "state,district,pincode,age_5_17,date\nTestState,TestDistrict,111111,100,01-01-2025"
    bio_csv = "state,district,pincode,bio_age_5_17,date\nTestState,TestDistrict,111111,50,01-01-2025"
    
    files = {
        'enrolment_file': ('enrol.csv', io.StringIO(enrol_csv), 'text/csv'),
        'biometric_file': ('bio.csv', io.StringIO(bio_csv), 'text/csv')
    }
    
    try:
        response = requests.post(f"{BASE_URL}/upload", files=files)
        if response.status_code == 200:
            data = response.json()
            
            # Verify TestDistrict exists
            districts = data.get('districts', [])
            found = any(d['district'] == 'TestDistrict' for d in districts)
            
            if found:
                log("Upload successful and verification passed (TestDistrict found) ✅", "SUCCESS")
                return True
            else:
                log("Upload successful but TestDistrict NOT found in response", "ERROR")
                return False
        else:
            log(f"Upload failed: {response.status_code}", "ERROR")
            return False
    except Exception as e:
        log(f"Upload exception: {e}", "ERROR")
        return False

def run_all_tests():
    log("🚀 STARTING COMPREHENSIVE AUTOMATION TEST SUITE", "INFO")
    print("-" * 50)
    
    if not test_health():
        sys.exit(1)
        
    initial_data = test_initial_data()
    if not initial_data:
        sys.exit(1)
        
    initial_count = initial_data['dataset_info']['enrolment_records']
    
    print("-" * 50)
    if test_official_sync():
        # Verify data increased/changed
        new_data = test_initial_data()
        if new_data:
            new_count = new_data['dataset_info']['enrolment_records']
            diff = new_count - initial_count
            if diff >= 0:
                 log(f"Data verification: Record count change: {diff} records", "SUCCESS")
            else:
                 log(f"Data verification: Record count decreased! Possible issue. ({diff})", "WARN")
    else:
        log("Sync test failed, aborting sequence.", "ERROR")
        
    print("-" * 50)
    test_upload_flow()
    
    print("-" * 50)
    log("✅ ALL AUTOMATED TESTS COMPLETED", "SUCCESS")

if __name__ == "__main__":
    run_all_tests()
