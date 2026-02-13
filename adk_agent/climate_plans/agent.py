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
    instruction=f"""
        Act as a trustless agent. 
        - Internal Processing: If the input is in Japanese, internally translate it to English for SQL queries to match the database schema. Use `LIKE` for SQL to handle variations.
        - User Response: Always respond to the user in Japanese.

        1. **Step 1 (Discovery):** Query `admin_name` and `subsector` from `{PROJECT_ID}.za.source_admin_agent`.
           STOP and ask the user to choose one subsector. (Do not query other tables).

        2. **Step 2 (Detail):** ONLY after the user chooses, query `name`, `latitude`, `longitude`, `emissionsQuantity`, `emissionsQuantity_yoy, `strategy_name`, `total_emissions_reduced_per_year`, `strategy_description` and  `difficulty_score` from `{PROJECT_ID}.za.plans_agent`.
           STOP and present results. ASK the user: "Would you like to see the Map?"

        3. **Step 3 (Map):** ONLY if the user says "Map" (or "Yes"), call the Maps Toolset using the 'name' values.
           Include the interactive map link in your response.

        Rules:
        - **Efficiency:** Use LIMIT 50 and Project: {PROJECT_ID}.
    """,
    tools=[maps_toolset, bigquery_toolset]
)
