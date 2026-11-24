"""Summarize `adk eval` result files, one line per eval case.

Usage:
    python3 summarize_results.py <path>... [--since EPOCH_SECONDS]

Each <path> is a *.evalset_result.json file or an `.adk/eval_history` folder. Pass one
folder per agent folder that was evaluated (simulated-service variants have their own).
For a folder, without `--since` only the newest result is read; with `--since` every
result modified at or after that time is read, so one invocation that ran several
evalsets is summarized as a whole.

With several runs per case (`adk eval --num_runs N`) each case shows `k/N` passed runs
and is marked UNSTABLE when some runs passed and some did not. The case status is
ADK's verdict over all its runs. A final `Cost` line adds up the agent's model calls,
tool calls, tokens and duration over all invocations of all runs.

Exit code: 0 every case passed, 1 any case did not pass, 2 bad usage or no results.
"""

import json
import sys
from dataclasses import dataclass
from pathlib import Path

STATUS = {1: "PASSED", 2: "FAILED", 3: "NOT_EVALUATED", 4: "INFORMATIONAL"}
ANSWER_LIMIT = 300
COST_METRICS = {
    "inference_call_count_v1": "model_calls",
    "tool_call_count_v1": "tool_calls",
    "token_usage_v1": "tokens",
}
DURATION_METRIC = "invocation_duration_v1"
SINCE_TOLERANCE = 1.0  # seconds; file times can be slightly earlier than `date +%s`


@dataclass
class Row:
    """One eval case of one result file."""

    eval_id: str
    status: str
    metrics: str
    answer: str
    runs: int = 1
    passed_runs: int | None = None

    @property
    def unstable(self) -> bool:
        """True when some runs of the case passed and some did not."""
        return self.passed_runs is not None and 0 < self.passed_runs < self.runs


def result_files(path: Path, since: float | None = None) -> list[Path]:
    """Return the result files to read for a file or an eval_history folder."""
    if path.is_file():
        return [path]
    files = sorted(path.glob("*.evalset_result.json"), key=lambda p: p.stat().st_mtime)
    if since is None:
        return files[-1:]
    return [f for f in files if f.stat().st_mtime >= since - SINCE_TOLERANCE]


def latest_result(path: Path) -> Path | None:
    """Return the result file to read: the path itself or the newest in a folder."""
    files = result_files(path)
    return files[0] if files else None


def status_name(value: int | str) -> str:
    """Return a readable status for ADK's numeric or textual status."""
    return STATUS.get(value, str(value)) if isinstance(value, int) else str(value)


def _format_metrics(results: list[dict]) -> str:
    """Describe the metrics that have a threshold as name=score/threshold."""
    return ", ".join(
        f"{m['metric_name']}={m['score']:.2f}/{m['threshold']}"
        for m in results
        if m.get("threshold") is not None and m.get("score") is not None
    )


def metric_text(case: dict) -> str:
    """Describe the case's metrics that have a threshold, from its first invocation."""
    for invocation in case.get("eval_metric_result_per_invocation", []):
        return _format_metrics(invocation.get("eval_metric_results", []))
    return ""


def answer_text(case: dict) -> str:
    """Return the agent's final answer of the first invocation, shortened."""
    for invocation in case.get("eval_metric_result_per_invocation", []):
        actual = invocation.get("actual_invocation") or {}
        parts = (actual.get("final_response") or {}).get("parts") or [{}]
        text = " ".join((parts[0].get("text") or "").split())
        return text[:ANSWER_LIMIT] or "(empty response)"
    return "(no invocation)"


def _is_failed(case: dict) -> bool:
    return status_name(case["final_eval_status"]) != "PASSED"


def _case_runs(result: dict) -> dict[str, list[dict]]:
    """Group the per-run case results by eval id."""
    runs: dict[str, list[dict]] = {}
    for case in result.get("eval_case_results", []):
        runs.setdefault(case["eval_id"], []).append(case)
    return runs


def summarize(result: dict) -> list[Row]:
    """Return one Row per case, sorted by id.

    Uses ADK's `multi_run_case_summaries` when present (several runs per case) and
    otherwise the case results themselves.
    """
    runs = _case_runs(result)
    summaries = {s["eval_id"]: s for s in result.get("multi_run_case_summaries") or []}
    rows = []
    for eval_id, cases in runs.items():
        summary = summaries.get(eval_id)
        if summary is not None:
            status = status_name(summary["final_eval_status"])
            metrics = _format_metrics(summary.get("overall_eval_metric_results", []))
            n_runs, passed = summary["num_runs"], summary["passed_runs"]
        else:
            # Without a summary the status is the worst of the runs.
            status = "FAILED" if any(_is_failed(c) for c in cases) else status_name(
                cases[0]["final_eval_status"]
            )
            metrics = metric_text(cases[0])
            n_runs = len(cases)
            passed = sum(not _is_failed(c) for c in cases) if n_runs > 1 else None
        shown = next((c for c in cases if _is_failed(c)), cases[0])
        rows.append(Row(eval_id, status, metrics, answer_text(shown), n_runs, passed))
    return sorted(rows, key=lambda row: row.eval_id)


def cost_totals(result: dict) -> dict[str, float]:
    """Add up the cost metrics ADK records for every invocation of every run.

    They describe the agent only: judge model calls are not included. Returns an empty
    dict when the result has no cost metrics.
    """
    totals: dict[str, float] = {}
    for case in result.get("eval_case_results", []):
        for invocation in case.get("eval_metric_result_per_invocation", []):
            counted = False
            for metric in invocation.get("eval_metric_results", []):
                name, score = metric.get("metric_name"), metric.get("score")
                known = name in COST_METRICS or name == DURATION_METRIC
                if score is None or not known:
                    continue
                if not counted:
                    totals["invocations"] = totals.get("invocations", 0) + 1
                    counted = True
                if name in COST_METRICS:
                    key = COST_METRICS[name]
                    totals[key] = totals.get(key, 0) + score
                elif name == DURATION_METRIC:
                    totals["seconds"] = totals.get("seconds", 0) + score
                    totals["max_seconds"] = max(totals.get("max_seconds", 0), score)
    return totals


def merge_costs(costs: list[dict[str, float]]) -> dict[str, float]:
    """Combine the cost totals of several result files."""
    merged: dict[str, float] = {}
    for cost in costs:
        for key, value in cost.items():
            if key == "max_seconds":
                merged[key] = max(merged.get(key, 0), value)
            else:
                merged[key] = merged.get(key, 0) + value
    return merged


def cost_line(cost: dict[str, float]) -> str:
    """Describe the cost totals in one line, or return an empty string."""
    if not cost:
        return ""
    parts = [f"invocations={cost.get('invocations', 0):.0f}"]
    for key in ("model_calls", "tool_calls", "tokens"):
        if key in cost:
            parts.append(f"{key}={cost[key]:.0f}")
    if "seconds" in cost:
        parts.append(f"seconds_total={cost['seconds']:.1f}")
        parts.append(f"seconds_max={cost['max_seconds']:.1f}")
    return "Cost (agent only, judge not included): " + " ".join(parts)


def _parse_args(argv: list[str]) -> tuple[list[Path], float | None] | None:
    """Return (paths, since), or None when the arguments are not valid."""
    paths, since, args = [], None, iter(argv[1:])
    for arg in args:
        if arg == "--since":
            try:
                since = float(next(args))
            except (StopIteration, ValueError):
                return None
        else:
            paths.append(Path(arg))
    return (paths, since) if paths else None


def main(argv: list[str]) -> int:
    """Print the summary and return the exit code."""
    parsed = _parse_args(argv)
    if parsed is None:
        print(__doc__)
        return 2
    paths, since = parsed
    files = [f for path in paths for f in result_files(path, since)]
    if not files:
        print(f"ERROR: no *.evalset_result.json found in {' '.join(map(str, paths))}")
        return 2
    total = passed = unstable = 0
    costs = []
    for file in files:
        try:
            result = json.loads(file.read_text(encoding="utf-8"))
            rows = summarize(result)
            costs.append(cost_totals(result))
        except (OSError, ValueError, KeyError) as error:
            print(f"ERROR: cannot read {file}: {error}")
            return 2
        print(f"Result file: {file}")
        for row in rows:
            runs = f" | {row.passed_runs}/{row.runs} runs" if row.runs > 1 else ""
            flag = " UNSTABLE" if row.unstable else ""
            print(f"{row.eval_id} | {row.status} | {row.metrics}{runs}{flag}")
            if row.status != "PASSED":
                print(f"    answer: {row.answer}")
        total += len(rows)
        passed += sum(row.status == "PASSED" for row in rows)
        unstable += sum(row.unstable for row in rows)
    line = f"Passed: {passed}  Failed: {total - passed}"
    print(line + (f"  Unstable: {unstable}" if unstable else ""))
    if cost := cost_line(merge_costs(costs)):
        print(cost)
    return 1 if passed < total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
