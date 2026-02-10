#!/bin/bash

# ==========================================
# MCP ZA Project - Complete Cleanup Script
# ==========================================

# 1. Configuration & Project Detection
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
DATASET_NAME="za"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# --- 修正箇所: 削除対象の相対パスを配列で定義 ---
ENV_PATHS=(
    "../adk_agent/climate_plans/.env"
    "../adk_agent/climate_sources/.env"
    "../adk_agent/market/.env"
)

if [ -z "$PROJECT_ID" ]; then
    echo "Error: Could not determine Google Cloud Project ID."
    exit 1
fi

# Determine bucket name (Updated for ZA)
if [ -z "$1" ]; then
    BUCKET_NAME="gs://za-data-$PROJECT_ID"
else
    BUCKET_NAME=$1
fi

echo "----------------------------------------------------------------"
echo "CLEANUP TARGETS"
echo "----------------------------------------------------------------"
echo "Project:   $PROJECT_ID"
echo "Dataset:   $DATASET_NAME"
echo "Bucket:    $BUCKET_NAME"
echo "Local Env: $ENV_PATHS"
echo "API Keys:  Keys named 'za-key-*'"
echo "----------------------------------------------------------------"
echo "WARNING: This will permanently delete the dataset, bucket, and API keys."
read -p "Are you sure you want to proceed? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cleanup cancelled."
    exit 1
fi
echo "----------------------------------------------------------------"

# ------------------------------------------
# Phase 1: BigQuery & Storage
# ------------------------------------------
echo "[1/5] Removing BigQuery Dataset..."
if bq show "$PROJECT_ID:$DATASET_NAME" >/dev/null 2>&1; then
    bq rm -r -f --dataset "$PROJECT_ID:$DATASET_NAME"
    echo "      Dataset '$DATASET_NAME' removed."
else
    echo "      Dataset not found. Skipping."
fi

echo "[2/5] Removing Storage Bucket..."
if gcloud storage buckets describe "$BUCKET_NAME" >/dev/null 2>&1; then
    gcloud storage rm --recursive "$BUCKET_NAME"
    echo "      Bucket '$BUCKET_NAME' deleted."
else
    echo "      Bucket not found. Skipping."
fi

# ------------------------------------------
# Phase 2: API Keys
# ------------------------------------------
echo "[3/5] Cleaning up API Keys..."
# Filter updated to 'za-key-*'
KEYS_TO_DELETE=$(gcloud alpha services api-keys list \
    --filter="displayName:za-key-*" \
    --format="value(name)" 2>/dev/null)

if [ -z "$KEYS_TO_DELETE" ]; then
    echo "      No matching API keys found."
else
    for KEY_NAME in $KEYS_TO_DELETE; do
        echo "      Deleting API Key: $KEY_NAME"
        gcloud alpha services api-keys delete "$KEY_NAME" --quiet
    done
    echo "      Keys deleted."
fi

# ------------------------------------------
# Phase 3: Local Config
# ------------------------------------------
echo "[4/5] Removing local configuration..."

for REL_PATH in "${ENV_PATHS[@]}"; do
    TARGET_FILE="$SCRIPT_DIR/$REL_PATH"
    if [ -f "$TARGET_FILE" ]; then
        rm "$TARGET_FILE"
        echo "      Deleted $TARGET_FILE"
    else
        echo "      File not found: $REL_PATH. Skipping."
    fi
done

# ------------------------------------------
# Phase 4: Disable APIs (Optional)
# ------------------------------------------
echo "[5/5] Checking Enabled APIs..."
echo "----------------------------------------------------------------"
read -p "Do you want to disable the enabled APIs? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Disabling APIs..."
    gcloud services disable mapstools.googleapis.com --project=$PROJECT_ID --force
    gcloud services disable bigquery.googleapis.com --project=$PROJECT_ID --force
    gcloud services disable apikeys.googleapis.com --project=$PROJECT_ID --force
    echo "APIs disabled."
else
    echo "Skipping API disablement."
fi

echo "----------------------------------------------------------------"
echo "Cleanup Complete!"
echo "----------------------------------------------------------------"