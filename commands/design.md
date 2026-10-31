---
description: "Add the Google ADK architecture section to plan.md"
---

# ADK Design

Design the Google ADK architecture for the current feature and record it in `plan.md`.

## User Input

$ARGUMENTS

Consider the user input before proceeding (if not empty).

## Steps

1. Run the project's prerequisites script with `--json --require-spec` from the
   project root: `.specify/scripts/bash/check-prerequisites.sh`, or
   `python3 .specify/scripts/python/check_prerequisites.py` when
   `.specify/init-options.json` has `"script": "py"`. Then read `FEATURE_DIR` from the output. Stop with a clear message if
   `spec.md` or `plan.md` is missing in `FEATURE_DIR`; for a missing `plan.md` suggest
   running the core plan command first.
2. Read `FEATURE_DIR/spec.md`, `FEATURE_DIR/plan.md` and, if present,
   `.specify/memory/constitution.md`. Ignore the constitution if it is still the
   unfilled template (placeholders such as `[PROJECT_NAME]`).
3. Read `.specify/extensions/adk/adk-config.yml` for `model` and `agent_dir`. If
   `agent_dir` is empty, propose a snake_case folder name for the agent package from the
   feature name and record it in the plan; do not treat the empty value as a gap.
4. Choose the orchestration pattern with this table. Prefer the first row that fits:

   | Situation in the spec | Pattern |
   |-----------------------|---------|
   | One goal, a few tools, no fixed sequence | `Agent` (single) |
   | Fixed order of steps, each by a specialised agent | `SequentialAgent` |
   | Independent subtasks that can run at the same time | `ParallelAgent` |
   | Output must be refined until a condition is met | `LoopAgent` |
   | Mix of AI steps and plain code, branching, or human input | `Workflow` (graph) |

   Start from a single `Agent`. Add agents only when the spec needs it, and say why.
5. Fill the template `.specify/extensions/adk/templates/adk-plan-section.md`:
   - Agents: name, role, model, tools and `output_key` of each agent.
   - Tools: one row per function tool, with typed parameters and the `FR-xxx` it
     serves. For an MCP server add a single row for its toolset (`McpToolset`) with the
     server URL; list individual tool names only if they are already known, otherwise
     write `all tools of the server` and do not mark it `[NEEDS CLARIFICATION]`.
   - State contract: every session state key, who writes it and who reads it.
   - Guardrails: what the agent must not do, taken from the spec and the constitution.
   - Evaluation: keep the text of the template.
   - Risks: loops, tool misuse, cost, missing credentials.
6. Write the result into `FEATURE_DIR/plan.md` under the heading `## ADK Architecture`.
   If that section already exists, replace only that section; otherwise append it at the
   end of the file. Do not change any other part of `plan.md`.
7. Report the chosen pattern, the agents and tools, and any item marked
   `[NEEDS CLARIFICATION]`. Suggest the next step: `__SPECKIT_COMMAND_TASKS__`, then
   `__SPECKIT_COMMAND_ADK_EVALSET__`.

## Rules

- Do not write agent code. This command only produces the design.
- Write in the same language as `spec.md`; keep ADK identifiers in English.
- Do not invent requirements. If the spec does not say, mark it `[NEEDS CLARIFICATION]`.
  Missing tool names of an MCP server are not a requirement gap.
- Every tool must trace to at least one functional requirement in the spec.
- Keep the design as small as the spec allows.
- Do not name evaluation criteria in the plan; `__SPECKIT_COMMAND_ADK_EVALSET__` chooses
  them from the configuration.
