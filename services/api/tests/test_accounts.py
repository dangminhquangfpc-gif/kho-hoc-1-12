import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from khohoc.accounts import password_hash, password_valid, ensure_manager
from khohoc.app import Settings, create_app
from khohoc.models import ContentQuestion, LearningUser, Exam
from khohoc.schemas import Question

ROOT = Path(__file__).resolve().parents[3]


@pytest.fixture
def school(tmp_path):
    app = create_app(Settings(database_url=f"sqlite:///{tmp_path}/school.db"))
    with TestClient(app) as client:
        with Session(app.state.engine) as db:
            db.add(
                LearningUser(
                    id="owner",
                    username="manager",
                    display_name="Quản lý",
                    role="manager",
                    password_hash=password_hash("Owner-password-123"),
                    active=True,
                    must_change_password=False,
                )
            )
            q = json.loads((ROOT / "data/seeds/practice_questions.json").read_text())[
                "questions"
            ][0]
            q = Question.model_validate(q).model_dump(mode="json")
            db.add(
                ContentQuestion(
                    id=q["id"],
                    payload=q,
                    fingerprint="test-fingerprint",
                    state="published",
                    rights_confirmed=True,
                )
            )
            db.add(
                Exam(
                    id="student-exam",
                    state="published",
                    payload=dict(
                        id="student-exam",
                        title="Đề có sẵn",
                        grade=5,
                        subject="toan",
                        textbook="ket_noi_tri_thuc",
                        topic=q["topic"],
                        duration_minutes=10,
                        question_ids=[q["id"]],
                    ),
                )
            )
            db.commit()
        login = client.post(
            "/auth/login",
            json={
                "username": "manager",
                "password": "Owner-password-123",
                "mobile": True,
            },
        ).json()
        manager = {"Authorization": "Bearer " + login["token"]}
        yield client, manager, q, app


def test_password_hashes_are_salted_and_not_reversible():
    a = password_hash("Long-password-123")
    b = password_hash("Long-password-123")
    assert a != b and password_valid("Long-password-123", a)
    assert not password_valid("wrong-password", a) and "Long-password" not in a


def test_registration_bulk_and_mandatory_change(school):
    client, manager, q, app = school
    created = client.post(
        "/classroom/students/bulk",
        headers=manager,
        json={
            "students": [
                {"username": "student01", "display_name": "Học viên một", "grade": 5},
                {"username": "student02", "display_name": "Học viên hai", "grade": 5},
            ]
        },
    )
    assert created.status_code == 201 and len(created.json()) == 2
    assert (
        client.post(
            "/classroom/students/bulk",
            headers=manager,
            json={
                "students": [
                    {"username": "newname", "display_name": "Mới"},
                    {"username": "student01", "display_name": "Trùng"},
                ]
            },
        ).status_code
        == 409
    )
    login = client.post(
        "/auth/login",
        json={
            "username": "student01",
            "password": created.json()[0]["temporary_password"],
            "mobile": True,
        },
    ).json()
    student = {"Authorization": "Bearer " + login["token"]}
    assert login["user"]["must_change_password"] is True
    assert (
        client.post(
            "/practice-attempts",
            headers=student,
            json={"grade": 5, "subject": "toan", "count": 1},
        ).status_code
        == 403
    )
    changed = client.post(
        "/auth/password",
        headers=student,
        json={
            "current_password": created.json()[0]["temporary_password"],
            "new_password": "Changed-password-123",
        },
    )
    assert changed.status_code == 200 and not changed.json()["must_change_password"]
    assert client.get("/classroom/students", headers=student).status_code == 403
    assert (
        client.post(
            "/auth/register",
            json={
                "username": "public01",
                "password": "Self-password-123",
                "display_name": "Tự đăng ký",
                "grade": 5,
                "role": "manager",
            },
        ).status_code
        == 422
    )
    registered = client.post(
        "/auth/register",
        json={
            "username": "public01",
            "password": "Self-password-123",
            "display_name": "Tự đăng ký",
            "grade": 5,
        },
    )
    assert (
        registered.status_code == 201 and registered.json()["user"]["role"] == "student"
    )
    students = client.get("/classroom/students", headers=manager).json()
    assert len(students) == 3 and all("password_hash" not in s for s in students)
    assert "newname" not in {s["username"] for s in students}


def test_server_results_and_cross_account_isolation(school):
    client, manager, q, app = school
    tokens = []
    for name in ("alice01", "bob0001"):
        r = client.post(
            "/auth/register",
            json={
                "username": name,
                "password": "Student-password-123",
                "display_name": name,
                "mobile": True,
            },
        ).json()
        tokens.append((r["user"]["id"], {"Authorization": "Bearer " + r["token"]}))
    aid, a = tokens[0]
    bid, b = tokens[1]
    attempt = client.post(
        "/exams/student-exam/attempts",
        headers=a,
    ).json()
    assert attempt["account_id"] == aid
    path = f"/attempts/{attempt['id']}"
    ah = {**a, "X-Attempt-Token": attempt["token"]}
    bh = {**b, "X-Attempt-Token": attempt["token"]}
    assert (
        client.post(path + "/submit", headers=bh, json={"answers": {}}).status_code
        == 404
    )
    result = client.post(
        path + "/submit",
        headers=ah,
        json={"answers": {q["id"]: q["correct_answer"]}, "score": 10000},
    )
    assert result.status_code == 200 and result.json()["score"] == 1
    assert len(client.get("/account/results", headers=a).json()) == 1
    assert client.get("/account/results", headers=b).json() == []
    assert (
        client.get(f"/classroom/students/{aid}/results", headers=b).status_code == 403
    )
    records = client.get(f"/classroom/students/{aid}/results", headers=manager).json()[
        "records"
    ]
    assert len(records) == 1 and records[0]["result"]["score"] == 1
    client.post(
        path + "/submit", headers=ah, json={"answers": {q["id"]: q["correct_answer"]}}
    )
    assert len(client.get("/account/results", headers=a).json()) == 1
    assert client.delete(path, headers=bh).status_code == 404
    assert client.delete(path, headers=ah).status_code == 204
    assert (
        len(
            client.get(f"/classroom/students/{aid}/results", headers=manager).json()[
                "records"
            ]
        )
        == 1
    )
    reset = client.post(f"/classroom/students/{aid}/reset-password", headers=manager)
    assert (
        reset.status_code == 200
        and client.get("/account/results", headers=a).status_code == 401
    )
    assert (
        client.post(
            "/auth/login",
            json={"username": "alice01", "password": "Student-password-123"},
        ).status_code
        == 401
    )


def test_login_throttle_and_other_manager_cannot_inspect(school):
    client, manager, q, app = school
    learner = client.post(
        "/auth/register",
        json={
            "username": "learner01",
            "password": "Student-password-123",
            "display_name": "Bạn A",
        },
    ).json()["user"]
    with Session(app.state.engine) as db:
        db.add(
            LearningUser(
                id="second",
                username="secondmanager",
                display_name="Khác",
                role="manager",
                password_hash=password_hash("Other-password-123"),
                active=True,
                must_change_password=False,
            )
        )
        db.commit()
    second = client.post(
        "/auth/login",
        json={
            "username": "secondmanager",
            "password": "Other-password-123",
            "mobile": True,
        },
    ).json()
    assert (
        client.get(
            f"/classroom/students/{learner['id']}/results",
            headers={"Authorization": "Bearer " + second["token"]},
        ).status_code
        == 404
    )
    for _ in range(8):
        assert (
            client.post(
                "/auth/login",
                json={"username": "doesnotexist", "password": "Wrong-password-123"},
            ).status_code
            == 401
        )
    assert (
        client.post(
            "/auth/login",
            json={"username": "doesnotexist", "password": "Wrong-password-123"},
        ).status_code
        == 429
    )


def test_local_manager_bootstrap_does_not_reset_existing_account(tmp_path):
    app = create_app(Settings(database_url=f"sqlite:///{tmp_path}/bootstrap.db"))
    with TestClient(app):
        path = tmp_path / "private" / "manager.txt"
        ensure_manager(app.state.engine, str(path))
        original = path.read_bytes()
        ensure_manager(app.state.engine, str(path))
        assert path.read_bytes() == original
        with Session(app.state.engine) as db:
            from sqlalchemy import select

            users = list(db.scalars(select(LearningUser)))
            assert len(users) == 1 and users[0].username == "quanly"
            assert users[0].must_change_password


def test_http_only_cookie_logout_and_owner_deletion(school):
    client, manager, q, app = school
    login = client.post(
        "/auth/login", json={"username": "manager", "password": "Owner-password-123"}
    )
    assert "token" not in login.json()
    cookie = login.headers.get("set-cookie", "")
    assert "HttpOnly" in cookie and "SameSite=strict" in cookie
    assert client.get("/auth/me").status_code == 200
    registered = client.post(
        "/auth/register",
        json={
            "username": "cleanup01",
            "password": "Student-password-123",
            "display_name": "Học viên thử",
        },
    ).json()
    sid = registered["user"]["id"]
    assert client.delete(f"/classroom/students/{sid}").status_code == 403
    assert (
        client.delete(f"/classroom/students/{sid}", headers=manager).status_code == 204
    )
    assert client.get("/auth/me").status_code == 401
    assert (
        client.post(
            "/auth/login",
            json={"username": "cleanup01", "password": "Student-password-123"},
        ).status_code
        == 401
    )
    client.post("/auth/logout")
    assert client.get("/auth/me").status_code == 401
