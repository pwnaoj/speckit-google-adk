import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = yaml.safe_load((ROOT / "extension.yml").read_text(encoding="utf-8"))


def declared_files():
    provides = MANIFEST["provides"]
    for kind in ("commands", "templates", "scripts"):
        for item in provides.get(kind, []):
            yield item["file"]
    for item in provides.get("config", []):
        yield item["template"]


def test_schema_and_identity():
    ext = MANIFEST["extension"]
    assert MANIFEST["schema_version"] == "1.0"
    assert re.fullmatch(r"[a-z0-9-]+", ext["id"])
    assert re.fullmatch(r"\d+\.\d+\.\d+", ext["version"])


def test_declared_files_exist():
    for file in declared_files():
        assert (ROOT / file).is_file(), file


def test_command_names_follow_extension_id():
    ext_id = MANIFEST["extension"]["id"]
    pattern = re.compile(rf"^speckit\.{ext_id}\.[a-z0-9-]+$")
    for command in MANIFEST["provides"]["commands"]:
        assert pattern.match(command["name"]), command["name"]


def test_hooks_reference_declared_commands():
    names = {c["name"] for c in MANIFEST["provides"]["commands"]}
    for event, hook in MANIFEST["hooks"].items():
        assert hook["command"] in names, event


def test_command_files_have_description_frontmatter():
    for command in MANIFEST["provides"]["commands"]:
        text = (ROOT / command["file"]).read_text(encoding="utf-8")
        assert text.startswith("---\ndescription:"), command["file"]


def test_command_scripts_are_declared():
    declared = {Path(f).name for f in declared_files()}
    for command in MANIFEST["provides"]["commands"]:
        text = (ROOT / command["file"]).read_text(encoding="utf-8")
        for script in re.findall(r"scripts/(\w+\.py)", text):
            assert script in declared, script


def test_template_and_script_names_are_lowercase_with_hyphens():
    pattern = re.compile(r"^[a-z0-9-]+$")
    provides = MANIFEST["provides"]
    for kind in ("templates", "scripts"):
        for item in provides.get(kind, []):
            assert pattern.match(item["name"]), item["name"]


def test_commands_support_both_prerequisite_script_flavors():
    for command in MANIFEST["provides"]["commands"]:
        text = (ROOT / command["file"]).read_text(encoding="utf-8")
        if "check-prerequisites.sh" in text:
            assert "check_prerequisites.py" in text, command["file"]


def test_plan_section_template_asks_for_project_specific_evaluation():
    text = (ROOT / "templates" / "adk-plan-section.md").read_text(encoding="utf-8")
    assert "Needs a simulated service" in text
    assert "__SPECKIT_COMMAND" not in text


def test_design_reads_the_planning_artifacts():
    text = (ROOT / "commands" / "design.md").read_text(encoding="utf-8")
    assert "research.md" in text
    assert "contracts/" in text
