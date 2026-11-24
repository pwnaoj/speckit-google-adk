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

1. Run the project's prerequisites script with `--json --require-spec` from the
   project root: `.specify/scripts/bash/check-prerequisites.sh`, or
   `python3 .specify/scripts/python/check_prerequisites.py` when
   `.specify/init-options.json` has `"script": "py"`. Then read `FEATURE_DIR`. The feature name is its last path segment.
2. Read `.specify/extensions/adk/adk-config.yml` for `agent_dir` and `eval_dir`. If
   `agent_dir` is empty, use the folder named under `### Agent package` in `plan.md`.
3. Check that `<eval_dir>/<feature-name>.evalset.json` and `<eval_dir>/test_config.json`
   exist. If not, stop and suggest `__SPECKIT_COMMAND_ADK_EVALSET__`.
4. Validate the evalset:
   `python3 .specify/extensions/adk/scripts/validate_evalset.py <evalset>`.
   Stop and show the errors if it fails.
5. Check that the model has a valid way to authenticate, for the agent and for the judge
   (both use the same process environment), without printing any secret value: check
   only that names are set. Look in the environment and in the first `.env` found going
   up from `agent_dir` to the project root (the one ADK loads; variables already
   exported win). Any of these is enough:
   - an API key: `GOOGLE_API_KEY` or `GEMINI_API_KEY`;
   - Vertex AI / Enterprise: `GOOGLE_GENAI_USE_ENTERPRISE` (or the deprecated
     `GOOGLE_GENAI_USE_VERTEXAI`) set to true, with `GOOGLE_CLOUD_PROJECT`, a location,
     and cloud credentials (`GOOGLE_APPLICATION_CREDENTIALS` or application default
     credentials from `gcloud auth application-default login`);
   - if the agent or the judge uses a model from another provider, that provider's
     credential.
   If none is found, stop and say which options are accepted. If you cannot tell whether
   cloud credentials are valid, say so and continue: `adk eval` will fail on the first
   call if they are not.
6. If `preflight_command` in the configuration is not empty, run it from the project
   root. If it exits with a non-zero code, stop, show its output and do not run `adk
   eval`: the environment the cases assume (data, services, files) is not ready.
7. Record the start time (`date +%s`). Then run, from the project root:
   `adk eval <agent_dir> <evalset> --config_file_path <eval_dir>/test_config.json`
   Add `--num_runs <repeats>` when `repeats` in the configuration is greater than 1.
   Use `uv run adk ...` when the project root has a `uv.lock`. If `adk` is not found,
   stop and tell the user to install `google-adk[eval]` or activate its environment.
   If the command fails with `Eval module is not installed`, say the same.
   `adk eval` exits with code 1 when any case fails, so a non-zero code is not an
   error by itself: it is a result. Decide by the files: if new
   `*.evalset_result.json` files appeared in `<agent_dir>/.adk/eval_history` since the
   recorded time, continue to step 8 whatever the exit code. If none appeared, nothing
   was evaluated (credentials, configuration, import error): show the last lines of the
   output, report an execution error and do not summarize.
   If other evalsets must also run (for example simulated-service variants), run each
   the same way and keep every agent folder used.
8. Summarize everything this invocation produced, passing every agent folder used:
   `python3 .specify/extensions/adk/scripts/summarize_results.py <agent_dir>/.adk/eval_history --since <start time>`
   Its exit code is 1 when any case did not pass, which is a result, and 2 when it found
   no results.
9. Get the provenance of the run:
   `python3 .specify/extensions/adk/scripts/eval_provenance.py --agent-dir <agent_dir> --evalset <evalset> --config <eval_dir>/test_config.json --repeats <repeats> --adk-version <version>`
   where `<version>` is the version printed by `adk --version` (with the same prefix as
   step 7).
10. Write `FEATURE_DIR/eval-report.md`, replacing the previous one, with:
   - a table (eval id, user story, scenario, status, score/threshold, and `k/N` runs
     when `repeats` is greater than 1). Mark the cases the summary flags `UNSTABLE`: they
     passed in some runs and failed in others;
   - the `Cost` line of step 8 as it is (agent only: judge calls are not counted);
   - a *Provenance* section with the lines printed in step 9, unchanged;
   - for every failed case, the scenario's *Then* quoted from `spec.md`, what the agent
     answered (the `answer:` line of step 8) and a suggested fix. The eval id
     `us<N>-sc<M>` gives the user story `N` and the scenario `M` in
     `FEATURE_DIR/spec.md`.
11. Append one row to `FEATURE_DIR/eval-history.md` (create it with this header if it does
   not exist: `| Date | Commit | Passed | Failed | Unstable | Repeats | Tokens |` and its
   separator line). Take every value from the summary and the provenance; never edit or
   delete earlier rows. Use `-` for a value that was not printed.

## Rules

- Never edit the evalset, the criteria or their thresholds to make a case pass.
- Do not change the agent code in this command; propose changes in the report.
- Fixes belong in the agent instructions, the tool descriptions or the spec.
- With MCP toolsets, many cases running in parallel can make the server close
  connections (`Connection closed`). ADK usually retries, but sometimes the agent runs
  without its tools (log line `will run without the tools from toolset`) and a case fails
  for that reason alone. Before proposing a fix for a failed case, rerun it alone with the
  `:ids` suffix; if it passes, report it as an infrastructure failure, not an agent defect.
- Report the numbers as they are; do not round failures up.
- With `repeats` greater than 1 each case runs that many times (more quota). ADK judges
  the case on all its runs; do not hide an `UNSTABLE` case because its verdict is PASSED.
