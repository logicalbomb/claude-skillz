# tests/test_skill_telemetry.py
"""Tests for skill telemetry declarations."""
from pathlib import Path

import yaml


SKILL_FILES = [
    Path("skills/adr/skill.md"),
    Path("skills/reflexion/capture.md"),
    Path("skills/reviews/project-weekly.md"),
    Path("skills/superpowers-enhanced/brainstorming-enhanced.md"),
    Path("skills/superpowers-enhanced/writing-plans-enhanced.md"),
]


def _parse_frontmatter(path: Path) -> dict:
    """Extract and parse YAML frontmatter from skill file."""
    content = path.read_text()
    parts = content.split("---", 2)
    assert len(parts) >= 3, f"{path} must have YAML frontmatter"
    return yaml.safe_load(parts[1])


def test_all_skills_have_version():
    """Every skill declares a version in frontmatter."""
    for skill_path in SKILL_FILES:
        fm = _parse_frontmatter(skill_path)
        assert "version" in fm, f"{skill_path} missing 'version' field"


def test_all_skills_have_telemetry_block():
    """Every skill declares telemetry expectations."""
    for skill_path in SKILL_FILES:
        fm = _parse_frontmatter(skill_path)
        assert "telemetry" in fm, f"{skill_path} missing 'telemetry' block"
        telemetry = fm["telemetry"]
        assert "expected_cadence" in telemetry, f"{skill_path} missing expected_cadence"
        assert "expected_participants" in telemetry, f"{skill_path} missing expected_participants"
        assert "health_signals" in telemetry, f"{skill_path} missing health_signals"


def test_health_signals_are_non_empty():
    """Every skill has at least one health signal."""
    for skill_path in SKILL_FILES:
        fm = _parse_frontmatter(skill_path)
        signals = fm["telemetry"]["health_signals"]
        assert len(signals) > 0, f"{skill_path} has no health signals"


def test_expected_cadence_is_valid():
    """expected_cadence uses known values."""
    valid_cadences = {"weekly", "on_demand", "organic"}
    for skill_path in SKILL_FILES:
        fm = _parse_frontmatter(skill_path)
        cadence = fm["telemetry"]["expected_cadence"]
        assert cadence in valid_cadences, f"{skill_path} has invalid cadence: {cadence}"


def test_expected_participants_is_valid():
    """expected_participants uses known values."""
    valid_participants = {"all", "at_least_one"}
    for skill_path in SKILL_FILES:
        fm = _parse_frontmatter(skill_path)
        participants = fm["telemetry"]["expected_participants"]
        assert participants in valid_participants, f"{skill_path} has invalid participants: {participants}"
