"""Assignment cloning, per-exam progress and private current-member rosters."""

import csv
import io
from copy import deepcopy
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import event, select, update
from sqlalchemy.orm import Session

from khohoc.models import (
    Attempt,
    ContentQuestion,
    Exam,
    GroupMember,
    LearningRecord,
    LearningUser,
    TeacherExam,
)
from test_accounts import school  # noqa: F401
from test_teacher_groups import register


@pytest.fixture
def classroom(school):  # noqa: F811
    client, manager, question, app = school
    teacher, teacher_id = register(client, "teacher01", "teacher")
    other, other_id = register(client, "teacher02", "teacher")
    pupils = [
        register(client, name, "student") for name in ("pupil01", "pupil02", "pupil03")
    ]
    group = client.post(
        "/classroom/groups", headers=teacher, json={"name": "Nhóm kiểm tra"}
    ).json()
    for headers, user_id in pupils:
        joined = client.post(
            "/classroom/groups/join", headers=headers, json={"code": group["join_code"]}
        )
        assert joined.status_code == 200
    client.cookies.clear()
    return (
        client,
        manager,
        question,
        app,
        teacher,
        teacher_id,
        other,
        other_id,
        pupils,
        group,
    )


def assign(client, teacher, group, source="student-exam"):
    response = client.post(
        f"/classroom/groups/{group['id']}/assignments",
        headers=teacher,
        json={"exam_id": source},
    )
    assert response.status_code == 201, response.text
    return response.json()


def start(client, headers, exam_id):
    response = client.post(f"/exams/{exam_id}/attempts", headers=headers)
    assert response.status_code == 201, response.text
    return response.json()


def finish(client, headers, attempt, answers):
    response = client.post(
        f"/attempts/{attempt['id']}/submit", headers=headers, json={"answers": answers}
    )
    assert response.status_code == 200, response.text
    return response.json()


def test_clone_keeps_source_unchanged_and_owner_only_management(classroom):
    client, manager, q, app, teacher, tid, other, oid, pupils, group = classroom
    path = f"/classroom/groups/{group['id']}/assignments"
    student, sid = pupils[0]
    for headers, status in (({}, 401), (student, 403), (other, 404), (manager, 404)):
        assert (
            client.post(
                path, headers=headers, json={"exam_id": "student-exam"}
            ).status_code
            == status
        )
        assert client.get(path, headers=headers).status_code == status
    created = assign(client, teacher, group)
    eid = created["exam_id"]
    assert eid != "student-exam"
    assert created["member_count"] == created["not_started_count"] == 3
    assert created["submitted_count"] == created["in_progress_count"] == 0
    with Session(app.state.engine) as db:
        source, clone = db.get(Exam, "student-exam"), db.get(Exam, eid)
        assert source.payload["id"] == "student-exam" and source.state == "published"
        assert clone.payload == {**source.payload, "id": eid}
        scope = db.get(TeacherExam, eid)
        assert scope.owner_id == tid and scope.group_id == group["id"]
    assert client.get(f"/exams/{eid}", headers=student).status_code == 200
    assert client.get(f"/exams/{eid}", headers=other).status_code == 404
    assert client.get(f"/exams/{eid}").status_code == 404
    for suffix in (f"/{eid}", f"/{eid}/results.csv"):
        for headers, status in (
            ({}, 401),
            (student, 403),
            (other, 404),
            (manager, 404),
        ):
            assert client.get(path + suffix, headers=headers).status_code == status
    own = client.get("/account/assignments", headers=student).json()
    assert len(own) == 1 and own[0]["exam_id"] == eid
    assert own[0]["status"] == "not_started"
    assert (
        not {"students", "member_count", "student_ids", "join_code", "submitted_count"}
        & own[0].keys()
    )
    assert client.get("/account/assignments").status_code == 401
    assert client.get("/account/assignments", headers=teacher).status_code == 403
    assert client.get(path, headers=teacher, params={"limit": 0}).status_code == 422


def test_progress_uses_latest_server_result_and_current_members(classroom):
    client, manager, q, app, teacher, tid, other, oid, pupils, group = classroom
    assigned = assign(client, teacher, group)
    eid = assigned["exam_id"]
    path = f"/classroom/groups/{group['id']}/assignments/{eid}"
    first, second, third = pupils
    good = start(client, first[0], eid)
    finish(client, first[0], good, {q["id"]: q["correct_answer"]})
    bad = start(client, first[0], eid)
    finish(client, first[0], bad, {})
    # Repeated submission is idempotent and deleting a draft does not erase the record.
    finish(client, first[0], bad, {})
    assert client.delete(f"/attempts/{bad['id']}", headers=first[0]).status_code == 204
    start(client, first[0], eid)  # A new draft never hides an already submitted result.
    second_draft = start(client, second[0], eid)
    expired = start(client, third[0], eid)
    # Unrelated public exam with the same title must not count toward this assignment.
    unrelated = start(client, third[0], "student-exam")
    finish(client, third[0], unrelated, {q["id"]: q["correct_answer"]})
    with Session(app.state.engine) as db:
        # Older deployments can persist JSON null instead of SQL NULL.
        db.execute(
            update(Attempt).where(Attempt.id == second_draft["id"]).values(result=None)
        )
        db.get(Attempt, expired["id"]).created_at = datetime.now(
            timezone.utc
        ) - timedelta(hours=25)
        record = db.get(LearningRecord, good["id"])
        record.payload = {**record.payload, "result": {"score": 7, "max_score": 10}}
        record.submitted_at = datetime.now(timezone.utc) - timedelta(minutes=2)
        recent = db.get(LearningRecord, bad["id"])
        recent.payload = {**recent.payload, "result": {"score": 3, "max_score": 4}}
        db.commit()
    detail = client.get(path, headers=teacher).json()
    assert (
        detail["member_count"],
        detail["submitted_count"],
        detail["in_progress_count"],
        detail["not_started_count"],
    ) == (3, 1, 1, 1)
    students = {s["id"]: s for s in detail["students"]}
    assert students[first[1]]["attempts_count"] == 2
    assert students[first[1]]["latest_percent"] == 75
    assert students[second[1]]["status"] == "in_progress"
    assert students[third[1]]["status"] == "not_started"
    assert students[third[1]]["latest_percent"] is None
    own = client.get("/account/assignments", headers=first[0]).json()[0]
    assert own["status"] == "submitted" and own["attempts_count"] == 2
    assert own["latest_percent"] == 75
    assert (
        client.delete(
            f"/classroom/groups/{group['id']}/members/{first[1]}", headers=teacher
        ).status_code
        == 204
    )
    assert client.get("/account/assignments", headers=first[0]).json() == []
    refreshed = client.get(path, headers=teacher).json()
    assert refreshed["member_count"] == 2 and refreshed["submitted_count"] == 0
    assert first[1] not in {s["id"] for s in refreshed["students"]}
    assert client.post(f"/exams/{eid}/attempts", headers=first[0]).status_code == 404


def test_latest_manual_review_is_blank_and_csv_safe(classroom):
    client, manager, q, app, teacher, tid, other, oid, pupils, group = classroom
    eid = assign(client, teacher, group)["exam_id"]
    student, sid = pupils[0]
    attempt = start(client, student, eid)
    finish(client, student, attempt, {})
    with Session(app.state.engine) as db:
        record = db.get(LearningRecord, attempt["id"])
        record.payload = {
            **record.payload,
            "result": {"score": None, "max_score": 10, "graded_score": 7},
        }
        db.get(LearningUser, sid).display_name = '\t=HYPERLINK("example")'
        exam = db.get(Exam, eid)
        exam.payload = {**exam.payload, "title": "+cmd|title"}
        db.commit()
    path = f"/classroom/groups/{group['id']}/assignments/{eid}"
    detail = client.get(path, headers=teacher).json()
    assert detail["submitted_count"] == 1
    assert detail["students"][0]["status"] == "submitted"
    assert detail["students"][0]["latest_percent"] is None
    response = client.get(path + "/results.csv", headers=teacher)
    assert response.status_code == 200
    assert response.content.startswith(b"\xef\xbb\xbf")
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["x-content-type-options"] == "nosniff"
    rows = list(csv.reader(io.StringIO(response.content.decode("utf-8-sig"))))
    assert len(rows) == 4  # Includes pupils who never submitted.
    assert rows[1][1].startswith("'+") and rows[1][3].startswith("'\t=")
    assert rows[1][6] == "1" and rows[1][7] == ""
    assert rows[2][6] == "0" and rows[2][7] == ""


@pytest.mark.parametrize(
    "invalid",
    ["missing", "archived", "withdrawn", "rights", "grade", "link", "malformed"],
)
def test_invalid_sources_cannot_be_assigned(classroom, invalid):
    client, manager, q, app, teacher, tid, other, oid, pupils, group = classroom
    with Session(app.state.engine) as db:
        exam = db.get(Exam, "student-exam")
        question = db.get(ContentQuestion, q["id"])
        if invalid == "missing":
            db.delete(exam)
        elif invalid == "archived":
            exam.state = "archived"
        elif invalid == "withdrawn":
            question.state = "withdrawn"
        elif invalid == "rights":
            question.rights_confirmed = False
        elif invalid == "grade":
            question.payload = {**question.payload, "grade": 6}
        elif invalid == "link":
            question.payload = {**question.payload, "source_type": "link_only"}
        else:
            exam.payload = {**exam.payload, "duration_minutes": 0}
        db.commit()
    response = client.post(
        f"/classroom/groups/{group['id']}/assignments",
        headers=teacher,
        json={"exam_id": "student-exam"},
    )
    assert response.status_code == (404 if invalid in {"missing", "archived"} else 409)
    with Session(app.state.engine) as db:
        assert list(db.scalars(select(TeacherExam))) == []


def test_generated_exams_and_archived_assignments_keep_scope(classroom):
    client, manager, q, app, teacher, tid, other, oid, pupils, group = classroom
    generated = client.post(
        "/practice-attempts",
        headers=teacher,
        json={"grade": 5, "subject": "toan", "count": 1, "group_id": group["id"]},
    )
    assert generated.status_code == 201
    eid = generated.json()["exam"]["id"]
    path = f"/classroom/groups/{group['id']}/assignments"
    listed = client.get(path, headers=teacher).json()
    assert [x["exam_id"] for x in listed] == [eid]
    assert listed[0]["in_progress_count"] == 0  # Teacher preview is not pupil progress.
    assert len(client.get("/account/assignments", headers=pupils[0][0]).json()) == 1
    other_group = client.post(
        "/classroom/groups", headers=other, json={"name": "Khác"}
    ).json()
    forbidden = client.post(
        f"/classroom/groups/{other_group['id']}/assignments",
        headers=other,
        json={"exam_id": eid},
    )
    assert forbidden.status_code == 404
    clone = assign(client, teacher, group, eid)
    assert clone["exam_id"] != eid
    assert (
        len(client.get(path, headers=teacher, params={"limit": 1, "offset": 1}).json())
        == 1
    )
    with Session(app.state.engine) as db:
        db.get(Exam, eid).state = "archived"
        db.get(Exam, clone["exam_id"]).state = "archived"
        db.commit()
    assert client.get(path, headers=teacher).json() == []
    assert client.get(path + "/" + eid, headers=teacher).status_code == 404
    assert client.get("/account/assignments", headers=pupils[0][0]).json() == []


def test_clone_resolves_replacements_without_rewriting_original(classroom):
    client, manager, q, app, teacher, tid, other, oid, pupils, group = classroom
    old_id, new_id = "toan5_002", "toan5_002_clean_v2"
    with Session(app.state.engine) as db:
        payload = deepcopy(q)
        payload["id"] = new_id
        db.add(
            ContentQuestion(
                id=new_id,
                payload=payload,
                fingerprint="replacement",
                state="published",
                rights_confirmed=True,
            )
        )
        exam = db.get(Exam, "student-exam")
        exam.payload = {**exam.payload, "question_ids": [old_id, new_id]}
        db.commit()
    cloned = assign(client, teacher, group)
    with Session(app.state.engine) as db:
        assert db.get(Exam, cloned["exam_id"]).payload["question_ids"] == [new_id]
        assert db.get(Exam, "student-exam").payload["question_ids"] == [old_id, new_id]


def test_large_roster_uses_batched_progress_queries(classroom):
    client, manager, q, app, teacher, tid, other, oid, pupils, group = classroom
    eid = assign(client, teacher, group)["exam_id"]
    with Session(app.state.engine) as db:
        stored_hash = db.get(LearningUser, tid).password_hash
        for index in range(40):
            ident = f"batch-student-{index}"
            db.add(
                LearningUser(
                    id=ident,
                    username=f"batch{index:03}",
                    display_name=f"Học viên {index}",
                    role="student",
                    password_hash=stored_hash,
                    manager_id=tid,
                )
            )
            db.add(GroupMember(group_id=group["id"], user_id=ident))
        db.commit()
    reads = []

    def track(connection, cursor, statement, parameters, context, executemany):
        if statement.lstrip().upper().startswith("SELECT"):
            reads.append(statement)

    event.listen(app.state.engine, "before_cursor_execute", track)
    try:
        response = client.get(
            f"/classroom/groups/{group['id']}/assignments/{eid}", headers=teacher
        )
    finally:
        event.remove(app.state.engine, "before_cursor_execute", track)
    assert response.status_code == 200
    assert response.json()["member_count"] == 43
    assert len(response.json()["students"]) == 43
    assert len(reads) <= 8  # A 43-member roster must not trigger per-pupil queries.
