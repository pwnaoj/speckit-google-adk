"""Print the provenance of an evaluation run as markdown bullets.

Usage:
    python3 eval_provenance.py --agent-dir DIR --evalset FILE --config FILE
                               [--repeats N] [--adk-version X]

Prints what is needed to reproduce and compare a run: date, git commit (and whether
the working tree had uncommitted changes), ADK version (given by the caller, because
this script runs with the system Python), hashes of the evalset, the test configuration
and the agent package, the judge model(s) declared in the configuration and the agent
model(s) found in the code (a text search, so it can miss or over-report), and the
repetitions.
Exit code: 0 printed, 2 bad usage or a missing file.
"""

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

IGNORED_DIRS = {".adk", "__pycache__", ".git", ".venv"}
MODEL_PATTERN = re.compile(r"""\bmodel\s*=\s*["']([\w.\-/:]+)["']""")


def short_hash(data: bytes) -> str:
    """Return the first 12 hex digits of the SHA-256 of the data."""
    return hashlib.sha256(data).hexdigest()[:12]


def package_files(agent_dir: Path) -> list[Path]:
    """Return the files of the agent package that define its behaviour, sorted."""
    return sorted(
        path
        for path in agent_dir.rglob("*")
        if path.is_file()
        and not IGNORED_DIRS & set(path.relative_to(agent_dir).parts)
        and not path.name.startswith(".env")
        and path.suffix != ".pyc"
    )


def package_hash(agent_dir: Path) -> str:
    """Hash the names and contents of the agent package files."""
    digest = hashlib.sha256()
    for path in package_files(agent_dir):
        digest.update(str(path.relative_to(agent_dir)).encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()[:12]


def agent_models(agent_dir: Path) -> list[str]:
    """Return the names assigned with `model="..."` in the package's Python files."""
    found = set()
    for path in package_files(agent_dir):
        if path.suffix == ".py":
            text = path.read_text(encoding="utf-8", errors="replace")
            found.update(MODEL_PATTERN.findall(text))
    return sorted(found)


def judge_models(config: dict) -> list[str]:
    """Return the judge models declared in the criteria of a test configuration."""
    models = set()
    for criterion in (config.get("criteria") or {}).values():
        if isinstance(criterion, dict):
            options = criterion.get("judge_model_options") or {}
            if options.get("judge_model"):
                models.add(options["judge_model"])
    return sorted(models)


def git_state(cwd: Path) -> str:
    """Return the short commit, with a note when the working tree has changes."""
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=cwd, capture_output=True, text=True, check=True,
        ).stdout.strip()
        dirty = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=cwd, capture_output=True, text=True, check=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "not a git repository"
    return commit + (" (uncommitted changes)" if dirty else "")


def build_lines(args: argparse.Namespace) -> list[str]:
    """Return the provenance bullets."""
    agent_dir, evalset, config_path = args.agent_dir, args.evalset, args.config
    config = json.loads(config_path.read_text(encoding="utf-8"))
    judges = judge_models(config)
    agents = agent_models(agent_dir)
    return [
        f"- Date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        f"- Commit: {git_state(Path.cwd())}",
        f"- google-adk: {args.adk_version or 'not given'}",
        f"- Evalset: {evalset.name} sha256:{short_hash(evalset.read_bytes())}",
        f"- Test config: {config_path.name} "
        f"sha256:{short_hash(config_path.read_bytes())}",
        f"- Agent package: {agent_dir.name} sha256:{package_hash(agent_dir)}",
        f"- Judge model: {', '.join(judges) or 'not declared (ADK default)'}",
        f"- Agent model (found in code): {', '.join(agents) or 'not found'}",
        f"- Repeats per case: {args.repeats}",
    ]


def main(argv: list[str]) -> int:
    """Print the provenance and return the exit code."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--agent-dir", type=Path, required=True)
    parser.add_argument("--evalset", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--repeats", type=int, default=1)
    parser.add_argument("--adk-version", default="")
    try:
        args = parser.parse_args(argv[1:])
    except SystemExit:
        return 2
    try:
        lines = build_lines(args)
    except (OSError, ValueError) as error:
        print(f"ERROR: {error}")
        return 2
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
