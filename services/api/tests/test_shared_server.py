"""Run on SQLite locally AND real PostgreSQL via scripts/test_shared_postgres.py."""

import json
import os
from pathlib import Path
import uuid
from concurrent.futures import ThreadPoolExecutor

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text, select
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session
from khohoc.accounts import password_hash
from khohoc.app import Settings, create_app
from khohoc.database import make_engine, migrate
from khohoc.models import (
    LearningUser,
    ContentQuestion,
    Exam,
    AttemptDraft,
    LearningSession,
)
from khohoc.server_security import reserve
from khohoc.server_admin import copy_sqlite

ROOT = Path(__file__).parents[3]
PASSWORD = "Synthetic-student-password-123"


@pytest.fixture(params=["sqlite", "postgresql"])
def school(request, tmp_path):
    postgres = request.param == "postgresql"
    if postgres and not os.environ.get("KHOHOC_TEST_POSTGRES_URL"):
        pytest.skip("PostgreSQL integration requires scripts/test_shared_postgres.py")
    admin = None
    if postgres:
        admin = make_engine(os.environ["KHOHOC_TEST_POSTGRES_URL"])
        schema = "test_" + uuid.uuid4().hex
        with admin.begin() as db:
            db.execute(text(f"CREATE SCHEMA {schema}"))
        url = (
            make_url(os.environ["KHOHOC_TEST_POSTGRES_URL"])
            .update_query_dict({"options": "-csearch_path=" + schema})
            .render_as_string(hide_password=False)
        )
    else:
        url = "sqlite:///" + str(tmp_path / "school.db")
    engine = make_engine(url)
    migrate(engine)
    migrate(engine)  # Reentrant, version checked; no fixture auto-publication.
    settings = Settings(
        database_url=url,
        mode="shared" if postgres else "development",
        public_origin="https://study.test.edu.vn",
        cors_origins=["https://study.test.edu.vn"],
    )
    question = json.loads((ROOT / "data/seeds/practice_questions.json").read_text())[
        "questions"
    ][0]
    from khohoc.schemas import Question

    question = Question.model_validate(question).model_dump(mode="json")
    with Session(engine) as db:
        for ident, role in [
            ("manager", "manager"),
            ("student", "student"),
            ("other", "student"),
        ]:
            db.add(
                LearningUser(
                    id=ident,
                    username=ident,
                    display_name="Kiểm thử " + ident,
                    role=role,
                    manager_id=None if role == "manager" else "manager",
                    password_hash=password_hash(PASSWORD),
                )
            )
        db.add(
            ContentQuestion(
                id=question["id"],
                payload=question,
                fingerprint="sync-test",
                state="published",
                rights_confirmed=True,
            )
        )
        db.add(
            Exam(
                id="sync-exam",
                state="published",
                payload=dict(
                    id="sync-exam",
                    title="Đề đồng bộ",
                    grade=question["grade"],
                    subject=question["subject"],
                    textbook="ket_noi_tri_thuc",
                    topic=question["topic"],
                    duration_minutes=15,
                    question_ids=[question["id"]],
                ),
            )
        )
        db.commit()
    with (
        TestClient(create_app(settings), base_url="https://study.test.edu.vn") as one,
        TestClient(create_app(settings), base_url="https://study.test.edu.vn") as two,
    ):
        yield one, two, engine, question, postgres
    engine.dispose()
    if admin:
        with admin.begin() as db:
            db.execute(text(f"DROP SCHEMA {schema} CASCADE"))
        admin.dispose()


def login(client, username="student"):
    response = client.post(
        "/auth/login", json={"username": username, "password": PASSWORD}
    )
    assert response.status_code == 200
    return response


def test_two_servers_sync_resume_submit_and_privacy(school):
    one, two, engine, q, postgres = school
    response = login(one)
    assert "HttpOnly" in response.headers["set-cookie"]
    assert "Secure" in response.headers["set-cookie"]
    login(two)
    attempt = one.post("/exams/sync-exam/attempts").json()
    path = "/account/attempts/" + attempt["id"]
    saved = one.post(
        path + "/draft", json={"revision": 0, "answers": {q["id"]: q["correct_answer"]}}
    )
    assert saved.status_code == 200
    assert two.get("/account/attempts").json()[0]["id"] == attempt["id"]
    resumed = two.get(path).json()
    assert resumed["answers"] == {q["id"]: q["correct_answer"]}
    assert "correct_answer" not in json.dumps(resumed)
    assert resumed["token"] == ""
    assert (
        one.post(path + "/draft", json={"revision": 0, "answers": {}}).status_code
        == 409
    )
    submitted = two.post(
        "/attempts/" + attempt["id"] + "/submit", json={"answers": resumed["answers"]}
    )
    assert submitted.status_code == 200 and submitted.json()["score"] == float(
        q["max_score"]
    )
    assert one.get("/account/results").json()[0]["id"] == attempt["id"]
    assert one.get("/account/attempts").json() == []
    login(two, "manager")
    assert (
        two.get("/classroom/students/student/results").json()["records"][0]["id"]
        == attempt["id"]
    )
    login(two, "other")
    assert two.get(path).status_code == 404
    assert (
        two.post(path + "/draft", json={"revision": 1, "answers": {}}).status_code
        == 404
    )
    assert two.get("/account/results").json() == []
    assert (
        two.get(
            "/attempts/" + attempt["id"] + "/result",
            headers={"X-Attempt-Token": attempt["token"]},
        ).status_code
        == 404
    )


def test_draft_validation_and_account_deletion(school):
    one, two, engine, q, postgres = school
    login(one)
    attempt = one.post("/exams/sync-exam/attempts").json()
    path = "/account/attempts/" + attempt["id"] + "/draft"
    assert (
        one.post(path, json={"revision": 0, "answers": {"unknown": ["1"]}}).status_code
        == 422
    )
    assert (
        one.post(path, json={"revision": 0, "answers": {q["id"]: ["1"]}}).status_code
        == 200
    )
    assert one.post("/account/delete", json={"password": PASSWORD}).status_code == 204
    with Session(engine) as db:
        assert db.get(AttemptDraft, attempt["id"]) is None


def test_shared_transport_origin_and_private_routes(school):
    one, two, engine, q, postgres = school
    if not postgres:
        pytest.skip("Shared mode requires PostgreSQL")
    assert one.get("/health").headers["strict-transport-security"] == "max-age=31536000"
    assert one.get("/health", headers={"Host": "evil.example"}).status_code == 400
    assert (
        one.get(
            "http://study.test.edu.vn/health", headers={"X-Forwarded-Proto": "https"}
        ).status_code
        == 400
    )
    assert (
        one.post(
            "/auth/login",
            headers={"Origin": "https://evil.example"},
            json={"username": "student", "password": PASSWORD},
        ).status_code
        == 403
    )
    assert one.get("/admin/questions").status_code == 404
    assert one.get("/openapi.json").status_code == 404
    assert one.post("/exams/sync-exam/attempts").status_code == 401
    login(one)
    cookie = one.cookies.get("khohoc_session")
    # Independent server process recognizes the database-backed session.
    two.cookies.set("khohoc_session", cookie)
    assert two.get("/auth/me").json()["id"] == "student"


def test_shared_auth_budget_survives_other_server(school):
    one, two, engine, q, postgres = school
    if not postgres:
        pytest.skip("Distributed throttle requires PostgreSQL")
    for index in range(10):
        client = one if index % 2 else two
        assert (
            client.post(
                "/auth/login", json={"username": "unknown", "password": PASSWORD}
            ).status_code
            == 401
        )
    response = two.post(
        "/auth/login", json={"username": "unknown", "password": PASSWORD}
    )
    assert response.status_code == 429
    assert response.headers["retry-after"] == "900"
    with ThreadPoolExecutor(max_workers=8) as pool:
        allowed = list(
            pool.map(lambda _: reserve(engine, "concurrent-test", 5, 60), range(20))
        )
    assert sum(allowed) == 5


def test_postgres_transfer_preserves_accounts_and_invalidates_sessions(
    school, tmp_path
):
    one, two, engine, q, postgres = school
    if not postgres:
        pytest.skip("Transfer destination must be PostgreSQL")
    from khohoc.models import Base

    # Recreate business tables, retaining explicit schema version.
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    source_path = tmp_path / "old.db"
    source = make_engine("sqlite:///" + str(source_path))
    migrate(source)
    with Session(source) as db:
        db.add(
            LearningUser(
                id="moved",
                username="moved_student",
                display_name="Học viên chuyển máy chủ",
                role="student",
                password_hash=password_hash(PASSWORD),
            )
        )
        from khohoc.models import LearningRecord, ClassroomGroup, GroupMember

        db.add(
            ClassroomGroup(
                id="old-group",
                owner_id="moved",
                name="Nhóm chuyển máy chủ",
                join_code="synthetic-code",
            )
        )
        db.add(GroupMember(group_id="old-group", user_id="moved"))
        db.add(
            LearningRecord(
                attempt_id="old-result",
                user_id="moved",
                payload={
                    "result": {
                        "title": "Kết quả trước chuyển",
                        "score": 8,
                        "max_score": 10,
                    }
                },
            )
        )
        from datetime import datetime, timezone, timedelta

        db.add(
            LearningSession(
                token_hash="old-session",
                user_id="moved",
                expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
            )
        )
        db.commit()
    copy_sqlite(source_path, engine)
    with Session(engine) as db:
        assert db.get(LearningUser, "moved").display_name == "Học viên chuyển máy chủ"
        assert db.scalar(select(LearningSession)) is None
    login(one, "moved_student")
    assert one.get("/account/results").json()[0]["result"]["score"] == 8
    assert one.get("/classroom/groups").json()[0]["name"] == "Nhóm chuyển máy chủ"
    with pytest.raises(ValueError, match="empty"):
        copy_sqlite(source_path, engine)
    source.dispose()


@pytest.mark.parametrize(
    "overrides",
    [
        {"database_url": "sqlite:///:memory:"},
        {"public_origin": "http://study.test.edu.vn"},
        {"public_origin": "https://localhost"},
        {"admin_token": "unsafe"},
        {"cors_origins": ["*"]},
    ],
)
def test_unsafe_shared_configuration_rejected(overrides):
    values = dict(
        mode="shared",
        database_url="postgresql+psycopg://user@localhost/school",
        public_origin="https://study.test.edu.vn",
        cors_origins=["https://study.test.edu.vn"],
    )
    values.update(overrides)
    with pytest.raises(ValueError):
        create_app(Settings(**values))


def test_concurrent_drafts_and_stale_submission(school):
    one, two, engine, q, postgres = school
    login(one)
    login(two)
    attempt = one.post("/exams/sync-exam/attempts").json()
    path = "/account/attempts/" + attempt["id"]

    def save(client):
        return client.post(
            path + "/draft",
            json={"revision": 0, "answers": {q["id"]: q["correct_answer"]}},
        ).status_code

    with ThreadPoolExecutor(max_workers=2) as pool:
        statuses = list(pool.map(save, [one, two]))
    assert sorted(statuses) == [200, 409]
    assert (
        one.post(
            "/attempts/" + attempt["id"] + "/submit",
            json={"draft_revision": 0, "answers": {}},
        ).status_code
        == 409
    )
    current = two.get(path).json()
    assert current["draft_revision"] == 1
    body = {"draft_revision": 1, "answers": current["answers"]}
    assert (
        two.post("/attempts/" + attempt["id"] + "/submit", json=body).status_code == 200
    )
    assert (
        one.post(path + "/draft", json={"revision": 1, "answers": {}}).status_code
        == 409
    )
    assert (
        two.post("/attempts/" + attempt["id"] + "/submit", json=body).status_code == 200
    )


def test_runtime_postgres_role_cannot_change_schema(school):
    one, two, engine, q, postgres = school
    if not postgres:
        pytest.skip("PostgreSQL role permissions")
    from khohoc.database import grant_runtime
    from sqlalchemy.exc import DBAPIError

    role = "runtime_" + uuid.uuid4().hex
    secret = uuid.uuid4().hex
    schema = engine.url.query["options"].removeprefix("-csearch_path=")
    with engine.begin() as connection:
        connection.execute(text(f"CREATE ROLE {role} LOGIN PASSWORD '{secret}'"))
    grant_runtime(engine, role, schema)
    runtime = make_engine(
        engine.url.set(username=role, password=secret).render_as_string(
            hide_password=False
        )
    )
    try:
        from khohoc.database import verify_schema

        verify_schema(runtime)
        config = Settings(
            mode="shared",
            database_url=runtime.url.render_as_string(hide_password=False),
            public_origin="https://study.test.edu.vn",
            cors_origins=["https://study.test.edu.vn"],
        )
        with TestClient(
            create_app(config), base_url="https://study.test.edu.vn"
        ) as client:
            login(client)
            attempt = client.post("/exams/sync-exam/attempts")
            assert attempt.status_code == 201
        with pytest.raises(DBAPIError):
            with runtime.begin() as connection:
                connection.execute(text("CREATE TABLE forbidden_table (id INTEGER)"))
        with pytest.raises(DBAPIError):
            with runtime.begin() as connection:
                connection.execute(text("UPDATE app_schema_version SET version=99"))
    finally:
        runtime.dispose()
        with engine.begin() as connection:
            connection.execute(text(f"DROP OWNED BY {role}"))
            connection.execute(text(f"DROP ROLE {role}"))


def test_shared_readiness_rejects_changed_schema_and_budget_failures_are_503(
    school, monkeypatch
):
    one, two, engine, q, postgres = school
    if not postgres:
        pytest.skip("Shared schema readiness requires PostgreSQL")
    import khohoc.app as app_module
    from sqlalchemy.exc import SQLAlchemyError

    assert one.get("/ready").status_code == 200
    with engine.begin() as connection:
        connection.execute(text("UPDATE app_schema_version SET version=99"))
    response = one.get("/ready")
    assert response.status_code == 503
    assert response.json() == {"status": "unavailable", "mode": "shared"}
    assert one.get("/health").status_code == 200
    with engine.begin() as connection:
        connection.execute(text("UPDATE app_schema_version SET version=1"))

    def unavailable(*args):
        raise SQLAlchemyError("private diagnostic must not reach clients")

    monkeypatch.setattr(app_module, "reserve", unavailable)
    response = one.get("/grades")
    assert response.status_code == 503
    assert "private diagnostic" not in response.text
    assert one.get("/ready").status_code == 200
