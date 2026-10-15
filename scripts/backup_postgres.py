"""Linux operator tool: authenticated PostgreSQL backups; restore only to new recovery_* DBs."""

import argparse
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import resource
import secrets
import struct
import subprocess
import tempfile
from urllib.parse import urlsplit, parse_qs

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.exceptions import InvalidTag

MAGIC = b"TUHOC111-PG-1\n"
MAX_BYTES = 512 * 1024 * 1024
BLOCK = 1024 * 1024
NAME = re.compile(r"tuhoc-pg-(\d{8}T\d{6}Z)-[a-f0-9]{12}\.tuhocpg")
ROOT = Path(__file__).resolve().parents[1]


def utcnow():
    return datetime.now(timezone.utc).replace(microsecond=0)


def limit_output():
    resource.setrlimit(resource.RLIMIT_FSIZE, (MAX_BYTES + 1, MAX_BYTES + 1))


def sync_directory(path):
    descriptor = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def keygen(path):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(secrets.token_bytes(32))
        stream.flush()
        os.fsync(stream.fileno())
    sync_directory(path.parent)


def read_key(path):
    if path.is_symlink() or not path.is_file() or path.stat().st_mode & 0o077:
        raise ValueError("Key must be a private regular file (0400/0600)")
    key = path.read_bytes()
    if len(key) != 32:
        raise ValueError("Invalid key length")
    return key


def private_directory(directory):
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    if directory.is_symlink() or directory.stat().st_mode & 0o077:
        raise ValueError("Backup directory must be private (0700)")


@contextmanager
def lock(directory):
    private_directory(directory)
    descriptor = os.open(
        directory / ".backup.lock", os.O_WRONLY | os.O_CREAT | os.O_NOFOLLOW, 0o600
    )
    with os.fdopen(descriptor, "w") as stream:
        fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield


def seal(source, destination, key, metadata):
    size = source.stat().st_size
    if size > MAX_BYTES:
        raise ValueError("Backup exceeds 512 MiB")
    header = json.dumps(
        {**metadata, "bytes": size, "sha256": digest(source)}, sort_keys=True
    ).encode()
    associated = MAGIC + struct.pack(">I", len(header)) + header
    nonce = secrets.token_bytes(12)
    encryptor = Cipher(algorithms.AES(key), modes.GCM(nonce)).encryptor()
    encryptor.authenticate_additional_data(associated)
    descriptor = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with source.open("rb") as incoming, os.fdopen(descriptor, "wb") as outgoing:
        outgoing.write(associated + nonce)
        while block := incoming.read(BLOCK):
            outgoing.write(encryptor.update(block))
        outgoing.write(encryptor.finalize() + encryptor.tag)
        outgoing.flush()
        os.fsync(outgoing.fileno())


def unseal(archive, destination, key):
    # Authenticate the full file and digest before the caller can touch any database.
    if (
        archive.is_symlink()
        or not archive.is_file()
        or archive.stat().st_size > MAX_BYTES + 8192
    ):
        raise ValueError("Invalid backup file")
    with archive.open("rb") as incoming:
        if incoming.read(len(MAGIC)) != MAGIC:
            raise ValueError("Invalid backup format")
        encoded_size = incoming.read(4)
        header_size = struct.unpack(">I", encoded_size)[0]
        if not 1 <= header_size <= 4096:
            raise ValueError("Invalid header")
        header = incoming.read(header_size)
        metadata = json.loads(header)
        if (
            not isinstance(metadata, dict)
            or type(metadata.get("bytes")) is not int
            or not 0 <= metadata["bytes"] <= MAX_BYTES
        ):
            raise ValueError("Invalid backup metadata")
        nonce = incoming.read(12)
        remaining = archive.stat().st_size - incoming.tell() - 16
        if remaining != metadata["bytes"]:
            raise ValueError("Truncated backup")
        incoming.seek(-16, 2)
        tag = incoming.read(16)
        incoming.seek(len(MAGIC) + 4 + header_size + 12)
        decryptor = Cipher(algorithms.AES(key), modes.GCM(nonce, tag)).decryptor()
        decryptor.authenticate_additional_data(MAGIC + encoded_size + header)
        descriptor = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        try:
            with os.fdopen(descriptor, "wb") as outgoing:
                while remaining:
                    block = incoming.read(min(remaining, BLOCK))
                    if not block:
                        raise ValueError("Truncated backup")
                    remaining -= len(block)
                    outgoing.write(decryptor.update(block))
                outgoing.write(decryptor.finalize())
            if not secrets.compare_digest(digest(destination), metadata["sha256"]):
                raise ValueError("Backup checksum mismatch")
            with destination.open("rb") as stream:
                if stream.read(5) != b"PGDMP":
                    raise ValueError("Not a PostgreSQL custom archive")
            if (
                metadata.get("schema_version") not in (1, 2)
                or metadata.get("format") != 1
            ):
                raise ValueError("Unsupported backup/schema version")
            created = datetime.fromisoformat(metadata["created_at"])
            if created.tzinfo is None:
                raise ValueError("Missing UTC timestamp")
            return metadata
        except BaseException:
            destination.unlink(missing_ok=True)
            raise


class PostgresDocker:
    def __init__(
        self,
        *,
        compose_file=None,
        env_file=None,
        project=None,
        container=None,
        username="tuhoc_owner",
    ):
        if not re.fullmatch(r"[a-z_][a-z0-9_]{0,62}", username):
            raise ValueError("Invalid PostgreSQL role")
        self.username = username
        self.compose_prefix = None
        self.prefix = ["docker", "--host=unix:///var/run/docker.sock"]
        if container:
            self.prefix += ["exec", "-i", container]
        else:
            self.prefix += ["compose"]
            if env_file:
                self.prefix += ["--env-file", str(env_file)]
            if project:
                self.prefix += ["--project-name", project]
            self.prefix += ["-f", str(compose_file)]
            self.compose_prefix = self.prefix.copy()
            self.prefix += ["exec", "-T", "db"]

    def configured_database(self):
        if self.compose_prefix is None:
            raise ValueError("Explicit source database required without Compose")
        result = subprocess.run(
            self.compose_prefix + ["config", "--format", "json"],
            capture_output=True,
            check=True,
            timeout=30,
        )
        value = json.loads(result.stdout)["services"]["api"]["environment"][
            "KHOHOC_DATABASE_URL"
        ]
        url = urlsplit(value)
        database = url.path.removeprefix("/")
        if (
            url.scheme != "postgresql+psycopg"
            or url.hostname != "db"
            or url.port not in (None, 5432)
            or not re.fullmatch(r"[a-z_][a-z0-9_]{0,62}", database)
        ):
            raise ValueError("Unsupported API database configuration")
        if {"dbname", "database", "service", "host", "hostaddr", "port"} & set(
            parse_qs(url.query)
        ):
            raise ValueError("Ambiguous API database configuration")
        return database

    def run(self, arguments, *, source=None, destination=None, capture=False):
        with tempfile.TemporaryFile() as errors:
            result = subprocess.run(
                self.prefix + arguments,
                stdin=source,
                stdout=subprocess.PIPE
                if capture
                else (destination or subprocess.DEVNULL),
                stderr=errors,
                timeout=300,
                check=False,
                preexec_fn=limit_output if destination is not None else None,
            )
        if result.returncode:
            raise RuntimeError(
                "PostgreSQL operation failed; database names, access and server logs should be checked privately"
            )
        return result.stdout if capture else None

    def sql(self, database, statement):
        return self.run(
            [
                "psql",
                "-X",
                "-v",
                "ON_ERROR_STOP=1",
                "-U",
                self.username,
                "-d",
                database,
                "-tAc",
                statement,
            ],
            capture=True,
        ).strip()

    def verify(self, database):
        version = self.sql(database, "SELECT version FROM app_schema_version")
        if version not in (b"1", b"2"):
            raise ValueError("Unsupported schema")
        self.sql(
            database,
            "SELECT id FROM learning_users LIMIT 1; SELECT attempt_id FROM learning_records LIMIT 1;",
        )
        if version == b"2":
            self.sql(database, "SELECT id FROM content_reports LIMIT 1")
        return int(version)


def atomic_json(path, value):
    descriptor, temporary = tempfile.mkstemp(prefix=".status-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w") as stream:
            json.dump(value, stream, sort_keys=True)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        sync_directory(path.parent)
    finally:
        Path(temporary).unlink(missing_ok=True)


def read_status(directory):
    path = directory / "status.json"
    if not path.exists():
        return {}
    if path.is_symlink() or path.stat().st_size > 8192:
        raise ValueError("Invalid status file")
    return json.loads(path.read_text())


def backup_status(directory, max_age_hours=26, now=None):
    try:
        value = read_status(directory)
        created = datetime.fromisoformat(value["last_success_at"])
        age = ((now or utcnow()) - created).total_seconds()
        name = value["archive"]
        if not NAME.fullmatch(name) or not 0 <= age <= max_age_hours * 3600:
            return "stale"
        archive = directory / name
        if (
            archive.is_symlink()
            or not archive.is_file()
            or digest(archive) != value["sha256"]
        ):
            return "invalid"
        return "fresh" if value.get("last_attempt_ok") is True else "failed"
    except (OSError, ValueError, KeyError, TypeError):
        return "missing"


def prune(directory, key, retention_days, database, now=None):
    if not 1 <= retention_days <= 365:
        raise ValueError("Retention must be 1–365 days")
    cutoff = (now or utcnow()) - timedelta(days=retention_days)
    candidates = sorted(
        (
            p
            for p in directory.iterdir()
            if NAME.fullmatch(p.name) and not p.is_symlink()
        ),
        reverse=True,
    )
    valid = 0
    removed = 0
    for archive in candidates:
        with tempfile.TemporaryDirectory(prefix="tuhoc-verify-") as temporary:
            try:
                metadata = unseal(archive, Path(temporary) / "dump", key)
            except (OSError, ValueError, KeyError, TypeError, struct.error, InvalidTag):
                continue
        if metadata.get("database") != database:
            continue
        created = datetime.fromisoformat(metadata["created_at"])
        if NAME.fullmatch(archive.name).group(1) != created.strftime("%Y%m%dT%H%M%SZ"):
            continue
        valid += 1
        if valid > 2 and created < cutoff:
            archive.unlink()
            removed += 1
    return removed


def backup(driver, database, directory, key_file, retention_days=None):
    if not re.fullmatch(r"[a-z_][a-z0-9_]{0,62}", database):
        raise ValueError("Invalid source database")
    with lock(directory):
        previous = read_status(directory)
        attempt_at = utcnow().isoformat()
        try:
            key = read_key(key_file)
            schema_version = driver.verify(database)
            with tempfile.TemporaryDirectory(prefix="tuhoc-pg-backup-") as temporary:
                temporary = Path(temporary)
                dump = temporary / "dump"
                with dump.open("xb") as output:
                    driver.run(
                        [
                            "pg_dump",
                            "-U",
                            driver.username,
                            "-d",
                            database,
                            "-Fc",
                            "--no-owner",
                            "--no-acl",
                        ],
                        destination=output,
                    )
                created = utcnow()
                metadata = dict(
                    format=1,
                    schema_version=schema_version,
                    database=database,
                    created_at=created.isoformat(),
                )
                encrypted = temporary / "encrypted"
                seal(dump, encrypted, key, metadata)
                unseal(encrypted, temporary / "verified", key)
                name = (
                    f"tuhoc-pg-{created:%Y%m%dT%H%M%SZ}-{secrets.token_hex(6)}.tuhocpg"
                )
                # Stage on the same filesystem for atomic, exclusive publication.
                descriptor, staging = tempfile.mkstemp(
                    prefix=".archive-", dir=directory
                )
                try:
                    with (
                        encrypted.open("rb") as incoming,
                        os.fdopen(descriptor, "wb") as outgoing,
                    ):
                        while block := incoming.read(BLOCK):
                            outgoing.write(block)
                        outgoing.flush()
                        os.fsync(outgoing.fileno())
                    os.link(staging, directory / name)
                finally:
                    Path(staging).unlink(missing_ok=True)
                sync_directory(directory)
                value = dict(
                    database=database,
                    last_success_at=created.isoformat(),
                    archive=name,
                    sha256=digest(directory / name),
                    last_attempt_at=attempt_at,
                    last_attempt_ok=True,
                )
                if retention_days is not None:
                    prune(directory, key, retention_days, database)
                atomic_json(directory / "status.json", value)
                return directory / name
        except Exception:
            atomic_json(
                directory / "status.json",
                {**previous, "last_attempt_at": attempt_at, "last_attempt_ok": False},
            )
            raise


def restore(driver, archive, database, key_file):
    if not re.fullmatch(r"recovery_[a-z0-9_]{1,50}", database):
        raise ValueError("Restore only accepts a NEW recovery_* database")
    key = read_key(key_file)
    with tempfile.TemporaryDirectory(prefix="tuhoc-pg-restore-") as temporary:
        dump = Path(temporary) / "dump"
        metadata = unseal(archive, dump, key)
        with dump.open("rb") as source:
            driver.run(["pg_restore", "--list"], source=source)
        # createdb refuses existing targets. Never issue drop/clean/overwrite commands.
        driver.run(
            ["createdb", "-U", driver.username, "--template=template0", database]
        )
        with dump.open("rb") as source:
            driver.run(
                [
                    "pg_restore",
                    "-U",
                    driver.username,
                    "-d",
                    database,
                    "--single-transaction",
                    "--exit-on-error",
                    "--no-owner",
                    "--no-acl",
                ],
                source=source,
            )
        if driver.verify(database) != metadata["schema_version"]:
            raise ValueError("Restored schema differs from archive metadata")
        driver.sql(
            database,
            "BEGIN; DELETE FROM learning_sessions; DELETE FROM request_budgets; COMMIT;",
        )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    generate = commands.add_parser("keygen")
    generate.add_argument("--key-file", required=True, type=Path)
    status = commands.add_parser("status")
    status.add_argument("--directory", required=True, type=Path)
    status.add_argument("--max-age-hours", type=int, default=26)
    for command in ("backup", "restore"):
        action = commands.add_parser(command)
        action.add_argument("--key-file", required=True, type=Path)
        action.add_argument(
            "--compose-file", type=Path, default=ROOT / "deploy/shared/compose.yaml"
        )
        action.add_argument(
            "--env-file", type=Path, default=ROOT / "deploy/shared/.env"
        )
        action.add_argument("--project-name")
        action.add_argument("--username", default="tuhoc_owner")
        if command == "backup":
            action.add_argument("--database")
            action.add_argument("--directory", required=True, type=Path)
            action.add_argument(
                "--retention-days", type=int, choices=range(1, 366), metavar="1–365"
            )
        else:
            action.add_argument("--database", required=True)
            action.add_argument("--archive", required=True, type=Path)
    args = parser.parse_args()
    try:
        if args.command == "keygen":
            keygen(args.key_file)
        elif args.command == "status":
            state = backup_status(args.directory, args.max_age_hours)
            print(json.dumps({"backup": state}))
            return 0 if state == "fresh" else 1
        else:
            driver = PostgresDocker(
                compose_file=args.compose_file,
                env_file=args.env_file,
                project=args.project_name,
                username=args.username,
            )
            if args.command == "backup":
                backup(
                    driver,
                    args.database or driver.configured_database(),
                    args.directory,
                    args.key_file,
                    args.retention_days,
                )
            else:
                restore(driver, args.archive, args.database, args.key_file)
        print("Hoàn tất. Không chia sẻ khóa hoặc dữ liệu sao lưu.")
        return 0
    except Exception as error:
        if args.command == "backup" and not isinstance(error, BlockingIOError):
            try:
                with lock(args.directory):
                    previous = read_status(args.directory)
                    atomic_json(
                        args.directory / "status.json",
                        {
                            **previous,
                            "last_attempt_at": utcnow().isoformat(),
                            "last_attempt_ok": False,
                        },
                    )
            except Exception:
                pass  # Never replace the original failure or overwrite an invalid status file.
        print(
            "Không hoàn tất. Kiểm tra trạng thái dịch vụ, khóa, quyền truy cập và tên database; không khôi phục đè dữ liệu đang dùng."
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
