import json
import subprocess

import eval_provenance as module


def make_project(tmp_path):
    agent = tmp_path / "my_agent"
    (agent / "__pycache__").mkdir(parents=True)
    (agent / ".adk" / "eval_history").mkdir(parents=True)
    (agent / "agent.py").write_text('root = Agent(model="gemini-x", name="a")\n')
    (agent / "prompt.md").write_text("Be brief.")
    (agent / ".env").write_text("SECRET=1")
    (agent / "__pycache__" / "agent.pyc").write_bytes(b"\x00")
    (agent / ".adk" / "eval_history" / "r.evalset_result.json").write_text("{}")
    evalset = tmp_path / "f.evalset.json"
    evalset.write_text("{}")
    config = tmp_path / "test_config.json"
    config.write_text(
        json.dumps(
            {"criteria": {"final_response_match_v2": {
                "threshold": 0.8, "judge_model_options": {"judge_model": "judge-y"}}}}
        )
    )
    return agent, evalset, config


def test_package_hash_ignores_secrets_caches_and_results(tmp_path):
    agent, _, _ = make_project(tmp_path)
    before = module.package_hash(agent)
    (agent / ".env").write_text("SECRET=2")
    (agent / ".adk" / "eval_history" / "new.evalset_result.json").write_text("{}")
    assert module.package_hash(agent) == before
    (agent / "prompt.md").write_text("Be long.")
    assert module.package_hash(agent) != before


def test_models_are_read_from_config_and_code(tmp_path):
    agent, _, config = make_project(tmp_path)
    assert module.agent_models(agent) == ["gemini-x"]
    assert module.judge_models(json.loads(config.read_text())) == ["judge-y"]
    assert module.judge_models({}) == []


def test_main_prints_all_fields_and_marks_dirty_tree(tmp_path, monkeypatch, capsys):
    agent, evalset, config = make_project(tmp_path)
    monkeypatch.chdir(tmp_path)
    for cmd in (["init", "-q"], ["add", "-A"],
                ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "x"]):
        subprocess.run(["git", *cmd], cwd=tmp_path, check=True)
    argv = ["x", "--agent-dir", str(agent), "--evalset", str(evalset),
            "--config", str(config), "--repeats", "3", "--adk-version", "2.15.0"]
    assert module.main(argv) == 0
    out = capsys.readouterr().out
    assert "- Commit: " in out and "uncommitted" not in out
    assert "- google-adk: 2.15.0" in out and "- Repeats per case: 3" in out
    assert "Judge model: judge-y" in out and "found in code): gemini-x" in out
    (agent / "prompt.md").write_text("changed")
    module.main(argv)
    assert "(uncommitted changes)" in capsys.readouterr().out


def test_missing_file_or_bad_usage_exit_2(tmp_path, capsys):
    agent, evalset, config = make_project(tmp_path)
    missing = ["x", "--agent-dir", str(agent), "--evalset", str(tmp_path / "no.json"),
               "--config", str(config)]
    assert module.main(missing) == 2
    assert module.main(["x"]) == 2
