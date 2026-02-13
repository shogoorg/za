# Zero Assembly (ゼロ会)

## 概要

包括的な排出量の洞察
1.  **世界中の排出量を追跡する:**　世界中の７億 4,500万の温室効果ガスと大気汚染物質の発生源から。
2.  **排出量削減の推定:**　世界中のあらゆる発生源に対する具体的かつ可能な気候アクションから。
3.  **排出量削減の購入:**　世界中のあらゆる発生源に対する具体的かつ可能な気候資金から。

### 利点　

*   世界の排出量を測定: Climate TRACEを利用して、温室効果ガス排出量をこれまでにない詳細さとスピードで追跡するテクノロジーを活用することで、意義のある気候変動対策をより迅速かつ容易に実施できるようにします。世界の排出量ネットゼロ達成を目指すすべての関係者にとって有益な情報を提供します。
*   フットプリントの削減: Climate TRACEを利用して、排出量の追跡にとどまらず、管理下にあるあらゆる排出源に対して実行可能な **気候変動アクション**を実行することで、具体的な排出削減目標を達成する方法を示します。
*   世界の排出量の購入: Climate TRACEを利用して、排出量の追跡にとどまらず、管理下にあるあらゆる排出源に対して実行可能な **気候変動資金**を実行することで、具体的な排出削減目標を達成する方法を示します。

### 主な機能
オープンデータ。100 を超える大学、科学者、AI 専門家からなる世界的な非営利連合によって構築されました。
*  744,678,997 件の排出資産を個別に、または都市、州、国など別に集計して調べます。ゼロ会は、4,700件の排出アセットを個別に、都道府県別に集計して調べます。
*  10の産業セクターを67のサブセクターに分割したグループ排出量
*  10年以上にわたるデータ（2015～2025年）を追跡し、2021年からは月次データが利用可能。ゼロ会は、1年のデータ（2024年）を追跡。
*  3つの温室効果ガスの影響を見る。ゼロ会は、1つの温室効果ガスの影響を見る。

## Deployment Guide

```bash
.
├── LICENSE
├── README.md
├── adk_agent
│   ├── climate_plans
│   ├── climate_sources
│   └── market
├── cleanup
│   └── cleanup_env.sh
├── data
│   ├── admins.csv
│   └── sources.csv
├── requirements.txt
├── server
│   ├── __init__.py
│   ├── __main__.py
│   └── agents
├── setup
│   ├── setup_bigquery.sh
│   ├── setup_csv.py
│   ├── setup_csv.sh
│   └── setup_env.sh
```

### 1. Authenticate with Google Cloud

```bash
gcloud auth application-default login
gcloud config set project [YOUR-PROJECT-ID]
export PROJECT_ID=$(gcloud config get project)
```

### 2. Clone the Repository
```bash
git clone https://github.com/shogoorg/za.git
cd za
```
```bash
git clone https://github.com/google-agentic-commerce/a2a-x402.git
```

### 3. Configure Environment

```bash
dos2unix setup/setup_env.sh
chmod +x setup/setup_env.sh
./setup/setup_env.sh
```
Could have

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

### 4. Provision BigQuery

```bash
dos2unix setup/setup_bigquery.sh
chmod +x setup/setup_bigquery.sh
./setup/setup_bigquery.sh
```
Could have
```bash
python3 setup/setup_csv.py
```
```bash
sources_admins_plans
sources_agent_short
plans_agent_short
```
## 5. Deployment Guide

climate_sourcesとclimate_plans

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install google-adk
```
```bash
cd adk_agent
adk web
```
market

```bash
export GOOGLE_API_KEY="<Your API KEY>"
source .venv/bin/activate
pip uninstall google-adk
pip install -r requirements.txt
```
```bash
python -m server
```
```bash
source .venv/bin/activate
adk web --port=8000
```
### 6. Chat with the Agent (Sample Narrative: Emission Strategy)
climate_sources
1. 東京都の排出量を追跡したい。
2. electricity-generation（発電）
3. （地図を表示しますか?）はい
4. レポートを作成したい。

climate_plans
1. 東京都の排出量削減を推定したい。
2. electricity-generation（発電）
3. （地図を表示しますか?）はい
4.  レポートを作成したい。

market
1. 東京都のelectricity-generation（発電）のSHINAGAWAのカーボンクレジットを購入したい。
2. (この支払いを承認しますか?) はい

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
| **plans** | Table containing the emission reduction solutions for all subsectors globally|