# Implementation Plan: Guía educativa de Colombia

**Branch**: `001-colombia-guide` | **Date**: 2026-10-31 | **Spec**: spec.md

**Input**: Feature specification from `/specs/001-colombia-guide/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Agente conversacional educativo que responde preguntas sobre Colombia consultando el MCP de API Colombia (HTTP, sin autenticación), construido con Google ADK.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.13

**Primary Dependencies**: google-adk 2.13.0 (McpToolset)

**Storage**: N/A

**Testing**: adk eval (evalset con criterios locales)

**Target Platform**: Local (adk run / adk web)

**Project Type**: single (paquete de agente)

**Performance Goals**: N/A

**Constraints**: Requiere acceso a https://api-colombia.com/api/v1/mcp

**Scale/Scope**: Un solo usuario por sesión

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

[Gates determined based on constitution file]

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
# [REMOVE IF UNUSED] Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# [REMOVE IF UNUSED] Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# [REMOVE IF UNUSED] Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure: feature modules, UI flows, platform tests]
```

**Structure Decision**: [Document the selected structure and reference the real
directories captured above]

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |

## ADK Architecture

### Pattern

**Chosen**: Agent (single)

**Why**: El spec describe un solo objetivo (responder preguntas sobre Colombia) con las herramientas de un único servidor MCP y sin secuencia fija ni subtareas paralelas, por lo que un `Agent` único es suficiente.

### Agent package

**Folder**: colombia_guide/ (contains `__init__.py`, `agent.py` and `root_agent`)

`agent_dir` está vacío en `adk-config.yml`; se propone `colombia_guide` a partir del nombre de la feature.

### Agents

| Name | Role | Model | Tools | output_key |
|------|------|-------|-------|------------|
| root_agent | Responde en español, con tono educativo, preguntas sobre Colombia usando solo datos del MCP; declara cuando no tiene un dato | gemini-flash-latest | api_colombia_toolset | - |

### Tools

| Name | Source | Purpose | Inputs | Output | Spec ref |
|------|--------|---------|--------|--------|----------|
| get_items_by_name | McpToolset (api-colombia) | Buscar un departamento por nombre para obtener su id (`resource`: string, `name`: string) | `resource`, `name` | lista de items con `id` y `name` | FR-001, FR-004 |
| get_cities_by_department | McpToolset (api-colombia) | Ciudades de un departamento | `departmentId`: integer | lista de ciudades | FR-001, FR-004 |
| get_touristic_attractions_by_department | McpToolset (api-colombia) | Atractivos turísticos de un departamento | `departmentId`: integer | lista de atractivos | FR-001, FR-004 |
| get_country_info | McpToolset (api-colombia) | Datos generales del país (moneda, idiomas, zona horaria) | sin parámetros | objeto con datos del país | FR-001, FR-004 |

Nota: las herramientas por departamento exigen el id numérico; el agente primero resuelve el id con `get_items_by_name` (resource `department`). Ids verificados: Boyacá = 7.

### State contract

| Key | Written by | Read by | Meaning |
|-----|-----------|---------|---------|
| (ninguna) | - | - | Agente único sin `output_key`; no se requiere estado de sesión compartido |

### Guardrails

- No responder con conocimiento propio: los datos deben venir del MCP de API Colombia (FR-001).
- Responder siempre en español y con tono educativo y claro (FR-002).
- No inventar datos; si el MCP no devuelve resultados o el tema está fuera de alcance (p. ej. el clima), declararlo y sugerir temas que sí puede tratar (FR-003).
- Aceptar nombres de departamentos sin tildes (caso límite del spec).
- Constitución: `.specify/memory/constitution.md` aún es la plantilla sin completar, por lo que no aporta guardrails adicionales.

### Evaluation

Every acceptance scenario in `spec.md` becomes one eval case with id `us<N>-sc<M>`.
Generate them with the ADK evalset command (`speckit.adk.evalset`).

### Risks

- Alucinación: el modelo podría responder desde su propio conocimiento en lugar de llamar al MCP; mitigar con instrucciones explícitas y `tool_trajectory_avg_score`.
- Disponibilidad: el servidor MCP requiere acceso de red a api-colombia.com; si falla, el agente debe declarar que no tiene el dato.
- Mal uso de herramientas: al exponer todas las herramientas del servidor, el modelo podría elegir una inadecuada (p. ej. departamento equivocado por falta de tildes).
- Bucles/costo: bajo; un solo agente sin bucles, pero conviene limitar llamadas encadenadas a herramientas.
- Credenciales: ninguna requerida (API sin autenticación).
