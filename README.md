# za

## Prerequisites

*   **Google Cloud Project** 
*   **Google Cloud Shell** 

## Deployment Guide

AIエージェントが、**「排出アセット（BigQuery）」**と**「地図情報（Google マップ）」**を駆使し、排出アセットの排出削減と歳出削減をする。

**「私は商人エージェントです。サブセクターと市町村において、排出アセットの排出削減と歳出削減をする」**

エージェントの実行能力（オーケストレーション）
1.  **分析（BigQuery）**: 過去データからサブセクターと市町村において、排出アセットの排出削減と歳出削減の分析をする。
2.  **予測（BigQuery）**: 予測データから、排出アセットの排出削減予測と歳出削減予測をする。
3.  **視覚化（Google マップ）**: 資金調圧する区役所を視覚化する。

### 1. Clone the Repository
```bash
git clone https://github.com/shogoorg/za.git
cd za

# Create virtual environment
python3 -m venv .venv

# If the above fails, you may need to install python3-venv:
# apt update && apt install python3-venv

# Activate virtual environment
source .venv/bin/activate

pip install -r requirements.txt

# Install ADK
pip install google-adk

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

1. 「東京都の非住宅の排出削減を計画しています。2025年に排出削減している３つの区市町村を特定してください。」
2. 「その区市町村の３つのアセットで、非住宅の排出削減量を確認してもらえますか？」
3. 「これをプレミアムサブセクターとして位置付けたいと思っています。東京都の非住宅のアセットでどれくらい排出削減していますか？」
4. 「2026年のカーボンプランニング予測が必要です。その非住宅の区市町村のアセットの2026年のカーボンクレジットを推定します。」
5. 「それで歳出削減できます。最後に、資金調達を確認しましょう。予定エリアに最も近い市役所を探して確認してください。」

### 7. Cleanup
```bash
dos2unix cleanup/cleanup_env.sh
chmod +x cleanup/cleanup_env.sh
./cleanup/cleanup_env.sh
```

### Data Logic & Narratives

### Data Logic & Narratives （最終構成）

| Table | 役割 (Demo Purpose) | Narrative Logic |
| :--- | :--- | :--- |
| **sources_agent** | **過去実績の分析＆ベンチマーク** | **2021年から2025年までの年次実績データ**を格納。このテーブルにより、エージェントは過去の削減トレンド、最も効率の良い地域（ベンチマーク）、および **2025年の確定収益（605万円）** を正確に分析・確定させることができます。 |
| **sources_prediction_agent** | **未来予測の戦略＆収益確定** | **2026年の予測データのみ**を格納。このテーブルは、エージェントが「過去の延長線上」として予測排出量、予測削減トン数、および **予測クレジット価値（200万円）** を提示し、「未来の収益目標」と「中期事業計画の収益性」を議論する基盤となります。 |