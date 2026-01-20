from fastapi.testclient import TestClient
from main import app
import io

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "Aadhaar Satark Intelligence Engine"}

def test_upload_missing_files():
    response = client.post("/upload")
    assert response.status_code == 422 # Validation error

# Note: Testing valid upload requires sample CSV bytes.
# We can mock this in a more advanced test file.
def test_generate_report_pdf():
    # Test with dummy data
    data = {
        "state": "TestState",
        "district": "TestDistrict",
        "expected_updates": 1000,
        "actual_updates": 500,
        "pending_updates": 500,
        "gap_percentage": 50.0,
        "status": "CRITICAL"
    }
    response = client.post("/generate-report", json=data)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
