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
python3 setup/setup_csv.py
```

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

## 5. Deployment Guide

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

### 6. Chat with the Agent (Sample Narrative: Emission Strategy)

Follow this sequence to see how the agent moves from national statistics to local action:

1. **Spotting the Issue:**
   "Show me the top 3 emission sources in Japan for 2024. I want to identify where the most urgent intervention is needed."
   (最も対策が必要な場所を特定するため、日本の排出量ワースト3を教えて。)

2. **Understanding the Context:**
   "For those top 3, what is the industry mix? Are they mostly 'Coal' power plants or 'BF/BOF' manufacturing? I need to know the primary driver."
   (ワースト3の産業構成は？石炭火力ですか、それとも製鉄所ですか？主な原因を知りたいです。)

3. **Setting the Benchmark:**
   "What is the maximum 'emissionsQuantity' for a single facility in Japan? I want to see how far the top facility is from the national average."
   (日本国内の単一施設の最大排出量は？トップの施設が全国平均からどれだけ突出しているか確認したい。)

4. **Predicting Impact (Forecasting):**
   "Take the #1 emitting facility. Based on its 'activity' data, if we reduce its operations by 15% next year, what is the projected emission amount for 2025?"
   (排出1位の施設について、もし来年その活動量を15%削減した場合、2025年の予測排出量はいくらになりますか？)

5. **Local Impact Verification:**
   "Lastly, find the nearest 'City Hall' or residential center to this facility. Provide a map link to assess how its emissions might affect the local community."
   (最後に、その施設に最も近い市役所や居住エリアを探して、地図リンクでその距離感を確認させて。)

### 7. Cleanup
```bash
dos2unix cleanup/cleanup_env.sh
chmod +x cleanup/cleanup_env.sh
./cleanup/cleanup_env.sh
```

### Data Logic & Narratives

The data in this repository is structured to support specific analytical narratives and successful agent reasoning chains using two primary tables.

| Table | Demo Purpose | Narrative Logic |
| :--- | :--- | :--- |
| **admins** | **Regional Scoping** | Acts as the administrative master data for Japanese Prefectures (Level 1). It allows the Agent to map regional names (e.g., "Aichi", "Hiroshima") to administrative IDs, enabling it to scope national emission data down to specific regional hotspots. |
| **sources** | **Asset Analysis & Forecasting** | Contains granular point-source data for 2024. By analyzing `emissionsQuantity` and specific `assetType` (such as 'Coal' for power or 'BF/BOF' for steel), the Agent identifies top polluters. Using the relationship between `activity` and `emissionsFactor`, it can simulate "what-if" scenarios and forecast 2025 emission reductions. |

