---
description: "Check traceability between spec.md, plan.md and the ADK evalset"
---

# ADK Review

Read-only check that the specification, the ADK design and the evaluation set agree.
It does not modify any file.

## User Input

$ARGUMENTS

Consider the user input before proceeding (if not empty).

## Steps

1. Run `.specify/scripts/bash/check-prerequisites.sh --json --require-spec` from the
   project root and read `FEATURE_DIR`. The feature name is its last path segment.
2. Read `.specify/extensions/adk/adk-config.yml` for `eval_dir`.
3. Run `python3 .specify/extensions/adk/scripts/check_traceability.py
   FEATURE_DIR/spec.md <eval_dir>/<feature-name>.evalset.json` and report every
   `MISSING` and `EXTRA` line.
4. Run `python3 .specify/extensions/adk/scripts/validate_evalset.py
   <eval_dir>/<feature-name>.evalset.json` and report its errors.
5. Read the `## ADK Architecture` section of `FEATURE_DIR/plan.md`. If it is missing,
   report it and suggest `__SPECKIT_COMMAND_ADK_DESIGN__`. Otherwise check that:
   - every functional requirement (`FR-xxx`) of the spec is referenced by at least one
     tool or agent, or by a guardrail;
   - every tool in the Tools table cites at least one `FR-xxx` that exists in the spec;
   - the chosen pattern is the simplest that the spec needs.
6. Print a short report with three sections (Traceability, Evalset, Design) and a
   final verdict: `OK`, or the list of items to fix, each with the command that fixes it.
   Report non-blocking observations as `Warnings`; they do not change the verdict.

## Rules

- Do not modify files; only report.
- Quote the id or requirement for every finding.
- Do not invent findings; if a check cannot be done, say why.
