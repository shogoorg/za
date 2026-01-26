import requests
import pandas as pd
import time
import os

# --- Configuration ---
BASE_URL = "https://api.climatetrace.org/v7/sources"
ADMIN_URL = "https://api.climatetrace.org/v7/admins/JPN/subdivisions"
DATA_DIR = "data"
EMISSIONS_FILE = os.path.join(DATA_DIR, "sources.csv")
ADMIN_FILE = os.path.join(DATA_DIR, "admins.csv")

YEARS = [2024, 2025]
LIMIT = 100
MAX_RECORDS = 1000

# Strict column order as specified
COLUMN_ORDER = [
    "id", "name", "sector", "subsector", "country", "assetType", "sourceType",
    "longitude", "latitude", "srid", "gas", "emissionsQuantity",
    "emissionsFactor", "emissionsFactorUnits", "activity", "activityUnits",
    "capacity", "capacityUnits", "capacityFactor", "year"
]

# HTTP headers to prevent blocking
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
}

def fetch_emission_data():
    all_results = []

    for year in YEARS:
        print(f"--- Fetching Year: {year} ---")
        offset = 0
        
        while offset < MAX_RECORDS:
            params = {
                "year": year,
                "gas": "co2e_100yr",
                "gadmId": "JPN",
                "limit": LIMIT,
                "offset": offset
            }
            
            try:
                response = requests.get(BASE_URL, params=params, headers=HEADERS, timeout=30)
                
                if response.status_code != 200:
                    print(f"   Error: API returned status {response.status_code}")
                    break
                
                data = response.json()
                if not data or len(data) == 0:
                    print(f"   No more data found for {year}.")
                    break
                
                # 1. Convert JSON to DataFrame and flatten nested 'centroid'
                df_batch = pd.json_normalize(data)
                
                # 2. Map the flattened centroid names to your specified names
                rename_map = {
                    "centroid.longitude": "longitude",
                    "centroid.latitude": "latitude",
                    "centroid.srid": "srid"
                }
                df_batch = df_batch.rename(columns=rename_map)

                # 3. Ensure all specified columns exist and follow the exact order
                # Missing columns will be filled with NaN (None)
                df_batch = df_batch.reindex(columns=COLUMN_ORDER)
                
                all_results.append(df_batch)
                print(f"   Offset {offset}: Retrieved {len(df_batch)} records.")
                
                offset += LIMIT
                time.sleep(1.5) # Sleep to avoid rate limiting
                
            except Exception as e:
                print(f"   Exception during fetch: {e}")
                break
        
        time.sleep(2) # Interval between years

    if all_results:
        # Combine all batches into one DataFrame
        return pd.concat(all_results, ignore_index=True)
    return pd.DataFrame()

def main():
    # Create directory if it doesn't exist
    os.makedirs(DATA_DIR, exist_ok=True)

    # --- Part 1: Sources ---
    df_sources = fetch_emission_data()
    
    if not df_sources.empty:
        # Save to CSV using the exact specified columns
        df_sources.to_csv(EMISSIONS_FILE, index=False, columns=COLUMN_ORDER, encoding='utf-8')
        print(f"\nSuccess! {EMISSIONS_FILE} saved with {len(df_sources)} records.")
    else:
        print("\nError: No emission data found.")

    # --- Part 2: Administrative Areas ---
    print("\n--- Fetching Administrative Areas ---")
    try:
        admin_response = requests.get(ADMIN_URL, headers=HEADERS, timeout=30)
        if admin_response.status_code == 200:
            admin_data = admin_response.json()
            df_admin = pd.DataFrame(admin_data)
            
            # Specify column order for admins.csv as well
            admin_cols = ["id", "name", "full_name", "level", "level_0_id", "level_1_id", "level_2_id"]
            df_admin = df_admin.reindex(columns=admin_cols)
            
            df_admin.to_csv(ADMIN_FILE, index=False, encoding='utf-8')
            print(f"Success! {ADMIN_FILE} saved.")
    except Exception as e:
        print(f"Error fetching admin areas: {e}")

if __name__ == "__main__":
    main()