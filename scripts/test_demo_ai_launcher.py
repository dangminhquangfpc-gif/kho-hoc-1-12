"""Upgrading must not reactivate a removed paid AI integration or delete secrets."""

import json
from pathlib import Path
import subprocess
import sys

import pytest

from run_local_demo import child_environment


@pytest.mark.parametrize(
    "config", ["invalid old config", json.dumps({"enabled": True})]
)
def test_legacy_private_files_are_ignored_and_preserved(tmp_path, config):
    config_path = tmp_path / "ai-config.json"
    key_path = tmp_path / "ai-secret.api-key"
    config_path.write_text(config)
    key_path.write_text("synthetic-private-test-key-only")
    before = {path: path.read_bytes() for path in (config_path, key_path)}

    actual = child_environment(tmp_path, 8011, 8091)

    assert not any(name.startswith("KHOHOC_AI_") for name in actual)
    assert {path: path.read_bytes() for path in before} == before
    assert "synthetic-private-test-key-only" not in repr(actual)


def test_inherited_paid_ai_and_production_settings_cannot_reactivate_service(
    tmp_path, monkeypatch
):
    for name, value in {
        "KHOHOC_AI_ENABLED": "true",
        "KHOHOC_AI_BASE_URL": "https://api.example.com/v1",
        "KHOHOC_AI_MODEL": "legacy-paid-model",
        "KHOHOC_AI_API_KEY": "synthetic-environment-key-only",
        "KHOHOC_AI_API_KEY_FILE": str(tmp_path / "missing-private-key"),
        "KHOHOC_AI_DAILY_USER_LIMIT": "100",
        "KHOHOC_AI_DAILY_SERVER_LIMIT": "1000",
        "KHOHOC_AI_OUTPUT_TOKENS": "800",
        "KHOHOC_DATABASE_URL": "postgresql://production.invalid/private",
        "KHOHOC_ADMIN_TOKEN": "synthetic-production-admin-credential",
    }.items():
        monkeypatch.setenv(name, value)

    actual = child_environment(tmp_path, 8011, 8091)

    assert not any(name.startswith("KHOHOC_AI_") for name in actual)
    assert "synthetic-environment-key-only" not in repr(actual)
    assert actual["KHOHOC_ADMIN_TOKEN"] == ""
    assert (
        actual["KHOHOC_DATABASE_URL"]
        == "sqlite:///" + (tmp_path / "demo.sqlite").as_posix()
    )
    assert actual["KHOHOC_MODE"] == "development"


def test_packaged_launcher_works_without_removed_configuration_helper():
    script = Path(__file__).with_name("run_local_demo.py")
    result = subprocess.run(
        [sys.executable, str(script), "--help"], capture_output=True, check=True
    )
    assert b"--no-browser" in result.stdout
