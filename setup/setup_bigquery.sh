#!/bin/bash

PROJECT_ID=$(gcloud config get-value project)
DATASET_NAME="za"
LOCATION="asia-northeast1"

# Generate bucket name if not provided
if [ -z "$1" ]; then
    BUCKET_NAME="gs://za-$PROJECT_ID"
    echo "No bucket provided. Using default: $BUCKET_NAME"
else
    BUCKET_NAME=$1
fi

echo "----------------------------------------------------------------"
echo "Climate TRACE Demo Setup"
echo "Project: $PROJECT_ID"
echo "Dataset: $DATASET_NAME"
echo "Bucket:  $BUCKET_NAME"
echo "----------------------------------------------------------------"

# 1. Create Bucket if it doesn't exist
echo "[1/7] Checking bucket $BUCKET_NAME..."
if gcloud storage buckets describe $BUCKET_NAME >/dev/null 2>&1; then
    echo "      Bucket already exists."
else
    echo "      Creating bucket $BUCKET_NAME..."
    gcloud storage buckets create $BUCKET_NAME --location=$LOCATION
fi

# 2. Upload Data
echo "[2/7] Uploading data to $BUCKET_NAME..."
gcloud storage cp data/*.csv $BUCKET_NAME

# 3. Create Dataset
echo "[3/7] Creating Dataset '$DATASET_NAME'..."
if bq show "$PROJECT_ID:$DATASET_NAME" >/dev/null 2>&1; then
    echo "      Dataset already exists. Skipping creation."
else    
    bq mk --location=$LOCATION --dataset \
        "$PROJECT_ID:$DATASET_NAME"
    echo "      Dataset created."
fi

# 4. Create Sources Table
echo "[4/7] Setting up Table: sources..."
bq query --use_legacy_sql=false \
"CREATE OR REPLACE TABLE \`$PROJECT_ID.$DATASET_NAME.sources\` (
    id STRING OPTIONS(description='Unique ID of the asset'),
    name STRING OPTIONS(description='Facility name'),
    sector STRING OPTIONS(description='Major sector, e.g., power, manufacturing'),
    subsector STRING OPTIONS(description='Sub-sector category'),
    country STRING OPTIONS(description='ISO Country Code (JPN)'),
    assetType STRING OPTIONS(description='Specific type of asset (coal, steel plant)'),
    sourceType STRING OPTIONS(description='Type of data source (point-source)'),
    longitude FLOAT64 OPTIONS(description='Longitude coordinate'),
    latitude FLOAT64 OPTIONS(description='Latitude coordinate'),
    srid INT64 OPTIONS(description='Spatial reference system ID'),
    gas STRING OPTIONS(description='Greenhouse gas type (co2e_100yr)'),
    emissionsQuantity FLOAT64 OPTIONS(description='Emissions quantity'),
    emissionsFactor FLOAT64 OPTIONS(description='Calculated emissions factor'),
    emissionsFactorUnits STRING OPTIONS(description='Units of emissions factor'),
    activity FLOAT64 OPTIONS(description='Measured activity level'),
    activityUnits STRING OPTIONS(description='Units of activity'),
    capacity FLOAT64 OPTIONS(description='Max capacity of the facility'),
    capacityUnits STRING OPTIONS(description='Units of capacity'),
    capacityFactor FLOAT64 OPTIONS(description='Capacity utilization factor'),
    year INT64 OPTIONS(description='Data year')
)
OPTIONS(
    description='Individual point-source emission data from Climate TRACE.'
);"

bq load --source_format=CSV --skip_leading_rows=1 --replace \
    "$PROJECT_ID:$DATASET_NAME.sources" "$BUCKET_NAME/sources.csv"

# 5. Create Countries Table
echo "[5/7] Setting up Table: countries..."
bq query --use_legacy_sql=false \
"CREATE OR REPLACE TABLE \`$PROJECT_ID.$DATASET_NAME.countries\` (
    rank INT64 OPTIONS(description='Global emission rank'),
    country_code STRING OPTIONS(description='ISO 3-letter country code'),
    name STRING OPTIONS(description='Country name'),
    gas STRING OPTIONS(description='Greenhouse gas type'),
    emissionsQuantity FLOAT64 OPTIONS(description='Total annual emissions'),
    emissionsPerCapita FLOAT64 OPTIONS(description='Emissions per capita'),
    percentage FLOAT64 OPTIONS(description='Percentage of global total'),
    emissionsPercentChange FLOAT64 OPTIONS(description='Year-over-year percentage change')
)
OPTIONS(
    description='National level emission rankings and summary stats.'
);"

bq load --source_format=CSV --skip_leading_rows=1 --replace \
    "$PROJECT_ID:$DATASET_NAME.countries" "$BUCKET_NAME/countries.csv"

# 6. Create Admins Table
echo "[6/7] Setting up Table: admins..."
bq query --use_legacy_sql=false \
"CREATE OR REPLACE TABLE \`$PROJECT_ID.$DATASET_NAME.admins\` (
    id STRING OPTIONS(description='GADM ID'),
    name STRING OPTIONS(description='Administrative area name'),
    full_name STRING OPTIONS(description='Full name with country code'),
    level INT64 OPTIONS(description='Hierarchy level (0=Country, 1=Prefecture, 2=City)'),
    level_0_id STRING,
    level_1_id STRING,
    level_2_id STRING
)
OPTIONS(
    description='Administrative boundary master data.'
);"

bq load --source_format=CSV --skip_leading_rows=1 --replace \
    "$PROJECT_ID:$DATASET_NAME.admins" "$BUCKET_NAME/admins.csv"

# 7. Step 7 TODO
echo "[7/7] TODO"

echo "----------------------------------------------------------------"
echo "Setup Complete!"
echo "----------------------------------------------------------------"