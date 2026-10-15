import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from khohoc.app import Settings, create_app
from khohoc.grading import grade, number
from khohoc.models import ContentQuestion
from khohoc.schemas import Question
from khohoc.content_fixes import QUESTION_REPLACEMENTS

ROOT = Path(__file__).resolve().parents[3]
TOKEN = "test-only-admin-token"
ADMIN = {"Authorization": "Bearer " + TOKEN}


@pytest.fixture
def client(tmp_path):
    app = create_app(
        Settings(database_url=f"sqlite:///{tmp_path}/test.db", admin_token=TOKEN)
    )
    with TestClient(app) as c:
        c.engine = app.state.engine
        yield c


@pytest.fixture
def seeded(client):
    data = json.loads((ROOT / "data/seeds/questions.json").read_text())
    data["questions"] += json.loads(
        (ROOT / "data/seeds/clean_questions.json").read_text()
    )["questions"]
    assert client.post("/admin/import", json=data, headers=ADMIN).status_code == 200
    exam = json.loads((ROOT / "data/seeds/exams.json").read_text())[0]
    exam["question_ids"] = [
        QUESTION_REPLACEMENTS.get(qid, qid) for qid in exam["question_ids"]
    ]
    for qid in exam["question_ids"]:
        assert (
            client.post(
                f"/admin/questions/{qid}/approve?rights_confirmed=true", headers=ADMIN
            ).status_code
            == 200
        )
        assert (
            client.post(f"/admin/questions/{qid}/publish", headers=ADMIN).status_code
            == 200
        )
    assert client.post("/admin/exams", json=exam, headers=ADMIN).status_code == 201
    assert (
        client.post(f"/admin/exams/{exam['id']}/publish", headers=ADMIN).status_code
        == 200
    )
    return client, data, exam


def test_full_practice_flow_and_answer_privacy(seeded):
    client, data, exam = seeded
    assert len(client.get("/grades").json()) == 12
    assert client.get("/grades/1/subjects").json()[0]["id"] == "toan"
    assert client.get("/exams?grade=1&subject=toan").json()[0]["id"] == exam["id"]
    detail = client.get("/exams/" + exam["id"]).json()
    assert "correct_answer" not in json.dumps(detail)
    assert "explanation" not in json.dumps(detail)
    attempt = client.post(f"/exams/{exam['id']}/attempts").json()
    h = {"X-Attempt-Token": attempt["token"]}
    url = f"/attempts/{attempt['id']}"
    assert client.get(url + "/result", headers=h).status_code == 409
    assert client.get(url + "/result").status_code == 404
    answers = {
        q["id"]: q["correct_answer"]
        for q in data["questions"]
        if q["id"] in exam["question_ids"]
    }
    result = client.post(url + "/submit", headers=h, json={"answers": answers})
    assert result.status_code == 200, result.text
    assert result.json()["score"] == result.json()["max_score"] == 13
    assert (
        client.post(url + "/submit", headers=h, json={"answers": answers}).json()
        == result.json()
    )
    assert (
        client.post(url + "/submit", headers=h, json={"answers": {}}).status_code == 409
    )
    assert client.get(url + "/result", headers=h).json()["details"][0]["explanation"]
    assert client.delete(url, headers=h).status_code == 204
    assert client.get(url + "/result", headers=h).status_code == 404


def test_snapshot_and_tampering(seeded):
    client, data, exam = seeded
    a = client.post(f"/exams/{exam['id']}/attempts").json()
    url = f"/attempts/{a['id']}/submit"
    h = {"X-Attempt-Token": a["token"]}
    assert (
        client.post(
            url, headers={"X-Attempt-Token": "wrong"}, json={"answers": {}}
        ).status_code
        == 404
    )
    assert (
        client.post(url, headers=h, json={"answers": {"unknown": ["A"]}}).status_code
        == 422
    )
    with Session(client.engine) as db:
        question = db.get(ContentQuestion, exam["question_ids"][0])
        question.payload = question.payload | {"correct_answer": ["B"]}
        db.commit()
    answer = {exam["question_ids"][0]: ["A"]}
    result = client.post(url, headers=h, json={"answers": answer}).json()
    assert result["details"][0]["score"] == 1


def test_draft_rights_and_admin_guard(client):
    data = json.loads((ROOT / "data/seeds/questions.json").read_text())
    assert client.post("/admin/import", json=data).status_code == 403
    assert client.get("/admin/questions").status_code == 403
    assert client.post("/admin/import", json=data, headers=ADMIN).status_code == 200
    q = data["questions"][0]["id"]
    assert (
        client.post("/admin/questions/" + q + "/publish", headers=ADMIN).status_code
        == 409
    )
    assert (
        client.post(
            "/admin/questions/" + q + "/approve?rights_confirmed=false", headers=ADMIN
        ).status_code
        == 422
    )
    assert client.get("/exams?grade=1").json() == []
    assert client.post("/admin/import", json=data, headers=ADMIN).status_code == 409
    assert len(client.get("/admin/questions", headers=ADMIN).json()) == 60


def q(type="numeric", **kwargs):
    return Question(
        id="q1",
        grade=5,
        subject="toan",
        topic="test",
        type=type,
        question="Test?",
        max_score=1,
        explanation="Explanation",
        correct_answer=["3/4"],
        license="original_content",
        rights_evidence="Original test fixture",
        **kwargs,
    )


@pytest.mark.parametrize("answer", ["0,75", "0.75", "3/4", "75/100"])
def test_fraction_decimal(answer):
    assert grade(q(), [answer])["score"] == 1


@pytest.mark.parametrize(
    "answer", ["1/0", "nan", "inf", "1e100000", '__import__("os")', "3/4 kg"]
)
def test_invalid_numeric(answer):
    assert grade(q(), [answer])["score"] == 0


def test_units_tolerance_and_case():
    assert number("0,25 km²", "ha") == 25
    assert number("150 cm", "m") == number("1,5", "m")
    with pytest.raises(ValueError):
        number("1 ha", "m")
    numeric = q().model_copy(
        update={
            "correct_answer": ["1"],
            "tolerance": __import__("decimal").Decimal(".01"),
        }
    )
    assert grade(numeric, ["1,009"])["score"] == 1
    assert grade(numeric, ["1,02"])["score"] == 0
    assert grade(q("short_answer"), [" 3/4 "])["score"] == 1


def test_multiple_and_partial_boolean():
    from khohoc.schemas import Option

    multiple = Question(
        id="multi",
        grade=5,
        subject="toan",
        topic="test",
        type="multiple_choice",
        question="Which?",
        options=[
            Option(id="A", text="a"),
            Option(id="B", text="b"),
            Option(id="C", text="c"),
        ],
        correct_answer=["A", "B"],
        max_score=2,
        explanation="a,b",
        license="original_content",
        rights_evidence="test",
    )
    assert grade(multiple, ["B", "A"])["score"] == 2
    assert grade(multiple, ["A"])["score"] == 0
    assert grade(multiple, ["A", "A", "B"])["score"] == 0
    boolean = multiple.model_copy(
        update={"type": "true_false", "correct_answer": ["true", "false", "true"]}
    )
    assert grade(boolean, ["true", "true", "true"])["score"] == pytest.approx(4 / 3)


def test_essay_is_not_an_official_score():
    from khohoc.schemas import RubricCriterion

    essay = Question(
        id="essay",
        grade=5,
        subject="toan",
        topic="test",
        type="essay",
        question="Explain",
        rubric=[RubricCriterion(description="Correct argument", points=1)],
        max_score=1,
        explanation="Explain",
        license="original_content",
        rights_evidence="test",
    )
    assert grade(essay, ["Whatever"])["score"] is None
    assert grade(essay, ["Whatever"])["status"] == "needs_manual_review"


def test_production_fail_closed():
    with pytest.raises(RuntimeError):
        create_app(Settings(mode="production"))


def test_body_limit(client):
    assert (
        client.post("/admin/import", content="x" * 2_000_001, headers=ADMIN).status_code
        == 413
    )
