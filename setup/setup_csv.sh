#!/bin/bash

mkdir -p data

EMISSIONS_FILE="data/sources.csv"
ADMIN_FILE="data/admins.csv"

YEAR=2024
LIMIT=100
MAX_RECORDS=1000

# --- Sources ---
echo "Fetching emission sources  - Max $MAX_RECORDS records..."
OFFSET=0
FIRST_FETCH=true

while [ $OFFSET -lt $MAX_RECORDS ]; do
    echo "   Fetching Offset: $OFFSET ..."
    RESPONSE=$(curl -s "https://api.climatetrace.org/v7/sources?year=$YEAR&gas=co2e_100yr&gadmId=JPN&limit=$LIMIT&offset=$OFFSET")

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

# --- Administrative Areas ---
echo "Fetching administrative areas..."
curl -s 'https://api.climatetrace.org/v7/admins?name=JPN&level=0&limit=100&offset=0' \
| jq -r '
  ["id", "name", "full_name", "level", "level_0_id", "level_1_id", "level_2_id"], 
  (.[] | [.id, .name, .full_name, .level, .level_0_id, .level_1_id, .level_2_id]) 
  | @csv' \
> "$ADMIN_FILE"

echo "------------------------------------------"
if [ -s "$EMISSIONS_FILE" ] && [ -s "$ADMIN_FILE" ]; then
    echo "Success! Three files are ready in ./data/"
    echo "$EMISSIONS_FILE (Lines: $(wc -l < "$EMISSIONS_FILE"))"
    echo "$ADMIN_FILE"
else
    echo "Error: Data retrieval failed."
fi