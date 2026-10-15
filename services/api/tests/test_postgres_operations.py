"""Operational failure/recovery tests; PostgreSQL cases use a disposable container only."""

from datetime import datetime, timedelta, timezone
import importlib.util
import os
from pathlib import Path
import secrets
import sys
import uuid

import pytest
from cryptography.exceptions import InvalidTag
from sqlalchemy import select
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

ROOT = Path(__file__).parents[3]


def load_script(name):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(
        name, ROOT / "scripts" / (name + ".py")
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


ops = load_script("backup_postgres")


def envelope(tmp_path, key, created=None, database="school"):
    created = created or ops.utcnow()
    plaintext = tmp_path / ("plain-" + secrets.token_hex(4))
    plaintext.write_bytes(b"PGDMP" + secrets.token_bytes(2 * ops.BLOCK + 37))
    archive = (
        tmp_path / f"tuhoc-pg-{created:%Y%m%dT%H%M%SZ}-{secrets.token_hex(6)}.tuhocpg"
    )
    ops.seal(
        plaintext,
        archive,
        key,
        dict(
            format=1,
            schema_version=1,
            database=database,
            created_at=created.isoformat(),
        ),
    )
    plaintext.unlink()
    return archive


@pytest.mark.parametrize(
    "failure", ["wrong_key", "changed_body", "changed_header", "truncated"]
)
def test_tampered_operations_archive_cannot_leave_plaintext(tmp_path, failure):
    key = secrets.token_bytes(32)
    archive = envelope(tmp_path, key)
    data = bytearray(archive.read_bytes())
    if failure == "wrong_key":
        key = secrets.token_bytes(32)
    elif failure == "changed_body":
        data[-100] ^= 1
    elif failure == "changed_header":
        data[len(ops.MAGIC) + 10] ^= 1
    else:
        data = data[:-7]
    archive.write_bytes(data)
    restored = tmp_path / "restored"
    with pytest.raises((InvalidTag, ValueError, KeyError)):
        ops.unseal(archive, restored, key)
    assert not restored.exists()


def test_operations_never_overwrite_keys_archives_or_plaintext(tmp_path):
    key_file = tmp_path / "postgres.backup-key"
    ops.keygen(key_file)
    original = key_file.read_bytes()
    with pytest.raises(FileExistsError):
        ops.keygen(key_file)
    assert key_file.read_bytes() == original
    archive = envelope(tmp_path, ops.read_key(key_file))
    restored = tmp_path / "existing"
    restored.write_bytes(b"keep this file")
    with pytest.raises(FileExistsError):
        ops.unseal(archive, restored, original)
    assert restored.read_bytes() == b"keep this file"
    with pytest.raises(FileExistsError):
        ops.seal(restored, archive, original, {})
    key_file.chmod(0o644)
    with pytest.raises(ValueError, match="private"):
        ops.read_key(key_file)


def test_operations_retention_protects_two_valid_copies_unknown_files_and_other_databases(
    tmp_path,
):
    key = secrets.token_bytes(32)
    now = ops.utcnow()
    old = [envelope(tmp_path, key, now - timedelta(days=days)) for days in (90, 80, 70)]
    current = envelope(tmp_path, key, now)
    unrelated = tmp_path / "do-not-delete.txt"
    unrelated.write_text("keep")
    other_database = envelope(
        tmp_path, key, now - timedelta(days=100), database="other"
    )
    other_key = envelope(tmp_path, secrets.token_bytes(32), now - timedelta(days=120))
    symlink = tmp_path / f"tuhoc-pg-{now:%Y%m%dT%H%M%SZ}-abcdefabcdef.tuhocpg"
    symlink.symlink_to(old[0])
    assert ops.prune(tmp_path, key, 30, "school", now) == 2
    assert not old[0].exists() and not old[1].exists()
    assert old[2].exists() and current.exists()
    assert (
        other_database.exists()
        and other_key.exists()
        and unrelated.exists()
        and symlink.is_symlink()
    )


def test_operations_lock_prevents_overlapping_backup_jobs(tmp_path):
    directory = tmp_path / "backups"
    with ops.lock(directory):
        with pytest.raises(BlockingIOError):
            with ops.lock(directory):
                pytest.fail("Overlapping lock acquired")


def test_operations_status_detects_missing_stale_failed_and_changed_backup(tmp_path):
    directory = tmp_path / "backups"
    directory.mkdir(mode=0o700)
    assert ops.backup_status(directory) == "missing"
    archive = envelope(directory, secrets.token_bytes(32))
    status = dict(
        last_success_at=ops.utcnow().isoformat(),
        archive=archive.name,
        sha256=ops.digest(archive),
        last_attempt_ok=True,
    )
    ops.atomic_json(directory / "status.json", status)
    assert ops.backup_status(directory) == "fresh"
    status["last_attempt_ok"] = False
    ops.atomic_json(directory / "status.json", status)
    assert ops.backup_status(directory) == "failed"
    status["last_success_at"] = (ops.utcnow() - timedelta(hours=27)).isoformat()
    ops.atomic_json(directory / "status.json", status)
    assert ops.backup_status(directory) == "stale"
    status.update(last_success_at=ops.utcnow().isoformat(), last_attempt_ok=True)
    ops.atomic_json(directory / "status.json", status)
    archive.write_bytes(b"broken")
    assert ops.backup_status(directory) == "invalid"


def test_operations_failed_backup_does_not_claim_success_or_prune(tmp_path):
    class FailingDriver:
        def verify(self, database):
            raise RuntimeError("Unavailable database")

    key = tmp_path / "postgres.backup-key"
    ops.keygen(key)
    directory = tmp_path / "backups"
    with pytest.raises(RuntimeError):
        ops.backup(FailingDriver(), "school", directory, key, 30)
    assert ops.read_status(directory)["last_attempt_ok"] is False
    assert not list(directory.glob("*.tuhocpg"))


@pytest.fixture
def pg_source(tmp_path):
    url = os.environ.get("KHOHOC_TEST_POSTGRES_URL")
    container = os.environ.get("KHOHOC_TEST_POSTGRES_CONTAINER")
    if not url or not container:
        pytest.skip(
            "Run scripts/test_shared_postgres.py for real PostgreSQL recovery tests"
        )
    from khohoc.accounts import password_hash
    from khohoc.database import make_engine, migrate
    from khohoc.models import (
        LearningUser,
        LearningRecord,
        LearningSession,
        ClassroomGroup,
        GroupMember,
    )

    database = "ops_" + uuid.uuid4().hex
    driver = ops.PostgresDocker(container=container, username="postgres")
    driver.run(["createdb", "-U", "postgres", database])
    engine = make_engine(
        make_url(url).set(database=database).render_as_string(hide_password=False)
    )
    targets = []
    key = tmp_path / "postgres.backup-key"
    ops.keygen(key)
    try:
        migrate(engine)
        with Session(engine) as db:
            db.add(
                LearningUser(
                    id="manager",
                    username="manager",
                    display_name="Quản lý phục hồi",
                    role="manager",
                    password_hash=password_hash("Synthetic-recovery-password-123"),
                )
            )
            db.add(
                LearningUser(
                    id="student",
                    username="student",
                    display_name="Học viên phục hồi",
                    role="student",
                    manager_id="manager",
                    password_hash=password_hash("Synthetic-recovery-password-123"),
                )
            )
            db.add(
                ClassroomGroup(
                    id="group",
                    owner_id="manager",
                    name="Nhóm khôi phục",
                    join_code="synthetic-backup-code",
                )
            )
            db.add(GroupMember(group_id="group", user_id="student"))
            db.add(
                LearningRecord(
                    attempt_id="historical-score",
                    user_id="student",
                    payload={
                        "result": {
                            "title": "Bài trước sự cố",
                            "score": 8,
                            "max_score": 10,
                        }
                    },
                )
            )
            db.add(
                LearningSession(
                    token_hash="f" * 64,
                    user_id="student",
                    expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
                )
            )
            db.commit()
        yield driver, database, engine, key, tmp_path, targets, url
    finally:
        engine.dispose()
        for name in targets + [database]:
            driver.run(["dropdb", "-U", "postgres", "--if-exists", "--force", name])


def target_database(targets):
    name = "recovery_" + uuid.uuid4().hex
    targets.append(name)
    return name


def test_operations_postgres_backup_restore_preserves_students_groups_scores_and_revokes_sessions(
    pg_source,
):
    from khohoc.models import LearningRecord, LearningSession
    from khohoc.database import make_engine
    from khohoc.app import Settings, create_app
    from fastapi.testclient import TestClient

    driver, database, engine, key, root, targets, url = pg_source
    archive = ops.backup(driver, database, root / "backups", key, 30)
    assert ops.backup_status(root / "backups") == "fresh"
    with Session(engine) as db:
        row = db.get(LearningRecord, "historical-score")
        row.payload = {"result": {"title": "Sau sao lưu", "score": 2, "max_score": 10}}
        db.commit()
    target = target_database(targets)
    ops.restore(driver, archive, target, key)
    target_url = (
        make_url(url).set(database=target).render_as_string(hide_password=False)
    )
    restored = make_engine(target_url)
    with Session(restored) as db:
        assert (
            db.get(LearningRecord, "historical-score").payload["result"]["score"] == 8
        )
        assert db.scalar(select(LearningSession)) is None
    restored.dispose()
    config = Settings(
        database_url=target_url,
        mode="shared",
        public_origin="https://study.test.edu.vn",
        cors_origins=["https://study.test.edu.vn"],
    )
    with TestClient(create_app(config), base_url="https://study.test.edu.vn") as client:
        assert client.get("/ready").status_code == 200
        login = client.post(
            "/auth/login",
            json={"username": "student", "password": "Synthetic-recovery-password-123"},
        )
        assert login.status_code == 200
        assert client.get("/classroom/groups").json()[0]["name"] == "Nhóm khôi phục"
        assert client.get("/account/results").json()[0]["result"]["score"] == 8
    with Session(engine) as db:
        assert (
            db.get(LearningRecord, "historical-score").payload["result"]["score"] == 2
        )
        assert db.scalar(select(LearningSession)) is not None


def test_operations_bad_key_does_not_create_database_and_existing_database_is_untouched(
    pg_source,
):
    driver, database, engine, key, root, targets, url = pg_source
    archive = ops.backup(driver, database, root / "backups", key)
    wrong = root / "wrong.backup-key"
    ops.keygen(wrong)
    target = target_database(targets)
    with pytest.raises(InvalidTag):
        ops.restore(driver, archive, target, wrong)
    assert (
        driver.sql(
            "postgres", f"SELECT count(*) FROM pg_database WHERE datname='{target}'"
        )
        == b"0"
    )
    with pytest.raises(ValueError, match="NEW recovery"):
        ops.restore(driver, archive, database, key)
    driver.run(["createdb", "-U", "postgres", target])
    driver.sql(
        target,
        "CREATE TABLE sentinel (value INTEGER); INSERT INTO sentinel VALUES (123);",
    )
    with pytest.raises(RuntimeError):
        ops.restore(driver, archive, target, key)
    assert driver.sql(target, "SELECT value FROM sentinel") == b"123"


def test_operations_key_failure_records_failed_job_without_removing_previous_archive(
    tmp_path,
):
    directory = tmp_path / "backups"
    directory.mkdir(mode=0o700)
    archive = envelope(directory, secrets.token_bytes(32))
    previous = dict(
        last_success_at=ops.utcnow().isoformat(),
        archive=archive.name,
        sha256=ops.digest(archive),
        last_attempt_ok=True,
    )
    ops.atomic_json(directory / "status.json", previous)

    class NeverCalled:
        def verify(self, database):
            pytest.fail("Missing key must not reach the database")

    with pytest.raises(ValueError, match="private"):
        ops.backup(NeverCalled(), "school", directory, tmp_path / "missing-key", 30)
    assert archive.exists()
    assert ops.read_status(directory)["last_success_at"] == previous["last_success_at"]
    assert ops.backup_status(directory) == "failed"


def test_operations_cli_config_failure_is_reported_without_private_diagnostics(
    tmp_path, monkeypatch, capsys
):
    directory = tmp_path / "backups"
    directory.mkdir(mode=0o700)
    archive = envelope(directory, secrets.token_bytes(32))
    ops.atomic_json(
        directory / "status.json",
        dict(
            last_success_at=ops.utcnow().isoformat(),
            archive=archive.name,
            sha256=ops.digest(archive),
            last_attempt_ok=True,
        ),
    )

    class BadConfiguration:
        def configured_database(self):
            raise RuntimeError("private database diagnostic")

    monkeypatch.setattr(ops, "PostgresDocker", lambda **kwargs: BadConfiguration())
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "backup_postgres.py",
            "backup",
            "--directory",
            str(directory),
            "--key-file",
            str(tmp_path / "key"),
        ],
    )
    assert ops.main() == 1
    assert "private database diagnostic" not in capsys.readouterr().out
    assert ops.backup_status(directory) == "failed"
    assert archive.exists()


@pytest.mark.parametrize(
    "url",
    [
        "postgresql+psycopg://app@external-db.test.edu.vn/tuhoc",
        "postgresql+psycopg://app@db:5555/tuhoc",
        "postgresql+psycopg://app@db/tuhoc?host=external-db.test.edu.vn",
        "postgresql+psycopg://app@db/tuhoc?dbname=another_database",
    ],
)
def test_operations_auto_source_rejects_external_or_ambiguous_database(
    tmp_path, monkeypatch, url
):
    from types import SimpleNamespace
    import json

    driver = ops.PostgresDocker(compose_file=tmp_path / "compose.yaml")
    value = {"services": {"api": {"environment": {"KHOHOC_DATABASE_URL": url}}}}
    monkeypatch.setattr(
        ops.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(stdout=json.dumps(value).encode()),
    )
    with pytest.raises(ValueError):
        driver.configured_database()
