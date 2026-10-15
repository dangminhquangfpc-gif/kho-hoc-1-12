#!/usr/bin/env python3
"""Configure the local text tutor without putting a key in commands or web files.

Uses only the Python standard library, so the bundled Windows Python can run it
before the demo virtual environment is prepared. It does not call an AI service.
"""

from __future__ import annotations

import argparse
import csv
import getpass
import ipaddress
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import tempfile
from urllib.parse import urlsplit
import warnings


CONFIG_NAME = "ai-config.json"
KEY_NAME = "ai-secret.api-key"
DEFAULT_BASE_URL = "https://api.openai.com/v1"
DEFAULT_MODEL = "gpt-4.1-mini"
CONFIG_FIELDS = {
    "version",
    "enabled",
    "base_url",
    "model",
    "api_key_file",
    "daily_user_limit",
    "daily_server_limit",
    "output_tokens",
}
INVALID_CONFIG = "Cấu hình AI không hợp lệ. Dừng demo rồi chạy lại công cụ cấu hình AI."
INVALID_KEY = (
    "Khóa AI hoặc quyền đọc khóa không hợp lệ. Hãy nhập lại bằng công cụ cấu hình."
)


class AIConfigurationError(RuntimeError):
    """An actionable failure that never includes a configuration or secret value."""


def _public_https_url(value: object) -> bool:
    if not isinstance(value, str) or len(value) > 300:
        return False
    try:
        url = urlsplit(value)
        host = url.hostname or ""
        if (
            url.scheme != "https"
            or not host
            or url.username is not None
            or url.password is not None
            or url.query
            or url.fragment
            or url.port not in (None, 443)
            or "\\" in value
            or "%" in value
            or ".." in url.path.split("/")
            or not re.fullmatch(r"/[a-zA-Z0-9_./-]*", url.path or "/")
            or host == "localhost"
            or host.endswith((".localhost", ".local", ".internal"))
        ):
            return False
        try:
            address = ipaddress.ip_address(host)
        except ValueError:
            return bool(
                re.fullmatch(r"[a-zA-Z0-9.-]+", host)
                and "." in host
                and all(part and len(part) <= 63 for part in host.split("."))
            )
        return address.is_global
    except (TypeError, ValueError):
        return False


def _validate_config(config: object) -> dict:
    if (
        not isinstance(config, dict)
        or set(config) != CONFIG_FIELDS
        or type(config["version"]) is not int
        or config["version"] != 1
        or type(config["enabled"]) is not bool
        or not _public_https_url(config["base_url"])
        or not isinstance(config["model"], str)
        or not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9._:/-]{0,99}", config["model"])
        or config["api_key_file"] != KEY_NAME
    ):
        raise AIConfigurationError(INVALID_CONFIG)
    for name, minimum, maximum in (
        ("daily_user_limit", 1, 50),
        ("daily_server_limit", 1, 500),
        ("output_tokens", 100, 1200),
    ):
        if type(config[name]) is not int or not minimum <= config[name] <= maximum:
            raise AIConfigurationError(INVALID_CONFIG)
    return config


def _pairs_without_duplicates(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for name, value in pairs:
        if name in result:
            raise AIConfigurationError(INVALID_CONFIG)
        result[name] = value
    return result


def _state_path(state: Path) -> Path:
    path = Path(state).absolute()
    if path.is_symlink() or (path.exists() and not path.is_dir()):
        raise AIConfigurationError(INVALID_CONFIG)
    return path


def _read_regular(path: Path, *, private: bool = False) -> bytes:
    try:
        if path.is_symlink():
            raise AIConfigurationError(INVALID_KEY if private else INVALID_CONFIG)
        descriptor = os.open(
            path,
            os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0),
        )
        with os.fdopen(descriptor, "rb") as source:
            details = os.fstat(source.fileno())
            if (
                not stat.S_ISREG(details.st_mode)
                or details.st_size > (4096 if private else 8192)
                or (
                    private
                    and os.name != "nt"
                    and stat.S_IMODE(details.st_mode) & 0o077
                )
            ):
                raise AIConfigurationError(INVALID_KEY if private else INVALID_CONFIG)
            return source.read(4097 if private else 8193)
    except OSError:
        raise AIConfigurationError(INVALID_KEY if private else INVALID_CONFIG) from None


def _read_config(state: Path) -> dict | None:
    path = state / CONFIG_NAME
    if path.is_symlink():
        raise AIConfigurationError(INVALID_CONFIG)
    if not path.exists():
        return None
    try:
        return _validate_config(
            json.loads(
                _read_regular(path).decode("utf-8"),
                object_pairs_hook=_pairs_without_duplicates,
            )
        )
    except (UnicodeError, ValueError, RecursionError):
        raise AIConfigurationError(INVALID_CONFIG) from None


def _validate_key(key: object) -> str:
    if not isinstance(key, str) or not re.fullmatch(r"[!-~]{16,512}", key):
        raise AIConfigurationError(INVALID_KEY)
    return key


def load_ai_environment(state: Path) -> dict[str, str]:
    """Load one complete, non-secret environment source for the local launcher.

    The returned values point at the private key file. They never contain its
    contents. An explicit operator AI environment should override this source as
    a whole; combining individual fields can accidentally mix providers/keys.
    """
    state = _state_path(state)
    config = _read_config(state)
    if config is None:
        return {}
    if not config["enabled"]:
        return {"KHOHOC_AI_ENABLED": "false"}
    try:
        _validate_key(
            _read_regular(state / KEY_NAME, private=True).decode("utf-8").strip()
        )
    except UnicodeError:
        raise AIConfigurationError(INVALID_KEY) from None
    return {
        "KHOHOC_AI_ENABLED": "true",
        "KHOHOC_AI_BASE_URL": config["base_url"],
        "KHOHOC_AI_MODEL": config["model"],
        "KHOHOC_AI_API_KEY_FILE": str(state / KEY_NAME),
        "KHOHOC_AI_DAILY_USER_LIMIT": str(config["daily_user_limit"]),
        "KHOHOC_AI_DAILY_SERVER_LIMIT": str(config["daily_server_limit"]),
        "KHOHOC_AI_OUTPUT_TOKENS": str(config["output_tokens"]),
    }


def _windows_private_acl(path: Path) -> None:
    """Remove inherited ACLs before the empty file receives any secret bytes."""
    try:
        identity = subprocess.run(
            ["whoami", "/user", "/fo", "csv", "/nh"],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        rows = list(csv.reader(identity.stdout.splitlines()))
        sid = rows[0][-1] if len(rows) == 1 else ""
        if not re.fullmatch(r"S-1-(?:[0-9]+-)*[0-9]+", sid):
            raise AIConfigurationError(INVALID_KEY)
        subprocess.run(
            ["icacls", str(path), "/inheritance:r", "/grant:r", f"*{sid}:F"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except (OSError, subprocess.SubprocessError):
        raise AIConfigurationError(INVALID_KEY) from None


def _private_temp(state: Path, contents: bytes) -> Path:
    descriptor, name = tempfile.mkstemp(prefix=".ai-", suffix=".tmp", dir=state)
    path = Path(name)
    try:
        if os.name == "nt":
            _windows_private_acl(path)
        else:
            os.fchmod(descriptor, 0o600)
        with os.fdopen(descriptor, "wb") as destination:
            descriptor = -1
            destination.write(contents)
            destination.flush()
            os.fsync(destination.fileno())
        return path
    except BaseException:
        if descriptor != -1:
            os.close(descriptor)
        path.unlink(missing_ok=True)
        raise


def _publish_pair(state: Path, key: bytes, config: bytes) -> None:
    """Replace both files, retaining secure backups until both renames succeed."""
    old_key = state / KEY_NAME
    old_config = state / CONFIG_NAME
    for path in (old_key, old_config):
        if path.is_symlink() or (path.exists() and not path.is_file()):
            raise AIConfigurationError(INVALID_CONFIG)
    temporary: list[Path] = []
    try:
        next_key = _private_temp(state, key)
        temporary.append(next_key)
        next_config = _private_temp(state, config)
        temporary.append(next_config)
        # Backups also receive a private ACL before receiving any bytes.
        key_backup = (
            _private_temp(state, _read_regular(old_key, private=True))
            if old_key.exists()
            else None
        )
        if key_backup:
            temporary.append(key_backup)
        config_backup = (
            _private_temp(state, _read_regular(old_config))
            if old_config.exists()
            else None
        )
        if config_backup:
            temporary.append(config_backup)
        key_published = False
        try:
            os.replace(next_key, old_key)
            key_published = True
            os.replace(next_config, old_config)
        except OSError:
            if key_published:
                if key_backup:
                    os.replace(key_backup, old_key)
                else:
                    old_key.unlink(missing_ok=True)
            raise
    except (OSError, UnicodeError):
        raise AIConfigurationError(
            "Không lưu được cấu hình AI. Cấu hình cũ được giữ lại; kiểm tra quyền ghi thư mục state."
        ) from None
    finally:
        for path in temporary:
            path.unlink(missing_ok=True)


def configure(
    state: Path,
    *,
    api_key: str,
    base_url: str = DEFAULT_BASE_URL,
    model: str = DEFAULT_MODEL,
    daily_user_limit: int = 10,
    daily_server_limit: int = 100,
    output_tokens: int = 800,
) -> dict:
    """Save validated local configuration. The caller must stop the demo first."""
    config = _validate_config(
        {
            "version": 1,
            "enabled": True,
            "base_url": base_url,
            "model": model,
            "api_key_file": KEY_NAME,
            "daily_user_limit": daily_user_limit,
            "daily_server_limit": daily_server_limit,
            "output_tokens": output_tokens,
        }
    )
    key = _validate_key(api_key)
    state = _state_path(state)
    try:
        state.mkdir(mode=0o700, parents=True, exist_ok=True)
        encoded = (json.dumps(config, ensure_ascii=False, indent=2) + "\n").encode(
            "utf-8"
        )
        _publish_pair(state, (key + "\n").encode("ascii"), encoded)
    except OSError:
        raise AIConfigurationError(
            "Không lưu được cấu hình AI. Kiểm tra quyền ghi thư mục state."
        ) from None
    return config


def disable(state: Path) -> None:
    """Disable the tutor while retaining the existing key for explicit reuse."""
    state = _state_path(state)
    config = _read_config(state)
    if config is None:
        return
    config["enabled"] = False
    temporary = None
    try:
        temporary = _private_temp(
            state,
            (json.dumps(config, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
        )
        os.replace(temporary, state / CONFIG_NAME)
    except OSError:
        raise AIConfigurationError(
            "Không lưu được cấu hình AI. Kiểm tra quyền ghi thư mục state."
        ) from None
    finally:
        if temporary:
            temporary.unlink(missing_ok=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Cấu hình khóa AI riêng trên máy chạy demo; không gửi khóa trong chat."
    )
    parser.add_argument(
        "--state", type=Path, default=Path(__file__).resolve().parents[1] / "state"
    )
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--daily-user-limit", type=int, default=10)
    parser.add_argument("--daily-server-limit", type=int, default=100)
    parser.add_argument("--output-tokens", type=int, default=800)
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--disable", action="store_true")
    action.add_argument("--status", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.disable:
            disable(args.state)
            print("Đã tắt AI trong cấu hình local. Khởi động lại demo để áp dụng.")
        elif args.status:
            configured = (
                load_ai_environment(args.state).get("KHOHOC_AI_ENABLED") == "true"
            )
            print(
                "Cấu hình AI local hợp lệ; chưa kiểm tra kết nối nhà cung cấp."
                if configured
                else "AI local chưa được bật."
            )
        else:
            if not sys.stdin.isatty():
                raise AIConfigurationError(
                    "Hãy chạy công cụ trong cửa sổ Terminal để nhập khóa ẩn; không truyền khóa qua lệnh hoặc tệp batch."
                )
            print("Dừng demo trước khi cấu hình. Khóa được lưu riêng trên máy này.")
            print(
                "AI có thể phát sinh phí theo tài khoản nhà cung cấp; công cụ này chưa gọi AI."
            )
            with warnings.catch_warnings():
                warnings.simplefilter("error", getpass.GetPassWarning)
                key = getpass.getpass("Nhập API key (không hiển thị): ")
            configure(
                args.state,
                api_key=key,
                base_url=args.base_url,
                model=args.model,
                daily_user_limit=args.daily_user_limit,
                daily_server_limit=args.daily_server_limit,
                output_tokens=args.output_tokens,
            )
            key = ""
            print(
                "Đã lưu cấu hình AI. Khởi động lại demo, đăng nhập rồi thử một câu hỏi ngắn để kiểm tra AI thật."
            )
        return 0
    except (AIConfigurationError, getpass.GetPassWarning) as exc:
        print(
            str(exc)
            if isinstance(exc, AIConfigurationError)
            else "Không nhập được khóa ở chế độ ẩn. Hãy dùng Terminal hỗ trợ nhập mật khẩu.",
            file=sys.stderr,
        )
        return 1
    except (EOFError, KeyboardInterrupt):
        print("Đã hủy; cấu hình đang có được giữ lại.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
