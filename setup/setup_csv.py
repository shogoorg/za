import requests
import pandas as pd
import time
import os
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# --- Configuration ---
# Set the parent GADM ID (Level 0 to get Level 1, or Level 1 to get Level 2)
TARGET_GADM_ID = "JPN" 

BASE_URL = "https://api.climatetrace.org/v7/sources"
# Dynamic URL based on the TARGET_GADM_ID
ADMIN_URL = f"https://api.climatetrace.org/v7/admins/{TARGET_GADM_ID}/subdivisions"

DATA_DIR = "data"
EMISSIONS_FILE = os.path.join(DATA_DIR, "sources.csv")
ADMIN_FILE = os.path.join(DATA_DIR, "admins.csv")

YEARS = [2024, 2025]
LIMIT = 100
MAX_RECORDS = 100

# Strict column order (No ingested_at)
COLUMN_ORDER = [
    "id", "name", "sector", "subsector", "country", "assetType", "sourceType",
    "longitude", "latitude", "srid", "gas", "emissionsQuantity",
    "emissionsFactor", "emissionsFactorUnits", "activity", "activityUnits",
    "capacity", "capacityUnits", "capacityFactor", "year", "gadm_id"
]

HEADERS = {"User-Agent": "Mozilla/5.0"}

# Session setup with retry strategy
session = requests.Session()
retries = Retry(total=5, backoff_factor=2, status_forcelist=[500, 502, 503, 504])
session.mount("https://", HTTPAdapter(max_retries=retries))

def fetch_and_save_region(gadm_id, filepath, is_start_of_file):
    """Fetch emission data for a specific GADM ID and append to CSV"""
    data_written = False
    for year in YEARS:
        print(f"   - Processing {gadm_id} for {year}...")
        offset = 0
        while offset < MAX_RECORDS:
            params = {"year": year, "gas": "co2e_100yr", "gadmId": gadm_id, "limit": LIMIT, "offset": offset}
            try:
                response = session.get(BASE_URL, params=params, headers=HEADERS, timeout=30)
                if response.status_code != 200: break
                data = response.json()
                if not data: break

                df = pd.json_normalize(data)
                df = df.rename(columns={
                    "centroid.longitude": "longitude", 
                    "centroid.latitude": "latitude", 
                    "centroid.srid": "srid"
                })
                df.insert(len(df.columns), "gadm_id", gadm_id)
                df = df.reindex(columns=COLUMN_ORDER)

                # Overwrite on the very first batch of the whole process, then append
                mode = 'w' if (is_start_of_file and not data_written) else 'a'
                header = (is_start_of_file and not data_written)
                df.to_csv(filepath, index=False, mode=mode, header=header, encoding='utf-8')
                
                data_written = True
                if len(data) < LIMIT: break
                offset += LIMIT
                time.sleep(1.2)
            except Exception as e:
                print(f"      [Warning] Skipping batch for {gadm_id}: {e}")
                break
    return data_written

def main():
    # Setup directory
    os.makedirs(DATA_DIR, exist_ok=True)
    print(f"--- Starting Extraction for Subdivisions of: {TARGET_GADM_ID} ---")

    # --- Step 1: Fetch Subdivision List ---
    # If TARGET_GADM_ID is Level 0, this gets Level 1. If Level 1, gets Level 2.
    print(f">>> Step 1: Fetching subdivisions from {ADMIN_URL}")
    gadm_list = []
    try:
        admin_res = session.get(ADMIN_URL, headers=HEADERS, timeout=30)
        if admin_res.status_code == 200:
            admin_data = admin_res.json()
            if not admin_data:
                print(f"No subdivisions found for {TARGET_GADM_ID}.")
                return
            
            df_admin = pd.DataFrame(admin_data)
            df_admin.to_csv(ADMIN_FILE, index=False)
            
            # Extract the list of sub-region IDs
            gadm_list = df_admin["id"].tolist()
            print(f"   Successfully retrieved {len(gadm_list)} sub-regions.")
        else:
            print(f"API Error: {admin_res.status_code}")
            return
    except Exception as e:
        print(f"Critical Error: Could not retrieve subdivision list: {e}")
        return

    # --- Step 2: Process Sub-regions Sequentially ---
    print(f"\n>>> Step 2: Processing {len(gadm_list)} regions...")
    for index, gid in enumerate(gadm_list):
        # The very first region in the list will trigger 'w' (overwrite) mode
        is_start = (index == 0)
        fetch_and_save_region(gid, EMISSIONS_FILE, is_start_of_file=is_start)
        time.sleep(0.5)

    print(f"\n--- Process Complete ---")
    print(f"Sub-regions processed: {len(gadm_list)}")
    print(f"Files saved in: {DATA_DIR}/")

if __name__ == "__main__":
    main()