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
## 5. Deployment Guide(AP2)
```bash
gcloud auth application-default login
gcloud config set project [YOUR-PROJECT-ID]
export PROJECT_ID=$(gcloud config get project)
```
```bash
gcloud services enable cloudresourcemanager.googleapis.com \
                       servicenetworking.googleapis.com \
                       run.googleapis.com \
                       cloudbuild.googleapis.com \
                       artifactregistry.googleapis.com \
                       aiplatform.googleapis.com \
                       compute.googleapis.com
```
```bash
echo "GOOGLE_GENAI_USE_VERTEXAI=TRUE" >> .env \
&& echo "GOOGLE_CLOUD_PROJECT=$PROJECT_ID" >> .env \
&& echo "GOOGLE_CLOUD_LOCATION=us-central1" >> .env
```
MCP Server
```bash
python3 server/server.py
python3 server/test_server.py
#http://localhost:8080
```
Client
```bash
cd adk_agent/
adk web
```
A2A Server 
```bash
python3 server/server.py
cd adk_agent/
python3 -m uvicorn currency_agent.agent:a2a_app --host localhost --port 10000
#http://localhost:10000
#http://localhost:10000/.well-known/agent.json
```
A2A Client
```bash
python3 currency_agent/test_client.py
```
### 6. Chat with the Agent (Sample Narrative: Emission Strategy)

*   **PURPOSE**: Develop a precise reduction strategy by benchmarking against the most efficient, *highly utilized* facility within a successful region and forecasting the potential impact if this efficiency is applied to the worst performer in the same region.

1.  **STEP: Location Selection (Identifying High-Demand Area/Top Reduction Prefecture)**
    *   **ENGLISH QUESTION**: "Identify the single prefecture (`admin_name`) in Japan that achieved the **largest total emission reduction** between 2024 and 2025."
    *   **日本語 (ユーザーの質問)**: 「2024年から2025年にかけて、**総排出削減量が最も大きかった**都道府県を日本全国から1つ特定してください。」

2.  **STEP: Success Model Definition (Benchmarking Best Efficiency & Utilization)**
    *   **ENGLISH QUESTION**: "For the prefecture identified in Step 1, find the single facility within that prefecture's **most successful `subsector`**. This facility must have a **2025 `capacityFactor` greater than 0.7 (highly utilized)** AND the lowest 2025 `emissionsFactor` within that subsector. This sets the 'Premium Efficiency Benchmark'."
    *   **日本語 (ユーザーの質問)**: 「ステップ1で特定した都道府県の中で、その都道府県の**最も削減に貢献したサブセクター**を特定してください。そのサブセクター内の施設のうち、**2025年の設備利用率（`capacityFactor`）が0.7を超え**、かつ`emissionsFactor`が最も低かった単一施設を見つけてください。これが『効率性目標ベンチマーク』です。」

3.  **STEP**: Identifying Target Facility (Worst Performer in the Same Sector/Region)
    *   **ENGLISH QUESTION**: "Now, focus on the **same `subsector`** identified in Step 2. Identify the single facility **within that same prefecture** (from Step 1) that had the **highest 2025 `emissionsQuantity`** for that subsector. This facility is the primary target for immediate best-practice transfer."
    *   **日本語 (ユーザーの質問)**: 「ステップ2で特定された**同じサブセクター**に焦点を当てます。そして、ステップ1で特定された**同じ都道府県内**で、2025年の`subsector`における**排出量が最も多い**単一施設を特定してください。これが即時ベストプラクティス展開のターゲット施設となります。」

4.  **STEP**: Impact Forecasting (Quantifying the Gain)
    *   **ENGLISH QUESTION**: "If the high-emitting target facility (Step 3) could achieve the **same `emissionsFactor` as the benchmark facility** (Step 2), what would be the **projected 2025 emission quantity** for that target facility? State the projected reduction amount."
    *   **日本語 (ユーザーの質問)**: 「ターゲット施設（ステップ3）が、ベンチマーク施設（ステップ2）と**同じ排出係数を達成できた**と仮定した場合、その施設の2025年の**予測排出量**はいくらになりますか？予測される削減量も提示してください。」

5.  **STEP**: Logistics Verification (Feasibility Check)
    *   **ENGLISH QUESTION**: "Provide a map link showing the location of the Top Reducing Prefecture center (Step 1) and the Target Facility (Step 3). Calculate the driving distance between them to assess the feasibility of direct technical consultation."
    *   **日本語 (ユーザーの質問)**: 「削減量トップの都道府県（ステップ1）と主要ターゲット施設（ステップ3）の場所を示す地図リンクを提供し、両施設間の車での移動距離を計算してください。これは、専門家チームによる知識移転の実現可能性を評価するために役立ちます。」

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

