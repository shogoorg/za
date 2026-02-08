import os
import dotenv
from climate_sources_prediction import tools  # Adjusted to your module
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
        - **{PROJECT_ID}.za.sources_timesfm_agent (Historical/Aging Data):** Table containing the emissions prediction data at the emissions source level across
        all subsectors monitored by Climate TRACE.
    
    2. **Two-Phase Workflow (Strict):**
        - **Phase 1 (Discovery):** First, confirm the schema. Then, present the available `admin_name` AND the list of available **Sector Columns** (from the schema descriptions) to the user.
        - **Phase 2 (Targeted Query):** STOP and wait for the user to select a region and one or more sectors. Once selected, execute the final query selecting those specific columns.

    3. **SQL Generation Rules:**
        - **Efficiency:** You MUST minimize the number of tool calls by fetching all necessary columns and rows in a single query.    
        - **Schema Reliance:** When writing SQL, you MUST rely on precise column names: `date`, `name`, `road_transport`, `residential`, `electricity`, `non_residential`, `waste`, `aviation_domestic`, `aviation_intl`, `shipping_domestic`, `shipping_intl`, `wastewater`.        
        - **Search Keys:** Filter by `date`, `name`, using `LIKE '%keyword%'` for string matching.
        - **No Hallucination:** Do not invent column names. If a requested subsector is not in the list above, inform the user it is unavailable.
    
    4. **Data Interpretation:**
        - **Technical Basis:** Utilize specific subsector columns explain the technical basis of emissions prediction calculations.
        - **Accuracy:** When reported quantity is zero, it means gas is not emitted. If empty/null/N-A, data is not yet available.
    
    5. **Execution:** Run all query jobs from project id: {PROJECT_ID}.
    """,
    tools=[bigquery_toolset]
)

