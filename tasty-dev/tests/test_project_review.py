# tests/test_project_review.py
import subprocess
import tempfile
import json
from pathlib import Path
from datetime import datetime, timedelta

def test_project_review_processes_queue():
    """Project review processes reflexion queue"""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        subprocess.run(["bin/init-project-storage", str(project_path)])

        # Add some reflexions to queue
        queue_dir = project_path / ".tasty-dev" / "queue"
        reflexion = {
            "context": "API design",
            "resolution": "Use REST",
            "classification": {"level": "strategic", "scope": "project-specific"},
            "status": "pending"
        }

        with open(queue_dir / "20260307-120000.json", "w") as f:
            json.dump(reflexion, f)

        result = subprocess.run(
            ["bin/run-project-review", str(project_path)],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        assert "processed" in result.stdout.lower()

def test_project_review_updates_last_review_date():
    """Project review updates config with last review date"""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        subprocess.run(["bin/init-project-storage", str(project_path)])

        subprocess.run(["bin/run-project-review", str(project_path)])

        config_path = project_path / ".tasty-dev" / "config.yaml"
        with open(config_path) as f:
            import yaml
            config = yaml.safe_load(f)

        assert config["last_project_review"] is not None
        review_date = datetime.fromisoformat(config["last_project_review"])
        assert (datetime.now() - review_date).total_seconds() < 60
