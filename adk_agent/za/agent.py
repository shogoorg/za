import os
import dotenv
from za import tools  # za に変更
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
                
                1.  **BigQuery toolset:** Use the \`{PROJECT_ID}.za.sources_admins\` table.
                    - **Keys:** Filter by `year`, `admin_name`, `admin_full_name`, `sector`, and `subsector` using `LIKE %keyword%` for all string matching.
                    - **Mandatory:** Include geographic coordinates (`latitude`, `longitude`) in your initial SELECT statement along with all other columns needed for your analysis. Do not make separate calls for location data.
                    Run all query jobs from project id: {PROJECT_ID}.

                2.  **Maps Toolset:** Use this **only once** at the end to visualize the coordinates already obtained from BigQuery. Do not search for locations.
            """,
    tools=[maps_toolset, bigquery_toolset]
)