"""The assigned-exam resume flow must not hide active drafts or offer expired ones."""

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session
from test_shared_server import school, login  # noqa: F401
from khohoc.models import Attempt, AccountAttempt


def test_assignment_sync_boundary_on_postgresql_and_sqlite(school):  # noqa: F811
    one, two, engine, question, postgres = school
    login(one, "manager")
    group = one.post("/classroom/groups", json={"name": "Nhóm bản nháp"}).json()
    group_url = f"/classroom/groups/{group['id']}"
    assert (
        one.post(group_url + "/members", json={"username": "student"}).status_code
        == 200
    )
    response = one.post(group_url + "/assignments", json={"exam_id": "sync-exam"})
    assert response.status_code == 201, response.text
    exam_id = response.json()["exam_id"]
    login(two)
    active = two.post(f"/exams/{exam_id}/attempts").json()
    cutoff = datetime.now(timezone.utc)
    with Session(engine) as db:
        original = db.get(Attempt, active["id"])
        original.created_at = cutoff - timedelta(minutes=30)
        snapshot = original.snapshot
        for index in range(101):
            ident = f"finished-assignment-{index}"
            db.add(
                Attempt(
                    id=ident,
                    token_hash="synthetic",
                    snapshot=snapshot,
                    result={"score": 1},
                    created_at=cutoff - timedelta(seconds=index),
                )
            )
            db.add(AccountAttempt(attempt_id=ident, user_id="student"))
        db.commit()
    pending = two.get("/account/attempts").json()
    assert len(pending) == 1 and pending[0]["exam_id"] == exam_id
    assert pending[0]["id"] == active["id"]
    path = "/account/attempts/" + active["id"]
    saved = two.post(path + "/draft", json={"revision": 0, "answers": {}})
    assert saved.status_code == 200
    assert two.get(path).json()["draft_revision"] == 1
    own = two.get("/account/assignments").json()[0]
    assert own["status"] == "in_progress"
    with Session(engine) as db:
        db.get(Attempt, active["id"]).created_at = cutoff - timedelta(
            hours=24, minutes=1
        )
        db.commit()
    assert two.get("/account/attempts").json() == []
    assert two.get(path).status_code == 410
    assert (
        two.post(path + "/draft", json={"revision": 1, "answers": {}}).status_code
        == 410
    )
    assert (
        two.post(
            "/attempts/" + active["id"] + "/submit", json={"answers": {}}
        ).status_code
        == 410
    )
    assert two.get("/account/assignments").json()[0]["status"] == "not_started"
    detail = one.get(group_url + "/assignments/" + exam_id).json()
    assert detail["in_progress_count"] == 0 and detail["not_started_count"] == 1
