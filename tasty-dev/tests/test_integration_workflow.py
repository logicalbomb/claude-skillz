# tests/test_integration_workflow.py
"""Integration tests for complete workflow"""
import subprocess
import tempfile
from pathlib import Path
import json
import yaml

def test_complete_reflexion_workflow():
    """Test complete workflow from trigger to ADR"""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)

        # Step 1: Initialize project
        result = subprocess.run(
            ["bin/init-project-storage", str(project_path)],
            capture_output=True
        )
        assert result.returncode == 0

        # Step 2: Capture a reflexion
        reflexion = {
            "context": "API design decision",
            "initial_suggestion": "Use GraphQL",
            "alternatives": ["REST", "gRPC"],
            "friction": "User prefers REST for simplicity",
            "resolution": "Use REST with OpenAPI",
            "why": "Team familiarity and tooling ecosystem"
        }

        result = subprocess.run(
            ["bin/capture-reflexion", str(project_path)],
            input=json.dumps(reflexion),
            capture_output=True,
            text=True
        )
        assert result.returncode == 0

        # Step 3: Verify queue entry
        queue_dir = project_path / ".tasty-dev" / "queue"
        queue_files = list(queue_dir.glob("*.json"))
        assert len(queue_files) == 1

        with open(queue_files[0]) as f:
            saved = json.load(f)
        assert saved["classification"]["level"] == "strategic"

        # Step 4: Run project review
        result = subprocess.run(
            ["bin/run-project-review", str(project_path)],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0

        # Step 5: Verify ADR directory exists (ADR creation now handled by adr-author skill)
        adr_dir = project_path / ".tasty-dev" / "adr"
        assert adr_dir.is_dir()

def test_adr_directory_initialized():
    """Test ADR directory is properly initialized by init-project-storage"""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        subprocess.run(["bin/init-project-storage", str(project_path)])

        adr_dir = project_path / ".tasty-dev" / "adr"
        assert adr_dir.is_dir()

        # ADR creation and querying now handled by adr-author skill
        # See skills/adr/TESTING.md for skill-level test scenarios
