# Example: Colombia en tus manos

[`colombia-en-tus-manos/`](colombia-en-tus-manos) is a snapshot of a real project built with
this extension: an educational agent, in Spanish, that answers questions about Colombia using
the API Colombia MCP server. It is a reference to read, not part of the extension, and it is
not installed with it.

| | |
|---|---|
| Source commit | `7cd03f5` of the original project (branch `001-colombia-educational-agent`) |
| Spec Kit | 1.2.6.dev0, Claude Code integration |
| Google ADK | 2.13.0 |
| Extension | 0.1.0 |

The snapshot is **not kept in sync** with the extension. If the commands change, the example
may lag behind them.

## What each step produced

| Step | Result in the snapshot |
|------|------------------------|
| `/speckit-constitution` | [`constitution.md`](colombia-en-tus-manos/constitution.md) (in the project: `.specify/memory/constitution.md`) |
| `/speckit-specify` | [`spec.md`](colombia-en-tus-manos/specs/001-colombia-educational-agent/spec.md): 4 user stories, 13 acceptance scenarios |
| `/speckit-plan` | [`plan.md`](colombia-en-tus-manos/specs/001-colombia-educational-agent/plan.md), `research.md`, `data-model.md`, `contracts/`, `quickstart.md` |
| **`/speckit-adk-design`** | The `## ADK Architecture` section of `plan.md`: alternatives considered, guardrails with the scenario that exercises each one, evaluation plan |
| `/speckit-tasks` | [`tasks.md`](colombia-en-tus-manos/specs/001-colombia-educational-agent/tasks.md) |
| **`/speckit-adk-evalset`** | [`tests/eval/`](colombia-en-tus-manos/tests/eval) |
| `/speckit-implement` | The agent package [`colombia_en_tus_manos/`](colombia-en-tus-manos/colombia_en_tus_manos) |
| **`/speckit-adk-eval`** | [`eval-report.md`](colombia-en-tus-manos/specs/001-colombia-educational-agent/eval-report.md): 13 of 13 cases passed, run in groups of 3 |

## What is worth reading

- **Guardrails table** in the plan: two requirements (read-only and no personal data) had no
  scenario; the table made that visible and one scenario (`us4-sc6`) was added afterwards.
- **Scenarios with a simulated service** (`us4-sc4`, `us4-sc5`): test-only variants of the agent
  in [`tests/sim/`](colombia-en-tus-manos/tests/sim), each with its own evalset in
  `tests/eval/sim/`. This is the pattern described in the extension README.
- **Evaluation in groups**: the project README and `quickstart.md` show how the cases are run
  three at a time, because many cases at once make the MCP server close connections.

## Not included

`.claude/` and `.specify/` (copies of the installed extension and Spec Kit), `uv.lock`,
editor settings, the author's drafts (`docs/`) and any local evaluation history.
