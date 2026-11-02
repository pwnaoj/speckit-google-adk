# Colombia en tus manos

Agente conversacional educativo, en español, que responde preguntas sobre Colombia
(departamentos y ciudades, turismo y naturaleza, gastronomía y cultura, datos generales del
país) usando exclusivamente los datos del servidor MCP de API-Colombia. Explica con tono
didáctico, aclara cuando una consulta es ambigua y reconoce con claridad lo que no sabe.

Construido con [Google ADK](https://google.github.io/adk-docs/) 2.13 y desarrollo dirigido por
especificaciones (Spec Kit). La especificación, el plan y las tareas están en
[`specs/001-colombia-educational-agent/`](specs/001-colombia-educational-agent/).

## Preparación

Requisitos: Python 3.13, [`uv`](https://docs.astral.sh/uv/) y una clave de Gemini.

```bash
uv sync
cp .env.example .env   # y completar GEMINI_API_KEY
```

`GEMINI_API_KEY` también puede definirse como variable de entorno. El `.env` no se versiona.

## Uso

```bash
uv run adk web
```

## Evaluación

Los casos se ejecutan por grupos de 3 como máximo. Con todos a la vez, el servidor MCP cierra
conexiones y algunos casos fallan por eso y no por el agente. El sufijo `:ids` selecciona los
casos del evalset:

```bash
EVALSET=tests/eval/001-colombia-educational-agent.evalset.json
CONFIG=tests/eval/test_config.json

# 11 escenarios contra el servicio real, en cinco ejecuciones
uv run adk eval colombia_en_tus_manos $EVALSET:us1-sc1,us1-sc2,us1-sc3 --config_file_path $CONFIG
uv run adk eval colombia_en_tus_manos $EVALSET:us2-sc1 --config_file_path $CONFIG
uv run adk eval colombia_en_tus_manos $EVALSET:us3-sc1,us3-sc2,us3-sc3 --config_file_path $CONFIG
uv run adk eval colombia_en_tus_manos $EVALSET:us4-sc1,us4-sc2,us4-sc3 --config_file_path $CONFIG
uv run adk eval colombia_en_tus_manos $EVALSET:us4-sc6 --config_file_path $CONFIG

# 2 escenarios contra un servicio simulado (servicio caído e instrucciones inyectadas)
PYTHONPATH=. uv run adk eval tests/sim/service_down tests/eval/sim/service_down.evalset.json \
  --config_file_path $CONFIG
PYTHONPATH=. uv run adk eval tests/sim/hostile_content tests/eval/sim/hostile_content.evalset.json \
  --config_file_path $CONFIG
```

Si un caso falla con «no puedo consultar los datos», repítalo solo antes de tocar el prompt: si
pasa, fue la conexión y no el agente. Las evaluaciones llaman al modelo. Más detalle en el
[quickstart](specs/001-colombia-educational-agent/quickstart.md).

## Estilo de código

El código sigue PEP 8 con líneas de hasta 100 columnas, verificado con
[`ruff`](https://docs.astral.sh/ruff/) (configuración en `pyproject.toml`):

```bash
uv run ruff check .
uv run ruff format --check .
```
