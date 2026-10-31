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

Both are offered as optional hooks after `/speckit-plan` and `/speckit-tasks`.

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

## Development

```bash
uv sync
uv run ruff check .
uv run pytest
```

## License

MIT
