import importlib.util
import json
from pathlib import Path
import plistlib
import pytest
from khohoc.schemas import Question, ExamInput
from khohoc.grading import grade
from khohoc.content_fixes import QUESTION_REPLACEMENTS
from test_accounts import school  # noqa: F401

ROOT = Path(__file__).resolve().parents[3]


def test_removed_statement_has_new_versions_without_changing_old_fixture():
    old = {
        q["id"]: q
        for q in json.loads((ROOT / "data/seeds/questions.json").read_text())[
            "questions"
        ]
    }
    clean = json.loads((ROOT / "data/seeds/clean_questions.json").read_text())[
        "questions"
    ]
    assert len(clean) == 12
    for raw in clean:
        q = Question.model_validate(raw)
        previous = old[q.id.removesuffix("_clean_v2")]
        assert QUESTION_REPLACEMENTS[previous["id"]] == q.id
        assert len(q.options) == len(q.correct_answer) == 1
        assert "Không thể giải bài này" not in q.model_dump_json()
        assert len(previous["options"]) == 2
        assert grade(q, q.correct_answer)["score"] == 1


def test_reference_pairs_are_complete_original_practice_and_not_source_transcriptions():
    mapping = json.loads((ROOT / "data/seeds/source_practice_map.json").read_text())
    exams = {
        e["id"]: ExamInput.model_validate(e)
        for e in json.loads(
            (ROOT / "data/seeds/source_practice_exams.json").read_text()
        )
    }
    bank = {
        q["id"]: Question.model_validate(q)
        for p in (ROOT / "data/seeds").glob("*questions.json")
        for q in json.loads(p.read_text())["questions"]
    }
    docs = {
        d["id"]: d
        for d in json.loads(
            (ROOT / "data/library/external_documents.json").read_text()
        )["documents"]
    }
    assert len(exams) == len(mapping["papers"]) == 991
    assert len(mapping["unavailable"]) == 525
    assert "web_fbf54a18ff2df1a3547334a2" in mapping["papers"]
    for did, pair in mapping["papers"].items():
        e = exams[pair["exam_id"]]
        assert len(e.question_ids) >= 20 and len(set(e.question_ids)) == len(
            e.question_ids
        )
        assert (e.grade, e.subject) == (docs[did]["grade"], docs[did]["subject"])
        assert "Tự biên soạn" in e.title
        assert "không phải bản chuyển nguyên văn" in pair["notice"]
        for qid in e.question_ids:
            assert qid not in QUESTION_REPLACEMENTS
            assert bank[qid].source_type == "original" and bank[qid].type != "essay"
    assert not set(mapping["papers"]) & set(mapping["unavailable"])


def test_account_delete_requires_password_and_preserves_pupils(school):  # noqa: F811
    client, manager, q, app = school
    teacher = client.post(
        "/auth/register",
        json=dict(
            username="delete_teacher",
            password="Teacher-password-123",
            display_name="Giáo viên",
            role="teacher",
            mobile=True,
        ),
    ).json()
    auth = {"Authorization": "Bearer " + teacher["token"]}
    created = client.post(
        "/classroom/students/bulk",
        headers=auth,
        json={
            "students": [
                dict(username="kept_student", display_name="Được giữ lại", grade=5)
            ]
        },
    ).json()[0]
    group = client.post(
        "/classroom/groups", headers=auth, json={"name": "Nhóm xóa"}
    ).json()
    client.post(
        "/classroom/groups/" + group["id"] + "/members",
        headers=auth,
        json={"username": "kept_student"},
    ).raise_for_status()
    exam = client.post(
        "/practice-attempts",
        headers=auth,
        json=dict(grade=5, subject="toan", count=1, group_id=group["id"]),
    ).json()["exam"]["id"]
    assert (
        client.post(
            "/account/delete", headers=auth, json={"password": "Wrong-password-123"}
        ).status_code
        == 400
    )
    assert client.get("/auth/me", headers=auth).status_code == 200
    assert (
        client.post(
            "/account/delete", headers=auth, json={"password": "Teacher-password-123"}
        ).status_code
        == 204
    )
    assert client.get("/auth/me", headers=auth).status_code == 401
    assert (
        client.post(
            "/auth/login",
            json=dict(username="delete_teacher", password="Teacher-password-123"),
        ).status_code
        == 401
    )
    assert client.get("/exams/" + exam, headers=manager).status_code == 404
    pupils = client.get("/classroom/students", headers=manager).json()
    assert created["id"] in {s["id"] for s in pupils}
    assert (
        client.post(
            "/account/delete", headers=manager, json={"password": "Owner-password-123"}
        ).status_code
        == 403
    )


def test_store_preflight_rejects_local_http_and_ios_identity_is_branded():
    spec = importlib.util.spec_from_file_location(
        "store_preflight", ROOT / "scripts/store_preflight.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for u in [
        "http://example.com",
        "https://localhost",
        "https://10.0.0.1",
        "https://127.0.0.1",
        "https://backend.invalid",
        "https://user:password@example.com",
    ]:
        with pytest.raises(ValueError):
            module.secure_public_url(u)
    assert (
        module.secure_public_url("https://learning.example.com/api/")
        == "https://learning.example.com/api"
    )
    info = plistlib.loads((ROOT / "apps/mobile/ios/Runner/Info.plist").read_bytes())
    assert info["CFBundleDisplayName"] == "Tự học 111"
    privacy = plistlib.loads(
        (ROOT / "apps/mobile/ios/Runner/PrivacyInfo.xcprivacy").read_bytes()
    )
    assert privacy["NSPrivacyTracking"] is False
    assert (
        "CA92.1"
        in privacy["NSPrivacyAccessedAPITypes"][0]["NSPrivacyAccessedAPITypeReasons"]
    )


def test_ios_privacy_manifest_is_in_runner_resources_not_test_resources():
    text = (ROOT / "apps/mobile/ios/Runner.xcodeproj/project.pbxproj").read_text()
    resources = text.split("/* Begin PBXResourcesBuildPhase section */", 1)[1].split(
        "/* End PBXResourcesBuildPhase section */", 1
    )[0]
    tests = resources.split("331C807F294A63A400263BE5 /* Resources */ = {", 1)[1].split(
        "};", 1
    )[0]
    runner = resources.split("97C146EC1CF9000F007C117D /* Resources */ = {", 1)[
        1
    ].split("};", 1)[0]
    assert "PrivacyInfo.xcprivacy in Resources" not in tests
    assert "PrivacyInfo.xcprivacy in Resources" in runner
