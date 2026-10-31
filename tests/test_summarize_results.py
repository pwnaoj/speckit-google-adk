import json
import shutil
from pathlib import Path

import summarize_results as module

FIXTURE = Path(__file__).parent / "fixtures" / "evalset_result.json"


def test_summarize_rows_sorted_with_status_and_metrics():
    rows = module.summarize(json.loads(FIXTURE.read_text(encoding="utf-8")))
    assert [r[0] for r in rows] == ["us1-sc1", "us1-sc2", "us2-sc1", "us3-sc1"]
    assert rows[0][1] == "FAILED"
    assert rows[1][1] == "PASSED"
    assert "final_response_match_v2=0.20/0.8" in rows[0][2]


def test_main_returns_one_when_a_case_failed(capsys):
    assert module.main(["x", str(FIXTURE)]) == 1
    out = capsys.readouterr().out
    assert "Passed: 3  Failed: 1" in out


def test_directory_uses_newest_result(tmp_path):
    shutil.copy(FIXTURE, tmp_path / "a.evalset_result.json")
    assert module.latest_result(tmp_path).name == "a.evalset_result.json"
    assert module.latest_result(tmp_path / "empty") is None


def test_status_name():
    assert module.status_name(1) == "PASSED"
    assert module.status_name("FAILED") == "FAILED"
