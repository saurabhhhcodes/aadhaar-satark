import pandas as pd
from services.processing import process_data
import io

def verify_data_merging():
    # Simulate the User's specific concern: Multiple case variations of the same entity
    # "Don't remove duplicacy... merge everything"
    
    # 1. Input Data: Split across 3 variations
    enrol_data = [
        {'state': 'West Bengal', 'district': 'Kolkata', 'age_5_17': 100},
        {'state': 'WEST BENGAL', 'district': 'Kolkata', 'age_5_17': 200},
        {'state': 'west bengal', 'district': 'Kolkata', 'age_5_17': 300},
    ]
    
    bio_data = [
        {'state': 'West Bengal', 'district': 'Kolkata', 'bio_age_5_17': 50},
        {'state': 'WEST BENGAL', 'district': 'Kolkata', 'bio_age_5_17': 50},
        {'state': 'west bengal', 'district': 'Kolkata', 'bio_age_5_17': 50},
    ]
    
    # Expected Totals
    total_enrolment_input = 100 + 200 + 300 # 600
    total_biometric_input = 50 + 50 + 50    # 150
    
    print(f"--- INPUT DATA ---")
    print(f"Total Enrolment Input: {total_enrolment_input}")
    print(f"Variations provided: 'West Bengal', 'WEST BENGAL', 'west bengal'")
    
    # Create DataFrames
    df_enrol = pd.DataFrame(enrol_data)
    df_bio = pd.DataFrame(bio_data)
    
    # 2. Process using the actual backend logic
    print(f"\n--- PROCESSING ---")
    result = process_data(df_enrol, df_bio)
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
        return

    # 3. Verify Output
    districts = result['districts']
    
    # Should be exactly ONE merged entry for "West Bengal" -> "Kolkata"
    kolkata_entries = [d for d in districts if d['district'] == 'Kolkata']
    
    print(f"\n--- OUTPUT RESULTS ---")
    print(f"Number of 'Kolkata' entries after merge: {len(kolkata_entries)}")
    
    if len(kolkata_entries) == 1:
        entry = kolkata_entries[0]
        print(f"Merged State Name: '{entry['state']}'")
        print(f"Merged Enrolment (Target): {entry['expected_updates']}")
        print(f"Merged Biometric (Actual): {entry['actual_updates']}")
        
        # Validation
        if entry['expected_updates'] == total_enrolment_input:
            print(f"✅ SUCCESS: Enrolment Data Preserved (600 == 600)")
        else:
            print(f"❌ FAILURE: Lost Enrolment Data ({entry['expected_updates']} != 600)")
            
        if entry['actual_updates'] == total_biometric_input:
            print(f"✅ SUCCESS: Biometric Data Preserved (150 == 150)")
        else:
            print(f"❌ FAILURE: Lost Biometric Data ({entry['actual_updates']} != 150)")
    else:
        print(f"❌ FAILURE: Duplicate entries found (Merging logic failed)")

if __name__ == "__main__":
    verify_data_merging()
