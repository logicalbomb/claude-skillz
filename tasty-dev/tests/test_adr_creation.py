# tests/test_adr_creation.py
"""Tests for ADR infrastructure: init-project-storage and MADR template."""
import subprocess
import tempfile
from pathlib import Path

import yaml


TEMPLATE_PATH = Path("templates/adr-template.md")


def _parse_frontmatter(content: str) -> dict:
    """Extract and parse YAML frontmatter from markdown content."""
    parts = content.split("---", 2)
    assert len(parts) >= 3, "Template must have YAML frontmatter between --- delimiters"
    return yaml.safe_load(parts[1])


def test_template_has_valid_yaml_frontmatter():
    """MADR template contains parseable YAML frontmatter."""
    content = TEMPLATE_PATH.read_text()
    frontmatter = _parse_frontmatter(content)
    assert isinstance(frontmatter, dict)


def test_template_has_required_frontmatter_fields():
    """MADR template includes all required metadata fields."""
    content = TEMPLATE_PATH.read_text()
    frontmatter = _parse_frontmatter(content)

    required_fields = [
        "status", "date", "decision-makers", "consulted", "informed",
        "domains", "affects", "related", "supersedes", "enforces",
        "discussion",
    ]
    for field in required_fields:
        assert field in frontmatter, f"Missing required field: {field}"


def test_template_has_discussion_metadata():
    """MADR template discussion block has participant tracking fields."""
    content = TEMPLATE_PATH.read_text()
    frontmatter = _parse_frontmatter(content)
    discussion = frontmatter["discussion"]

    assert "participants" in discussion
    assert "unread_by" in discussion
    assert "started" in discussion
    assert "last_updated" in discussion


def test_template_has_required_sections():
    """MADR template has all required markdown sections."""
    content = TEMPLATE_PATH.read_text()

    required_sections = [
        "## Context and Problem Statement",
        "## Decision Drivers",
        "## Considered Options",
        "## Decision Outcome",
        "### Consequences",
        "## Pros and Cons of the Options",
        "## Discussion",
        "## More Information",
    ]
    for section in required_sections:
        assert section in content, f"Missing required section: {section}"


def test_init_project_storage_creates_adr_directory():
    """init-project-storage creates .tasty-dev/adr/ directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        result = subprocess.run(
            ["bin/init-project-storage", str(project_path)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert (project_path / ".tasty-dev" / "adr").is_dir()


def test_init_project_storage_creates_config():
    """init-project-storage creates config.yaml with expected fields."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        subprocess.run(
            ["bin/init-project-storage", str(project_path)],
            capture_output=True,
        )

        config_path = project_path / ".tasty-dev" / "config.yaml"
        assert config_path.exists()

        config = yaml.safe_load(config_path.read_text())
        assert "knowledge_repo" in config
        assert "last_project_review" in config
        assert "last_knowledge_review" in config


def test_init_project_storage_is_idempotent():
    """Running init-project-storage twice does not overwrite config."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)

        # First run
        subprocess.run(
            ["bin/init-project-storage", str(project_path)],
            capture_output=True,
        )

        # Modify config to prove it isn't overwritten
        config_path = project_path / ".tasty-dev" / "config.yaml"
        config = yaml.safe_load(config_path.read_text())
        config["knowledge_repo"] = "/some/path"
        with open(config_path, "w") as f:
            yaml.dump(config, f)

        # Second run
        subprocess.run(
            ["bin/init-project-storage", str(project_path)],
            capture_output=True,
        )

        # Config should retain modification
        config = yaml.safe_load(config_path.read_text())
        assert config["knowledge_repo"] == "/some/path"
