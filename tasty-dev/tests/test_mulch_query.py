# tests/test_mulch_query.py
import subprocess
import tempfile
from pathlib import Path

def test_query_mulch_integration():
    """query-mulch integrates with mulch CLI"""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        subprocess.run(["bin/init-project-storage", str(project_path)])

        # This test assumes mulch CLI is installed
        # Skip if not available
        check = subprocess.run(
            ["which", "ml"],
            capture_output=True
        )

        if check.returncode != 0:
            import pytest
            pytest.skip("mulch CLI not installed")

        # Query should work even with empty mulch
        result = subprocess.run(
            ["bin/query-mulch", str(project_path), "testing"],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
