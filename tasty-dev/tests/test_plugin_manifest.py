import yaml
import pytest
from pathlib import Path
from typing import Any, Dict, Optional
import re


def extract_frontmatter(content: str) -> Optional[Dict[str, Any]]:
    """Extract YAML frontmatter from markdown content.

    Args:
        content: Markdown content with YAML frontmatter

    Returns:
        Dictionary of frontmatter data, or None if no frontmatter found
    """
    # Match YAML frontmatter between --- delimiters
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if not match:
        return None

    frontmatter_text = match.group(1)
    return yaml.safe_load(frontmatter_text)


def test_skill_manifest_exists() -> None:
    """Skill manifest file must exist"""
    manifest_path = Path("SKILL.md")
    assert manifest_path.exists(), "SKILL.md file not found"


def test_skill_manifest_valid_yaml_frontmatter() -> None:
    """Skill manifest must have valid YAML frontmatter"""
    with open("SKILL.md") as f:
        content = f.read()

    frontmatter = extract_frontmatter(content)
    assert frontmatter is not None, "No YAML frontmatter found in SKILL.md"
    assert isinstance(frontmatter, dict), "Frontmatter must be a dictionary"


def test_skill_manifest_has_required_fields() -> None:
    """Skill manifest must have name, version, description in frontmatter"""
    with open("SKILL.md") as f:
        content = f.read()

    frontmatter = extract_frontmatter(content)
    assert frontmatter is not None, "No YAML frontmatter found"

    assert "name" in frontmatter, "Missing 'name' field"
    assert "version" in frontmatter, "Missing 'version' field"
    assert "description" in frontmatter, "Missing 'description' field"

    assert frontmatter["name"] == "tasty-dev", f"Expected name 'tasty-dev', got '{frontmatter['name']}'"
    assert frontmatter["version"] == "0.1.0", f"Expected version '0.1.0', got '{frontmatter['version']}'"
