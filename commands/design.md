---
description: "Add the Google ADK architecture section to plan.md"
---

# ADK Design

Design the Google ADK architecture for the current feature and record it in `plan.md`.

## User Input

$ARGUMENTS

Consider the user input before proceeding (if not empty).

## Steps

1. Run the project's prerequisites script, only one of the two, with `--json
   --require-spec` from the project root: `python3
   .specify/scripts/python/check_prerequisites.py` when `.specify/init-options.json` has
   `"script": "py"`, otherwise `.specify/scripts/bash/check-prerequisites.sh`. Then read
   `FEATURE_DIR` from the output. Stop with a clear message if
   `spec.md` or `plan.md` is missing in `FEATURE_DIR`; for a missing `plan.md` suggest
   running the core plan command first.
2. Read `FEATURE_DIR/spec.md`, `FEATURE_DIR/plan.md` and, if present,
   `.specify/memory/constitution.md`. Ignore the constitution if it is still the
   unfilled template (placeholders such as `[PROJECT_NAME]`). Also read the other
   planning artifacts in `FEATURE_DIR` when they exist (`research.md`, `data-model.md` and
   the files in `contracts/`): they hold decisions such as tool names and service URLs.
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
   | A main agent must decide at run time which specialist handles each request | Coordinator `Agent` with `sub_agents` |
   | Mix of AI steps and plain code, branching, or human input | `Workflow` (graph) |

   Start from a single `Agent`. Add agents only when the spec needs it, and say why.
   Independently of the pattern: if the agent must carry many domain procedures and only
   some apply to each request, ADK Skills (`SkillToolset`, an experimental feature) load
   instructions on demand. Propose them only if the instructions cannot stay in one
   prompt, and say so in the plan; a prompt that fits comfortably does not need them.
5. Fill the template `.specify/extensions/adk/templates/adk-plan-section.md`:
   - Pattern: the chosen one, why, and the alternatives considered (the next simpler and
     the next more complex pattern, each with the reason it was rejected; if no simpler
     pattern exists, say so).
   - Agents: name, role, model, tools and `output_key` of each agent.
   - Tools: one row per function tool, with typed parameters and the `FR-xxx` it
     serves. For an MCP server add a single row for its toolset (`McpToolset`) with the
     server URL. Take the tool names and the URL from the planning artifacts. Only if no
     artifact lists the tools, write `all tools of the server` there; never copy that
     phrase next to a list of names, and do not mark missing tool names
     `[NEEDS CLARIFICATION]`.
   - State contract: every session state key, who writes it and who reads it.
   - Guardrails: one row per limit the agent must respect, taken from the spec and the
     constitution, with the requirement it serves, the mechanism that enforces it
     (`prompt`, `callback`, `plugin` or `tool_filter`) and *Verified by*: the id(s)
     `us<N>-sc<M>` of the acceptance scenario(s) that exercise it (user story `N`, scenario
     `M` as numbered in `spec.md`), or `none`.
   - Evaluation: fill every field from real data. The evalset path uses `eval_dir` from
     the configuration and the feature directory name. Count the acceptance scenarios of
     `spec.md`. Take the criteria and thresholds from `criteria` and `check_tools` in the
     configuration. List the scenarios whose Given changes what a tool returns (service
     error or hostile content): they cannot run against the live service. Do not list those
     the live service produces by itself, such as a search with no matches. Name how
     they are simulated only if the plan already says so; otherwise write
     `[NEEDS CLARIFICATION: how these scenarios are simulated]`.
   - Risks: loops, tool misuse, cost, missing credentials.
6. Check coverage before writing: every `FR-xxx` of the spec must appear in the Tools or
   Guardrails tables (add a row for any that does not), and every tool must cite a
   requirement. List each guardrail whose *Verified by* is `none` under Risks as an
   unverified requirement.
7. Write the result into `FEATURE_DIR/plan.md` under the heading `## ADK Architecture`.
   If that section already exists, replace only that section; otherwise append it at the
   end of the file. Do not change any other part of `plan.md`.
8. Report the chosen pattern, the agents and tools, and any item marked
   `[NEEDS CLARIFICATION]` and any unverified requirement. Suggest the next step: `__SPECKIT_COMMAND_TASKS__`, then
   `__SPECKIT_COMMAND_ADK_EVALSET__`.

## Rules

- Do not write agent code. This command only produces the design.
- Write in the same language as `spec.md`; keep ADK identifiers in English.
- Do not invent requirements. If the spec does not say, mark it `[NEEDS CLARIFICATION]`.
  Missing tool names of an MCP server are not a requirement gap.
- Every tool must trace to at least one functional requirement in the spec.
- Keep the design as small as the spec allows.
- Do not choose evaluation criteria yourself: in the Evaluation section report only those in
  the configuration; `__SPECKIT_COMMAND_ADK_EVALSET__` applies them.
