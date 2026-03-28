# tests/test_telemetry_writer.py
"""Tests for telemetry trace writer."""
import json
import os
import subprocess
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib


def _setup_user_dir(tmp_path: Path) -> Path:
    """Create a user dir with telemetry enabled."""
    user_dir = tmp_path / ".tasty-dev"
    user_dir.mkdir()
    (user_dir / "telemetry").mkdir()
    (user_dir / "config.toml").write_text('[telemetry]\nenabled = true\n')
    return user_dir


def test_write_trace_creates_file(tmp_path):
    """write-telemetry-trace creates a trace file in the correct location."""
    user_dir = _setup_user_dir(tmp_path)

    trace_data = json.dumps({
        "skill": "adr-author",
        "skill_version": "0.1.0",
        "tastydev_version": "0.1.0",
        "mode": "review",
        "project": "git@github.com:org/project-alpha.git",
        "user": "zac",
        "steps": [
            {"status": "completed", "description": "Resolve project root", "detail": "found .tasty-dev/config.yaml"}
        ],
        "outcome": ["ADRs reviewed: 1"],
        "issues": []
    })

    result = subprocess.run(
        ["bin/write-telemetry-trace"],
        input=trace_data,
        capture_output=True,
        text=True,
        env={"TASTYDEV_USER_DIR": str(user_dir), "PATH": os.environ.get("PATH", "/usr/bin:/bin")},
    )

    assert result.returncode == 0

    project_dir = user_dir / "telemetry" / "github.com-org-project-alpha"
    assert project_dir.is_dir()

    trace_files = list(project_dir.glob("*-adr-author.md"))
    assert len(trace_files) == 1


def test_write_trace_has_correct_structure(tmp_path):
    """Trace file has YAML frontmatter and markdown body."""
    user_dir = _setup_user_dir(tmp_path)

    trace_data = json.dumps({
        "skill": "adr-author",
        "skill_version": "0.1.0",
        "tastydev_version": "0.1.0",
        "mode": "create",
        "project": "git@github.com:org/project-alpha.git",
        "user": "zac",
        "steps": [
            {"status": "completed", "description": "Step 1", "detail": "done"}
        ],
        "outcome": ["ADRs created: 1"],
        "issues": ["User skipped skeptical review"]
    })

    result = subprocess.run(
        ["bin/write-telemetry-trace"],
        input=trace_data,
        capture_output=True,
        text=True,
        env={"TASTYDEV_USER_DIR": str(user_dir), "PATH": os.environ.get("PATH", "/usr/bin:/bin")},
    )

    assert result.returncode == 0

    project_dir = user_dir / "telemetry" / "github.com-org-project-alpha"
    trace_file = list(project_dir.glob("*.md"))[0]
    content = trace_file.read_text()

    assert content.startswith("---")
    assert "skill: adr-author" in content
    assert "## Steps" in content
    assert "## Outcome" in content
    assert "## Issues" in content
    assert "User skipped skeptical review" in content


def test_write_trace_skips_when_disabled(tmp_path):
    """write-telemetry-trace does nothing when telemetry is disabled."""
    user_dir = tmp_path / ".tasty-dev"
    user_dir.mkdir()
    (user_dir / "telemetry").mkdir()
    (user_dir / "config.toml").write_text('[telemetry]\nenabled = false\n')

    trace_data = json.dumps({
        "skill": "adr-author",
        "skill_version": "0.1.0",
        "tastydev_version": "0.1.0",
        "mode": "review",
        "project": "git@github.com:org/test.git",
        "user": "zac",
        "steps": [],
        "outcome": [],
        "issues": []
    })

    result = subprocess.run(
        ["bin/write-telemetry-trace"],
        input=trace_data,
        capture_output=True,
        text=True,
        env={"TASTYDEV_USER_DIR": str(user_dir), "PATH": os.environ.get("PATH", "/usr/bin:/bin")},
    )

    assert result.returncode == 0
    telemetry_dir = user_dir / "telemetry"
    assert list(telemetry_dir.iterdir()) == []


def test_write_trace_skips_when_no_config(tmp_path):
    """write-telemetry-trace does nothing when config.toml is missing."""
    user_dir = tmp_path / ".tasty-dev"
    user_dir.mkdir()
    (user_dir / "telemetry").mkdir()

    trace_data = json.dumps({
        "skill": "adr-author",
        "skill_version": "0.1.0",
        "tastydev_version": "0.1.0",
        "mode": "review",
        "project": "git@github.com:org/test.git",
        "user": "zac",
        "steps": [],
        "outcome": [],
        "issues": []
    })

    result = subprocess.run(
        ["bin/write-telemetry-trace"],
        input=trace_data,
        capture_output=True,
        text=True,
        env={"TASTYDEV_USER_DIR": str(user_dir), "PATH": os.environ.get("PATH", "/usr/bin:/bin")},
    )

    assert result.returncode == 0
    telemetry_dir = user_dir / "telemetry"
    assert list(telemetry_dir.iterdir()) == []
