import json
from pathlib import Path

import check_traceability as module

FIXTURES = Path(__file__).parent / "fixtures"


def test_scenario_ids_from_spec():
    text = (FIXTURES / "spec.md").read_text(encoding="utf-8")
    assert module.scenario_ids(text) == ["us1-sc1", "us1-sc2", "us2-sc1", "us3-sc1"]


def test_scenarios_outside_a_story_are_ignored():
    assert module.scenario_ids("1. **Given** x, **When** y, **Then** z") == []


def test_compare_reports_both_directions():
    missing, extra = module.compare(["us1-sc1", "us1-sc2"], ["us1-sc1", "us9-sc1"])
    assert missing == ["us1-sc2"]
    assert extra == ["us9-sc1"]


def test_main_exit_codes(tmp_path, capsys):
    spec = str(FIXTURES / "spec.md")
    assert module.main(["x", spec, str(FIXTURES / "evalset.json")]) == 0
    partial = json.loads((FIXTURES / "evalset.json").read_text(encoding="utf-8"))
    partial["eval_cases"].pop()
    path = tmp_path / "partial.json"
    path.write_text(json.dumps(partial), encoding="utf-8")
    assert module.main(["x", spec, str(path)]) == 1
    assert "MISSING" in capsys.readouterr().out
    assert module.main(["x"]) == 2
