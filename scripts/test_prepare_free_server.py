"""Credential-safe owner setup; no hosted accounts or external databases are used."""

from contextlib import contextmanager
import importlib.util
from pathlib import Path
import stat
from unittest.mock import MagicMock

import pytest
from sqlalchemy.engine import make_url
from sqlalchemy.dialects.postgresql import dialect as postgres_dialect

SPEC = importlib.util.spec_from_file_location(
    "prepare_free_server", Path(__file__).with_name("prepare_free_server.py")
)
setup = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(setup)
OWNER = "postgresql://neondb_owner:owner-secret@ep-orange-cloud-123456.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"


def test_owner_url_uses_verified_tls_local_ca_and_fixed_driver():
    url = setup.normalize_owner_url(OWNER)
    assert url.drivername == "postgresql+psycopg"
    assert url.query == {
        "sslmode": "verify-full",
        "sslrootcert": setup.certifi.where(),
        "channel_binding": "require",
    }
    assert url.password == "owner-secret"
    modern = OWNER.replace(".us-east-2.", ".c-2.us-east-2.")
    assert setup.normalize_owner_url(modern).host.endswith(".aws.neon.tech")


@pytest.mark.parametrize(
    "url",
    [
        OWNER.replace("ep-orange-cloud-123456.", "ep-orange-cloud-123456-pooler."),
        OWNER.replace(".aws.neon.tech", ".aws.neon.tech.evil.example"),
        OWNER.replace(".aws.neon.tech", ".azure.neon.tech"),
        OWNER.replace("ep-orange-cloud-123456.us-east-2.aws.neon.tech", "localhost"),
        OWNER.replace("neondb_owner", "tuhoc_app"),
        OWNER.replace("sslmode=require", "sslmode=disable"),
        OWNER + "&sslrootcert=/untrusted.pem",
        OWNER + "&options=-csearch_path=evil",
        OWNER + "&sslmode=verify-full",
        OWNER.replace("/neondb?", ":5433/neondb?"),
        OWNER.replace(":owner-secret@", "@"),
        "not-a-url-owner-secret",
    ],
)
def test_untrusted_owner_inputs_refused_without_echo(url):
    with pytest.raises(setup.PreparationError) as failure:
        setup.normalize_owner_url(url)
    assert "owner-secret" not in str(failure.value)
    assert "ep-orange" not in str(failure.value)


def test_owner_input_file_permissions_and_symlink(tmp_path):
    private = tmp_path / "owner.private"
    private.write_text(OWNER)
    private.chmod(0o600)
    assert setup.read_owner_url(private).username == "neondb_owner"
    private.chmod(0o644)
    with pytest.raises(setup.PreparationError, match="0600"):
        setup.read_owner_url(private)
    linked = tmp_path / "linked"
    linked.symlink_to(private)
    with pytest.raises(setup.PreparationError, match="regular file"):
        setup.read_owner_url(linked)


def test_private_output_never_overwrites_or_follows_symlinks(tmp_path):
    target = tmp_path / "private"
    result = setup._new_private_directory(target)
    setup._private_write(result / "render-private.env", "secret")
    assert stat.S_IMODE(target.stat().st_mode) == 0o700
    assert stat.S_IMODE((target / "render-private.env").stat().st_mode) == 0o600
    with pytest.raises(setup.PreparationError, match="already exists"):
        setup._new_private_directory(target)
    with pytest.raises(FileExistsError):
        setup._private_write(target / "render-private.env", "overwritten")
    assert (target / "render-private.env").read_text() == "secret"
    link = tmp_path / "linked-parent"
    link.symlink_to(target, target_is_directory=True)
    with pytest.raises(setup.PreparationError, match="symbolic"):
        setup._new_private_directory(link / "child")
    assert not (target / "child").exists()


def test_runtime_url_has_new_password_and_container_ca_only():
    url = make_url(
        setup.runtime_database_url(setup.normalize_owner_url(OWNER), "runtime-secret")
    )
    assert url.username == "tuhoc_app"
    assert url.password == "runtime-secret"
    assert "owner-secret" not in url.render_as_string(hide_password=False)
    assert url.query["sslmode"] == "verify-full"
    assert url.query["sslrootcert"] == "/etc/ssl/certs/ca-certificates.crt"
    assert url.query["channel_binding"] == "require"


class FakeConnection:
    dialect = postgres_dialect()

    def __init__(self, *, exists=False, relations=0, permissions=True):
        self.statements = []
        self.exists, self.relations, self.permissions = exists, relations, permissions

    def execute(self, statement, parameters=None):
        query = str(statement)
        self.statements.append((query, parameters))
        result = MagicMock()
        result.mappings.return_value.one.return_value = {
            "owner_role": "neondb_owner",
            "database_name": "neondb",
            "can_create_role": self.permissions,
            "owns_database": True,
            "can_create_schema": True,
        }
        if "SELECT EXISTS" in query:
            result.scalar_one.return_value = self.exists
        elif "SELECT COUNT" in query:
            result.scalar_one.return_value = self.relations
        return result


class FakeEngine:
    url = setup.normalize_owner_url(OWNER)

    def __init__(self, connection):
        self.connection = connection
        self.disposed = False
        self.committed = False

    @contextmanager
    def connect(self):
        yield self.connection

    @contextmanager
    def begin(self):
        yield self.connection
        self.committed = True

    def dispose(self):
        self.disposed = True


@pytest.mark.parametrize(
    "options,match",
    [
        ({"exists": True}, "already exists"),
        ({"relations": 1}, "not empty"),
        ({"permissions": False}, "owner must"),
    ],
)
def test_plan_refuses_existing_role_tables_or_insufficient_owner(options, match):
    connection = FakeConnection(**options)
    with pytest.raises(setup.PreparationError, match=match):
        setup.inspect_plan(FakeEngine(connection))
    assert not any("CREATE ROLE" in query for query, _ in connection.statements)


def test_plan_is_readonly_and_writes_no_private_files(tmp_path):
    connection = FakeConnection()
    engine = FakeEngine(connection)
    result = setup.prepare(engine, directory=tmp_path / "must-not-exist")
    assert result["mode"] == "plan"
    assert not (tmp_path / "must-not-exist").exists()
    assert not engine.committed
    assert connection.statements[0][0] == "SET TRANSACTION READ ONLY"
    assert all(
        not query.startswith(("CREATE ", "REVOKE ", "DO "))
        for query, _ in connection.statements
    )


def test_create_role_has_no_admin_powers_or_password_in_sql():
    connection = FakeConnection()
    setup._create_runtime_role(connection, "runtime-password-secret")
    sql = "\n".join(query for query, _ in connection.statements)
    assert "runtime-password-secret" not in sql
    assert "LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE" in sql
    assert "NOINHERIT NOREPLICATION NOBYPASSRLS" in sql
    assert "tuhoc_app" in sql
    assert connection.statements[0][1] == {"password": "runtime-password-secret"}
    assert connection.statements[-1][0].endswith("'', true)")


def test_apply_shares_real_connection_and_only_writes_runtime_credentials(
    tmp_path, monkeypatch
):
    connection = FakeConnection()
    engine = FakeEngine(connection)
    calls = []
    monkeypatch.setattr(
        setup, "migrate", lambda facade: calls.append(("migrate", facade.connection))
    )
    monkeypatch.setattr(
        setup,
        "grant_runtime",
        lambda facade, role: calls.append((role, facade.connection)),
    )

    def manager(bind, path):
        calls.append(("manager", bind))
        setup._private_write(path, "temporary manager password")

    monkeypatch.setattr(setup, "ensure_manager", manager)
    result = setup.prepare(engine, directory=tmp_path / "private", apply=True)
    assert engine.committed
    assert result["mode"] == "applied"
    assert calls == [
        ("migrate", connection),
        ("manager", connection),
        ("tuhoc_app", connection),
    ]
    files = list((tmp_path / "private").iterdir())
    assert len(files) == 3
    assert all("owner-secret" not in path.read_text() for path in files)
    runtime = (tmp_path / "private/render-private.env").read_text()
    assert runtime.startswith("KHOHOC_DATABASE_URL=postgresql+psycopg://tuhoc_app:")
    assert "REVOKE CREATE ON SCHEMA public FROM PUBLIC" in [
        query for query, _ in connection.statements
    ]
    assert 'REVOKE CREATE, TEMPORARY ON DATABASE "neondb" FROM PUBLIC' in [
        query for query, _ in connection.statements
    ]


def test_failure_keeps_private_outputs_without_leaking_exception(tmp_path, monkeypatch):
    engine = FakeEngine(FakeConnection())
    monkeypatch.setattr(
        setup, "migrate", lambda _: (_ for _ in ()).throw(RuntimeError(OWNER))
    )
    with pytest.raises(setup.PreparationError) as failure:
        setup.prepare(engine, directory=tmp_path / "private", apply=True)
    assert (tmp_path / "private").is_dir()
    assert not engine.committed
    assert "owner-secret" not in str(failure.value)
    assert "ep-orange" not in str(failure.value)
    assert "Keep the private output" in str(failure.value)


def test_cli_sanitizes_driver_errors_and_disposes_engine(monkeypatch, capsys):
    engine = FakeEngine(FakeConnection())
    monkeypatch.setattr(
        setup, "read_owner_url", lambda _: setup.normalize_owner_url(OWNER)
    )
    monkeypatch.setattr(setup, "owner_engine", lambda _: engine)
    monkeypatch.setattr(
        setup,
        "prepare",
        lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError(OWNER)),
    )
    assert setup.main([]) == 1
    output = capsys.readouterr()
    assert "owner-secret" not in output.out + output.err
    assert "ep-orange" not in output.out + output.err
    assert "exception text were hidden" in output.err
    assert engine.disposed


def test_content_archive_requires_reviewed_sha_before_connecting(tmp_path):
    engine = FakeEngine(FakeConnection())
    with pytest.raises(setup.PreparationError, match="reviewed"):
        setup.prepare(
            engine, directory=tmp_path / "private", content_archive=tmp_path / "missing"
        )
    assert engine.connection.statements == []
    assert not (tmp_path / "private").exists()


def test_content_archive_validated_before_connect_and_applied_in_owner_transaction(
    tmp_path, monkeypatch
):
    import hashlib
    from khohoc import content_transfer

    content = tmp_path / "public-content.json"
    content.write_bytes(b"fixed-public-archive")
    expected = hashlib.sha256(content.read_bytes()).hexdigest()
    counts = {"questions": 2, "exams": 1, "documents": 1}
    monkeypatch.setattr(
        content_transfer,
        "validate_archive",
        lambda *args, **kwargs: {"manifest": {"counts": counts}},
    )
    calls = []
    monkeypatch.setattr(
        content_transfer,
        "import_published_content",
        lambda bind, path, **kwargs: calls.append((bind, path, kwargs)),
    )
    monkeypatch.setattr(setup, "migrate", lambda _: None)
    monkeypatch.setattr(setup, "grant_runtime", lambda *args: None)
    monkeypatch.setattr(setup, "ensure_manager", lambda *args: None)
    engine = FakeEngine(FakeConnection())
    result = setup.prepare(
        engine,
        directory=tmp_path / "private",
        content_archive=content,
        content_sha256=expected,
        library_root=tmp_path,
        apply=True,
    )
    assert result["content"] == {"sha256": expected, "counts": counts}
    assert len(calls) == 2
    assert all(call[0] is engine.connection for call in calls)
    assert "apply" not in calls[0][2]
    assert calls[1][2]["apply"] is True
    assert all(call[2]["expected_sha256"] == expected for call in calls)
    assert all(call[2]["library_root"] == tmp_path for call in calls)


def test_content_changed_checksum_fails_before_connect_and_file_creation(tmp_path):
    content = tmp_path / "content.json"
    content.write_text("changed archive")
    engine = FakeEngine(FakeConnection())
    with pytest.raises(setup.PreparationError, match="SHA256 differs"):
        setup.prepare(
            engine,
            directory=tmp_path / "private",
            content_archive=content,
            content_sha256="0" * 64,
            apply=True,
        )
    assert not (tmp_path / "private").exists()
    assert not engine.connection.statements


def test_cli_cleanup_error_does_not_expose_owner_url(monkeypatch, capsys):
    engine = FakeEngine(FakeConnection())
    monkeypatch.setattr(
        setup, "read_owner_url", lambda _: setup.normalize_owner_url(OWNER)
    )
    monkeypatch.setattr(setup, "owner_engine", lambda _: engine)
    monkeypatch.setattr(setup, "prepare", lambda *args, **kwargs: {"mode": "plan"})
    monkeypatch.setattr(
        engine, "dispose", lambda: (_ for _ in ()).throw(RuntimeError(OWNER))
    )
    assert setup.main([]) == 0
    output = capsys.readouterr()
    assert "owner-secret" not in output.out + output.err
    assert "ep-orange" not in output.out + output.err
