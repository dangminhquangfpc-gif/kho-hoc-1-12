#!/usr/bin/env python3
"""Run the packaged, real-backend demo on the user's own computer."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import ProxyHandler, Request, build_opener
import venv
import webbrowser


ROOT = Path(__file__).resolve().parents[1]
OPENER = build_opener(ProxyHandler({}))


class DemoError(RuntimeError):
    """An actionable startup failure, displayed without a Python traceback."""


def port_number(value: str) -> int:
    try:
        number = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError("Port must be a number") from None
    if not 1024 <= number <= 65535:
        raise argparse.ArgumentTypeError("Choose a port between 1024 and 65535")
    return number


def check_files() -> None:
    required = (
        "apps/mobile/build/web/index.html",
        "services/api/requirements.lock.txt",
        "services/api/khohoc/phone_preview.py",
        "scripts/serve_demo.py",
        "data/seeds/questions.json",
        "data/seeds/language_questions.json",
        "data/seeds/exams.json",
        "data/seeds/language_exams.json",
        "data/library/documents.json",
    )
    missing = [name for name in required if not (ROOT / name).is_file()]
    if missing:
        raise DemoError(
            "The demo package is incomplete. Extract the whole ZIP first. Missing: "
            + ", ".join(missing)
        )


def check_ports(api_port: int, web_port: int) -> None:
    if api_port == web_port:
        raise DemoError(
            "Backend and demo need different ports (--api-port and --port)."
        )
    for label, port in (("Backend", api_port), ("Demo", web_port)):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
                probe.bind(("127.0.0.1", port))
        except OSError as exc:
            raise DemoError(
                f"{label} port {port} is unavailable. Close the program already using "
                f"it, or rerun with --api-port 8011 --port 8091. ({exc})"
            ) from None


def checked_wheelhouse() -> tuple[Path | None, bytes]:
    """Verify the Windows bundle before allowing pip to consume its wheels."""
    wheelhouse = ROOT / "wheelhouse"
    if os.name != "nt" or not wheelhouse.is_dir():
        return None, b""
    manifest = wheelhouse / "SHA256SUMS.json"
    try:
        manifest_bytes = manifest.read_bytes()
        hashes = json.loads(manifest_bytes)
    except (OSError, ValueError) as exc:
        raise DemoError(
            f"The offline package has no readable wheel checksum manifest: {exc}. "
            "Extract a fresh copy of the whole demo ZIP."
        ) from None
    if not isinstance(hashes, dict) or not hashes:
        raise DemoError("The offline wheel checksum manifest is empty or invalid.")
    expected_files = set()
    for name, expected in hashes.items():
        if (
            not isinstance(name, str)
            or Path(name).name != name
            or not name.endswith(".whl")
            or not isinstance(expected, str)
            or len(expected) != 64
            or any(character not in "0123456789abcdef" for character in expected)
        ):
            raise DemoError("The offline wheel checksum manifest has an invalid entry.")
        expected_files.add(name)
        try:
            with (wheelhouse / name).open("rb") as wheel:
                actual = hashlib.file_digest(wheel, "sha256").hexdigest()
        except OSError:
            raise DemoError(
                f"Offline dependency {name} is missing. Extract the whole demo ZIP."
            ) from None
        if actual != expected:
            raise DemoError(
                f"Offline dependency {name} failed its checksum. "
                "Extract a fresh copy of the demo ZIP."
            )
    actual_files = {wheel.name for wheel in wheelhouse.glob("*.whl")}
    if actual_files != expected_files:
        raise DemoError(
            "The offline wheel directory differs from its checksum manifest. "
            "Extract a fresh copy of the demo ZIP."
        )
    return wheelhouse, manifest_bytes


def python_environment(state: Path) -> Path:
    """Install the checked-in lock only when this package's lock has changed."""
    environment = ROOT / ".demo-venv"
    executable = environment / (
        "Scripts/python.exe" if os.name == "nt" else "bin/python"
    )
    lock = ROOT / "services/api/requirements.lock.txt"
    stamp = state / "requirements.sha256"
    wheelhouse, manifest_bytes = checked_wheelhouse()
    fingerprint = hashlib.sha256(
        lock.read_bytes()
        + f"\n{sys.version_info[:2]}\n{sys.platform}".encode("ascii")
        + manifest_bytes
    ).hexdigest()
    ready = executable.is_file() and stamp.is_file()
    if ready and stamp.read_text(encoding="utf-8").strip() == fingerprint:
        return executable

    print(
        "Preparing Python dependencies from the verified offline package."
        if wheelhouse
        else "Preparing Python dependencies. The first launch needs Internet access.",
        flush=True,
    )
    try:
        venv.EnvBuilder(with_pip=True).create(environment)
        offline_options = (
            ["--no-index", "--no-cache-dir", "--find-links", str(wheelhouse)]
            if wheelhouse
            else []
        )
        completed = subprocess.run(
            [
                str(executable),
                "-X",
                "utf8",
                "-m",
                "pip",
                "install",
                "--disable-pip-version-check",
                *offline_options,
                "-r",
                str(lock),
            ],
            cwd=ROOT,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise DemoError(f"Could not prepare Python dependencies: {exc}") from None
    if completed.returncode:
        raise DemoError(
            "Offline dependency installation failed. Check the error above, "
            "then extract a fresh copy of the whole demo ZIP."
            if wheelhouse
            else "Dependency installation failed. Check the installation error above "
            "and your Internet connection, then run start-demo again."
        )
    stamp.write_text(fingerprint + "\n", encoding="utf-8")
    return executable


def child_environment(state: Path, api_port: int, web_port: int) -> dict[str, str]:
    # Never inherit a configured production database or an administrator credential.
    environ = {
        key: value for key, value in os.environ.items() if not key.startswith("KHOHOC_")
    }
    environ.update(
        {
            "PYTHONPATH": os.pathsep.join((str(ROOT / "services/api"), str(ROOT))),
            "PYTHONUTF8": "1",
            "PYTHONIOENCODING": "utf-8",
            "KHOHOC_MODE": "development",
            "KHOHOC_DATABASE_URL": "sqlite:///" + (state / "demo.sqlite").as_posix(),
            "KHOHOC_ADMIN_TOKEN": "",
            "KHOHOC_MANAGER_CREDENTIALS_FILE": str(state / "TAI-KHOAN-QUAN-LY.txt"),
            "KHOHOC_CORS_ORIGINS": json.dumps(
                [f"http://localhost:{web_port}", f"http://127.0.0.1:{web_port}"]
            ),
            "KHOHOC_DEMO_API_URL": f"http://127.0.0.1:{api_port}",
        }
    )
    return environ


def start_server(
    executable: Path,
    target: str,
    port: int,
    log,
    environ: dict[str, str],
    *,
    factory: bool = False,
) -> subprocess.Popen:
    command = [str(executable), "-X", "utf8", "-m", "uvicorn", target]
    if factory:
        command.append("--factory")
    command.extend(["--host", "127.0.0.1", "--port", str(port), "--no-access-log"])
    options = (
        {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP}
        if os.name == "nt"
        else {"start_new_session": True}
    )
    return subprocess.Popen(
        command,
        cwd=ROOT,
        env=environ,
        stdin=subprocess.DEVNULL,
        stdout=log,
        stderr=subprocess.STDOUT,
        **options,
    )


def response(url: str):
    try:
        with OPENER.open(Request(url), timeout=1) as result:
            if result.status == 200:
                return result.read(2_000_000)
    except (OSError, HTTPError, URLError):
        return None
    return None


def demo_ready(api_port: int, web_port: int) -> bool:
    health = response(f"http://127.0.0.1:{api_port}/health")
    proxied_grades = response(f"http://127.0.0.1:{web_port}/api/grades")
    frontend = response(f"http://127.0.0.1:{web_port}/")
    try:
        return (
            health is not None
            and json.loads(health).get("status") == "ok"
            and proxied_grades is not None
            and [row["id"] for row in json.loads(proxied_grades)] == list(range(1, 13))
            and frontend is not None
            and b"flutter_bootstrap.js" in frontend
        )
    except (ValueError, AttributeError, KeyError, TypeError):
        return False


def stop_owned(children: list[subprocess.Popen]) -> None:
    for child in reversed(children):
        if child.poll() is None:
            child.terminate()
    for child in reversed(children):
        try:
            child.wait(timeout=5)
        except subprocess.TimeoutExpired:
            child.kill()
            child.wait(timeout=5)


def run(api_port: int, web_port: int, no_browser: bool) -> None:
    check_files()
    check_ports(api_port, web_port)
    state = ROOT / "state"
    state.mkdir(parents=True, exist_ok=True)
    executable = python_environment(state)
    # Dependencies can take time to install; check again before starting children.
    check_ports(api_port, web_port)
    environ = child_environment(state, api_port, web_port)
    children = []
    api_log = state / "api.log"
    web_log = state / "demo.log"
    print(
        "Starting the local backend and loading authored sample content...", flush=True
    )
    with (
        api_log.open("ab", buffering=0) as backend_output,
        web_log.open("ab", buffering=0) as web_output,
    ):
        try:
            children.append(
                start_server(
                    executable,
                    "khohoc.phone_preview:create_preview",
                    api_port,
                    backend_output,
                    environ,
                    factory=True,
                )
            )
            children.append(
                start_server(
                    executable, "scripts.serve_demo:app", web_port, web_output, environ
                )
            )
            deadline = time.monotonic() + 300
            while not demo_ready(api_port, web_port):
                failed = [child for child in children if child.poll() is not None]
                if failed:
                    raise DemoError(
                        f"A demo service exited during startup. See {api_log} and {web_log}."
                    )
                if time.monotonic() >= deadline:
                    raise DemoError(
                        f"The demo did not become ready within 300 seconds. See {api_log} and {web_log}."
                    )
                time.sleep(0.25)
            if any(child.poll() is not None for child in children):
                raise DemoError(f"A demo service exited. See {api_log} and {web_log}.")
            url = f"http://localhost:{web_port}"
            print(f"DEMO READY: {url}", flush=True)
            print(
                "Tai khoan quan ly: mo tep state/TAI-KHOAN-QUAN-LY.txt tren may nay; doi mat khau khi dang nhap lan dau.",
                flush=True,
            )
            print(
                "Keep this window open. Press Ctrl+C here to stop the demo.", flush=True
            )
            print(
                f"Your local practice database is saved at: {state / 'demo.sqlite'}",
                flush=True,
            )
            if not no_browser:
                try:
                    if not webbrowser.open(url):
                        print(f"Open this address in your browser: {url}", flush=True)
                except webbrowser.Error:
                    print(f"Open this address in your browser: {url}", flush=True)
            while True:
                if any(child.poll() is not None for child in children):
                    raise DemoError(
                        f"A demo service stopped. See {api_log} and {web_log}."
                    )
                time.sleep(0.5)
        finally:
            stop_owned(children)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api-port", type=port_number, default=8000)
    parser.add_argument("--port", type=port_number, default=8080)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()
    if sys.version_info[:2] != (3, 12):
        print(
            "Python 3.12 is required. Install it from https://www.python.org/downloads/ "
            "and enable 'Add Python to PATH', then run start-demo again.",
            file=sys.stderr,
        )
        return 1
    try:
        run(args.api_port, args.port, args.no_browser)
    except KeyboardInterrupt:
        print("\nDemo stopped. Your saved practice data remains in state/demo.sqlite.")
    except (DemoError, OSError) as exc:
        print(f"\nCould not start demo: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
