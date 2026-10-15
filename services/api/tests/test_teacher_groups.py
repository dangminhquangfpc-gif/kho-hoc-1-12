"""Role enforcement and teacher privacy across independently owned groups."""

from test_accounts import school  # noqa: F401


def register(client, name, role):
    response = client.post(
        "/auth/register",
        json=dict(
            username=name,
            password="Test-password-123",
            display_name=name,
            role=role,
            mobile=True,
        ),
    )
    assert response.status_code == 201, response.text
    return {"Authorization": "Bearer " + response.json()["token"]}, response.json()[
        "user"
    ]["id"]


def test_teacher_groups_enforce_ownership_and_student_cannot_generate(school):  # noqa: F811
    client, manager, question, app = school
    teacher, tid = register(client, "teacher01", "teacher")
    other, _ = register(client, "teacher02", "teacher")
    student, sid = register(client, "student01", "student")
    payload = dict(grade=5, subject="toan", count=1)
    assert (
        client.post("/practice-attempts", headers=student, json=payload).status_code
        == 403
    )
    client.cookies.clear()
    assert client.post("/practice-attempts", json=payload).status_code == 401
    assert (
        client.post("/practice-attempts", headers=teacher, json=payload).status_code
        == 201
    )
    review = {**payload, "question_ids": [question["id"]]}
    assert (
        client.post("/practice-attempts", headers=student, json=review).status_code
        == 403
    )
    fixed = client.post("/exams/student-exam/attempts", headers=student).json()
    assert (
        client.post(
            f"/attempts/{fixed['id']}/submit",
            headers={**student, "X-Attempt-Token": fixed["token"]},
            json={"answers": {}},
        ).status_code
        == 200
    )
    assert (
        client.post("/practice-attempts", headers=student, json=review).status_code
        == 201
    )
    assert (
        client.post(
            "/classroom/groups", headers=student, json={"name": "Forbidden"}
        ).status_code
        == 403
    )
    group = client.post(
        "/classroom/groups", headers=teacher, json={"name": "Nhóm Toán 6"}
    ).json()
    gid = group["id"]
    assert client.get("/classroom/students", headers=teacher).json() == []
    assert (
        client.get(f"/classroom/students/{sid}/results", headers=teacher).status_code
        == 404
    )
    # An unconnected teacher cannot claim an arbitrary public student account.
    assert (
        client.post(
            f"/classroom/groups/{gid}/members",
            headers=teacher,
            json={"username": "student01"},
        ).status_code
        == 404
    )
    assert (
        client.post(
            "/classroom/groups/join", headers=student, json={"code": group["join_code"]}
        ).status_code
        == 200
    )
    assert (
        client.post(
            "/classroom/groups/join", headers=student, json={"code": group["join_code"]}
        ).status_code
        == 200
    )
    generated = client.post(
        "/practice-attempts", headers=teacher, json={**payload, "group_id": gid}
    )
    assert generated.status_code == 201, generated.text
    exam_id = generated.json()["exam"]["id"]
    assert client.get(f"/exams/{exam_id}", headers=student).status_code == 200
    assert client.get(f"/exams/{exam_id}", headers=other).status_code == 404
    client.cookies.clear()
    assert client.get(f"/exams/{exam_id}").status_code == 404
    assert client.post(f"/exams/{exam_id}/attempts", headers=student).status_code == 201
    assert client.post(f"/exams/{exam_id}/attempts", headers=other).status_code == 404
    listed = client.get(
        "/exams", headers=student, params={"grade": 5, "subject": "toan"}
    ).json()
    assert exam_id in {e["id"] for e in listed}
    other_listed = client.get(
        "/exams", headers=other, params={"grade": 5, "subject": "toan"}
    ).json()
    assert exam_id not in {e["id"] for e in other_listed}
    assert (
        client.post(
            "/practice-attempts", headers=other, json={**payload, "group_id": gid}
        ).status_code
        == 404
    )
    assert len(client.get("/classroom/students", headers=teacher).json()) == 1
    assert (
        client.get(f"/classroom/students/{sid}/results", headers=teacher).status_code
        == 200
    )
    assert (
        client.get(f"/classroom/students/{sid}/results", headers=other).status_code
        == 404
    )
    assert (
        client.post(
            f"/classroom/students/{sid}/reset-password", headers=teacher
        ).status_code
        == 403
    )
    assert (
        client.delete(f"/classroom/students/{sid}", headers=teacher).status_code == 403
    )
    assert client.delete(f"/classroom/groups/{gid}", headers=other).status_code == 404
    assert (
        client.delete(
            f"/classroom/groups/{gid}/members/{sid}", headers=other
        ).status_code
        == 404
    )
    # Private join code and peer IDs never reach student clients.
    sg = client.get("/classroom/groups", headers=student).json()[0]
    assert "join_code" not in sg and sg["student_ids"] == []
    assert (
        client.delete(
            f"/classroom/groups/{gid}/members/{sid}", headers=teacher
        ).status_code
        == 204
    )
    assert (
        client.get(f"/classroom/students/{sid}/results", headers=teacher).status_code
        == 404
    )
    assert client.get(f"/exams/{exam_id}", headers=student).status_code == 404
    created = client.post(
        "/classroom/students/bulk",
        headers=teacher,
        json={
            "students": [
                dict(username="owned001", display_name="Học viên được cấp", grade=6)
            ]
        },
    )
    assert created.status_code == 201
    assert (
        client.post(
            f"/classroom/groups/{gid}/members",
            headers=teacher,
            json={"username": "owned001"},
        ).status_code
        == 200
    )
    assert client.get("/classroom/groups", headers=teacher).json()[0][
        "student_ids"
    ] == [created.json()[0]["id"]]
    assert client.delete(f"/classroom/groups/{gid}", headers=teacher).status_code == 204
    assert len(client.get("/classroom/students", headers=teacher).json()) == 1
    assert client.get("/classroom/groups", headers=teacher).json() == []
