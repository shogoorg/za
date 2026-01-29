import requests
import pandas as pd
import time
import os
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# --- Configuration ---
# List of GADM IDs to process sequentially.
TARGET_GADM_IDS = ["JPN", "JPN.41_1"] 

BASE_URL = "https://api.climatetrace.org/v7/sources"

DATA_DIR = "data"
EMISSIONS_FILE = os.path.join(DATA_DIR, "sources.csv")
ADMIN_FILE = os.path.join(DATA_DIR, "admins.csv") # Unified Admin File

YEARS = [2024, 2025]
LIMIT = 100
MAX_RECORDS = 100

# Strict column order
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


def fetch_and_save_region(gadm_id, filepath, is_initial_write):
    """Fetch emission data for a specific GADM ID and append to sources.csv"""
    data_written = False
    
    file_exists = os.path.exists(filepath)
    
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
                df = df.assign(gadm_id=gadm_id)
                df = df.reindex(columns=COLUMN_ORDER)

                # sources.csv logic: 'w' only if it's the absolute first region and file doesn't exist
                mode = 'w' if is_initial_write and not data_written and not file_exists else 'a'
                header_write = is_initial_write and not data_written and not file_exists
                
                df.to_csv(filepath, index=False, mode=mode, header=header_write, encoding='utf-8')
                
                data_written = True
                if len(data) < LIMIT: break
                offset += LIMIT
                time.sleep(1.2)
            except Exception as e:
                print(f"      [Warning] Skipping batch for {gadm_id}: {e}")
                break
    return data_written


def append_admin_data(df_admin: pd.DataFrame, filepath: str, is_first_global_run: bool):
    """Appends administrative data to the unified admin file."""
    
    file_exists = os.path.exists(filepath)
    
    # Write header only if this is the very first target ID being processed AND the file doesn't exist yet.
    header_write = is_first_global_run and not file_exists
    mode = 'a'
    
    # We explicitly define columns for the admin file just in case the API structure changes.
    admin_cols = ["id", "name", "full_name", "level", "level_0_id", "level_1_id", "level_2_id"]
    
    # Reindex columns to ensure order and fill missing if necessary
    df_admin = df_admin.reindex(columns=admin_cols)
    
    df_admin.to_csv(filepath, index=False, mode=mode, header=header_write, encoding='utf-8')


def process_gadm_id(target_id: str, is_first_global_run: bool):
    """Fetches subdivisions for a single target ID and processes them."""
    
    admin_url = f"https://api.climatetrace.org/v7/admins/{target_id}/subdivisions"
    
    print(f"--- Starting Extraction for Target: {target_id} ---")

    # --- Step 1: Fetch Subdivision List ---
    print(f">>> Step 1: Fetching subdivisions from {admin_url}")
    gadm_list = []

    try:
        admin_res = session.get(admin_url, headers=HEADERS, timeout=30)
        if admin_res.status_code == 200:
            admin_data = admin_res.json()
            if not admin_data:
                print(f"No subdivisions found for {target_id}. Skipping.")
                return
            
            df_admin = pd.DataFrame(admin_data)
            
            # ★★★ Append data to the unified admins.csv ★★★
            append_admin_data(df_admin, ADMIN_FILE, is_first_global_run)
            print(f"   Admin data appended to {ADMIN_FILE}.")

            gadm_list = df_admin["id"].tolist()
            print(f"   Successfully retrieved {len(gadm_list)} sub-regions.")
        else:
            print(f"API Error for {target_id}: {admin_res.status_code}")
            return
    except Exception as e:
        print(f"Critical Error during subdivision fetch for {target_id}: {e}")
        return

    # --- Step 2: Process Sub-regions Sequentially ---
    print(f"\n>>> Step 2: Processing {len(gadm_list)} regions...")
    for index, gid in enumerate(gadm_list):
        # Header write flag is only True if this is the first region of the very first TARGET_GADM_IDS entry.
        write_header_flag = is_first_global_run and (index == 0)
        
        fetch_and_save_region(gid, EMISSIONS_FILE, is_initial_write=write_header_flag)
        time.sleep(0.5)

    print(f"--- Extraction for {target_id} complete. ---")


def main():
    # Setup directory
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Check if the emission file exists (to control header writing for sources.csv)
    emission_file_was_created = not os.path.exists(EMISSIONS_FILE)

    # Process all TARGET_GADM_IDS sequentially
    for i, target_id in enumerate(TARGET_GADM_IDS):
        
        # is_first_global_run is True ONLY for the very first item in the list AND if the file didn't exist before.
        is_first_global_run = (i == 0) and emission_file_was_created 

        process_gadm_id(target_id, is_first_global_run)
        
    print(f"\n======== Global Process Complete. Total Targets Processed: {len(TARGET_GADM_IDS)} ========")
    print(f"Final data saved to: {EMISSIONS_FILE} and {ADMIN_FILE}")


if __name__ == "__main__":
    main()