from fastapi.testclient import TestClient
from main import app
import io
import pandas as pd

client = TestClient(app)

def create_csv_content(data):
    df = pd.DataFrame(data)
    bg = io.BytesIO()
    df.to_csv(bg, index=False)
    bg.seek(0)
    return bg

def test_comprehensive_upload_flow():
    # 1. Create Synthetic "Real" Data (Not generic dummies)
    enrolment_data = {
        'date': ['01-01-2025']*4,
        'state': ['S1', 'S1', 'S2', 'S2'],
        'district': ['D1', 'D2', 'D3', 'D4'],
        'pincode': [1, 2, 3, 4],
        'age_0_5': [10, 10, 10, 10], 
        'age_5_17': [1000, 2000, 1500, 5000],  # The Stock
        'age_18_greater': [100, 100, 100, 100]
    }
    
    biometric_data = {
        'date': ['01-01-2025']*4,
        'state': ['S1', 'S1', 'S2', 'S2'],
        'district': ['D1', 'D2', 'D3', 'D4'],
        'pincode': [1, 2, 3, 4],
        'bio_age_5_17': [200, 1800, 1500, 100], # The Flow (Updates)
        'bio_age_17_': [10, 10, 10, 10]
    }
    
    # Logic Expectations:
    # D1: 1000 - 200 = 800 Pending (80% Gap) -> CRITICAL
    # D2: 2000 - 1800 = 200 Pending (10% Gap) -> SAFE
    # D3: 1500 - 1500 = 0 Pending (0% Gap) -> SAFE
    # D4: 5000 - 100 = 4900 Pending (98% Gap) -> CRITICAL (Anomaly likely due to magnitude)

    files = {
        'enrolment_file': ('enrol.csv', create_csv_content(enrolment_data), 'text/csv'),
        'biometric_file': ('bio.csv', create_csv_content(biometric_data), 'text/csv')
    }

    response = client.post("/upload", files=files)
    
    assert response.status_code == 200
    json_data = response.json()
    
    districts = json_data['districts']
    
    # Assert D1
    d1 = next(d for d in districts if d['district'] == 'D1')
    assert d1['status'] == 'CRITICAL'
    assert d1['gap_percentage'] == 80.0
    assert "High Deficit" in d1['ai_reasoning']

    # Assert D2
    d2 = next(d for d in districts if d['district'] == 'D2')
    assert d2['status'] == 'SAFE'
    assert d2['gap_percentage'] == 10.0

    # Assert Summary
    summary = json_data['summary']
    assert summary['processed_districts'] == 4
    assert summary['critical_districts_count'] == 2 # D1 and D4

def test_messy_input_normalization():
    # Test Data Hygiene: Mixed Case, Numeric Districts, Spacing
    enrolment_data = {
        'state': ['west bengal', 'WEST BENGAL', '  Odisha '],
        'district': ['kolkata', 'Kolkata', '100000'], # Duplicate district (diff case), and invalid numeric
        'age_5_17': [1000, 1000, 500] 
    }
    biometric_data = {
        'state': ['West Bengal', 'West Bengal', 'Odisha'],
        'district': ['Kolkata', 'Kolkata', '100000'],
        'bio_age_5_17': [500, 500, 100]
    }
    
    # Expected Behavior:
    # 1. '100000' should be filtered out.
    # 2. 'west bengal'/'WEST BENGAL' should normalize to 'West Bengal'.
    # 3. 'kolkata'/'Kolkata' should normalize and aggregate to one entry 'Kolkata'.
    
    files = {
        'enrolment_file': ('enrol_messy.csv', create_csv_content(enrolment_data), 'text/csv'),
        'biometric_file': ('bio_messy.csv', create_csv_content(biometric_data), 'text/csv')
    }
    
    response = client.post("/upload", files=files)
    assert response.status_code == 200
    data = response.json()
    
    districts = data['districts']
    
    # Check invalid filtered out
    invalid_dist = next((d for d in districts if d['district'] == '100000'), None)
    assert invalid_dist is None, "Numeric district '100000' should be filtered out"
    
    # Check Normalization & Aggregation
    kolkata = next(d for d in districts if d['district'] == 'Kolkata')
    assert kolkata['state'] == 'West Bengal' # Title Case
    # Total age_5_17 should be 2000 (1000+1000)
    assert kolkata['expected_updates'] == 2000 

