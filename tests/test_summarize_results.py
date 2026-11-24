import json
import os
import shutil
from pathlib import Path

import summarize_results as module

FIXTURES = Path(__file__).parent / "fixtures"
FIXTURE = FIXTURES / "evalset_result.json"
MULTIRUN = FIXTURES / "evalset_result_multirun.json"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_summarize_rows_sorted_with_status_and_metrics():
    rows = module.summarize(load(FIXTURE))
    assert [r.eval_id for r in rows] == ["us1-sc1", "us1-sc2", "us2-sc1", "us3-sc1"]
    assert rows[0].status == "FAILED"
    assert rows[1].status == "PASSED"
    assert "final_response_match_v2=0.20/0.8" in rows[0].metrics
    assert not any(r.unstable for r in rows)


def test_failed_case_shows_the_answer_and_empty_is_flagged(capsys):
    rows = module.summarize(load(FIXTURE))
    assert rows[0].answer == "(empty response)"
    assert rows[3].answer == "No tengo datos del clima."
    assert module.main(["x", str(FIXTURE)]) == 1
    out = capsys.readouterr().out
    assert "Passed: 3  Failed: 1" in out
    assert "answer: (empty response)" in out
    assert "answer: No tengo" not in out


def test_multirun_result_uses_adk_summaries_and_marks_unstable(capsys):
    rows = {r.eval_id: r for r in module.summarize(load(MULTIRUN))}
    assert len(rows) == 3
    assert (rows["us1-sc1"].status, rows["us1-sc1"].passed_runs) == ("PASSED", 3)
    assert not rows["us1-sc1"].unstable
    assert rows["us1-sc2"].unstable and rows["us1-sc2"].passed_runs == 2
    assert rows["us1-sc2"].answer == "No puedo consultar."
    assert not rows["us2-sc1"].unstable and rows["us2-sc1"].status == "FAILED"
    assert module.main(["x", str(MULTIRUN)]) == 1
    out = capsys.readouterr().out
    line = "us1-sc2 | FAILED | final_response_match_v2=0.67/0.8 | 2/3 runs UNSTABLE"
    assert line in out
    assert "Passed: 1  Failed: 2  Unstable: 1" in out


def test_multirun_without_summaries_groups_runs_by_eval_id():
    result = load(MULTIRUN)
    del result["multi_run_case_summaries"]
    rows = {r.eval_id: r for r in module.summarize(result)}
    assert len(rows) == 3
    assert rows["us1-sc2"].status == "FAILED"
    assert rows["us1-sc2"].unstable and rows["us1-sc2"].runs == 3


def test_directory_without_since_uses_newest_result(tmp_path):
    shutil.copy(FIXTURE, tmp_path / "a.evalset_result.json")
    assert module.latest_result(tmp_path).name == "a.evalset_result.json"
    assert module.latest_result(tmp_path / "empty") is None


def test_since_reads_every_result_of_the_invocation(tmp_path):
    old, new1, new2 = (tmp_path / f"{n}.evalset_result.json" for n in "abc")
    for index, file in enumerate((old, new1, new2)):
        shutil.copy(FIXTURE, file)
        os.utime(file, (1000 + index * 100, 1000 + index * 100))
    assert module.result_files(tmp_path) == [new2]
    assert module.result_files(tmp_path, since=1100) == [new1, new2]


def test_several_folders_are_summarized_together(tmp_path, capsys):
    main_dir, variant_dir = tmp_path / "main", tmp_path / "variant"
    for folder, source in ((main_dir, FIXTURE), (variant_dir, MULTIRUN)):
        folder.mkdir()
        shutil.copy(source, folder / "x.evalset_result.json")
    assert module.main(["x", str(main_dir), str(variant_dir)]) == 1
    out = capsys.readouterr().out
    assert out.count("Result file:") == 2
    assert "Passed: 4  Failed: 3  Unstable: 1" in out


def test_no_results_or_bad_usage_exit_2(tmp_path, capsys):
    assert module.main(["x", str(tmp_path)]) == 2
    assert module.main(["x"]) == 2
    assert module.main(["x", str(tmp_path), "--since", "abc"]) == 2
    assert module.main(["x", str(tmp_path), "--since"]) == 2
    assert "no *.evalset_result.json" in capsys.readouterr().out


def test_status_name_knows_informational():
    assert module.status_name(1) == "PASSED"
    assert module.status_name(4) == "INFORMATIONAL"
    assert module.status_name("FAILED") == "FAILED"
