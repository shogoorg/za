#!/bin/bash

PROJECT_ID=$(gcloud config get-value project)
DATASET_NAME="za"

LOCATION="US"

# Generate bucket name if not provided
if [ -z "$1" ]; then
    BUCKET_NAME="gs://za-data-$PROJECT_ID" 
    echo "No bucket provided. Using default: $BUCKET_NAME"
else
    BUCKET_NAME=$1
fi

echo "----------------------------------------------------------------"
echo "Setup"
echo "Project: $PROJECT_ID"
echo "Dataset: $DATASET_NAME"
echo "Bucket:  $BUCKET_NAME"
echo "----------------------------------------------------------------"

# Create Bucket if it doesn't exist
echo "Checking bucket $BUCKET_NAME..."
if gcloud storage buckets describe $BUCKET_NAME >/dev/null 2>&1; then
    echo "      Bucket already exists."
else
    echo "      Creating bucket $BUCKET_NAME..."
    gcloud storage buckets create $BUCKET_NAME --location=$LOCATION
fi

# Upload Data
echo "Uploading data to $BUCKET_NAME..."
gcloud storage cp data/*.csv $BUCKET_NAME

# Create Dataset
echo "Creating Dataset '$DATASET_NAME'..."
if bq show "$PROJECT_ID:$DATASET_NAME" >/dev/null 2>&1; then
    echo "      Dataset already exists. Skipping creation."
else    
    bq mk --location=$LOCATION --dataset \
        "$PROJECT_ID:$DATASET_NAME"
    echo "      Dataset created."
fi

# Create Sources Table
echo "Setting up Table: sources..."
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
    description='Individual point-source emission data'
);"

bq load --source_format=CSV --skip_leading_rows=1 --replace \
    "$PROJECT_ID:$DATASET_NAME.sources" "$BUCKET_NAME/sources.csv"

# Create Admins Table
echo "Setting up Table: admins..."
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

# Create Admins Table
echo "Setting up Table: admins..."
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

echo "----------------------------------------------------------------"
echo "Setup Complete!"
echo "----------------------------------------------------------------"