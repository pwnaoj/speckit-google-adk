# Spec Kit extension for Google ADK

Spec-driven development of [Google ADK](https://adk.dev) agents with
[Spec Kit](https://github.com/github/spec-kit). Every acceptance scenario in `spec.md`
becomes a traceable evaluation case, and the agent architecture is decided in `plan.md`
before any code is written.

Tested with Spec Kit 1.2.6.dev0, Google ADK 2.13.0 and Claude Code. Python only.

## Commands

| Command | What it does |
|---------|--------------|
| `/speckit-adk-design` | Adds an `## ADK Architecture` section to `plan.md` (pattern, agents, tools, state, guardrails). |
| `/speckit-adk-evalset` | Generates `*.evalset.json` and `test_config.json` from the scenarios in `spec.md`. |
| `/speckit-adk-eval` | Runs `adk eval` and writes `eval-report.md` with results by user story. Calls the model. |
| `/speckit-adk-review` | Read-only check of traceability between `spec.md`, `plan.md` and the evalset. |

`design`, `evalset` and `eval` are offered as optional hooks after `/speckit-plan`,
`/speckit-tasks` and `/speckit-implement`. `review` is run by hand.

Helper scripts (standard library only, installed in `.specify/extensions/adk/scripts/`):
`validate_evalset.py`, `check_traceability.py` and `summarize_results.py`.

## Requirements

- Spec Kit with the Claude Code integration.
- `google-adk[eval]` 2.13.0 or later (`adk eval` needs the `eval` extra).
- `GEMINI_API_KEY` in the environment or in the agent folder's `.env`.

## Install

From a Spec Kit project initialised with Claude Code:

```bash
specify extension add --dev /path/to/speckit-google-adk
```

## Configure

Edit `.specify/extensions/adk/adk-config.yml`:

| Key | Meaning |
|-----|---------|
| `agent_dir` | Folder of the agent package. |
| `model` | Model for newly designed agents. |
| `eval_dir` | Where evalsets are written (default `tests/eval`). |
| `criteria` | Criteria for `test_config.json` (local, no cloud service). |

## Traceability

Eval ids follow `us<N>-sc<M>`: user story `N`, acceptance scenario `M`. Results of
`adk eval` report the same ids.

## Example

[examples/colombia-guide](examples/colombia-guide) is a complete run: spec, plan with
ADK architecture, evalset, agent and evaluation report.

## Development

```bash
uv sync
uv run ruff check .
uv run pytest
```

## License

MIT

## Evaluation notes

- The default criterion is `final_response_match_v2` (LLM judge). Do not use
  `response_match_score` for free-text answers; it compares words and fails correct ones.
- Tool-call checks are off by default (`check_tools: false`): ids resolved at runtime and
  repeated calls make them fail without a real error.
- With MCP toolsets, `adk eval` may log `Connection closed` while cases run in parallel.
  Usually ADK retries and the run completes, but with many cases at once the agent can run
  without its tools (log line `will run without the tools from toolset`) and cases fail
  for that reason alone. Rerun failed cases individually with the `:ids` suffix
  (`file.evalset.json:us1-sc1,us1-sc2`) and run large evalsets in groups.
