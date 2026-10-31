"""Check that every acceptance scenario of spec.md has an eval case, and vice versa.

Usage: python3 check_traceability.py <spec.md> <evalset.json>

Scenario ids follow us<N>-sc<M>: user story N, numbered acceptance scenario M.
Exit code 0 when both sides match, 1 when there are gaps, 2 on bad usage.
"""

import json
import re
import sys
from pathlib import Path

STORY = re.compile(r"^#{2,4}\s*User Story\s+(\d+)\b", re.IGNORECASE)
SCENARIO = re.compile(r"^\s*(\d+)\.\s+\*\*Given\*\*", re.IGNORECASE)


def scenario_ids(spec_text: str) -> list[str]:
    """Return the scenario ids found in the text of a spec."""
    ids = []
    story = None
    for line in spec_text.splitlines():
        if match := STORY.match(line):
            story = match.group(1)
        elif story and (match := SCENARIO.match(line)):
            ids.append(f"us{story}-sc{match.group(1)}")
    return ids


def eval_ids(evalset: dict) -> list[str]:
    """Return the eval_id of every case in an evalset."""
    return [case.get("eval_id", "") for case in evalset.get("eval_cases", [])]


def compare(scenarios: list[str], cases: list[str]) -> tuple[list[str], list[str]]:
    """Return (scenarios without a case, cases without a scenario)."""
    return (
        [item for item in scenarios if item not in cases],
        [item for item in cases if item not in scenarios],
    )


def main(argv: list[str]) -> int:
    """Run the check and print the result."""
    if len(argv) != 3:
        print(__doc__)
        return 2
    try:
        spec_text = Path(argv[1]).read_text(encoding="utf-8")
        evalset = json.loads(Path(argv[2]).read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        print(f"ERROR: {error}")
        return 1
    scenarios = scenario_ids(spec_text)
    missing, extra = compare(scenarios, eval_ids(evalset))
    for item in missing:
        print(f"MISSING: scenario {item} has no eval case")
    for item in extra:
        print(f"EXTRA: eval case {item} has no scenario in the spec")
    if not scenarios:
        print("ERROR: no acceptance scenarios found in the spec")
    if not (missing or extra) and scenarios:
        print(f"OK: {len(scenarios)} scenarios match {len(scenarios)} eval cases")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
