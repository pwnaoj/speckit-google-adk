## ADK Architecture

### Pattern

**Chosen**: [Agent | SequentialAgent | ParallelAgent | LoopAgent | Workflow (graph)]

**Why**: [One or two sentences tied to the spec. Start from a single Agent and justify anything more.]

### Agents

| Name | Role | Model | Tools | output_key |
|------|------|-------|-------|------------|
| [root_agent] | [what it decides or produces] | [model] | [tool names] | [state key or -] |

### Tools

| Name | Purpose | Inputs | Output | Spec ref |
|------|---------|--------|--------|----------|
| [tool_name] | [one line] | [typed parameters] | [return shape] | [FR-001] |

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
