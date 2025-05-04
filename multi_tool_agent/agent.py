from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters

async def get_mysql_tools_async():
  """Gets tools from the MySQL MCP Server."""
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
  print("Database MCP Toolset created successfully.")
  return tools, exit_stack


async def googlemaps_tools_async():
    """Gets tools from the Google Maps MCP Server."""
    print("Attempting to connect to MCP Google Maps...")
    """Gets tools from MCP Server."""
    tools, exit_stack = await MCPToolset.from_server(
        connection_params=StdioServerParameters(
            command='npx',
            args=["-y",    # Arguments for the command
                  "@modelcontextprotocol/server-google-maps",
                  ],
            env = {
                "GOOGLE_MAPS_API_KEY": "<<INPUT_API_KEY_HERE>>"
                }
        )
    )
    print("Maps MCP Toolset created successfully.")
    return tools, exit_stack

async def bq_tools_async():
    """Gets tools from the BigQuery MCP Server."""
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
  """Gets tools from All MCP Servers and initialize agent"""
  db_tools, exit_stack = await get_mysql_tools_async()
  map_tools, map_exit_stack = await googlemaps_tools_async()
  bq_tools, bq_exit_stack = await bq_tools_async()

  agent = LlmAgent(
      model='gemini-2.5-pro-preview-03-25', # Adjust model name if needed based on availability
      name='database_assistant',
      instruction='Help user interact with the local database using available tools.',
      tools=[*db_tools, *map_tools, *bq_tools], # Provide the MCP tools to the ADK agent
  )
  return agent, bq_exit_stack

root_agent = create_agent()
