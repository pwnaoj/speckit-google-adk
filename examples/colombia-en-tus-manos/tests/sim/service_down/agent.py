"""Variante de prueba: todas las herramientas devuelven un error 503 (escenario us4-sc4)."""

from colombia_en_tus_manos.agent import root_agent as production_agent


def _service_unavailable(tool, args, tool_context):
    return {
        "isError": True,
        "content": [{"type": "text", "text": "503 Service Unavailable"}],
    }


root_agent = production_agent.model_copy(update={"before_tool_callback": _service_unavailable})
