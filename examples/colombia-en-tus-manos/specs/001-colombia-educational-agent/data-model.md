# Data Model: Colombia en tus manos

El agente no persiste datos ni define modelos propios: lee entidades de API-Colombia a través
de las herramientas MCP y las explica. Los campos de abajo son los que el agente usa, tomados
de respuestas reales del servicio (2026-10-31).

## Entidades (solo lectura)

| Entidad | Recurso MCP | Campos usados | Relaciones |
|---|---|---|---|
| Departamento | `department` | `id`, `name`, `description`, `cityCapitalId` | tiene ciudades y atractivos |
| Ciudad | `city` | `id`, `name`, `departmentId` | pertenece a un departamento |
| Atractivo turístico | `touristattraction` | `name`, `description`, `cityId` | asociado a un departamento |
| País | (herramienta `get_country_info`) | moneda, idiomas, zona horaria | — |
| Plato típico | `typicaldish` | `name`, `description`, `ingredients`, `departmentId` | opcionalmente un departamento |
| Volcán | `volcano` | `name`, `description`, `elevation`, `volcanoType`, `departmentId` | un departamento |

## Reglas

- **Identidad**: los departamentos se identifican por `id` numérico; el nombre solo sirve para
  resolverlo. Un nombre puede coincidir con varios (Santander y Norte de Santander).
- **Sin escritura**: ninguna entidad se crea ni se modifica (FR-007).
- **Datos volátiles**: campos como `activityLevel` del volcán cambian con el tiempo y no
  se usan como referencia en la evaluación.

## Estado de la conversación

No hay estado propio más allá del historial de sesión que gestiona ADK. El agente no guarda
datos personales (FR-010).
