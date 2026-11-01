## ADK Architecture

### Pattern

**Chosen**: [Agent | SequentialAgent | ParallelAgent | LoopAgent | Workflow (graph)]

**Why**: [One or two sentences tied to the spec. Start from a single Agent and justify anything more.]

### Agent package

**Folder**: [snake_case_name]/

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

**Evalset**: [<eval_dir>/<feature-dir-name>.evalset.json]

**Cases**: [number of acceptance scenarios; one case each]

**Criteria**: [criteria and thresholds from the configuration; tool-call checks on or off]

**Needs a simulated service**: [ids of the scenarios whose Given changes what the data
service returns (error, empty or hostile content) and how they are simulated; "none" if no
scenario needs it]

### Risks

- [Loops, tool hallucination, cost, missing credentials, ...]
