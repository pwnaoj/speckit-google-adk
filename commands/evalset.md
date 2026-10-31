---
description: "Generate an ADK evalset from the acceptance scenarios in spec.md"
---

# ADK Evalset

Turn each acceptance scenario of `spec.md` into a traceable ADK eval case.

## User Input

$ARGUMENTS

Consider the user input before proceeding (if not empty).

## Steps

1. Run `.specify/scripts/bash/check-prerequisites.sh --json --require-spec` from the
   project root and read `FEATURE_DIR` from the output. Stop with a clear message if
   `spec.md` is missing.
2. Read `FEATURE_DIR/spec.md`. If `FEATURE_DIR/plan.md` has an `## ADK Architecture`
   section, read it to learn the tool names. Read
   `.specify/extensions/adk/adk-config.yml` for `agent_dir`, `eval_dir` and `criteria`.
3. List the scenarios. For every `User Story N` and each numbered acceptance scenario
   `M` below it, create the id `us<N>-sc<M>` (for example `us1-sc2`).
4. Build one eval case per scenario from the template
   `.specify/extensions/adk/templates/adk-evalset.template.json`:
   - `eval_id`: the id from step 3.
   - `user_content`: a realistic user message that realises the scenario's *Given* and
     *When*. If the *Given* needs prior state, put it in `session_input.state`.
   - `final_response`: the expected outcome from the scenario's *Then*, short and
     checkable.
   - `intermediate_data.tool_uses`: the tool calls (`name`, `args`) the scenario
     requires, using names from the plan. Include a call only when its name and all its
     arguments are known; arguments resolved at runtime (such as ids returned by an
     earlier call) are not known, so leave the list empty in that case.
   - `session_input.app_name`: the name of the agent folder (`agent_dir`). If it is
     empty, use the folder named under `### Agent package` in `plan.md`; if that is not possible, ask the user.
5. Write `<eval_dir>/<feature-dir-name>.evalset.json`, using the feature directory name
   as `eval_set_id`. Create `eval_dir` if needed.
6. Write `<eval_dir>/test_config.json` with the `criteria` from the configuration.
   If `check_tools` is `true`, add `"tool_trajectory_avg_score": {"threshold": 1.0,
   "match_type": "IN_ORDER"}` to `criteria`; otherwise do not add it.
7. Show a table with id, user story, scenario and expected tool calls. List any
   scenario you could not turn into a case and why. Suggest running
   `adk eval <agent_dir> <eval_dir>/<feature-dir-name>.evalset.json --config_file_path <eval_dir>/test_config.json --print_detailed_results`.

## Rules

- Never rename or renumber ids afterwards; they link evaluation results to the spec.
- One case per scenario; do not merge or split scenarios.
- Do not invent behaviour that is not in the spec. Mark doubtful expectations with
  `[NEEDS CLARIFICATION]` in the report, not inside the JSON.
- The output must be valid JSON, without comments.
- If an evalset for this feature already exists, keep the ids and update only cases
  whose scenario text changed; report what changed.
