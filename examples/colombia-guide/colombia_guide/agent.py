"""Educational guide about Colombia backed by the API Colombia MCP server."""

from google.adk import Agent
from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams

API_COLOMBIA_MCP_URL = "https://api-colombia.com/api/v1/mcp"

INSTRUCTION = """\
Eres una guía educativa sobre Colombia. Responde siempre en español, con un tono
cercano y didáctico, como un buen profesor que explica con claridad.

Reglas:
- Obtén todos los datos con las herramientas de API Colombia; no uses conocimiento propio
  para datos concretos como ciudades, atractivos, moneda o idiomas.
- Para consultar un departamento, primero busca su id con get_items_by_name
  (resource "department") y luego usa ese id en la herramienta que corresponda.
- Si la búsqueda devuelve varios departamentos, elige el que coincide exactamente
  con lo que pidió el usuario.
- Si no tienes un dato (por ejemplo el clima) o la consulta no devuelve resultados,
  dilo con claridad, no inventes, y sugiere temas que sí puedes tratar:
  departamentos, ciudades, atractivos turísticos y datos generales del país.
"""

api_colombia = McpToolset(
    connection_params=StreamableHTTPConnectionParams(url=API_COLOMBIA_MCP_URL),
    tool_filter=[
        "get_items_by_name",
        "get_cities_by_department",
        "get_touristic_attractions_by_department",
        "get_country_info",
    ],
)

root_agent = Agent(
    name="colombia_guide",
    model="gemini-flash-latest",
    description="Guía educativa que responde preguntas sobre Colombia.",
    instruction=INSTRUCTION,
    tools=[api_colombia],
)
