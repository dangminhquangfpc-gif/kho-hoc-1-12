import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from khohoc.app import Settings, create_app
from khohoc.models import ContentQuestion

ROOT = Path(__file__).resolve().parents[3]
ADMIN = {"Authorization": "Bearer custom-practice-test"}


@pytest.fixture
def seeded(tmp_path):
    app = create_app(
        Settings(
            database_url=f"sqlite:///{tmp_path}/custom.db",
            admin_token="custom-practice-test",
        )
    )
    with TestClient(app) as client:
        rows = json.loads((ROOT / "data/seeds/practice_questions.json").read_text())[
            "questions"
        ]
        qs = [q for q in rows if q["topic"] in ("natural", "add_decimal")][:12]
        client.post(
            "/admin/import", headers=ADMIN, json={"questions": qs}
        ).raise_for_status()
        for q in qs[:-1]:
            client.post(
                f"/admin/questions/{q['id']}/approve",
                headers=ADMIN,
                params={"rights_confirmed": "true"},
            ).raise_for_status()
            client.post(
                f"/admin/questions/{q['id']}/publish", headers=ADMIN
            ).raise_for_status()
        client.engine = app.state.engine
        yield client, qs


def test_custom_practice_filters_deduplicates_and_never_exposes_keys(seeded):
    client, questions = seeded
    options = client.get(
        "/practice-options", params={"grade": 5, "subject": "toan"}
    ).json()
    assert options["total"] == 10
    assert any(
        t["name"] == "Số tự nhiên" and t["count"] == 7 for t in options["topics"]
    )
    response = client.post(
        "/practice-attempts",
        json={
            "grade": 5,
            "subject": "toan",
            "topic": "natural",
            "difficulty": "medium",
            "textbook": "ket_noi_tri_thuc",
            "count": 7,
        },
    )
    assert response.status_code == 201, response.text
    attempt = response.json()
    assert len({q["id"] for q in attempt["questions"]}) == 7
    assert "correct_answer" not in response.text and "explanation" not in response.text
    assert attempt["practice_filter"]["topic"] == "natural"
    assert (
        client.post(
            "/practice-attempts",
            json={"grade": 5, "subject": "toan", "topic": "natural", "count": 9},
        ).status_code
        == 422
    )
    assert (
        client.post(
            "/practice-attempts", json={"grade": 5, "subject": "vat_li", "count": 1}
        ).status_code
        == 422
    )
    assert (
        client.post(
            "/practice-attempts", json={"grade": 5, "subject": "toan", "count": 51}
        ).status_code
        == 422
    )


def test_targeted_review_uses_only_published_questions_and_snapshot(seeded):
    client, questions = seeded
    q = questions[0]
    body = {"grade": 5, "subject": "toan", "count": 1, "question_ids": [q["id"]]}
    attempt = client.post("/practice-attempts", json=body).json()
    with Session(client.engine) as db:
        row = db.get(ContentQuestion, q["id"])
        row.payload = {**row.payload, "correct_answer": ["99999"]}
        row.state = "draft"
        db.commit()
    response = client.post(
        f"/attempts/{attempt['id']}/submit",
        headers={"X-Attempt-Token": attempt["token"]},
        json={"answers": {q["id"]: q["correct_answer"]}},
    )
    assert response.status_code == 200 and response.json()["score"] == 1
    assert client.post("/practice-attempts", json=body).status_code == 409
    assert (
        client.post(
            "/practice-attempts", json={**body, "question_ids": [questions[-1]["id"]]}
        ).status_code
        == 409
    )
    assert (
        client.post(
            "/practice-attempts",
            json={**body, "count": 2, "question_ids": [q["id"], q["id"]]},
        ).status_code
        == 422
    )
    assert client.get(f"/attempts/{attempt['id']}/result").status_code == 404


def test_multiple_topics_are_balanced_and_all_selected_topics_appear(seeded):
    client, _ = seeded
    result = client.post(
        "/practice-attempts",
        json={
            "grade": 5,
            "subject": "toan",
            "topics": ["natural", "add_decimal"],
            "count": 6,
        },
    )
    assert result.status_code == 201
    topics = [q["topic"] for q in result.json()["questions"]]
    assert topics.count("natural") == topics.count("add_decimal") == 3
    assert (
        client.post(
            "/practice-attempts",
            json={
                "grade": 5,
                "subject": "toan",
                "topics": ["natural", "add_decimal"],
                "count": 1,
            },
        ).status_code
        == 422
    )
    assert (
        client.post(
            "/practice-attempts",
            json={
                "grade": 5,
                "subject": "toan",
                "topics": ["natural", "not_available"],
                "count": 2,
            },
        ).status_code
        == 422
    )
