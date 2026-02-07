import requests
import pandas as pd
import time
import os

# --- Configuration ---
TARGET_GADM_IDS = ["JPN"] 

BASE_URL = "https://api.climatetrace.org/v7/sources"
DATA_DIR = "data"
EMISSIONS_FILE = os.path.join(DATA_DIR, "sources.csv")
ADMIN_FILE = os.path.join(DATA_DIR, "admins.csv")

YEARS = [2021, 2022, 2023, 2024, 2025]
# 保存したいカラムを定義
ADMIN_COLS = ["id", "name", "full_name", "level", "level_0_id", "level_1_id", "level_2_id"]
COLUMN_ORDER = [
    "id", "name", "sector", "subsector", "country", "assetType", "sourceType",
    "longitude", "latitude", "srid", "gas", "emissionsQuantity",
    "emissionsFactor", "emissionsFactorUnits", "activity", "activityUnits",
    "capacity", "capacityUnits", "capacityFactor", "year", "gadm_id"
]
HEADERS = {"User-Agent": "Mozilla/5.0"}

def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # --- Step 1 & 2: 処理対象の地域IDをリストアップし、ADMIN_FILEを保存する ---
    if os.path.exists(ADMIN_FILE):
        os.remove(ADMIN_FILE)
        print(f">>> Removed old {ADMIN_FILE}")
            
    unique_gids = set()
    all_admins = []  # 追加：全行政データを格納するリスト

    for target in TARGET_GADM_IDS:
        admin_url = f"https://api.climatetrace.org/v7/admins/{target}/subdivisions"
        res = requests.get(admin_url, headers=HEADERS)
        if res.status_code == 200:
            data = res.json()
            all_admins.extend(data) # 追加：取得したリストを結合
            for sub in data:
                unique_gids.add(sub['id'])
    
    # 追加：収集した行政データをCSVとして保存
    if all_admins:
        pd.DataFrame(all_admins).reindex(columns=ADMIN_COLS).to_csv(ADMIN_FILE, index=False, encoding='utf-8')
        print(f">>> Saved administrative data to {ADMIN_FILE}")

    print(f">>> Target regions identified: {len(unique_gids)}")

    # --- Step 2: 既存ファイルを削除してクリーンな状態で開始する ---
    if os.path.exists(EMISSIONS_FILE):
        os.remove(EMISSIONS_FILE)
        print(f">>> Removed old {EMISSIONS_FILE}")

    # --- Step 3: APIからデータを取得し、そのまま保存する ---
    first_write = True

    for gid in sorted(list(unique_gids)):
        for year in YEARS:
            print(f"    - Fetching {gid} for {year}...")
            params = {"year": year, "gas": "co2e_100yr", "gadmId": gid, "limit": 100}
            
            try:
                resp = requests.get(BASE_URL, params=params, headers=HEADERS, timeout=30)
                if resp.status_code == 200:
                    data = resp.json()
                    if data:
                        df = pd.json_normalize(data)
                        df = df.rename(columns={
                            "centroid.longitude": "longitude", 
                            "centroid.latitude": "latitude", 
                            "centroid.srid": "srid"
                        })
                        df = df.assign(gadm_id=gid)
                        
                        output_df = df.reindex(columns=COLUMN_ORDER)
                        
                        mode = 'w' if first_write else 'a'
                        header = first_write
                        output_df.to_csv(EMISSIONS_FILE, index=False, mode=mode, header=header, encoding='utf-8')
                        first_write = False
                
                time.sleep(0.5)
            except Exception as e:
                print(f"      [Error] {gid}: {e}")

    print(f"\n======== Process Complete. Raw data saved to {EMISSIONS_FILE} ========")

if __name__ == "__main__":
    main()