#!/bin/bash

# dataディレクトリの作成
mkdir -p data

# 出力ファイル設定
EMISSIONS_FILE="data/sources.csv"
COUNTRIES_FILE="data/countries.csv"
ADMIN_FILE="data/admins.csv"

# 1回あたりの取得数
LIMIT=100
# 最大取得数
MAX_RECORDS=1000

# --- 1. 排出源データ (Sources) の取得 (100件ずつ最大1000件) ---
echo "1. Fetching emission sources for Japan (Level 0) - Max $MAX_RECORDS records..."
OFFSET=0
FIRST_FETCH=true

while [ $OFFSET -lt $MAX_RECORDS ]; do
    echo "   Fetching Offset: $OFFSET ..."
    RESPONSE=$(curl -s "https://api.climatetrace.org/v7/sources?year=2024&gas=co2e_100yr&gadmId=JPN&limit=$LIMIT&offset=$OFFSET")

    if [ "$RESPONSE" == "[]" ] || [ -z "$RESPONSE" ] || [[ "$RESPONSE" == *"detail"* ]]; then
        break
    fi

    if [ "$FIRST_FETCH" = true ]; then
        echo "$RESPONSE" | jq -r '
        [
            "id", "name", "sector", "subsector", "country", "assetType", "sourceType", 
            "longitude", "latitude", "srid", "gas", "emissionsQuantity", 
            "emissionsFactor", "emissionsFactorUnits", "activity", "activityUnits", 
            "capacity", "capacityUnits", "capacityFactor", "year"
        ],
        (.[] | [
            .id, .name, .sector, .subsector, .country, .assetType, .sourceType,
            .centroid.longitude, .centroid.latitude, .centroid.srid, .gas, .emissionsQuantity,
            .emissionsFactor, .emissionsFactorUnits, .activity, .activityUnits,
            .capacity, .capacityUnits, .capacityFactor, .year
        ]) | @csv' > "$EMISSIONS_FILE"
        FIRST_FETCH=false
    else
        echo "$RESPONSE" | jq -r '
        (.[] | [
            .id, .name, .sector, .subsector, .country, .assetType, .sourceType,
            .centroid.longitude, .centroid.latitude, .centroid.srid, .gas, .emissionsQuantity,
            .emissionsFactor, .emissionsFactorUnits, .activity, .activityUnits,
            .capacity, .capacityUnits, .capacityFactor, .year
        ]) | @csv' >> "$EMISSIONS_FILE"
    fi

    OFFSET=$((OFFSET + LIMIT))
    
    sleep 0.5
done

# --- 2. 国別ランキングデータ (Countries Ranking) の取得 ---
echo "2. Fetching full country rankings for 2024..."
# .rankings 配列から全項目を抽出
curl -s 'https://api.climatetrace.org/v7/rankings/countries?gas=co2e_100yr&start=2024-01-01&end=2024-12-31' \
| jq -r '
  [
    "rank", "country_code", "name", "gas", "emissionsQuantity", 
    "emissionsPerCapita", "percentage", "emissionsPercentChange"
  ],
  (.rankings[] | [
    .rank, .country, .name, .gas, .emissionsQuantity, 
    .emissionsPerCapita, .percentage, .emissionsPercentChange
  ]) | @csv' \
> "$COUNTRIES_FILE"

# --- 3. 行政区画データ (Administrative Areas) の取得 ---
echo "3. Fetching administrative areas for Japan..."
curl -s 'https://api.climatetrace.org/v7/admins?name=JPN&level=0&limit=100&offset=0' \
| jq -r '
  ["id", "name", "full_name", "level", "level_0_id", "level_1_id", "level_2_id"], 
  (.[] | [.id, .name, .full_name, .level, .level_0_id, .level_1_id, .level_2_id]) 
  | @csv' \
> "$ADMIN_FILE"

# --- 結果の確認 ---
echo "------------------------------------------"
if [ -s "$EMISSIONS_FILE" ] && [ -s "$COUNTRIES_FILE" ] && [ -s "$ADMIN_FILE" ]; then
    echo "Success! Three files are ready in ./data/"
    echo "1. $EMISSIONS_FILE (Lines: $(wc -l < "$EMISSIONS_FILE"))"
    echo "2. $COUNTRIES_FILE"
    echo "3. $ADMIN_FILE"
else
    echo "Error: Data retrieval failed."
fi