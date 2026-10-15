"""Feedback ownership, immutable grades, review conflicts, deletion and upgrades."""

import pytest
from sqlalchemy import select, text
from sqlalchemy.orm import Session
from test_accounts import school  # noqa: F401
from test_teacher_groups import register

from khohoc.database import migrate, verify_schema, SCHEMA_VERSION
from khohoc.models import ContentReport, LearningUser
from khohoc.library import LibraryDocument


def send(client, headers, qid, attempt_id):
    return client.post(
        "/content-reports",
        headers=headers,
        json={
            "target_kind": "question",
            "target_id": qid,
            "attempt_id": attempt_id,
            "category": "unclear",
            "message": "Cần giải thích rõ hơn bước giải bài này.",
        },
    )


def test_owned_feedback_review_conflict_and_immutable_grade(school):  # noqa: F811
    client, manager, q, app = school
    teacher, _ = register(client, "feedback_teacher", "teacher")
    other, _ = register(client, "feedback_other", "teacher")
    student, sid = register(client, "feedback_student", "student")
    peer, _ = register(client, "feedback_peer", "student")
    attempt = client.post("/exams/student-exam/attempts", headers=student).json()
    submitted = client.post(
        f"/attempts/{attempt['id']}/submit", headers=student, json={"answers": {}}
    ).json()
    assert send(client, peer, q["id"], attempt["id"]).status_code == 404
    assert send(client, student, "missing", attempt["id"]).status_code == 404
    report = send(client, student, q["id"], attempt["id"])
    assert report.status_code == 201
    rid = report.json()["id"]
    assert report.json()["revision"] == 1
    assert "correct_answer" not in report.text and "token" not in report.text
    assert send(client, student, q["id"], attempt["id"]).status_code == 409
    assert len(client.get("/content-reports", headers=student).json()) == 1
    assert client.get("/content-reports", headers=peer).json() == []
    assert client.get("/classroom/content-reports", headers=student).status_code == 403
    assert client.get("/classroom/content-reports", headers=teacher).json() == []
    body = {
        "revision": 1,
        "status": "in_review",
        "response": "Tôi sẽ kiểm tra lại cách trình bày.",
    }
    review_url = f"/classroom/content-reports/{rid}/review"
    assert client.post(review_url, headers=teacher, json=body).status_code == 404
    group = client.post(
        "/classroom/groups", headers=teacher, json={"name": "Nhóm phản hồi"}
    ).json()
    client.post(
        "/classroom/groups/join", headers=student, json={"code": group["join_code"]}
    )
    inbox = client.get("/classroom/content-reports", headers=teacher).json()
    assert inbox[0]["reporter"]["username"] == "feedback_student"
    assert client.get("/classroom/content-reports", headers=other).json() == []
    reviewed = client.post(review_url, headers=teacher, json=body)
    assert reviewed.status_code == 200 and reviewed.json()["revision"] == 2
    assert client.post(review_url, headers=manager, json=body).status_code == 409
    assert (
        client.post(review_url, headers=other, json={**body, "revision": 2}).status_code
        == 404
    )
    assert client.post(review_url, headers=student, json=body).status_code == 403
    assert (
        client.get("/content-reports", headers=student).json()[0]["response"]
        == body["response"]
    )
    client.delete(f"/classroom/groups/{group['id']}/members/{sid}", headers=teacher)
    assert client.get("/classroom/content-reports", headers=teacher).json() == []
    assert (
        client.post(
            review_url, headers=teacher, json={**body, "revision": 2}
        ).status_code
        == 404
    )
    done = client.post(
        review_url, headers=manager, json={**body, "revision": 2, "status": "resolved"}
    )
    assert done.status_code == 200 and done.json()["revision"] == 3
    assert (
        client.post(
            review_url, headers=manager, json={**body, "revision": 3}
        ).status_code
        == 409
    )
    assert (
        client.get(f"/attempts/{attempt['id']}/result", headers=student).json()
        == submitted
    )
    assert send(client, student, q["id"], attempt["id"]).status_code == 201
    assert (
        client.get("/content-reports?status=resolved", headers=student).json()[0]["id"]
        == rid
    )
    assert (
        len(client.get("/content-reports?limit=1&offset=1", headers=student).json())
        == 1
    )
    client.cookies.clear()
    assert client.get("/content-reports").status_code == 401


def test_document_reports_quota_validation_and_self_delete(school):  # noqa: F811
    client, manager, q, app = school
    student, sid = register(client, "document_reporter", "student")
    with Session(app.state.engine) as db:
        for n in range(22):
            db.add(
                LibraryDocument(
                    id=f"doc-{n}",
                    fingerprint=f"report-doc-{n}",
                    payload={
                        "title": "Bài học tiếng Việt",
                        "summary": "Ôn tập theo bài học",
                    },
                    state="draft" if n == 21 else "published",
                    rights_confirmed=True,
                )
            )
        db.commit()
    payload = {
        "target_kind": "document",
        "target_id": "doc-0",
        "category": "typo",
        "message": "Chỗ này cần thêm dấu tiếng Việt.",
    }
    assert (
        client.post(
            "/content-reports", headers=student, json={**payload, "target_id": "doc-21"}
        ).status_code
        == 404
    )
    assert (
        client.post(
            "/content-reports", headers=student, json={**payload, "message": "  "}
        ).status_code
        == 422
    )
    assert (
        client.post(
            "/content-reports",
            headers=student,
            json={**payload, "reviewer_id": "owner"},
        ).status_code
        == 422
    )
    for n in range(20):
        response = client.post(
            "/content-reports",
            headers=student,
            json={**payload, "target_id": f"doc-{n}"},
        )
        assert response.status_code == 201, response.text
    assert (
        client.post(
            "/content-reports", headers=student, json={**payload, "target_id": "doc-20"}
        ).status_code
        == 429
    )
    assert (
        client.get("/content-reports?offset=19&limit=10", headers=student).json()[0][
            "excerpt"
        ]
        == "Ôn tập theo bài học"
    )
    assert (
        client.post(
            "/account/delete", headers=student, json={"password": "Test-password-123"}
        ).status_code
        == 204
    )
    with Session(app.state.engine) as db:
        assert db.get(LearningUser, sid) is None
        assert db.scalars(select(ContentReport)).all() == []


def test_deleting_reviewer_removes_authored_feedback_and_preserves_student(school):  # noqa: F811
    client, manager, q, app = school
    teacher, tid = register(client, "deleting_reviewer", "teacher")
    student, sid = register(client, "retained_student", "student")
    group = client.post(
        "/classroom/groups", headers=teacher, json={"name": "Nhóm"}
    ).json()
    client.post(
        "/classroom/groups/join", headers=student, json={"code": group["join_code"]}
    )
    attempt = client.post("/exams/student-exam/attempts", headers=student).json()
    report = send(client, student, q["id"], attempt["id"]).json()
    review = client.post(
        f"/classroom/content-reports/{report['id']}/review",
        headers=teacher,
        json={
            "revision": 1,
            "status": "resolved",
            "response": "Nội dung phản hồi cá nhân của giáo viên.",
        },
    )
    assert review.status_code == 200
    assert (
        client.post(
            "/account/delete", headers=teacher, json={"password": "Test-password-123"}
        ).status_code
        == 204
    )
    result = client.get("/content-reports", headers=student).json()[0]
    assert "cá nhân" not in result["response"] and result["revision"] == 3
    with Session(app.state.engine) as db:
        assert db.get(ContentReport, report["id"]).reviewed_by is None
        assert db.get(LearningUser, sid)


def test_schema_one_upgrade_preserves_accounts_and_is_repeatable(school):  # noqa: F811
    client, manager, q, app = school
    with app.state.engine.begin() as db:
        db.execute(text("DROP TABLE content_reports"))
        db.execute(text("UPDATE app_schema_version SET version=1"))
    with pytest.raises(RuntimeError):
        verify_schema(app.state.engine)
    migrate(app.state.engine)
    migrate(app.state.engine)
    verify_schema(app.state.engine)
    with app.state.engine.connect() as db:
        assert (
            db.scalar(text("SELECT version FROM app_schema_version")) == SCHEMA_VERSION
        )
        assert db.scalar(text("SELECT count(*) FROM learning_users")) == 1
    assert client.get("/classroom/students", headers=manager).status_code == 200
