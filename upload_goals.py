import pandas as pd
import requests
import json

# Configuration
CSV_FILE = "main.goals.csv"
ENDPOINT_URL = "http://localhost:8000/goals/" # Adjust port if necessary

def push_goals_from_csv():
    try:
        # 1. Load the CSV
        df = pd.read_csv(CSV_FILE)
        
        print(f"Reading {len(df)} records from {CSV_FILE}...")

        success_count = 0
        error_count = 0

        # 2. Iterate through rows
        for index, row in df.iterrows():
            user_id = str(row['userId'])
            goal_text = str(row['goals'])

            # The Goal model expects a list of strings: List[str]
            # We wrap the text in a list.
            payload = {
                "userId": user_id,
                "goals": [goal_text] 
            }

            # 3. Push to endpoint
            response = requests.post(ENDPOINT_URL, json=payload)

            if response.status_code == 201:
                print(f"✅ Success: Processed User {user_id}")
                success_count += 1
            else:
                print(f"❌ Failed: User {user_id} - Status: {response.status_code}")
                print(f"   Response: {response.text}")
                error_count += 1

        print("\n--- Summary ---")
        print(f"Total processed: {success_count}")
        print(f"Total failed: {error_count}")

    except FileNotFoundError:
        print(f"Error: File '{CSV_FILE}' not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    push_goals_from_csv()