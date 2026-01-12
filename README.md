# za

## Prerequisites

*   **Google Cloud Project** 
*   **Google Cloud Shell** 

## Deployment Guide

### 1. Clone the Repository
```bash
git clone https://github.com/shogoorg/za.git
cd za
```
### 2. Authenticate with Google Cloud

```bash
gcloud auth application-default login
gcloud config set project [YOUR-PROJECT-ID]
export PROJECT_ID=$(gcloud config get project)

```

### 3. Configure Environment

```bash
gcloud services enable \
  bigquery.googleapis.com \
  aiplatform.googleapis.com \
  apikeys.googleapis.com \
  mapstools.googleapis.com \
  cloudresourcemanager.googleapis.com

gcloud beta services mcp enable mapstools.googleapis.com --project=$PROJECT_ID
gcloud beta services mcp enable bigquery.googleapis.com --project=$PROJECT_ID
```

```bash
gcloud alpha services api-keys create \
    --display-name="za-key" \
    --api-target=service=mapstools.googleapis.com \
    --format="value(keyString)"
```

```bash
dos2unix setup/setup_env.sh
chmod +x setup/setup_env.sh
./setup/setup_env.sh
```

### 4. Provision BigQuery

```bash
dos2unix setup/setup_csv.sh
chmod +x setup/setup_csv.sh
./setup/setup_csv.sh
```

```bash
dos2unix setup/setup_bigquery.sh
chmod +x setup/setup_bigquery.sh
./setup/setup_bigquery.sh
```

### 5. Install ADK and Run Agent

```bash

# Create virtual environment
python3 -m venv .venv

# If the above fails, you may need to install python3-venv:
# apt update && apt install python3-venv

# Activate virtual environment
source .venv/bin/activate

pip install -r requirements.txt

# Install ADK
pip install google-adk

# Navigate to the app directory
cd adk_agent/

# Run the ADK web interface
adk web
```

### 6. Chat with the Agent


*   "日本でCO2排出量が最も多い施設トップ5を教えてください。セクター名も含めて。"
*   "日本の都道府県を教えてください。レベルIDを含めて。"


### 7. Cleanup
```bash
dos2unix cleanup/cleanup_env.sh
chmod +x cleanup/cleanup_env.sh
./cleanup/cleanup_env.sh
```

| Table | Demo Purpose | Narrative Logic |
| :--- | :--- | :--- |
| **`sources`** | Data for aggregated emissions totals and individual sources.||
| **`admins`** | Metadata for nations and their 1st and 2nd levels of subdivision (e.g. states and counties). Climate TRACE uses identifiers and boundary data from GADM, the Database of Global Administrative Areas. This API's endpoints use the gadmId parameter for a unique identifier of an administrative area.||
