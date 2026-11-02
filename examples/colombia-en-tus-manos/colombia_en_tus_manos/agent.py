"""Agente «Colombia en tus manos».

Expone `root_agent`, el agente de ADK que responde preguntas sobre Colombia con los datos del
servidor MCP de API-Colombia (solo lectura, con cinco herramientas habilitadas). Su
instrucción está en `prompts.py`.
"""

from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams

from .prompts import INSTRUCTION

API_COLOMBIA_MCP_URL = "https://api-colombia.com/api/v1/mcp"

# Segundos máximos para establecer la conexión con el servidor MCP (el parámetro `timeout` de ADK;
# la lectura tiene su propio límite, `sse_read_timeout`). 15 s en lugar de los 5 s por defecto,
# para tolerar un servicio público lento. Es un valor elegido sin medir y no evita los cierres
# de conexión intermitentes cuando se evalúan muchos casos a la vez (ver
# specs/001-colombia-educational-agent/eval-report.md).
SERVER_TIMEOUT_SECONDS = 15.0

api_colombia_toolset = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url=API_COLOMBIA_MCP_URL, timeout=SERVER_TIMEOUT_SECONDS
    ),
    tool_filter=[
        "get_items_by_name",
        "search_items",
        "get_cities_by_department",
        "get_touristic_attractions_by_department",
        "get_country_info",
    ],
)

root_agent = Agent(
    name="root_agent",
    model="gemini-flash-latest",
    instruction=INSTRUCTION,
    tools=[api_colombia_toolset],
)
