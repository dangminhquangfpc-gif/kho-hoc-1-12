import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from khohoc.app import Settings, create_app
from khohoc.models import AuditEvent, ContentQuestion, Exam
from khohoc.question_versions import QuestionRevision

ROOT = Path(__file__).resolve().parents[3]
ADMIN = {"Authorization": "Bearer test-only-question-revision-token"}


@pytest.fixture
def revision_client(tmp_path):
    app = create_app(
        Settings(
            database_url=f"sqlite:///{tmp_path}/revisions.db",
            admin_token="test-only-question-revision-token",
        )
    )
    with TestClient(app) as client:
        client.engine = app.state.engine
        questions = json.loads((ROOT / "data/seeds/questions.json").read_text())[
            "questions"
        ][:2]
        assert (
            client.post(
                "/admin/import", json={"questions": questions}, headers=ADMIN
            ).status_code
            == 200
        )
        yield client


def current(client):
    response = client.get("/admin/questions/toan1_001", headers=ADMIN)
    assert response.status_code == 200, response.text
    return response.json()


def edit(client, *, version=1, payload=None):
    question = payload or current(client)["question"]
    return client.post(
        "/admin/questions/toan1_001/edit",
        headers=ADMIN,
        json={
            "expected_version": version,
            "question": question,
            "note": "Sửa đáp án để kiểm tra lịch sử.",
        },
    )


def changed(client):
    return current(client)["question"] | {
        "correct_answer": ["B"],
        "explanation": "Lời giải đã được chỉnh sửa trong kiểm thử.",
    }


def publish(client, version=1):
    assert (
        client.post(
            f"/admin/questions/toan1_001/approve?rights_confirmed=true&expected_version={version}",
            headers=ADMIN,
        ).status_code
        == 200
    )
    assert (
        client.post(
            f"/admin/questions/toan1_001/publish?expected_version={version}",
            headers=ADMIN,
        ).status_code
        == 200
    )


def test_history_requires_admin_and_edit_does_not_leak_keys(revision_client):
    client = revision_client
    for path in (
        "/admin/questions/toan1_001",
        "/admin/questions/toan1_001/versions",
    ):
        assert client.get(path).status_code == 403
    assert (
        client.post(
            "/admin/questions/toan1_001/edit",
            json={
                "expected_version": 1,
                "question": current(client)["question"],
                "note": "Unauthorized request",
            },
        ).status_code
        == 403
    )
    assert (
        client.post(
            "/admin/questions/toan1_001/rollback",
            json={"expected_version": 1, "target_version": 1, "note": "Unauthorized"},
        ).status_code
        == 403
    )
    history = client.get("/admin/questions/toan1_001/versions", headers=ADMIN).json()
    assert [row["version"] for row in history["versions"]] == [1]


def test_edit_blocks_future_exam_attempts_and_preserves_started_snapshot(
    revision_client,
):
    client = revision_client
    publish(client)
    exam = {
        "id": "revision_exam",
        "title": "Đề kiểm tra phiên bản",
        "grade": 1,
        "subject": "toan",
        "question_ids": ["toan1_001"],
        "duration_minutes": 10,
    }
    assert client.post("/admin/exams", json=exam, headers=ADMIN).status_code == 201
    assert (
        client.post("/admin/exams/revision_exam/publish", headers=ADMIN).status_code
        == 200
    )
    attempt = client.post("/exams/revision_exam/attempts").json()
    response = edit(client, payload=changed(client))
    assert response.status_code == 200, response.text
    assert response.json() == {
        "id": "toan1_001",
        "version": 2,
        "state": "draft",
        "rights_confirmed": False,
        "exams_reset_to_draft": ["revision_exam"],
    }
    assert client.get("/exams?grade=1").json() == []
    assert client.get("/exams/revision_exam").status_code == 404
    assert client.post("/exams/revision_exam/attempts").status_code == 404
    assert (
        client.post("/admin/exams/revision_exam/publish", headers=ADMIN).status_code
        == 409
    )
    result = client.post(
        f"/attempts/{attempt['id']}/submit",
        headers={"X-Attempt-Token": attempt["token"]},
        json={"answers": {"toan1_001": ["A"]}},
    )
    assert result.status_code == 200, result.text
    assert result.json()["score"] == 1
    assert result.json()["details"][0]["correct_answer"] == ["A"]
    publish(client, version=2)
    # Exam needs explicit republication even after the new question is published.
    assert client.get("/exams/revision_exam").status_code == 404
    assert (
        client.post("/admin/exams/revision_exam/publish", headers=ADMIN).status_code
        == 200
    )
    public = client.get("/exams/revision_exam").json()
    assert "correct_answer" not in json.dumps(public)
    assert "explanation" not in json.dumps(public)
    with Session(client.engine) as session:
        assert session.get(Exam, "revision_exam").state == "published"
        assert session.get(ContentQuestion, "toan1_001").version == 2
        assert (
            session.scalar(
                select(AuditEvent).where(AuditEvent.action == "question-edit")
            ).target
            == "toan1_001:v2"
        )


def test_rollback_creates_new_draft_revision_and_keeps_intermediate_versions(
    revision_client,
):
    client = revision_client
    original = current(client)["question"]
    assert edit(client, payload=changed(client)).status_code == 200
    publish(client, version=2)
    response = client.post(
        "/admin/questions/toan1_001/rollback",
        headers=ADMIN,
        json={
            "expected_version": 2,
            "target_version": 1,
            "note": "Khôi phục đáp án gốc",
        },
    )
    assert response.status_code == 200, response.text
    assert response.json()["version"] == 3
    detail = current(client)
    assert detail["question"] == original
    assert detail["state"] == "draft"
    assert detail["rights_confirmed"] is False
    history = client.get("/admin/questions/toan1_001/versions", headers=ADMIN).json()
    assert [row["version"] for row in history["versions"]] == [3, 2, 1]
    assert history["versions"][0]["operation"] == "rollback"
    assert history["versions"][0]["restored_from"] == 1
    assert history["versions"][1]["question"]["correct_answer"] == ["B"]
    with Session(client.engine) as session:
        assert (
            session.scalar(
                select(AuditEvent).where(AuditEvent.action == "question-rollback")
            ).target
            == "toan1_001:v3:from-v1"
        )


def test_stale_edits_and_rollbacks_do_not_overwrite_new_content(revision_client):
    client = revision_client
    assert edit(client, payload=changed(client)).status_code == 200
    assert (
        edit(
            client, payload=current(client)["question"] | {"topic": "stale"}
        ).status_code
        == 409
    )
    response = client.post(
        "/admin/questions/toan1_001/rollback",
        headers=ADMIN,
        json={"expected_version": 1, "target_version": 1, "note": "Stale rollback"},
    )
    assert response.status_code == 409
    assert current(client)["version"] == 2
    with Session(client.engine) as session:
        assert len(list(session.scalars(select(QuestionRevision)))) == 2


def test_stale_moderation_forms_require_review_of_current_version(revision_client):
    client = revision_client
    assert edit(client, payload=changed(client)).status_code == 200
    assert (
        client.post(
            "/admin/questions/toan1_001/approve?rights_confirmed=true&expected_version=1",
            headers=ADMIN,
        ).status_code
        == 409
    )
    assert current(client)["state"] == "draft"
    assert (
        client.post(
            "/admin/questions/toan1_001/approve?rights_confirmed=true&expected_version=2",
            headers=ADMIN,
        ).status_code
        == 200
    )
    assert (
        client.post(
            "/admin/questions/toan1_001/publish?expected_version=1", headers=ADMIN
        ).status_code
        == 409
    )
    assert current(client)["state"] == "approved"
    assert (
        client.post(
            "/admin/questions/toan1_001/publish?expected_version=2", headers=ADMIN
        ).status_code
        == 200
    )


def test_invalid_edits_are_atomic_and_cannot_change_id_or_duplicate_text(
    revision_client,
):
    client = revision_client
    original = current(client)
    second = client.get("/admin/questions/toan1_002", headers=ADMIN).json()["question"]
    candidates = [
        (original["question"] | {"id": "different"}, 422),
        (original["question"] | {"correct_answer": ["missing-option"]}, 422),
        (original["question"] | {"subject": "not-a-subject"}, 422),
        (original["question"] | {"question": second["question"]}, 409),
        (original["question"], 409),
    ]
    for payload, expected in candidates:
        response = edit(client, payload=payload)
        assert response.status_code == expected, response.text
        assert current(client) == original
    with Session(client.engine) as session:
        assert list(session.scalars(select(QuestionRevision))) == []


def test_edit_cannot_move_question_to_another_grade_while_referenced(revision_client):
    client = revision_client
    assert (
        client.post(
            "/admin/exams",
            headers=ADMIN,
            json={
                "id": "draft_exam",
                "title": "Đề nháp",
                "grade": 1,
                "subject": "toan",
                "question_ids": ["toan1_001"],
                "duration_minutes": 5,
            },
        ).status_code
        == 201
    )
    response = edit(client, payload=current(client)["question"] | {"grade": 5})
    assert response.status_code == 409
    assert current(client)["version"] == 1


def test_missing_versions_and_blank_notes_do_not_change_content(revision_client):
    client = revision_client
    assert client.get("/admin/questions/missing", headers=ADMIN).status_code == 404
    for target, expected in [(1, 409), (900, 404)]:
        assert (
            client.post(
                "/admin/questions/toan1_001/rollback",
                headers=ADMIN,
                json={"expected_version": 1, "target_version": target, "note": "Test"},
            ).status_code
            == expected
        )
    assert (
        client.post(
            "/admin/questions/toan1_001/edit",
            headers=ADMIN,
            json={"expected_version": 1, "question": changed(client), "note": "   "},
        ).status_code
        == 422
    )
    assert current(client)["version"] == 1
