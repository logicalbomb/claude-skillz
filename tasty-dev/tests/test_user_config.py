# tests/test_user_config.py
"""Tests for user-level config initialization."""
import os
import subprocess
import tempfile
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib


def test_init_user_config_creates_config_toml(tmp_path):
    """init-user-config creates config.toml with telemetry disabled."""
    config_dir = tmp_path / ".tasty-dev"
    env = os.environ.copy()
    env["TASTYDEV_USER_DIR"] = str(config_dir)
    result = subprocess.run(
        ["bin/init-user-config"],
        capture_output=True,
        text=True,
        env=env,
    )

    assert result.returncode == 0
    config_path = config_dir / "config.toml"
    assert config_path.exists()

    with open(config_path, "rb") as f:
        config = tomllib.load(f)

    assert config["telemetry"]["enabled"] is False


def test_init_user_config_creates_telemetry_dir(tmp_path):
    """init-user-config creates the telemetry directory."""
    config_dir = tmp_path / ".tasty-dev"
    env = os.environ.copy()
    env["TASTYDEV_USER_DIR"] = str(config_dir)
    subprocess.run(
        ["bin/init-user-config"],
        capture_output=True,
        env=env,
    )

    assert (config_dir / "telemetry").is_dir()


def test_init_user_config_is_idempotent(tmp_path):
    """Running init-user-config twice does not overwrite config."""
    config_dir = tmp_path / ".tasty-dev"
    env = os.environ.copy()
    env["TASTYDEV_USER_DIR"] = str(config_dir)

    # First run
    subprocess.run(
        ["bin/init-user-config"],
        capture_output=True,
        env=env,
    )

    # Modify config
    config_path = config_dir / "config.toml"
    config_path.write_text('[telemetry]\nenabled = true\n')

    # Second run
    subprocess.run(
        ["bin/init-user-config"],
        capture_output=True,
        env=env,
    )

    # Should retain modification
    with open(config_path, "rb") as f:
        config = tomllib.load(f)
    assert config["telemetry"]["enabled"] is True
