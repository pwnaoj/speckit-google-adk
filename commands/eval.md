---
description: "Run adk eval for the feature and map failures to user stories"
---

# ADK Eval

Run the feature's evalset with `adk eval` and report the results by acceptance scenario.
This command calls the model (and the judge model), so it uses API quota.

## User Input

$ARGUMENTS

Consider the user input before proceeding (if not empty).

## Steps

1. Run `.specify/scripts/bash/check-prerequisites.sh --json --require-spec` from the
   project root and read `FEATURE_DIR`. The feature name is its last path segment.
2. Read `.specify/extensions/adk/adk-config.yml` for `agent_dir` and `eval_dir`. If
   `agent_dir` is empty, use the folder named under `### Agent package` in `plan.md`.
3. Check that `<eval_dir>/<feature-name>.evalset.json` and `<eval_dir>/test_config.json`
   exist. If not, stop and suggest `__SPECKIT_COMMAND_ADK_EVALSET__`.
4. Validate the evalset:
   `python3 .specify/extensions/adk/scripts/validate_evalset.py <evalset>`.
   Stop and show the errors if it fails.
5. Check that `GEMINI_API_KEY` is available (in the environment or in
   `<agent_dir>/.env`) without printing its value. If it is missing, stop and say so.
6. Run, from the project root:
   `adk eval <agent_dir> <evalset> --config_file_path <eval_dir>/test_config.json`
   Use `uv run adk ...` when the project root has a `uv.lock`. If `adk` is not found,
   stop and tell the user to install `google-adk[eval]` or activate its environment.
   If the command fails with `Eval module is not installed`, say the same.
7. Summarize the newest result:
   `python3 .specify/extensions/adk/scripts/summarize_results.py <agent_dir>/.adk/eval_history`
8. Write `FEATURE_DIR/eval-report.md` with a table (eval id, user story, scenario,
   status, score/threshold). The eval id `us<N>-sc<M>` gives the user story `N` and the
   scenario number `M` in `FEATURE_DIR/spec.md`. For every failed case, quote the scenario's *Then* from
   `spec.md`, say what the agent answered (from the run output) and suggest a fix.

## Rules

- Never edit the evalset, the criteria or their thresholds to make a case pass.
- Do not change the agent code in this command; propose changes in the report.
- Fixes belong in the agent instructions, the tool descriptions or the spec.
- `Connection closed` log lines from MCP servers are retried by ADK; they are not
  failures.
- Report the numbers as they are; do not round failures up.
