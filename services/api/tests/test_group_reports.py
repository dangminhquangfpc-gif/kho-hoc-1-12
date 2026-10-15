"""CSV reports use server results and current membership, without cross-teacher leaks."""

import csv
import io

from sqlalchemy.orm import Session
from test_accounts import school  # noqa: F401
from test_teacher_groups import register
from khohoc.models import LearningRecord, LearningUser


def test_group_csv_scores_membership_and_privacy(school):  # noqa: F811
    client, manager, question, app = school
    teacher, tid = register(client, "report_teacher", "teacher")
    other, _ = register(client, "other_teacher", "teacher")
    student, sid = register(client, "report_student", "student")
    second, second_id = register(client, "empty_student", "student")
    unrelated, unrelated_id = register(client, "unrelated_student", "student")
    group = client.post(
        "/classroom/groups", headers=teacher, json={"name": '=HYPERLINK("bad")'}
    ).json()
    gid = group["id"]
    url = f"/classroom/groups/{gid}/results.csv"
    for auth in (student, second):
        assert (
            client.post(
                "/classroom/groups/join",
                headers=auth,
                json={"code": group["join_code"]},
            ).status_code
            == 200
        )
    with Session(app.state.engine) as db:
        db.get(LearningUser, sid).display_name = "+SUM(1,2)\nHọc viên"
        for aid, uid, score, maximum in [
            ("a", sid, 1, 2),
            ("b", sid, 9, 10),
            ("c", unrelated_id, 10, 10),
        ]:
            db.add(
                LearningRecord(
                    attempt_id=aid,
                    user_id=uid,
                    payload={
                        "exam": {"title": "Đề"},
                        "result": {"score": score, "max_score": maximum},
                    },
                )
            )
        db.commit()
    response = client.get(url, headers=teacher)
    assert response.status_code == 200
    assert response.content.startswith(b"\xef\xbb\xbf")
    assert response.headers["cache-control"] == "no-store"
    assert "attachment" in response.headers["content-disposition"]
    rows = list(csv.reader(io.StringIO(response.content.decode("utf-8-sig"))))
    assert len(rows) == 3
    assert rows[0][2] == "Họ và tên"
    empty, completed = rows[1:]
    assert empty[1] == "empty_student" and empty[4:6] == ["0", ""]
    assert completed[1] == "report_student" and completed[4:6] == ["2", "70.0"]
    assert completed[0].startswith("'=") and completed[2].startswith("'+")
    assert completed[6].endswith("Z")
    assert "unrelated_student" not in response.text
    for auth, expected in [(other, 404), (manager, 404), (student, 403)]:
        assert client.get(url, headers=auth).status_code == expected
    assert (
        client.get("/classroom/groups/missing/results.csv", headers=teacher).status_code
        == 404
    )
    client.cookies.clear()
    assert client.get(url).status_code == 401
    assert (
        client.delete(
            f"/classroom/groups/{gid}/members/{sid}", headers=teacher
        ).status_code
        == 204
    )
    assert "report_student" not in client.get(url, headers=teacher).text
    assert (
        client.delete(
            f"/classroom/groups/{gid}/members/{second_id}", headers=teacher
        ).status_code
        == 204
    )
    assert (
        len(
            list(
                csv.reader(
                    io.StringIO(
                        client.get(url, headers=teacher).content.decode("utf-8-sig")
                    )
                )
            )
        )
        == 1
    )
