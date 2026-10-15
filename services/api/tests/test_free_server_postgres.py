"""First-run owner transactions, only on the disposable PostgreSQL test service."""

import importlib.util
import os
from pathlib import Path
import stat
import uuid

import pytest
from sqlalchemy import create_engine, event, func, select, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from khohoc import content_transfer
from khohoc.content_transfer import ARCHIVE_KIND, canonical_bytes, digest
from khohoc.database import verify_schema
from khohoc.library import DocumentInput, LibraryDocument
from khohoc.models import ContentQuestion, Exam, LearningUser
from khohoc.question_versions import QuestionRevision
from khohoc.schemas import ExamInput, Question

ROOT = Path(__file__).resolve().parents[3]


@pytest.fixture
def provisioner():
    spec = importlib.util.spec_from_file_location(
        "free_server_postgresql_setup", ROOT / "scripts/prepare_free_server.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def empty_postgresql():
    raw_url = os.environ.get("KHOHOC_TEST_POSTGRES_URL")
    if not raw_url:
        pytest.skip("Run scripts/test_shared_postgres.py for a disposable PostgreSQL")
    url = make_url(raw_url)
    container = os.environ.get("KHOHOC_TEST_POSTGRES_CONTAINER", "")
    if (
        url.host not in {"127.0.0.1", "localhost"}
        or url.database != "postgres"
        or not container.startswith("tuhoc-integration-")
    ):
        pytest.fail("First-run tests require the dedicated disposable test container")
    admin = create_engine(url, isolation_level="AUTOCOMMIT", hide_parameters=True)
    name = "freepilot_" + uuid.uuid4().hex
    role_created_here = False
    owner = None
    with admin.connect() as connection:
        exists = connection.execute(
            text("SELECT EXISTS(SELECT 1 FROM pg_roles WHERE rolname='tuhoc_app')")
        ).scalar_one()
        if exists:
            admin.dispose()
            pytest.fail("Fresh disposable test cluster unexpectedly has a runtime role")
        connection.execute(text(f'CREATE DATABASE "{name}"'))
    try:
        owner = create_engine(url.set(database=name), hide_parameters=True)
        yield owner
    finally:
        # Only this fixture's random database and a role absent before it began.
        # Test-owned runtime engines are disposed inside their tests before here.
        if owner is not None:
            owner.dispose()
        with admin.connect() as connection:
            role_created_here = connection.execute(
                text("SELECT EXISTS(SELECT 1 FROM pg_roles WHERE rolname='tuhoc_app')")
            ).scalar_one()
            connection.execute(text(f'DROP DATABASE "{name}"'))
            if role_created_here:
                connection.execute(text("DROP ROLE tuhoc_app"))
        admin.dispose()


@pytest.fixture
def small_archive(tmp_path):
    question = Question.model_validate(
        dict(
            id="first-run-question",
            grade=1,
            subject="toan",
            topic="phep_cong",
            type="numeric",
            difficulty="easy",
            question="Tính 1 + 1.",
            correct_answer=["2"],
            max_score=1,
            explanation="1 + 1 = 2.",
            source_type="original",
            license="original_content",
            rights_evidence="Nội dung kiểm thử tự biên soạn, không chép tài liệu khác.",
        )
    ).model_dump(mode="json")
    exam = ExamInput.model_validate(
        dict(
            id="first-run-exam",
            title="Đề kiểm tra khởi tạo máy chủ",
            grade=1,
            subject="toan",
            question_ids=[question["id"]],
            duration_minutes=15,
        )
    ).model_dump(mode="json")
    document = DocumentInput.model_validate(
        dict(
            id="first-run-guide",
            title="Hướng dẫn kiểm thử khởi tạo",
            grade=1,
            subject="toan",
            topic="phep_cong",
            summary="Tài liệu tự biên soạn cho database kiểm thử tạm.",
            author="Kiểm thử Tự học 111",
            source_name="Fixture gốc",
            source_type="original",
            license="original_content",
            rights_evidence="Tài liệu kiểm thử tự biên soạn, không có thông tin học viên.",
            distribution_allowed=True,
            sections=[{"heading": "Lời giải", "text": "1 + 1 = 2. Đáp số: 2."}],
        )
    ).model_dump(mode="json")
    content = {
        "questions": [{"payload": question, "version": 3}],
        "exams": [{"payload": exam}],
        "documents": [
            {
                "payload": document,
                "version": 2,
                "updated_at": "2026-10-15T00:00:00+00:00",
            }
        ],
    }
    payload = canonical_bytes(
        dict(
            kind=ARCHIVE_KIND,
            schema_version=1,
            content=content,
            manifest=dict(
                content_sha256=digest(canonical_bytes(content)),
                counts={key: len(rows) for key, rows in content.items()},
                pdf_sha256={},
            ),
        )
    )
    path = tmp_path / "reviewed-public-content.json"
    path.write_bytes(payload)
    return path, digest(payload), question


def database_state(engine):
    """Observe schema/role/ACL state without touching the database's privileges."""
    with engine.connect() as connection:
        return (
            connection.execute(
                text(
                    "SELECT COUNT(*) FROM pg_class c JOIN pg_namespace n "
                    "ON n.oid=c.relnamespace WHERE n.nspname='public' "
                    "AND c.relkind IN ('r','p','v','m','S','f')"
                )
            ).scalar_one(),
            connection.execute(
                text("SELECT COUNT(*) FROM pg_roles WHERE rolname='tuhoc_app'")
            ).scalar_one(),
            connection.execute(
                text("SELECT nspacl::text FROM pg_namespace WHERE nspname='public'")
            ).scalar_one(),
            connection.execute(
                text(
                    "SELECT datacl::text FROM pg_database WHERE datname=current_database()"
                )
            ).scalar_one(),
        )


def prepare_options(tmp_path, small_archive):
    path, checksum, _ = small_archive
    return dict(
        directory=tmp_path / "private-output",
        content_archive=path,
        content_sha256=checksum,
        library_root=tmp_path,
    )


def test_postgresql_first_run_plan_is_readonly(
    empty_postgresql, provisioner, tmp_path, small_archive
):
    engine = empty_postgresql
    options = prepare_options(tmp_path, small_archive)
    before = database_state(engine)
    statements = []

    def observe(connection, cursor, statement, parameters, context, many):
        statements.append(statement.strip().upper())

    event.listen(engine, "before_cursor_execute", observe)
    try:
        result = provisioner.prepare(engine, **options)
    finally:
        event.remove(engine, "before_cursor_execute", observe)
    assert result["mode"] == "plan"
    assert result["content"]["counts"] == {"questions": 1, "exams": 1, "documents": 1}
    assert statements and all(
        statement.startswith(("SELECT ", "SET TRANSACTION READ ONLY"))
        for statement in statements
    )
    assert not options["directory"].exists()
    assert database_state(engine) == before


def test_postgresql_first_run_apply_permissions_and_repeat_refusal(
    empty_postgresql, provisioner, tmp_path, small_archive
):
    engine = empty_postgresql
    options = prepare_options(tmp_path, small_archive)
    result = provisioner.prepare(engine, **options, apply=True)
    assert result["mode"] == "applied"
    verify_schema(engine)
    question = small_archive[2]
    with Session(engine) as db:
        manager = db.scalar(select(LearningUser))
        assert manager.role == "manager" and manager.must_change_password
        manager_password_hash = manager.password_hash
        assert db.scalar(select(func.count()).select_from(ContentQuestion)) == 1
        assert db.scalar(select(func.count()).select_from(Exam)) == 1
        assert db.scalar(select(func.count()).select_from(LibraryDocument)) == 1
        revision = db.get(QuestionRevision, (question["id"], 3))
        assert revision.payload == question and revision.actor == "content-transfer"
    with engine.connect() as connection:
        powers = connection.execute(
            text(
                "SELECT rolsuper,rolcreatedb,rolcreaterole,rolinherit,rolreplication,"
                "rolbypassrls FROM pg_roles WHERE rolname='tuhoc_app'"
            )
        ).one()
        assert not any(powers)
    private = options["directory"]
    saved = {path.name: path.read_bytes() for path in private.iterdir()}
    assert stat.S_IMODE(private.stat().st_mode) == 0o700
    assert all(stat.S_IMODE(path.stat().st_mode) == 0o600 for path in private.iterdir())
    env = saved["render-private.env"].decode().strip().split("=", 1)[1]
    runtime_url = make_url(env)
    assert runtime_url.username == "tuhoc_app" and runtime_url.password
    # Only this disposable loopback test uses plaintext PostgreSQL transport.
    # The emitted Render configuration itself retains verify-full and CA trust.
    assert runtime_url.query["sslmode"] == "verify-full"
    runtime = create_engine(runtime_url.set(query={}), hide_parameters=True)
    try:
        verify_schema(runtime)
        with Session(runtime) as db:
            extra = question | {
                "id": "runtime-dml-probe",
                "question": "Câu kiểm tra quyền ghi của runtime.",
            }
            row = ContentQuestion(
                id=extra["id"],
                payload=extra,
                fingerprint=uuid.uuid4().hex,
                state="draft",
                rights_confirmed=False,
            )
            db.add(row)
            db.flush()  # INSERT
            row.version = 2
            db.flush()  # UPDATE
            assert db.get(ContentQuestion, row.id).version == 2  # SELECT
            db.delete(row)
            db.commit()  # DELETE
        for sql in (
            "CREATE TABLE public.forbidden_first_run (id INTEGER)",
            "CREATE SCHEMA forbidden_first_run",
            "CREATE TEMP TABLE forbidden_first_run (id INTEGER)",
            "CREATE ROLE forbidden_first_run",
            "ALTER ROLE tuhoc_app CREATEROLE",
            "UPDATE app_schema_version SET version=99",
        ):
            with pytest.raises(DBAPIError) as denied:
                with runtime.begin() as connection:
                    connection.execute(text(sql))
            assert denied.value.orig.sqlstate == "42501"
    finally:
        runtime.dispose()
    for output in (private, tmp_path / "another-private-output"):
        with pytest.raises(provisioner.PreparationError, match="already exists"):
            provisioner.prepare(engine, **(options | {"directory": output}), apply=True)
    assert not (tmp_path / "another-private-output").exists()
    assert {path.name: path.read_bytes() for path in private.iterdir()} == saved
    with Session(engine) as db:
        assert db.scalar(select(LearningUser.password_hash)) == manager_password_hash
        assert db.scalar(select(func.count()).select_from(ContentQuestion)) == 1
    verify_schema(engine)


def test_postgresql_first_run_failure_rolls_back_content_role_schema_and_grants(
    empty_postgresql, provisioner, tmp_path, small_archive, monkeypatch
):
    engine = empty_postgresql
    options = prepare_options(tmp_path, small_archive)
    before = database_state(engine)
    imported = []
    real_import = content_transfer.import_published_content
    real_write = provisioner._private_write

    def observe_import(connection, *args, **kwargs):
        result = real_import(connection, *args, **kwargs)
        if kwargs.get("apply"):
            assert (
                connection.execute(
                    text("SELECT COUNT(*) FROM local_questions")
                ).scalar_one()
                == 1
            )
            assert (
                connection.execute(
                    text("SELECT COUNT(*) FROM learning_users")
                ).scalar_one()
                == 1
            )
            imported.append(result["inserted"])
        return result

    def fail_after_credentials(path, value):
        if path.name == "README-private.txt":
            raise RuntimeError("synthetic-private-detail-must-not-leak")
        return real_write(path, value)

    monkeypatch.setattr(content_transfer, "import_published_content", observe_import)
    monkeypatch.setattr(provisioner, "_private_write", fail_after_credentials)
    with pytest.raises(provisioner.PreparationError) as failure:
        provisioner.prepare(engine, **options, apply=True)
    assert "synthetic-private-detail" not in str(failure.value)
    assert imported == [{"questions": 1, "exams": 1, "documents": 1}]
    assert database_state(engine) == before
    private = options["directory"]
    assert private.is_dir() and stat.S_IMODE(private.stat().st_mode) == 0o700
    assert {path.name for path in private.iterdir()} == {
        "manager-credentials.txt",
        "render-private.env",
    }
    assert all(stat.S_IMODE(path.stat().st_mode) == 0o600 for path in private.iterdir())
