import os
import dotenv
from climate import tools  # Adjusted to your module
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
        - **{PROJECT_ID}.za.sources_plans_agent (Forecast/Strategy Data):** Table containing the emission reduction solutions for all subsectors
        globally
    2. **SQL Generation Rules:**
        - **Schema Reliance:** When writing SQL, you MUST rely on the precise column names provided in the schema descriptions. Use the exact naming conventions from the table definitions (e.g., `emissionsQuantity`, `emissionsFactor`, `strategy_name`, `difficulty_score`).
        - **Search Keys:** Filter by `year`, `admin_name`, `name`, `sector`, and `subsector` using `LIKE '%keyword%'` for string matching.
        - **Coordinate Handling:** Always include geographic coordinates (`latitude`, `longitude`) in your initial SELECT statement for asset identification.
        - **Constraint:** You MUST NOT use `latitude` or `longitude` as primary search filters in WHERE clauses. Use them only for identifying the location of the results found.

    3. **Data Interpretation:**
        - **Technical Basis:** Utilize `emissions_quantity` and `total_emissions_reduced_per_year` to explain the technical basis of emissions calculations.
        - **Accuracy:** When reported quantity is zero, it means gas is not emitted. If empty/null/N-A, data is not yet available.
        - **Strategy Context:** For reduction plans, refer to the `difficulty_score` to explain the effort and capital cost required (lower = easier).

    4. **Execution:** Run all query jobs from project id: {PROJECT_ID}.
    """,
    tools=[bigquery_toolset]
)

