# tests/test_weekly_nudge.py
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
import yaml
import subprocess

def test_nudge_when_review_overdue():
    """Hook nudges when review is overdue"""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        subprocess.run(["bin/init-project-storage", str(project_path)])

        # Set last review to 8 days ago
        config_path = project_path / ".tasty-dev" / "config.yaml"
        with open(config_path) as f:
            config = yaml.safe_load(f)

        config["last_project_review"] = (
            datetime.now() - timedelta(days=8)
        ).isoformat()

        with open(config_path, "w") as f:
            yaml.dump(config, f)

        # Run hook
        from hooks.nudge_weekly_review import check_review_needed
        result = check_review_needed(project_path)

        assert result is not None
        assert result["days_since"] == 8
        assert result["severity"] == "gentle"

def test_no_nudge_when_review_recent():
    """Hook doesn't nudge when review is recent"""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        subprocess.run(["bin/init-project-storage", str(project_path)])

        # Set last review to 2 days ago
        config_path = project_path / ".tasty-dev" / "config.yaml"
        with open(config_path) as f:
            config = yaml.safe_load(f)

        config["last_project_review"] = (
            datetime.now() - timedelta(days=2)
        ).isoformat()

        with open(config_path, "w") as f:
            yaml.dump(config, f)

        from hooks.nudge_weekly_review import check_review_needed
        result = check_review_needed(project_path)

        assert result is None
