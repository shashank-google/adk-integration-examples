from google.adk.agents import Agent
import asyncio
from dotenv import load_dotenv
from google.genai import types
from google.adk.agents.llm_agent import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService # Optional
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams, StdioServerParameters
from google.adk.tools.toolbox_tool import ToolboxTool


def get_weather(city: str) -> dict:
    """Retrieves the current weather report for a specified city.

    Returns:
        dict: A dictionary containing the weather information with a 'status' key ('success' or 'error') and a 'report' key with the weather details if successful, or an 'error_message' if an error occurred.
    """
    if city.lower() == "new york":
        return {"status": "success",
                "report": "The weather in New York is sunny with a temperature of 25 degrees Celsius (41 degrees Fahrenheit)."}
    else:
        return {"status": "error",
                "error_message": f"Weather information for '{city}' is not available."}

def get_current_time(city:str) -> dict:
    """Returns the current time in a specified city.

    Args:
        dict: A dictionary containing the current time for a specified city information with a 'status' key ('success' or 'error') and a 'report' key with the current time details in a city if successful, or an 'error_message' if an error occurred.
    """
    import datetime
    from zoneinfo import ZoneInfo

    if city.lower() == "new york":
        tz_identifier = "America/New_York"
    else:
        return {"status": "error",
                "error_message": f"Sorry, I don't have timezone information for {city}."}

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return {"status": "success",
            "report": f"""The current time in {city} is {now.strftime("%Y-%m-%d %H:%M:%S %Z%z")}"""}

def get_exchange_rate(
    currency_from: str = "USD",
    currency_to: str = "EUR",
    currency_date: str = "latest",
):
    """Retrieves the exchange rate between two currencies on a specified date."""
    import requests

    response = requests.get(
        f"https://api.frankfurter.app/{currency_date}",
        params={"from": currency_from, "to": currency_to},
    )
    return response.json()

async def get_mysql_tools_async():
  """Gets tools from the File System MCP Server."""
  print("Attempting to connect to MCP MySQL server...")
  tools, exit_stack = await MCPToolset.from_server(
      # Use StdioServerParameters for local process communication
      connection_params=StdioServerParameters(
          command='npx', # Command to run the server
          args=[
                "mcprunner",
                "MYSQL_HOST=10.83.1.3",
                "MYSQL_PORT=3306",
                "MYSQL_USER=root",
                "MYSQL_PASS=root",
                "MYSQL_DB=imdb_full",
                "ALLOW_INSERT_OPERATION=false",
                "ALLOW_UPDATE_OPERATION=false",
                "ALLOW_DELETE_OPERATION=false",
                "MYSQL_LOG_LEVEL=DEBUG",
                "--",
                "npx",
                "-y",
                "@benborla29/mcp-server-mysql"            
            ],
      )
  )
  print("MCP Toolset created successfully.")
  return tools, exit_stack

async def filesystem_tools_async():
    """Gets tools from the File System MCP Server."""
    print("Attempting to connect to MCP Fileserver...")
    """Gets tools from MCP Server."""
    tools, exit_stack = await MCPToolset.from_server(
        connection_params=StdioServerParameters(
            command='npx',
            args=["-y",    # Arguments for the command
                  "@modelcontextprotocol/server-filesystem",
                  # TODO: IMPORTANT! Change the path below to an ABSOLUTE path on your system.
                  "/Users/agarwalsh/Downloads/to_delete/agent-file-system",
                  ],
        )
    )
    print("MCP Toolset created successfully.")
    return tools, exit_stack

async def googlemaps_tools_async():
    """Gets tools from the File System MCP Server."""
    print("Attempting to connect to MCP Google Maps...")
    """Gets tools from MCP Server."""
    tools, exit_stack = await MCPToolset.from_server(
        connection_params=StdioServerParameters(
            command='npx',
            args=["-y",    # Arguments for the command
                  "@modelcontextprotocol/server-google-maps",
                  ],
            env = {
                "GOOGLE_MAPS_API_KEY": "AIzaSyB7_7YBPYv-Hk_QhxDgOEB1Zwp8T8WtzK0"
                }
        )
    )
    print("MCP Toolset created successfully.")
    return tools, exit_stack

async def bq_tools_async():
    """Gets tools from the File System MCP Server."""
    print("Attempting to connect to MCP BigQuery...")
    """Gets tools from MCP Server."""
    tools, exit_stack = await MCPToolset.from_server(
        connection_params=StdioServerParameters(
            command='npx',
            args=["-y",    # Arguments for the command
                  "@ergut/mcp-bigquery-server",
                  "--project-id",
                  "pso-db-migrations",
                  "--location",
                  "US"
                  ],
        )
    )
    print("BQ MCP Toolset created successfully.")
    return tools, exit_stack

async def create_agent():
  """Gets tools from MCP Server."""
  tools, exit_stack = await get_mysql_tools_async()
  # fs_tools, fs_exit_stack = await filesystem_tools_async()
  map_tools, map_exit_stack = await googlemaps_tools_async()
  bq_tools, bq_exit_stack = await bq_tools_async()

  agent = LlmAgent(
      model='gemini-2.5-pro-preview-03-25', # Adjust model name if needed based on availability
      name='database_assistant',
      instruction='Help user interact with the local database using available tools.',
      tools=[*tools, *map_tools, *bq_tools], # Provide the MCP tools to the ADK agent
  )
  return agent, bq_exit_stack


def create_agent_toolbox():
    toolbox = ToolboxTool("http://127.0.0.1:5000")
    tools=toolbox.get_toolset(toolset_name='my-toolset')
    return Agent(
        name="weather_time_agent",
        model="gemini-2.0-flash",
        description="Agent to answer questions about database.",
        instruction="Help user interact with the local database using available tools.",
        tools=tools
    )


#root_agent = create_agent_toolbox()
root_agent = create_agent()
