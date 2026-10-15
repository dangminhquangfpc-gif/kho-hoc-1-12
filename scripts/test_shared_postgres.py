"""Disposable, password-protected PostgreSQL integration test; publishes loopback only."""

import os
from pathlib import Path
import secrets
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
DOCKER = ["docker", "--host=unix:///var/run/docker.sock"]


def main():
    name = "tuhoc-integration-" + secrets.token_hex(5)
    password = secrets.token_urlsafe(32)
    with tempfile.TemporaryDirectory(prefix="tuhoc-pg-") as directory:
        env_file = Path(directory) / "postgres.env"
        env_file.write_text("POSTGRES_PASSWORD=" + password + "\n")
        env_file.chmod(0o600)
        try:
            subprocess.run(
                DOCKER
                + [
                    "run",
                    "-d",
                    "--name",
                    name,
                    "--env-file",
                    str(env_file),
                    "-p",
                    "127.0.0.1::5432",
                    "postgres:17",
                ],
                check=True,
                stdout=subprocess.DEVNULL,
            )
            deadline = time.monotonic() + 60
            while subprocess.run(
                DOCKER
                + ["exec", name, "pg_isready", "-h", "127.0.0.1", "-U", "postgres"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            ).returncode:
                if time.monotonic() > deadline:
                    raise RuntimeError("PostgreSQL did not become ready")
                time.sleep(0.25)
            address = subprocess.check_output(
                DOCKER + ["port", name, "5432/tcp"], text=True
            ).strip()
            port = address.rsplit(":", 1)[1]
            environment = os.environ.copy()
            environment["PYTHONPATH"] = str(ROOT / "services/api")
            environment["KHOHOC_TEST_POSTGRES_URL"] = (
                f"postgresql+psycopg://postgres:{password}@127.0.0.1:{port}/postgres"
            )
            environment["KHOHOC_TEST_POSTGRES_CONTAINER"] = name
            return subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    "-q",
                    "services/api/tests/test_shared_server.py",
                    "services/api/tests/test_assignment_sync.py",
                    "services/api/tests/test_postgres_operations.py",
                    "services/api/tests/test_content_transfer.py",
                    "services/api/tests/test_free_server_postgres.py",
                    "-k",
                    "postgresql or unsafe or operations",
                ],
                cwd=ROOT,
                env=environment,
            ).returncode
        finally:
            subprocess.run(
                DOCKER + ["rm", "-f", name],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )


if __name__ == "__main__":
    sys.exit(main())
