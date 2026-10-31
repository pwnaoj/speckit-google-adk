"""Summarize an `adk eval` result file, one line per eval id.

Usage: python3 summarize_results.py <result.evalset_result.json | eval_history_dir>

When given a directory, the newest *.evalset_result.json inside it is used.
Exit code 0 when every case passed, 1 when any failed, 2 on bad usage.
"""

import json
import sys
from pathlib import Path

STATUS = {1: "PASSED", 2: "FAILED", 3: "NOT_EVALUATED"}


def latest_result(path: Path) -> Path | None:
    """Return the result file to read: the path itself or the newest in a folder."""
    if path.is_file():
        return path
    files = sorted(path.glob("*.evalset_result.json"), key=lambda p: p.stat().st_mtime)
    return files[-1] if files else None


def status_name(value: int | str) -> str:
    """Return a readable status for ADK's numeric or textual status."""
    return STATUS.get(value, str(value)) if isinstance(value, int) else str(value)


def metric_text(case: dict) -> str:
    """Describe the metrics that have a threshold as name=score/threshold."""
    parts = []
    for invocation in case.get("eval_metric_result_per_invocation", []):
        for metric in invocation.get("eval_metric_results", []):
            if metric.get("threshold") is None or metric.get("score") is None:
                continue
            parts.append(
                f"{metric['metric_name']}={metric['score']:.2f}/{metric['threshold']}"
            )
    return ", ".join(parts)


def summarize(result: dict) -> list[tuple[str, str, str]]:
    """Return (eval_id, status, metrics) for every case, sorted by id."""
    rows = [
        (
            case["eval_id"],
            status_name(case["final_eval_status"]),
            metric_text(case),
        )
        for case in result.get("eval_case_results", [])
    ]
    return sorted(rows)


def main(argv: list[str]) -> int:
    """Print the summary and return the exit code."""
    if len(argv) != 2:
        print(__doc__)
        return 2
    path = latest_result(Path(argv[1]))
    if path is None:
        print(f"ERROR: no *.evalset_result.json in {argv[1]}")
        return 1
    try:
        rows = summarize(json.loads(path.read_text(encoding="utf-8")))
    except (OSError, ValueError, KeyError) as error:
        print(f"ERROR: cannot read {path}: {error}")
        return 1
    print(f"Result file: {path}")
    for eval_id, status, metrics in rows:
        print(f"{eval_id} | {status} | {metrics}")
    failed = [row for row in rows if row[1] != "PASSED"]
    print(f"Passed: {len(rows) - len(failed)}  Failed: {len(failed)}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
