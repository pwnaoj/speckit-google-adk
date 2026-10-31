"""Validate an ADK evalset generated from spec.md.

Usage: python3 validate_evalset.py <evalset.json>

Exit code 0 when valid, 1 when there are errors, 2 on bad usage.
"""

import json
import re
import sys
from pathlib import Path

ID_PATTERN = re.compile(r"^us\d+-sc\d+$")


def structural_errors(data: dict) -> list[str]:
    """Return the problems found in the evalset structure."""
    errors = []
    if not data.get("eval_set_id"):
        errors.append("eval_set_id is missing")
    cases = data.get("eval_cases")
    if not isinstance(cases, list) or not cases:
        return errors + ["eval_cases must be a non-empty list"]
    seen = set()
    for index, case in enumerate(cases):
        errors += case_errors(case, index, seen)
    return errors


def case_errors(case: dict, index: int, seen: set[str]) -> list[str]:
    """Return the problems found in one eval case."""
    eval_id = case.get("eval_id", "")
    label = eval_id or f"eval_cases[{index}]"
    errors = []
    if not ID_PATTERN.match(eval_id):
        errors.append(f"{label}: eval_id must look like us<N>-sc<M>")
    if eval_id in seen:
        errors.append(f"{label}: duplicated eval_id")
    seen.add(eval_id)
    if not case.get("conversation"):
        errors.append(f"{label}: conversation is empty")
    elif not user_text(case["conversation"][0]):
        errors.append(f"{label}: first invocation has no user text")
    if not (case.get("session_input") or {}).get("app_name"):
        errors.append(f"{label}: session_input.app_name is missing")
    return errors


def user_text(invocation: dict) -> str:
    """Return the user message text of an invocation, or an empty string."""
    parts = (invocation.get("user_content") or {}).get("parts") or [{}]
    return parts[0].get("text", "")


def adk_errors(raw: str) -> list[str]:
    """Validate with ADK's own EvalSet model when google-adk is installed."""
    try:
        from google.adk.evaluation.eval_set import EvalSet
    except ImportError:
        return []
    try:
        EvalSet.model_validate_json(raw)
    except ValueError as error:
        return [f"ADK EvalSet validation failed: {error}"]
    return []


def main(argv: list[str]) -> int:
    """Run the validation and print the result."""
    if len(argv) != 2:
        print(__doc__)
        return 2
    path = Path(argv[1])
    try:
        raw = path.read_text(encoding="utf-8")
        data = json.loads(raw)
    except (OSError, ValueError) as error:
        print(f"ERROR: cannot read {path}: {error}")
        return 1
    errors = structural_errors(data) + adk_errors(raw)
    for error in errors:
        print(f"ERROR: {error}")
    if not errors:
        print(f"OK: {len(data['eval_cases'])} eval cases in {path}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
