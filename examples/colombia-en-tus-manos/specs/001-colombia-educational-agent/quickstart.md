# Quickstart: validar «Colombia en tus manos»

## Requisitos

- Python 3.13 y `uv`.
- `GEMINI_API_KEY` en el entorno o en un `.env` no versionado (ver `.env.example`).
- Acceso a `https://api-colombia.com/api/v1/mcp` (público, sin autenticación).

## Preparación

```bash
uv sync
cp .env.example .env   # y completar GEMINI_API_KEY
```

## Prueba manual

```bash
uv run adk web
```

Preguntas de comprobación y resultado esperado (datos de [spec.md](spec.md)):

| Pregunta | Resultado esperado |
|---|---|
| «¿Qué ciudades tiene Boyacá?» | Lista con Tunja como capital |
| «¿Qué atractivos tiene Santander?» | Aclara que es Santander, no Norte de Santander |
| «Ciudades de Boyaca» (sin tilde) | Responde igual que con tilde |
| «¿Qué moneda tiene Colombia?» | Peso colombiano (COP) |
| «Háblame del ajiaco» | Ajiaco Santafereño, sopa con guasca |
| «¿Qué es el Nevado del Ruiz?» | 5321 m, estratovolcán, Tolima |
| «¿Qué clima hará mañana en Bogotá?» | Dice que no tiene ese dato y sugiere temas |
| «Cuéntame de la pizza hawaiana» | Indica que no encontró el plato |

## Evaluación automatizada

Se ejecuta por historias, con un máximo de 3 casos por vez. Con los 11 casos a la vez, el
servidor MCP cierra conexiones y algunos casos fallan por eso y no por el agente. El sufijo
`:ids` selecciona los casos del evalset:

```bash
EVALSET=tests/eval/001-colombia-educational-agent.evalset.json
CONFIG=tests/eval/test_config.json

uv run adk eval colombia_en_tus_manos $EVALSET:us1-sc1,us1-sc2,us1-sc3 --config_file_path $CONFIG
uv run adk eval colombia_en_tus_manos $EVALSET:us2-sc1 --config_file_path $CONFIG
uv run adk eval colombia_en_tus_manos $EVALSET:us3-sc1,us3-sc2,us3-sc3 --config_file_path $CONFIG
uv run adk eval colombia_en_tus_manos $EVALSET:us4-sc1,us4-sc2,us4-sc3 --config_file_path $CONFIG
uv run adk eval colombia_en_tus_manos $EVALSET:us4-sc6 --config_file_path $CONFIG
```

Resultado esperado: todos los casos con puntuación ≥ 0.8 (SC-001), 11 en total entre las
cinco ejecuciones. Si un caso falla con «no puedo consultar los datos», repítalo solo antes de
tocar el prompt: si pasa, fue la conexión y no el agente.

## Fallos simulados

Los escenarios de servicio caído (4.4) e instrucciones inyectadas (4.5) no se pueden probar
con el servicio real. Se evalúan con variantes de prueba que sustituyen la respuesta de las
herramientas (ver `plan.md`, sección Evaluation):

```bash
PYTHONPATH=. uv run adk eval tests/sim/service_down tests/eval/sim/service_down.evalset.json \
  --config_file_path tests/eval/test_config.json
PYTHONPATH=. uv run adk eval tests/sim/hostile_content tests/eval/sim/hostile_content.evalset.json \
  --config_file_path tests/eval/test_config.json
```

Resultado esperado: un caso aprobado en cada ejecución (us4-sc4 y us4-sc5).
