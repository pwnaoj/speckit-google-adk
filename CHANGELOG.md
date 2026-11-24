# Changelog

## 0.2.0

- Requires `google-adk[eval]` 2.15.0 or later.
- `eval`: checks authentication for any provider (API key, Vertex AI / Enterprise, other)
  without printing secrets; stops if there is none.
- `eval`: optional `preflight_command` must pass before evaluating.
- `eval`: a non-zero exit code of `adk eval` is a result; it is an error only when no new
  result file appears.
- `eval`: `repeats` runs each case N times (`--num_runs`); the report shows `k/N` and
  flags unstable cases.
- `summarize_results.py`: takes several files or folders and `--since`, so all results of
  one invocation are summarized; groups repeated runs by case, uses ADK's
  `multi_run_case_summaries`, knows status 4 (INFORMATIONAL); exits 2 when it finds no
  results.
- `summarize_results.py`: adds a `Cost` line (agent model calls, tool calls, tokens and
  time over all invocations of all runs; the judge is not included).
- `summarize_results.py`: a case with no invocation (ADK writes it as FAILED when the agent
  never answers, for example without credentials) is shown as ERROR, not counted as an
  agent failure; exit 2 when every case is an ERROR. Found in a real run without
  credentials.
- Docs: what was tested end to end, `--parallelism` with MCP toolsets and judge variance.
- Add `eval_provenance.py`: commit, hashes of evalset, test config and agent package,
  judge and agent models, repeats and date.
- `eval` writes the provenance and cost in `eval-report.md` and appends a row to
  `eval-history.md`.

## 0.1.0 (2026-11-02)

- Add `speckit.adk.design` and `speckit.adk.evalset`.
- Add `speckit.adk.eval` and `speckit.adk.review`, and the `after_implement` hook.
- Add scripts to validate evalsets, check traceability and summarize results.
- Add plan section, evalset and configuration templates.
- Default criterion is `final_response_match_v2`; tool-call checks are opt-in.
- Add an example (a snapshot of a real project) and pytest/ruff checks.
- `design`: alternatives considered, guardrails table with mechanism and the scenario that
  verifies each one, a coverage check, a coordinator pattern and a note on ADK Skills
  (experimental). The column is named *Exercised by*: it records which scenario exercises a
  limit, not that the evaluation would detect its violation.
