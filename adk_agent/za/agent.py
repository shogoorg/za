import os
import dotenv
from za import tools  # Adjusted to your module
from google.adk.agents import LlmAgent

dotenv.load_dotenv()

PROJECT_ID = os.getenv('GOOGLE_CLOUD_PROJECT', 'project_not_set')

maps_toolset = tools.get_maps_mcp_toolset()
bigquery_toolset = tools.get_bigquery_mcp_toolset()

root_agent = LlmAgent(
    model='gemini-3-flash-preview',
    name='root_agent',
    instruction=fr"""
                Help the user answer questions by following this strict workflow:
                
                1.  **BigQuery Toolset:** Use the following two primary tables for all data operations.
                    - **{PROJECT_ID}.za.sources_agent (Historical/Aging Data):** Use this for all historical analysis (e.g., trend analysis, calculating 2025 actual earnings, identifying the best-performing regions).
                    - **{PROJECT_ID}.za.sources_prediction_agent (Forecast Data):** Use this *only* for answering questions about **2026 predictions, forecast profits, and future strategic planning**.
                    
                    - **Schema Reliance:** When writing SQL, you **MUST** rely on the precise column names and data types provided in the schema descriptions. Use camelCase naming strictly (e.g., `emissionsQuantity`, `emissionsFactor`, `predicted_credit_value_jpy`).
                    - **Search Keys:** Filter by `year`, `admin_name`, `name`, `sector`, and `subsector` using `LIKE '%keyword%'` for string matching.
                    - **Coordinate Handling (Crucial):** Always include geographic coordinates (`latitude`, `longitude`) in your initial SELECT statement. This is mandatory for identifying assets.
                    - **Constraint (Filtering):** You **MUST NOT** use `latitude` or `longitude` as primary search filters or in WHERE clauses. Use them only for identifying the location of the results found.
                    - **Data Accuracy:** When applicable, utilize `emissionsFactor` and `emissionsFactorUnits` to provide a clear context and explain the technical basis of the emissions calculation (e.g., "The emissions factor shows a 5% improvement in efficiency.").
                    - Run all query jobs from project id: {PROJECT_ID}.

                2.  **Maps Toolset:** Use this **only once** at the end to visualize the coordinates (`latitude`, `longitude`) already obtained from BigQuery. Do not use this tool to search for new locations.
            """,
    tools=[maps_toolset, bigquery_toolset]
)