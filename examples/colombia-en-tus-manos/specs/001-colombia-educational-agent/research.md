# Research: Colombia en tus manos

Verificado el 2026-10-31 contra el servidor MCP `https://api-colombia.com/api/v1/mcp`
(protocolo `2025-03-26`, servidor `api-colombia` 1.7.2) y PyPI.

## 1. Versión y soporte de ADK

- **Decision**: `google-adk[eval,mcp]>=2.13` con Python 3.13.
- **Rationale**: PyPI publica 2.13.0 (requiere Python ≥ 3.11); coincide con la restricción de
  la constitución.
- **Alternatives considered**: ADK 1.x (descartada por la constitución).

## 2. Integración con el servidor MCP

- **Decision**: `McpToolset` con transporte HTTP streamable hacia la URL del servidor, sin
  cabeceras de autenticación.
- **Rationale**: la constitución (III) exige MCP; el servidor es público, de solo lectura y
  responde a `initialize` y `tools/list` sin credenciales (comprobado).
- **Alternatives considered**: REST directo (admitido solo si el MCP no cubre la necesidad;
  no es el caso); cliente HTTP propio (rechazado por Principio IV).

## 3. Herramientas expuestas al agente

El servidor ofrece 11 herramientas. Se habilitan cinco con `tool_filter`:

| Herramienta | Uso | Requisito |
|---|---|---|
| `get_items_by_name` | Resolver departamentos por nombre (devuelve el id), buscar platos (`typicaldish`) y volcanes (`volcano`) | FR-004, FR-005 |
| `search_items` | Alternativa cuando el nombre se escribió sin tildes (ignora acentos) | FR-006 |
| `get_cities_by_department` | Ciudades por id de departamento | FR-004 |
| `get_touristic_attractions_by_department` | Atractivos por id de departamento | FR-004 |
| `get_country_info` | Moneda, idiomas, zona horaria | FR-004 |

- **Rationale**: el principio de menor privilegio (III) y la simplicidad (IV). Las dos
  herramientas por departamento exigen id numérico, por eso el agente resuelve primero el
  nombre.
- **Alternatives considered**: exponer las 11 (más superficie de uso indebido y más tokens
  de contexto); no habilitar `search_items` (inviable, ver sección 4).

## 4. Reconocimiento de nombres sin tildes y ambiguos

Pruebas contra el servidor (2026-10-31):

| Llamada | Resultado |
|---|---|
| `get_items_by_name(department, "Boyaca")` | `[]`: **no** ignora tildes |
| `get_items_by_name(department, "Boyacá")` | Boyacá (id 7) |
| `search_items(department, "Boyaca")` | Ignora tildes, pero devuelve primero Arauca, porque su descripción menciona Boyacá |
| `get_items_by_name(department, "Santander")` | Norte de Santander (id 23) y Santander: dos coincidencias |

- **Decision**: el agente intenta primero `get_items_by_name`. Si no hay resultados y el nombre
  parece escrito sin tildes, lo reintenta con la tilde restituida o usa `search_items` y
  elige solo el elemento cuyo `name` coincide con lo pedido, descartando los que solo lo
  mencionan en la descripción.
- **Rationale**: cubre FR-006 con el prompt y las herramientas del servidor, sin normalizar
  texto en código propio (Principio IV).
- **Alternatives considered**: normalizar texto en código propio (rechazado: capa propia sin
  necesidad demostrada); usar solo `search_items` (devuelve ruido en descripciones).
- **Riesgo**: un modelo puede elegir el elemento equivocado entre los resultados de
  `search_items`; el caso del escenario 1.3 lo cubre en la evaluación.

## 5. Modelo

- **Decision**: `gemini-flash-latest`, el valor de `adk-config.yml`.
- **Rationale**: tareas de recuperación y redacción corta; menor costo y latencia.
- **Alternatives considered**: un modelo mayor (sin evidencia de necesidad).

## 6. Evaluación

- **Decision**: evalset de ADK con `final_response_match_v2`, umbral 0.8, juez
  `gemini-flash-latest`; sin `tool_trajectory_avg_score` (`check_tools: false`).
- **Rationale**: la respuesta es texto libre; los ids se resuelven en tiempo de ejecución, lo
  que haría frágil la comparación de trayectoria. Los hechos fijados en los escenarios dan una
  referencia comprobable (SC-004).
- **Alternatives considered**: `response_match_score` (compara palabras, penaliza respuestas
  correctas).
- **Limitación**: el juez no consulta la API; los escenarios de servicio caído e inyección
  requieren respuestas simuladas del servicio en la evaluación.

### Simulación del servicio (us4-sc4 y us4-sc5)

- **Decision**: variantes de prueba del agente en `tests/sim/` con un `before_tool_callback`
  propio que sustituye el resultado de las herramientas; un evalset por variante.
- **Rationale**: es la opción más simple y usa una API estable de ADK. Probada el 2026-10-31
  con `adk eval` sobre una copia del agente: ambos escenarios pasan, incluida la ubicación en
  subcarpetas. El servicio caído debe fallar en todas las herramientas; con un fallo parcial el
  agente reintenta con otras grafías y alcanza el servicio real.
- **Alternatives considered**: la simulación de entorno de ADK (`EnvironmentSimulationFactory`,
  funciona igual, pero la documentación la marca como experimental y el plan no fija la versión
  de ADK); un servidor MCP falso (probaría también la caída de la conexión, pero añade un
  componente a mantener, contra el Principio IV; no probado); verificación manual (rompe el
  Principio VI y SC-001).
- **Requisitos prácticos**: la raíz del proyecto en `PYTHONPATH` al ejecutar `adk eval`; el
  `app_name` del evalset es el nombre de la carpeta de la variante.

## 7. Resolución del Technical Context

No quedan marcadores `NEEDS CLARIFICATION`.
