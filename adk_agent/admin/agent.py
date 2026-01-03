import os
import dotenv
from admin import tools  #  sourcesに変更
from google.adk.agents import LlmAgent

dotenv.load_dotenv()

PROJECT_ID = os.getenv('GOOGLE_CLOUD_PROJECT', 'project_not_set')

maps_toolset = tools.get_maps_mcp_toolset()
bigquery_toolset = tools.get_bigquery_mcp_toolset()

root_agent = LlmAgent(
    model='gemini-3-pro-preview',
    name='root_agent',
    instruction=f"""
                Help the user answer questions by strategically combining insights from two sources:
                
                1.  **BigQuery toolset:** Access administrative data in the 'admin' dataset. Do not use any other dataset.
                Run all query jobs from project id: {PROJECT_ID}.

                2.  **Maps Toolset:** Use this for geographic analysis of emission sources (e.g., factories, power plants) and visualizing their locations.
                Include a hyperlink to an interactive map in your response where appropriate.
            """, #  adminに変更
    tools=[maps_toolset, bigquery_toolset]
)