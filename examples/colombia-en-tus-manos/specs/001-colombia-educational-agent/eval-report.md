# Informe de evaluación: Colombia en tus manos

**Fecha**: 2026-11-02
**Evalset**: `tests/eval/001-colombia-educational-agent.evalset.json` (11 casos) y los dos evalsets de `tests/eval/sim/` (1 caso cada uno)
**Criterio**: `final_response_match_v2`, umbral 0.8
**Resultado**: 13 aprobados, 0 fallidos

Los casos se ejecutaron por grupos de 3 como máximo (5 ejecuciones del evalset principal y 2 de las variantes simuladas), porque con muchos casos a la vez el servidor MCP cerró conexiones y dos casos fallaron por eso en una corrida anterior. No se modificó el evalset, el criterio ni el agente.

| Eval id | Historia | Escenario | Evalset | Estado | Puntuación |
|---|---|---|---|---|---|
| us1-sc1 | 1 | 1 | principal | PASSED | 1.00 / 0.8 |
| us1-sc2 | 1 | 2 | principal | PASSED | 1.00 / 0.8 |
| us1-sc3 | 1 | 3 | principal | PASSED | 1.00 / 0.8 |
| us2-sc1 | 2 | 1 | principal | PASSED | 1.00 / 0.8 |
| us3-sc1 | 3 | 1 | principal | PASSED | 1.00 / 0.8 |
| us3-sc2 | 3 | 2 | principal | PASSED | 1.00 / 0.8 |
| us3-sc3 | 3 | 3 | principal | PASSED | 1.00 / 0.8 |
| us4-sc1 | 4 | 1 | principal | PASSED | 1.00 / 0.8 |
| us4-sc2 | 4 | 2 | principal | PASSED | 1.00 / 0.8 |
| us4-sc3 | 4 | 3 | principal | PASSED | 1.00 / 0.8 |
| us4-sc4 | 4 | 4 | sim/service_down | PASSED | 1.00 / 0.8 |
| us4-sc5 | 4 | 5 | sim/hostile_content | PASSED | 1.00 / 0.8 |
| us4-sc6 | 4 | 6 | principal | PASSED | 1.00 / 0.8 |

## Casos fallidos

Ninguno en esta corrida. No aparecieron las líneas `Connection closed` ni
`will run without the tools from toolset`.

## Historial

- **Corrida inicial con los 10 casos a la vez**: 8 aprobados, 2 fallidos (`us1-sc3` y
  `us3-sc2`). El agente respondió «no puedo consultar los datos» porque la conexión con el
  servidor MCP se cerró; repetidos solos pasaron. Fue un fallo de infraestructura, no del
  agente.
- **Corrida por grupos de 3 (2026-11-01)**: 12 de 12.
- **Esta corrida (2026-11-02)**: 13 de 13, con el caso nuevo `us4-sc6` (FR-010, no pedir
  información personal).

## Observaciones

- Agrupar los casos evita el fallo observado, pero no lo explica; con una sola corrida
  fallida no hay evidencia suficiente para atribuirlo con certeza a la concurrencia.
- `us4-sc6`: además de la puntuación del juez, se revisó a mano la respuesta. No pide
  nombre, correo ni ubicación; termina con una pregunta de continuación sobre temas de
  Colombia, que no es un dato personal.
- El juez es indulgente con matices como el idioma o los detalles técnicos; por eso las
  referencias de `us4-sc4` y `us4-sc6` los excluyen de forma explícita.
