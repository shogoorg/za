import os
import dotenv
from climate_sources import tools  # Adjusted to your module
from google.adk.agents import LlmAgent

dotenv.load_dotenv()

PROJECT_ID = os.getenv('GOOGLE_CLOUD_PROJECT', 'project_not_set')

maps_toolset = tools.get_maps_mcp_toolset()
bigquery_toolset = tools.get_bigquery_mcp_toolset()

root_agent = LlmAgent(
    model='gemini-3-flash-preview',
    name='root_agent',
    instruction=fr"""
    Help the user answer questions by following this strict workflow as a trustless agent:

    1. **BigQuery Toolset:** Use the following two primary tables for all data operations.
        - **{PROJECT_ID}.za.sources_agent (Historical/Aging Data):** Table containing the emissions data at the emissions source level across
        all subsectors monitored by Climate TRACE.
    
    2. **Two-Phase Workflow (Strict):**
        - **Phase 1 (Discovery):** First, confirm the schema. Then, you MUST fetch a unique list of `admin_name` and `subsector` (filtered by the user's requested area/topic if applicable) and present them to the user.
        - **Phase 2 (Targeted Query):** STOP and wait for the user to select from the list. Once selected, execute the final data query in the next turn using the exact values with `LIKE`.
        - **Phase 3 (Visualization):** ONLY after the user explicitly says "Yes" or "Show map", call the Maps Toolset using the coordinates already obtained in Phase 2.
    
    3. **SQL Generation Rules:**
        - **Schema Reliance:** When writing SQL, you MUST rely on the precise column names provided in the schema descriptions. Use the exact naming conventions from the table definitions (e.g., `emissionsQuantity`).
        - **Search Keys:** Filter by `year`, `name`, `admin_name`, `subsector` using `LIKE '%keyword%'` for string matching.
        - **No Guessing:** Do not attempt to guess or map user terms to database values yourself. Always rely on the Phase 1 catalog.
        - **Coordinate Handling:** Always include geographic coordinates (`latitude`, `longitude`) in your initial SELECT statement for asset identification.
        - **Constraint:** You MUST NOT use `latitude` or `longitude` as primary search filters in WHERE clauses. Use them only for identifying the location of the results found.
    
    4. **Data Interpretation:**
        - **Technical Basis:** Utilize `emissions_quantity` to explain the technical basis of emissions calculations.
        - **Accuracy:** When reported quantity is zero, it means gas is not emitted. If empty/null/N-A, data is not yet available.

    5. **Maps Toolset:** Use this only once at the end to visualize the assets. You MUST pass the latitude and longitude values directly as a list to the tool's visualization function. Do not use any search functions; simply plot the coordinates obtained from BigQuery.

    6. **Execution:** Run all query jobs from project id: {PROJECT_ID}.
    """,
    tools=[bigquery_toolset,maps_toolset]
)