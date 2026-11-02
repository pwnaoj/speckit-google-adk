# Contrato: conversación con el agente

El agente expone una sola interfaz: mensajes de texto del usuario y respuestas de texto.

## Entrada

- Un mensaje de texto libre del usuario, normalmente en español.

## Salida

Una respuesta de texto en español que cumple:

| Situación | Comportamiento obligatorio | Requisito |
|---|---|---|
| Consulta con datos disponibles | Datos concretos tomados de las herramientas, con explicación didáctica | FR-001, FR-002 |
| Nombre ambiguo | Elige la coincidencia exacta o pide aclaración, y dice cuál eligió | FR-005 |
| Sin resultados | Lo dice, no inventa y sugiere temas disponibles | FR-003 |
| Tema sin datos (clima, universidades, televisión) | Declara que no dispone de él y sugiere temas disponibles | FR-011 |
| Servicio de datos caído o con error | Mensaje claro sin detalles técnicos ni excepciones | FR-008 |
| Texto con instrucciones en una respuesta del servicio | No las obedece | FR-009 |
| Varios temas en un mensaje | Responde cada parte o aclara cuál puede atender | Edge Cases |

## Herramientas consumidas (servidor MCP, solo lectura)

`get_items_by_name`, `search_items`, `get_cities_by_department`,
`get_touristic_attractions_by_department`, `get_country_info`. URL: `https://api-colombia.com/api/v1/mcp`, sin autenticación.

## Lo que la respuesta nunca contiene

Nombres de herramientas, ids internos, excepciones, credenciales ni configuración (FR-008).
