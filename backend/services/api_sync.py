import requests
import pandas as pd
from typing import Dict, List, Optional
import os
from .processing import smart_merge

# Resource IDs from Data.Gov.in
RESOURCES = {
    "biometric": "65454dab-1517-40a3-ac1d-47d4dfe6891c",
    "demographic": "19eac040-0b94-49fa-b239-4f2fd8677d53",
    "enrolment": "ecd49b12-3084-4521-8f7e-ca8bf72069ba"
}

from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("DATA_GOV_API_KEY", "579b464db66ec23bdd000001cdd3946e44ce4aad7209ff7b23ac571b") # Fallback for demo
BASE_URL = "https://api.data.gov.in/resource/"

TOTAL_RECORDS_TO_FETCH = 2000  # Fetch enough data to show impact, but don't slow down demo

def fetch_data_gov_resource(resource_id: str, limit: int = 500) -> Optional[pd.DataFrame]:
    """
    Fetches data from a specific Data.Gov.in resource with pagination.
    Fetches up to TOTAL_RECORDS_TO_FETCH records.
    """
    all_records = []
    offset = 0
    
    print(f"📡 Connecting to Data.Gov.in Resource: {resource_id}...")
    
    while len(all_records) < TOTAL_RECORDS_TO_FETCH:
        params = {
            "api-key": API_KEY,
            "format": "json",
            "limit": limit,
            "offset": offset
        }
        url = f"{BASE_URL}{resource_id}"
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'records' in data and len(data['records']) > 0:
                records = data['records']
                all_records.extend(records)
                print(f"   🔹 Fetched {len(records)} records (Total: {len(all_records)})")
                
                if len(records) < limit:
                    break # No more data available
                
                offset += limit
            else:
                break # No records returned
                
        except Exception as e:
            print(f"❌ Error fetching resource {resource_id} at offset {offset}: {e}")
            break
            
    if all_records:
        df = pd.DataFrame(all_records)
        print(f"✅ Successfully loaded {len(df)} records from {resource_id}")
        return df
        
    return None

def sync_all_official_data(master_enrol: pd.DataFrame, master_bio: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """Syncs all official datasets and merges them into the master dataframes."""
    print("🚀 Starting sync with Data.Gov.in Official Portal...")
    
    # Enrolment
    new_enrol = fetch_data_gov_resource(RESOURCES["enrolment"])
    if new_enrol is not None:
        master_enrol = smart_merge(master_enrol, new_enrol)
        print(f"✅ Synced Enrolment: Added/Updated records.")

    # Biometric
    new_bio = fetch_data_gov_resource(RESOURCES["biometric"])
    if new_bio is not None:
        master_bio = smart_merge(master_bio, new_bio)
        print(f"✅ Synced Biometric: Added/Updated records.")

    return {
        "enrolment": master_enrol,
        "biometric": master_bio
    }
