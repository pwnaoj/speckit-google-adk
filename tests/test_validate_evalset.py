import copy
import json
from pathlib import Path

import validate_evalset as module

FIXTURES = Path(__file__).parent / "fixtures"


def load():
    return json.loads((FIXTURES / "evalset.json").read_text(encoding="utf-8"))


def test_fixture_is_valid():
    assert module.structural_errors(load()) == []


def test_main_ok_and_exit_codes(capsys):
    assert module.main(["x", str(FIXTURES / "evalset.json")]) == 0
    assert module.main(["x"]) == 2
    assert module.main(["x", str(FIXTURES / "missing.json")]) == 1


def test_bad_id_and_duplicate():
    data = load()
    data["eval_cases"][0]["eval_id"] = "case-1"
    data["eval_cases"][1]["eval_id"] = data["eval_cases"][2]["eval_id"]
    errors = module.structural_errors(data)
    assert any("us<N>-sc<M>" in e for e in errors)
    assert any("duplicated" in e for e in errors)


def test_missing_parts():
    data = copy.deepcopy(load())
    case = data["eval_cases"][0]
    case["conversation"] = []
    del case["session_input"]
    errors = module.structural_errors(data)
    assert any("conversation is empty" in e for e in errors)
    assert any("app_name" in e for e in errors)


def test_empty_cases():
    assert module.structural_errors({"eval_set_id": "x", "eval_cases": []})
