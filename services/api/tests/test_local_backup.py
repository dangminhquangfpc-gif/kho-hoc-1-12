import importlib.util
from pathlib import Path
import sqlite3

import pytest
from cryptography.exceptions import InvalidTag
from sqlalchemy import create_engine

from khohoc.models import Base

spec = importlib.util.spec_from_file_location(
    "backup_local", Path(__file__).parents[3] / "scripts" / "backup_local.py"
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


@pytest.fixture
def files(tmp_path):
    database = tmp_path / "source.db"
    engine = create_engine("sqlite:///" + str(database))
    Base.metadata.create_all(engine)
    engine.dispose()
    key = tmp_path / "key"
    module.write_private(key, bytes(range(32)))
    return database, key, tmp_path / "backup.enc", tmp_path / "restored.db"


def test_live_wal_roundtrip_preserves_private_data(files):
    database, key, archive, restored = files
    with sqlite3.connect(database) as db:
        db.execute("PRAGMA journal_mode=WAL")
        db.execute("CREATE TABLE backup_probe (value TEXT)")
        db.execute(
            "INSERT INTO backup_probe VALUES (?)", ("kết quả học viên riêng tư",)
        )
        db.commit()
        module.backup(database, archive, key)
        assert "học viên".encode() not in archive.read_bytes()
        module.restore(archive, restored, key)
        with sqlite3.connect(restored) as recovered:
            assert recovered.execute("SELECT value FROM backup_probe").fetchone() == (
                "kết quả học viên riêng tư",
            )


@pytest.mark.parametrize("failure", ["wrong_key", "tampered"])
def test_authentication_failure_leaves_no_restore(files, failure):
    database, key, archive, restored = files
    module.backup(database, archive, key)
    if failure == "wrong_key":
        key.write_bytes(b"x" * 32)
    else:
        payload = bytearray(archive.read_bytes())
        payload[-1] ^= 1
        archive.write_bytes(payload)
    with pytest.raises(InvalidTag):
        module.restore(archive, restored, key)
    assert not restored.exists()


def test_refuses_overwrite_database_and_backup(files):
    database, key, archive, restored = files
    module.backup(database, archive, key)
    original = archive.read_bytes()
    with pytest.raises(FileExistsError):
        module.backup(database, archive, key)
    assert archive.read_bytes() == original
    restored.write_bytes(b"existing data")
    with pytest.raises(FileExistsError):
        module.restore(archive, restored, key)
    assert restored.read_bytes() == b"existing data"


def test_rejects_unrelated_database(files):
    database, key, archive, restored = files
    unrelated = database.parent / "unrelated.db"
    with sqlite3.connect(unrelated) as db:
        db.execute("CREATE TABLE other (id INTEGER)")
    with pytest.raises(ValueError):
        module.backup(unrelated, archive, key)
    assert not archive.exists()


def test_missing_source_is_not_created(files):
    database, key, archive, restored = files
    missing = database.parent / "missing.db"
    with pytest.raises(sqlite3.OperationalError):
        module.backup(missing, archive, key)
    assert not missing.exists()


def test_restored_backend_can_authenticate_existing_student(files):
    from fastapi.testclient import TestClient
    from sqlalchemy.orm import Session
    from khohoc.accounts import password_hash
    from khohoc.app import Settings, create_app
    from khohoc.models import LearningUser

    database, key, archive, restored = files
    engine = create_engine("sqlite:///" + str(database))
    with Session(engine) as session:
        session.add(
            LearningUser(
                id="backup-student",
                username="student_test",
                display_name="Học viên kiểm thử",
                role="student",
                grade=6,
                active=True,
                must_change_password=False,
                password_hash=password_hash("Synthetic-test-password-123"),
            )
        )
        session.commit()
    engine.dispose()
    module.backup(database, archive, key)
    module.restore(archive, restored, key)
    app = create_app(Settings(database_url="sqlite:///" + str(restored)))
    with TestClient(app) as client:
        assert client.get("/health").status_code == 200
        response = client.post(
            "/auth/login",
            json={
                "username": "student_test",
                "password": "Synthetic-test-password-123",
            },
        )
        assert response.status_code == 200
        assert response.json()["user"]["display_name"] == "Học viên kiểm thử"
        assert response.json()["user"]["role"] == "student"
