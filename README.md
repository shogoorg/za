# za

## Deployment Guide

1.  排出量を追跡する: セクター別と行政区画別のアセットの排出量を追跡する。
2.  排出量削減の推定: セクター別と行政区画別のアセットの排出量削減を推定する。
3.  排出量削減の購入: セクター別と行政区画別のアセットの排出量削減を購入する。

### 1. Clone the Repository
```bash
git clone https://github.com/shogoorg/za.git
```
```bash
git clone https://github.com/google-agentic-commerce/a2a-x402.git
```
```bash
cd za
uv venv --python 3.13
source .venv/bin/activate
uv sync
uv pip install -r requirements.txt
uv pip install google-adk
```

```bash
cp -r ~/GitHub/a2a-x402/python/examples/ap2-demo/.venv/lib/python3.13/site-packages/x402 ~/GitHub/za/.venv/lib/python3.13/site-packages/
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
export GOOGLE_API_KEY="<Your API KEY>"
source .venv/bin/activate
uv run server
```
new Terminal
```bash
cd adk_agent
uv run adk web --port=8000
```

### 6. Chat with the Agent (Sample Narrative: Emission Strategy)

1. 東京都の排出量を追跡したい。
2. electricity-generation（発電）の排出量を追跡したい。地図を表示して。
3. 東京都の排出量削減を推定したい。
4. electricity-generation（発電）の排出削減を推定したい。地図を表示して。
5. 東京都のelectricity-generation（発電）のカーボンクレジットを購入したい。

### 7. Cleanup
```bash
dos2unix cleanup/cleanup_env.sh
chmod +x cleanup/cleanup_env.sh
./cleanup/cleanup_env.sh
```
### Data Logic & Narratives
| Table | Demo Purpose |
| :--- | :--- | 
| **sources** | Table containing the emissions data at the emissions source level across all subsectors monitored by Climate TRACE. |
subsectors monitored by Climate TRACE. |
| **plans** | Table containing the emission reduction solutions for all subsectors globally|