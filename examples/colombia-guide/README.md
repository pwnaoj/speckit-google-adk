# Example: Colombia guide

An educational agent that answers questions about Colombia through the
[API Colombia](https://api-colombia.com) MCP server. It was produced with this extension:

| Step | Command | Result |
|------|---------|--------|
| Specification | `/speckit-specify` | `specs/001-colombia-guide/spec.md` |
| Plan | `/speckit-plan` + `/speckit-adk-design` | `specs/001-colombia-guide/plan.md` (`## ADK Architecture`) |
| Evaluation set | `/speckit-adk-evalset` | `tests/eval/` |
| Implementation | hand-written | `colombia_guide/` |
| Evaluation | `/speckit-adk-eval` | `specs/001-colombia-guide/eval-report.md` |
| Review | `/speckit-adk-review` | traceability OK (chat report) |

Run the evaluation from this folder (needs `google-adk[eval]` and `GEMINI_API_KEY`):

```bash
adk eval colombia_guide tests/eval/001-colombia-guide.evalset.json \
  --config_file_path tests/eval/test_config.json
```

Eval ids (`us1-sc1`, ...) match the acceptance scenarios in `spec.md`.
