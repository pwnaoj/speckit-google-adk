## ADK Architecture

### Pattern

**Chosen**: [Agent | SequentialAgent | ParallelAgent | LoopAgent | Workflow (graph)]

**Why**: [One or two sentences tied to the spec. Start from a single Agent and justify anything more.]

### Agent package

**Folder**: [snake_case_name]/ (contains `__init__.py`, `agent.py` and `root_agent`)

### Agents

| Name | Role | Model | Tools | output_key |
|------|------|-------|-------|------------|
| [root_agent] | [what it decides or produces] | [model] | [tool names] | [state key or -] |

### Tools

| Name | Source | Purpose | Inputs | Output | Spec ref |
|------|--------|---------|--------|--------|----------|
| [tool_name] | [function / McpToolset / built-in] | [one line] | [typed parameters] | [return shape] | [FR-001] |

### State contract

| Key | Written by | Read by | Meaning |
|-----|-----------|---------|---------|
| [key] | [agent] | [agent] | [what it holds] |

### Guardrails

- [What the agent must not do, from the spec and the constitution]

### Evaluation

Every acceptance scenario in `spec.md` becomes one eval case with id `us<N>-sc<M>`.
Generate them with the ADK evalset command (`speckit.adk.evalset`).

### Risks

- [Loops, tool hallucination, cost, missing credentials, ...]
