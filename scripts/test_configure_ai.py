"""Operator configuration checks use synthetic keys and never contact a provider."""

import json
import os
from pathlib import Path
import socket
import stat
import subprocess
import sys

import pytest

import configure_ai
from configure_ai import AIConfigurationError, configure, disable, load_ai_environment


KEY = "synthetic-test-secret-never-a-real-provider-key"
OTHER_KEY = "another-synthetic-key-never-a-real-provider-key"


@pytest.fixture
def state(tmp_path):
    return tmp_path / "state"


def enabled_state(state):
    configure(state, api_key=KEY)
    return state


def read_config(state):
    return json.loads((state / "ai-config.json").read_text(encoding="utf-8"))


def write_config(state, value):
    (state / "ai-config.json").write_text(json.dumps(value), encoding="utf-8")


def assert_private_error(action):
    with pytest.raises(AIConfigurationError) as failure:
        action()
    message = str(failure.value) + repr(failure.value)
    assert KEY not in message
    assert OTHER_KEY not in message


def test_missing_configuration_stays_disabled_without_creating_files(state):
    assert load_ai_environment(state) == {}
    assert not state.exists()


def test_lifecycle_exposes_only_environment_names_and_private_key_path(state, capsys):
    configure(
        state,
        api_key=KEY,
        base_url="https://api.example.com/v1",
        model="test-model",
        daily_user_limit=3,
        daily_server_limit=20,
        output_tokens=500,
    )
    config = read_config(state)
    assert config == {
        "version": 1,
        "enabled": True,
        "base_url": "https://api.example.com/v1",
        "model": "test-model",
        "api_key_file": "ai-secret.api-key",
        "daily_user_limit": 3,
        "daily_server_limit": 20,
        "output_tokens": 500,
    }
    environment = load_ai_environment(state)
    assert environment == {
        "KHOHOC_AI_ENABLED": "true",
        "KHOHOC_AI_BASE_URL": "https://api.example.com/v1",
        "KHOHOC_AI_MODEL": "test-model",
        "KHOHOC_AI_API_KEY_FILE": str((state / "ai-secret.api-key").resolve()),
        "KHOHOC_AI_DAILY_USER_LIMIT": "3",
        "KHOHOC_AI_DAILY_SERVER_LIMIT": "20",
        "KHOHOC_AI_OUTPUT_TOKENS": "500",
    }
    assert (state / "ai-secret.api-key").read_text().strip() == KEY
    assert KEY not in json.dumps(config)
    assert KEY not in repr(environment)
    assert KEY not in capsys.readouterr().out

    disable(state)
    assert read_config(state)["enabled"] is False
    assert load_ai_environment(state) == {"KHOHOC_AI_ENABLED": "false"}
    assert (state / "ai-secret.api-key").read_text().strip() == KEY

    configure(state, api_key=OTHER_KEY)
    assert load_ai_environment(state)["KHOHOC_AI_ENABLED"] == "true"
    assert (state / "ai-secret.api-key").read_text().strip() == OTHER_KEY


@pytest.mark.skipif(
    os.name == "nt", reason="Windows uses a private ACL instead of POSIX modes"
)
def test_key_permissions_are_private_and_wide_permissions_fail_closed(state):
    enabled_state(state)
    key = state / "ai-secret.api-key"
    assert stat.S_IMODE(key.stat().st_mode) == 0o600
    assert stat.S_IMODE((state / "ai-config.json").stat().st_mode) == 0o600
    key.chmod(0o644)
    assert_private_error(lambda: load_ai_environment(state))
    key.chmod(0o600)
    assert load_ai_environment(state)["KHOHOC_AI_ENABLED"] == "true"


@pytest.mark.parametrize(
    "contents",
    [
        b"",
        b"short",
        b"two tokens with spaces",
        b"a" * 513,
        b"invalid-utf8-\xff-key-material",
    ],
)
def test_tampered_key_material_fails_closed(state, contents):
    enabled_state(state)
    (state / "ai-secret.api-key").write_bytes(contents)
    assert_private_error(lambda: load_ai_environment(state))


def test_enabled_configuration_with_missing_key_fails_closed(state):
    enabled_state(state)
    (state / "ai-secret.api-key").unlink()
    assert_private_error(lambda: load_ai_environment(state))


@pytest.mark.parametrize(
    "patch",
    [
        {"version": 2},
        {"version": True},
        {"enabled": "true"},
        {"enabled": 1},
        {"unknown_field": "unexpected"},
        {"api_key_file": "../outside.api-key"},
        {"api_key_file": "/tmp/outside.api-key"},
        {"model": ""},
        {"daily_user_limit": 0},
        {"daily_user_limit": 51},
        {"daily_user_limit": True},
        {"daily_server_limit": 501},
        {"daily_server_limit": "100"},
        {"output_tokens": 99},
        {"output_tokens": 1201},
    ],
)
def test_malformed_configuration_is_rejected_without_secret_echo(state, patch):
    enabled_state(state)
    write_config(state, read_config(state) | patch)
    assert_private_error(lambda: load_ai_environment(state))


@pytest.mark.parametrize(
    "contents",
    [
        "not json",
        "[]",
        "null",
        '{"enabled":true,"enabled":false}',
        '{"version":1,"version":2}',
        '{"version":1,"daily_user_limit":NaN}',
    ],
)
def test_non_object_duplicate_and_non_standard_json_are_rejected(state, contents):
    enabled_state(state)
    (state / "ai-config.json").write_text(contents, encoding="utf-8")
    assert_private_error(lambda: load_ai_environment(state))


@pytest.mark.parametrize(
    "invalid",
    [
        {"api_key": "too-short"},
        {"api_key": "invalid key with spaces"},
        {"api_key": "a" * 513},
        {"api_key": "synthetic-key-with-nul-\x00"},
        {"api_key": "synthetic-unicode-秘密-key"},
        {"base_url": "http://api.example.com/v1"},
        {"base_url": "https://localhost/v1"},
        {"base_url": "https://127.0.0.1/v1"},
        {"base_url": "https://api.example.com/v1?key=" + KEY},
        {"base_url": "https://user:" + KEY + "@api.example.com/v1"},
        {"model": "bad model"},
        {"daily_user_limit": 0},
        {"daily_server_limit": 501},
        {"output_tokens": 1201},
    ],
)
def test_invalid_new_settings_preserve_existing_working_configuration(state, invalid):
    enabled_state(state)
    config = (state / "ai-config.json").read_bytes()
    key = (state / "ai-secret.api-key").read_bytes()
    arguments = {"api_key": OTHER_KEY} | invalid
    assert_private_error(lambda: configure(state, **arguments))
    assert (state / "ai-config.json").read_bytes() == config
    assert (state / "ai-secret.api-key").read_bytes() == key
    assert load_ai_environment(state)["KHOHOC_AI_ENABLED"] == "true"


def test_failed_configuration_publish_restores_key_and_removes_temporary_secrets(
    state, monkeypatch
):
    enabled_state(state)
    old_config = (state / "ai-config.json").read_bytes()
    old_key = (state / "ai-secret.api-key").read_bytes()
    replace = configure_ai.os.replace
    failed = False

    def fail_config_once(source, target):
        nonlocal failed
        if (
            not failed
            and Path(source).name.startswith(".ai-")
            and Path(target) == state / "ai-config.json"
        ):
            failed = True
            raise OSError("Synthetic write failure")
        return replace(source, target)

    monkeypatch.setattr(configure_ai.os, "replace", fail_config_once)
    assert_private_error(lambda: configure(state, api_key=OTHER_KEY, model="new-model"))
    assert failed
    assert (state / "ai-config.json").read_bytes() == old_config
    assert (state / "ai-secret.api-key").read_bytes() == old_key
    assert list(state.glob(".ai-*.tmp")) == []
    assert load_ai_environment(state)["KHOHOC_AI_MODEL"] == "gpt-4.1-mini"


@pytest.mark.skipif(
    os.name == "nt", reason="Creating symlinks on Windows can need elevated privileges"
)
def test_symlink_state_is_rejected_without_changing_target(tmp_path):
    target = tmp_path / "target"
    enabled_state(target)
    alias = tmp_path / "state-link"
    alias.symlink_to(target, target_is_directory=True)
    before = {path.name: path.read_bytes() for path in target.iterdir()}
    assert_private_error(lambda: load_ai_environment(alias))
    assert_private_error(lambda: configure(alias, api_key=OTHER_KEY))
    assert_private_error(lambda: disable(alias))
    assert {path.name: path.read_bytes() for path in target.iterdir()} == before


@pytest.mark.skipif(
    os.name == "nt", reason="Creating symlinks on Windows can need elevated privileges"
)
@pytest.mark.parametrize("filename", ["ai-config.json", "ai-secret.api-key"])
def test_symlink_configuration_or_key_is_rejected_without_changing_target(
    state, tmp_path, filename
):
    enabled_state(state)
    original = state / filename
    external = tmp_path / ("outside-" + filename)
    original.replace(external)
    original.symlink_to(external)
    before = external.read_bytes()
    assert_private_error(lambda: load_ai_environment(state))
    assert_private_error(lambda: configure(state, api_key=OTHER_KEY))
    assert external.read_bytes() == before


def test_configuration_and_loading_never_connect_to_a_provider(state, monkeypatch):
    def denied(*args, **kwargs):
        raise AssertionError("Configuration must not make network requests")

    monkeypatch.setattr(socket, "socket", denied)
    monkeypatch.setattr(socket, "create_connection", denied)
    enabled_state(state)
    assert load_ai_environment(state)["KHOHOC_AI_ENABLED"] == "true"
    disable(state)


def test_windows_acl_uses_operator_sid_without_passing_secret_to_commands(
    tmp_path, monkeypatch
):
    path = tmp_path / "private.tmp"
    calls = []

    def run(arguments, **kwargs):
        calls.append((arguments, kwargs))
        return subprocess.CompletedProcess(
            arguments,
            0,
            stdout='"example\\operator","S-1-5-21-100-200-300-1001"\r\n',
        )

    monkeypatch.setattr(configure_ai.subprocess, "run", run)
    configure_ai._windows_private_acl(path)
    assert calls[0][0] == ["whoami", "/user", "/fo", "csv", "/nh"]
    assert calls[1][0] == [
        "icacls",
        str(path),
        "/inheritance:r",
        "/grant:r",
        "*S-1-5-21-100-200-300-1001:F",
    ]
    assert calls[1][1]["check"] is True
    assert calls[1][1]["stdout"] is subprocess.DEVNULL
    assert calls[1][1]["stderr"] is subprocess.DEVNULL
    assert KEY not in repr(calls)


def test_windows_acl_failure_does_not_echo_subprocess_output(tmp_path, monkeypatch):
    def denied(arguments, **kwargs):
        raise subprocess.CalledProcessError(1, arguments, output=KEY, stderr=KEY)

    monkeypatch.setattr(configure_ai.subprocess, "run", denied)
    assert_private_error(
        lambda: configure_ai._windows_private_acl(tmp_path / "private.tmp")
    )


def test_cli_status_does_not_display_key(state):
    enabled_state(state)
    completed = subprocess.run(
        [
            sys.executable,
            str(Path(__file__).with_name("configure_ai.py")),
            "--state",
            str(state),
            "--status",
        ],
        capture_output=True,
        text=True,
        check=False,
        timeout=5,
    )
    assert completed.returncode == 0
    assert KEY not in completed.stdout + completed.stderr
