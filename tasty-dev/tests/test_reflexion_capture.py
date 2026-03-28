# tests/test_reflexion_capture.py
import subprocess
import tempfile
import json
from pathlib import Path
from datetime import datetime

def test_capture_reflexion_creates_queue_entry():
    """Capture creates entry in reflexion queue"""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        subprocess.run(["bin/init-project-storage", str(project_path)])

        reflexion_data = {
            "context": "Adding API endpoint",
            "initial_suggestion": "Use REST",
            "alternatives": ["GraphQL", "gRPC"],
            "friction": "User prefers GraphQL",
            "resolution": "Switch to GraphQL",
            "why": "Better for our use case with nested data"
        }

        result = subprocess.run(
            ["bin/capture-reflexion", str(project_path)],
            input=json.dumps(reflexion_data),
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        queue_dir = project_path / ".tasty-dev" / "queue"
        queue_files = list(queue_dir.glob("*.json"))
        assert len(queue_files) == 1

        with open(queue_files[0]) as f:
            saved = json.load(f)

        assert saved["context"] == reflexion_data["context"]
        assert saved["resolution"] == reflexion_data["resolution"]
        assert "timestamp" in saved
        assert "classification" in saved

def test_capture_reflexion_infers_classification():
    """Capture infers strategic vs tactical classification"""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        subprocess.run(["bin/init-project-storage", str(project_path)])

        # Strategic decision (architecture change)
        strategic_data = {
            "context": "Database selection",
            "initial_suggestion": "SQLite",
            "friction": "Need distributed transactions",
            "resolution": "Use PostgreSQL with two-phase commit",
            "why": "Required for our distributed architecture"
        }

        subprocess.run(
            ["bin/capture-reflexion", str(project_path)],
            input=json.dumps(strategic_data),
            text=True
        )

        queue_files = list((project_path / ".tasty-dev" / "queue").glob("*.json"))
        with open(queue_files[0]) as f:
            saved = json.load(f)

        assert saved["classification"]["level"] == "strategic"
