# Spec Kit extension for Google ADK

Spec-driven development of [Google ADK](https://adk.dev) agents with
[Spec Kit](https://github.com/github/spec-kit). Every acceptance scenario in `spec.md`
becomes a traceable evaluation case, and the agent architecture is decided in `plan.md`
before any code is written.

Tested with Spec Kit 1.2.6.dev0, Google ADK 2.13.0 and Claude Code, on one real project.
Python only. See [Known limitations](#known-limitations).

## Commands

| Command | What it does |
|---------|--------------|
| `/speckit-adk-design` | Adds an `## ADK Architecture` section to `plan.md`: pattern and alternatives, agents, tools, state, guardrails (with the scenario that verifies each one) and evaluation plan. |
| `/speckit-adk-evalset` | Generates `*.evalset.json` and `test_config.json` from the scenarios in `spec.md`. |
| `/speckit-adk-eval` | Runs `adk eval` and writes `eval-report.md` with results by user story. Calls the model. |
| `/speckit-adk-review` | Read-only check of traceability between `spec.md`, `plan.md` and the evalset. |

Helper scripts (standard library only, installed in `.specify/extensions/adk/scripts/`):
`validate_evalset.py`, `check_traceability.py` and `summarize_results.py`.

## Requirements

- Spec Kit with the Claude Code integration (scripts in bash or Python are both supported).
- `google-adk[eval]` 2.13.0 or later: `adk eval` needs the `eval` extra. If the agent uses
  an MCP server, also the `mcp` extra (`google-adk[eval,mcp]`); `eval` does not include it.
- `GEMINI_API_KEY` in the environment or in a `.env` the agent can find (ADK looks for it
  from the agent folder up to the project root). Do not commit it.

## Install

From a Spec Kit project initialised with Claude Code:

```bash
specify extension add --dev /path/to/speckit-google-adk
```

## Quick start

Run the Spec Kit flow in this order. The extension adds the steps in bold:

| # | Command | Result |
|---|---------|--------|
| 1 | `/speckit-constitution` | Project principles in `.specify/memory/constitution.md`. Keep them about the project, not about tools. |
| 2 | `/speckit-specify` | `spec.md`. Keep the template structure (see [Traceability](#traceability)). |
| 3 | `/speckit-plan` | `plan.md`, `research.md` and the other planning files. |
| 4 | **`/speckit-adk-design`** | `## ADK Architecture` section in `plan.md`, including the agent package folder. |
| 5 | `/speckit-tasks` | `tasks.md`. |
| 6 | **`/speckit-adk-evalset`** | `tests/eval/<feature>.evalset.json` and `test_config.json`. |
| 7 | `/speckit-implement` | The agent package, created from the plan. `adk create` is optional. |
| 8 | **`/speckit-adk-eval`** | `eval-report.md`. See [Running the evaluation](#running-the-evaluation). |

`/speckit-adk-review` can be run at any point after step 6.

## Configure

Edit `.specify/extensions/adk/adk-config.yml`:

| Key | Meaning |
|-----|---------|
| `agent_dir` | Folder of the agent package. If empty, the folder proposed in the plan is used. |
| `model` | Model for newly designed agents. |
| `eval_dir` | Where evalsets are written (default `tests/eval`). |
| `criteria` | Criteria for `test_config.json`. The default is `final_response_match_v2` (LLM judge, needs only `GEMINI_API_KEY`). Do not use `response_match_score` for free-text answers: it compares words and fails correct ones. |
| `check_tools` | Also check tool calls (off by default: ids resolved at runtime and repeated calls make it fail without a real error). |

## Traceability

Eval ids follow `us<N>-sc<M>`: user story `N`, acceptance scenario `M`. Results of
`adk eval` report the same ids.

The scripts read `spec.md` and expect the Spec Kit template structure: headings
`User Story N` (or `Historia de usuario N`) and numbered scenarios that start with
`**Given**` (or `**Dado**`). Content can be in any language, but if those headings or
keywords are changed the traceability check finds no scenarios.

## Hooks

`design`, `evalset` and `eval` are offered as **optional** hooks after `/speckit-plan`,
`/speckit-tasks` and `/speckit-implement`. Nothing runs unless you type the command.
Notes:

- Hooks are instructions to the AI agent, not code Spec Kit runs: they can be skipped.
- Other extensions share the same events. They are offered in the order of
  `.specify/extensions.yml`, not by priority.
- `specify extension disable adk` turns the hooks off without uninstalling.

## Running the evaluation

- Run `adk eval` on groups of **3 cases at most**, selecting them with the `:ids` suffix:
  `adk eval <agent_dir> file.evalset.json:us1-sc1,us1-sc2,us1-sc3 --config_file_path ...`.
  You can ask for this when invoking the command, for example
  `/speckit-adk-eval run in groups of 3`.
- With MCP toolsets, many cases in parallel make the server close connections
  (`Connection closed`). Usually ADK retries, but sometimes the agent runs without its
  tools (log line `will run without the tools from toolset`) and cases fail for that reason
  alone. In one project, 10 cases at once failed about 1 in 5; groups of 3 had no failures.
- If a case fails with an answer like "I cannot query the data right now", rerun it alone
  before changing the prompt. If it passes, it was the connection, not the agent.

## Scenarios that need a simulated service

Scenarios such as "the data service fails" or "the service returns hostile text" cannot run
against the live service. `design` lists them under *Needs a simulated service* in the plan.
The extension does not simulate anything; this is one approach that worked:

- A test-only variant of the agent, in its own folder, that imports the real `root_agent`
  and copies it with `model_copy(update={"before_tool_callback": ...})`. The callback
  replaces the tool result. For "service down", make **every** tool fail: if only one
  name fails, the agent retries with another spelling and reaches the real service.
- One evalset per variant, with `app_name` equal to the variant folder name.
- Run `adk eval` with the project root in `PYTHONPATH` (it does not add it by itself).

`evalset` writes all scenarios to one file, so move those cases to their own evalsets by
hand. Until then `review` reports them as `MISSING`, which is expected.

## Known limitations

- Validated on **one project** and one MCP server. Behaviour with other servers, tool types
  or specs in other layouts is unknown.
- Specific to ADK 2.13: evalset format and criteria change between versions.
- Skills and several design options are mentioned but only the common patterns were
  exercised.

## Example

[examples/colombia-guide](examples/colombia-guide) is a small complete run: spec, plan with
ADK architecture, evalset, agent and evaluation report.

## Development

```bash
uv sync
uv run ruff check .
uv run pytest
```

## License

MIT
