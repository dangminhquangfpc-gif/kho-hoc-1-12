import importlib.util
import json
from pathlib import Path
import plistlib
import struct
import zipfile
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
        module.secure_public_url("https://learning.school.edu.vn/api/")
        == "https://learning.school.edu.vn/api"
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


@pytest.fixture
def store_preflight():
    spec = importlib.util.spec_from_file_location(
        "store_preflight", ROOT / "scripts/store_preflight.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize(
    "url",
    [
        "https://school.example.com",
        "https://school.example",
        "https://school.test",
        "https://school.edu.vn:0",
        "https://school.edu.vn:99999",
        "https://[::1]",
        "https://school.edu.vn/../api",
        "https://school.edu.vn/\napi",
        "https://bad_host.edu.vn",
        "https://school.edu.vn\\@127.0.0.1",
    ],
)
def test_store_urls_reject_examples_and_malformed_addresses(store_preflight, url):
    with pytest.raises(ValueError):
        store_preflight.secure_public_url(url)


def publisher_metadata():
    return {
        "publisher_name": "Nhà phát hành",
        "support_email": "help@school.edu.vn",
        "privacy_policy_url": "https://school.edu.vn/privacy",
        "account_deletion_url": "https://school.edu.vn/delete-account",
        "content_review_complete": True,
        "child_privacy_review_complete": True,
        "data_safety_review_complete": True,
        "device_testing_complete": True,
        "store_account_verified": True,
    }


def test_publisher_reviews_require_real_booleans_and_valid_contact(store_preflight):
    config = publisher_metadata()
    store_preflight.validate_publisher(config)
    for field in (
        "content_review_complete",
        "child_privacy_review_complete",
        "data_safety_review_complete",
        "device_testing_complete",
        "store_account_verified",
    ):
        for value in (False, "false", "true", 1, None):
            with pytest.raises(ValueError, match=field):
                store_preflight.validate_publisher({**config, field: value})
    for value in (
        "invalid",
        "a@localhost",
        "support@example.com",
        "Name <a@school.edu.vn>",
    ):
        with pytest.raises(ValueError):
            store_preflight.validate_publisher({**config, "support_email": value})


def test_store_probe_refuses_private_dns_before_opening_url(
    store_preflight, monkeypatch
):
    monkeypatch.setattr(
        store_preflight.socket,
        "getaddrinfo",
        lambda *a, **kw: [(2, 1, 6, "", ("10.20.30.40", 443))],
    )
    monkeypatch.setattr(
        store_preflight.urllib.request,
        "build_opener",
        lambda *a: pytest.fail("network opened"),
    )
    with pytest.raises(ValueError, match="DNS"):
        store_preflight.check_endpoint(
            "https://school.edu.vn/health", json_response=True
        )
    with pytest.raises(ValueError, match="chuyển hướng"):
        store_preflight.NoRedirect().redirect_request(
            None, None, 302, "", {}, "http://localhost"
        )


def bundle_fixture(path, *, elf_alignment=16_384, bundle_alignment=2, signed=False):
    # ELF64 with one PT_LOAD; sufficient to exercise alignment rejection, not an executable.
    elf = bytearray(120)
    elf[:6] = b"\x7fELF\x02\x01"
    struct.pack_into("<Q", elf, 32, 64)
    struct.pack_into("<HH", elf, 54, 56, 1)
    struct.pack_into("<I", elf, 64, 1)
    struct.pack_into("<Q", elf, 112, elf_alignment)
    # BundleConfig.optimizations.uncompress_native_libraries {enabled:true, alignment:16K}
    native = bytes((8, 1, 16, bundle_alignment))
    optimizations = bytes((18, len(native))) + native
    config = bytes((18, len(optimizations))) + optimizations
    with zipfile.ZipFile(path, "w") as bundle:
        bundle.writestr("BundleConfig.pb", config)
        bundle.writestr("base/lib/arm64-v8a/libapp.so", elf)
        if signed:
            bundle.writestr("META-INF/UPLOAD.RSA", b"synthetic-signature-marker")
    return path


def test_engineering_bundle_audit_checks_16kb_and_signature(store_preflight, tmp_path):
    path = tmp_path / "engineering.aab"
    report = store_preflight.inspect_android_bundle(
        bundle_fixture(path), require_unsigned=True
    )
    assert report["signed"] is False
    assert report["bundle_page_alignment"] == 16_384
    assert report["native_libraries"][0]["minimum_load_alignment"] == 16_384
    assert len(report["sha256"]) == 64
    assert report["device_16kb_runtime_tested"] is False
    with pytest.raises(ValueError, match="PT_LOAD"):
        store_preflight.inspect_android_bundle(bundle_fixture(path, elf_alignment=4096))
    with pytest.raises(ValueError, match="ZIP 16 KB"):
        store_preflight.inspect_android_bundle(bundle_fixture(path, bundle_alignment=1))
    with pytest.raises(ValueError, match="chữ ký"):
        store_preflight.inspect_android_bundle(
            bundle_fixture(path, signed=True), require_unsigned=True
        )


def test_bundle_audit_rejects_truncated_elf_and_proto(store_preflight, tmp_path):
    path = tmp_path / "truncated.aab"
    with zipfile.ZipFile(path, "w") as bundle:
        bundle.writestr("BundleConfig.pb", b"\x12\x7f")
        bundle.writestr("base/lib/arm64-v8a/libapp.so", b"bad")
    with pytest.raises(ValueError, match="cắt ngắn"):
        store_preflight.inspect_android_bundle(path)
    bundle_fixture(path)
    with zipfile.ZipFile(path, "a") as bundle:
        bundle.writestr("base/lib/x86_64/libbad.so", b"bad")
    with pytest.raises(ValueError, match="ELF"):
        store_preflight.inspect_android_bundle(path)


def test_engineering_inspect_needs_no_credentials_or_backend(
    store_preflight, tmp_path, monkeypatch, capsys
):
    path = bundle_fixture(tmp_path / "engineering.aab")
    report = tmp_path / "readiness.json"
    monkeypatch.setattr(
        store_preflight,
        "check_endpoint",
        lambda *a, **kw: pytest.fail("backend contacted"),
    )
    assert (
        store_preflight.main(
            [
                "--platform",
                "android",
                "--engineering",
                "--inspect-aab",
                str(path),
                "--report",
                str(report),
            ]
        )
        == 0
    )
    result = json.loads(report.read_text())
    assert result["engineering"] is True and result["store_ready"] is False
    assert result["bundle"]["signed"] is False
    assert "AAB engineering" in capsys.readouterr().out


def test_engineering_build_forces_unsigned_even_with_signing_environment(
    store_preflight, tmp_path, monkeypatch
):
    root = tmp_path / "checkout"
    aab = root / "apps/mobile/build/app/outputs/bundle/release/app-release.aab"
    aab.parent.mkdir(parents=True)
    bundle_fixture(aab)
    calls = []
    monkeypatch.setattr(store_preflight, "ROOT", root)
    monkeypatch.setenv("ORG_GRADLE_PROJECT_tuhocRequireUploadSigning", "true")
    monkeypatch.setattr(
        store_preflight.subprocess, "run", lambda *a, **kw: calls.append((a, kw))
    )
    store_preflight.main(["--platform", "android", "--engineering", "--build"])
    assert calls[0][0][0] == ["flutter", "pub", "get", "--enforce-lockfile"]
    args, kwargs = calls[1]
    assert args[0][:3] == ["flutter", "build", "appbundle"]
    assert "--no-pub" not in args[0]
    assert kwargs["env"]["ORG_GRADLE_PROJECT_tuhocEngineering"] == "true"
    assert kwargs["env"]["ORG_GRADLE_PROJECT_tuhocRequireUploadSigning"] == "false"


def test_store_checks_health_and_readiness_without_accepting_shared_mode(
    store_preflight, tmp_path, monkeypatch
):
    path = tmp_path / "publisher.json"
    path.write_text(json.dumps(publisher_metadata()))
    urls = []

    def endpoint(url, **kwargs):
        urls.append(url)
        if url.endswith("/ready"):
            return {"status": "ok", "mode": "shared"}
        return {"status": "ok", "mode": "production"}

    monkeypatch.setattr(store_preflight, "check_endpoint", endpoint)
    with pytest.raises(ValueError, match="ready"):
        store_preflight.main(
            [
                "--platform",
                "android",
                "--api-base-url",
                "https://school.edu.vn/api",
                "--publisher-config",
                str(path),
            ]
        )
    assert urls == [
        "https://school.edu.vn/privacy",
        "https://school.edu.vn/delete-account",
        "https://school.edu.vn/api/health",
        "https://school.edu.vn/api/ready",
    ]
