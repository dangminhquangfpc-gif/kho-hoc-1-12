"""The demo must select one AI credential source and keep production state out."""

import os
from pathlib import Path
import subprocess
import sys

import pytest

from configure_ai import configure
from run_local_demo import DemoError, child_environment


@pytest.fixture(autouse=True)
def isolated_ai_environment(monkeypatch):
    for name in tuple(os.environ):
        if name.startswith("KHOHOC_AI_"):
            monkeypatch.delenv(name)


def test_saved_operator_config_uses_private_file_not_its_contents(
    tmp_path, monkeypatch
):
    configure(tmp_path, api_key="synthetic-private-test-key-only")
    monkeypatch.setenv("KHOHOC_DATABASE_URL", "postgresql://production.invalid/private")
    monkeypatch.setenv("KHOHOC_ADMIN_TOKEN", "synthetic-production-admin-credential")
    actual = child_environment(tmp_path, 8011, 8091)
    assert actual["KHOHOC_AI_ENABLED"] == "true"
    assert actual["KHOHOC_AI_API_KEY_FILE"] == str(tmp_path / "ai-secret.api-key")
    assert "KHOHOC_AI_API_KEY" not in actual
    assert "synthetic-private-test-key-only" not in repr(actual)
    assert actual["KHOHOC_ADMIN_TOKEN"] == ""
    assert actual["KHOHOC_DATABASE_URL"].startswith("sqlite:///")


def test_explicit_secret_source_never_inherits_saved_provider_or_file(
    tmp_path, monkeypatch
):
    configure(tmp_path, api_key="synthetic-private-file-key-only")
    monkeypatch.setenv("KHOHOC_AI_ENABLED", "true")
    monkeypatch.setenv("KHOHOC_AI_BASE_URL", "https://api.example.com/v1")
    monkeypatch.setenv("KHOHOC_AI_MODEL", "operator-model")
    monkeypatch.setenv("KHOHOC_AI_API_KEY", "synthetic-env-key-for-test-only")
    actual = child_environment(tmp_path, 8011, 8091)
    assert "KHOHOC_AI_API_KEY_FILE" not in actual
    assert actual["KHOHOC_AI_API_KEY"] == "synthetic-env-key-for-test-only"
    assert actual["KHOHOC_AI_BASE_URL"] == "https://api.example.com/v1"
    assert actual["KHOHOC_AI_MODEL"] == "operator-model"


def test_explicit_disable_ignores_even_an_invalid_saved_config(tmp_path, monkeypatch):
    (tmp_path / "ai-config.json").write_text("not-json")
    monkeypatch.setenv("KHOHOC_AI_ENABLED", "false")
    actual = child_environment(tmp_path, 8011, 8091)
    assert {k: v for k, v in actual.items() if k.startswith("KHOHOC_AI_")} == {
        "KHOHOC_AI_ENABLED": "false"
    }


def test_invalid_file_fails_without_echoing_its_contents(tmp_path):
    (tmp_path / "ai-config.json").write_text("synthetic-sensitive-invalid-value")
    with pytest.raises(DemoError) as error:
        child_environment(tmp_path, 8011, 8091)
    assert "configure-ai.bat" in str(error.value)
    assert "synthetic-sensitive-invalid-value" not in str(error.value)


def test_packaged_script_can_import_configuration_helper():
    script = Path(__file__).with_name("run_local_demo.py")
    result = subprocess.run(
        [sys.executable, str(script), "--help"], capture_output=True, check=True
    )
    assert b"--no-browser" in result.stdout
