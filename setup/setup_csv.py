import requests
import pandas as pd
import time
import os

# --- Configuration ---
# ターゲットとなるID。APIの生データを取得するため、重なりのないように指定します。
TARGET_GADM_IDS = ["JPN.41_1"] 

BASE_URL = "https://api.climatetrace.org/v7/sources"
DATA_DIR = "data"
EMISSIONS_FILE = os.path.join(DATA_DIR, "sources.csv")
ADMIN_FILE = os.path.join(DATA_DIR, "admins.csv")

YEARS = [2021, 2022, 2023, 2024, 2025]
COLUMN_ORDER = [
    "id", "name", "sector", "subsector", "country", "assetType", "sourceType",
    "longitude", "latitude", "srid", "gas", "emissionsQuantity",
    "emissionsFactor", "emissionsFactorUnits", "activity", "activityUnits",
    "capacity", "capacityUnits", "capacityFactor", "year", "gadm_id"
]
HEADERS = {"User-Agent": "Mozilla/5.0"}

def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # --- Step 1: 処理対象の地域IDを重複なくリストアップする ---
    # これはAPIを叩く回数を正しく制御するためであり、データ内容の加工ではありません。
    unique_gids = set()
    for target in TARGET_GADM_IDS:
        admin_url = f"https://api.climatetrace.org/v7/admins/{target}/subdivisions"
        res = requests.get(admin_url, headers=HEADERS)
        if res.status_code == 200:
            for sub in res.json():
                unique_gids.add(sub['id'])
    
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
            # 取得条件は固定（ガス種：co2e_100yr）
            params = {"year": year, "gas": "co2e_100yr", "gadmId": gid, "limit": 100}
            
            try:
                resp = requests.get(BASE_URL, params=params, headers=HEADERS, timeout=30)
                if resp.status_code == 200:
                    data = resp.json()
                    if data:
                        # APIのレスポンスをそのままDataFrameに変換
                        df = pd.json_normalize(data)
                        df = df.rename(columns={
                            "centroid.longitude": "longitude", 
                            "centroid.latitude": "latitude", 
                            "centroid.srid": "srid"
                        })
                        df = df.assign(gadm_id=gid)
                        
                        # 指定されたカラム順に整理（加工はせず、並び替えのみ）
                        output_df = df.reindex(columns=COLUMN_ORDER)
                        
                        # ファイルに書き込み
                        mode = 'w' if first_write else 'a'
                        header = first_write
                        output_df.to_csv(EMISSIONS_FILE, index=False, mode=mode, header=header, encoding='utf-8')
                        first_write = False
                
                time.sleep(0.5) # APIへのマナーとして待機
            except Exception as e:
                print(f"      [Error] {gid}: {e}")

    print(f"\n======== Process Complete. Raw data saved to {EMISSIONS_FILE} ========")

if __name__ == "__main__":
    main()