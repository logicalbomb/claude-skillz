# tests/test_project_storage.py
import subprocess
import tempfile
from pathlib import Path
import yaml

def test_init_project_storage_creates_directories() -> None:
    """init-project-storage creates required directories"""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        result = subprocess.run(
            ["bin/init-project-storage", str(project_path)],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        assert (project_path / ".tasty-dev").exists()
        assert (project_path / ".tasty-dev" / "adr").exists()
        assert (project_path / ".tasty-dev" / "mulch").exists()
        assert (project_path / ".tasty-dev" / "queue").exists()
        assert (project_path / ".tasty-dev" / "config.yaml").exists()

def test_init_project_storage_creates_config() -> None:
    """init-project-storage creates valid config"""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        subprocess.run(["bin/init-project-storage", str(project_path)])

        config_path = project_path / ".tasty-dev" / "config.yaml"
        with open(config_path) as f:
            config = yaml.safe_load(f)

        assert "knowledge_repo" in config
        assert "last_project_review" in config
        assert config["last_project_review"] is None

def test_init_project_storage_idempotent() -> None:
    """Running init-project-storage twice should be safe"""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)

        # Run once
        subprocess.run(["bin/init-project-storage", str(project_path)])

        # Modify config
        config_path = project_path / ".tasty-dev" / "config.yaml"
        with open(config_path, "w") as f:
            yaml.dump({"custom": "value"}, f)

        # Run again - should not overwrite
        subprocess.run(["bin/init-project-storage", str(project_path)])

        # Verify config was not overwritten
        with open(config_path) as f:
            config = yaml.safe_load(f)
        assert config == {"custom": "value"}

def test_init_project_storage_creates_parent_dirs() -> None:
    """init-project-storage should create parent directories"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Nested path that doesn't exist
        project_path = Path(tmpdir) / "subdir" / "project"

        result = subprocess.run(
            ["bin/init-project-storage", str(project_path)],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        assert (project_path / ".tasty-dev").exists()
