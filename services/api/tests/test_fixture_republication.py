"""Restarting the preview cannot approve admin edits under fixture IDs."""

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from khohoc.app import Settings, create_app
from khohoc.schemas import ExamInput
from khohoc.phone_preview import create_preview

ROOT = Path(__file__).resolve().parents[3]
ADMIN = {"Authorization": "Bearer fixture-review-test-token"}


@pytest.fixture
def fixture_client(tmp_path, monkeypatch):
    database_url = f"sqlite:///{tmp_path}/fixture-review.db"
    monkeypatch.setenv("KHOHOC_DATABASE_URL", database_url)
    app = create_app(
        Settings(database_url=database_url, admin_token="fixture-review-test-token")
    )
    with TestClient(app) as client:
        yield client


def import_first_question(client):
    question = json.loads((ROOT / "data/seeds/questions.json").read_text())[
        "questions"
    ][0]
    response = client.post(
        "/admin/import", headers=ADMIN, json={"questions": [question]}
    )
    assert response.status_code == 200, response.text
    return client.get("/admin/questions/toan1_001", headers=ADMIN).json()["question"]


@pytest.mark.parametrize("publish_edit", [False, True])
def test_preview_refuses_edited_fixture_even_if_already_published(
    fixture_client, publish_edit
):
    client = fixture_client
    question = import_first_question(client)
    edited = question | {
        "correct_answer": ["B"],
        "explanation": "Admin-edited answer for this regression test.",
    }
    response = client.post(
        "/admin/questions/toan1_001/edit",
        headers=ADMIN,
        json={
            "expected_version": 1,
            "question": edited,
            "note": "An edit requiring a new review.",
        },
    )
    assert response.status_code == 200, response.text
    expected_state = "draft"
    if publish_edit:
        assert (
            client.post(
                "/admin/questions/toan1_001/approve",
                headers=ADMIN,
                params={"rights_confirmed": "true", "expected_version": 2},
            ).status_code
            == 200
        )
        assert (
            client.post(
                "/admin/questions/toan1_001/publish",
                headers=ADMIN,
                params={"expected_version": 2},
            ).status_code
            == 200
        )
        expected_state = "published"
    with pytest.raises(RuntimeError, match="Refusing changed question fixture"):
        create_preview()
    current = client.get("/admin/questions/toan1_001", headers=ADMIN).json()
    assert current["version"] == 2
    assert current["question"] == edited
    assert current["state"] == expected_state
    assert current["rights_confirmed"] is publish_edit
    # Refusal happens before importing or approving any other fixture.
    assert len(client.get("/admin/questions", headers=ADMIN).json()) == 1
    assert client.get("/exams?grade=1").json() == []


def test_preview_refuses_reused_exam_id_before_approving_questions(fixture_client):
    client = fixture_client
    import_first_question(client)
    exam = json.loads((ROOT / "data/seeds/exams.json").read_text())[0]
    altered_exam = exam | {
        "title": "A different admin-created exam under the fixture ID",
        "question_ids": ["toan1_001"],
    }
    assert (
        client.post("/admin/exams", headers=ADMIN, json=altered_exam).status_code == 201
    )
    with pytest.raises(RuntimeError, match="Refusing changed exam fixture"):
        create_preview()
    current = client.get("/admin/questions/toan1_001", headers=ADMIN).json()
    assert current["state"] == "draft"
    assert current["rights_confirmed"] is False
    assert client.get("/admin/exams", headers=ADMIN).json() == [
        {
            "exam": ExamInput.model_validate(altered_exam).model_dump(mode="json"),
            "state": "draft",
        }
    ]


def test_preview_refuses_changed_document_metadata_before_approving_questions(
    fixture_client,
):
    client = fixture_client
    import_first_question(client)
    note = json.loads((ROOT / "data/library/documents.json").read_text())["documents"][
        0
    ]
    edited_note = note | {"summary": "Admin-edited summary requiring fresh review."}
    response = client.post(
        "/admin/documents/import", headers=ADMIN, json={"documents": [edited_note]}
    )
    assert response.status_code == 200, response.text
    with pytest.raises(RuntimeError, match="Refusing changed document fixture"):
        create_preview()
    assert (
        client.get("/admin/questions/toan1_001", headers=ADMIN).json()["state"]
        == "draft"
    )
    document = client.get("/admin/documents", headers=ADMIN).json()[0]
    assert document["state"] == "draft"
    assert document["rights_confirmed"] is False
    assert client.get("/documents").json() == []


def test_repeated_normal_preview_setup_preserves_nonfixture_drafts(fixture_client):
    client = fixture_client
    with TestClient(create_preview()) as preview:
        assert len(preview.get("/documents").json()) == 50
        public = preview.get("/exams/tieng_viet1_practice")
        assert public.status_code == 200
        assert "correct_answer" not in public.text
        assert "explanation" not in public.text
    question = client.get("/admin/questions/toan1_001", headers=ADMIN).json()[
        "question"
    ]
    outside_fixture = question | {
        "id": "nonfixture_admin_question",
        "question": "Một câu hỏi do quản trị viên nhập riêng, cần được duyệt riêng.",
    }
    response = client.post(
        "/admin/import", headers=ADMIN, json={"questions": [outside_fixture]}
    )
    assert response.status_code == 200, response.text
    with TestClient(create_preview()) as preview:
        assert preview.get("/exams/tieng_anh12_practice").status_code == 200
        assert len(preview.get("/documents").json()) == 50
        assert preview.get("/admin/exams").status_code == 404
    stored = client.get(
        "/admin/questions/nonfixture_admin_question", headers=ADMIN
    ).json()
    assert stored["state"] == "draft"
    assert stored["rights_confirmed"] is False
