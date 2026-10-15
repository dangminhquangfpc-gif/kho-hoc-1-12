"""Content-only initialization, also exercised on disposable real PostgreSQL."""

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import uuid

import pytest
from sqlalchemy import func, select, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from khohoc.app import fingerprint
from khohoc.content_transfer import (
    canonical_bytes,
    digest,
    export_published_content,
    import_published_content,
    validate_archive,
)
from khohoc.content_fixes import QUESTION_REPLACEMENTS
from khohoc.database import make_engine, migrate
from khohoc.library import (
    DocumentInput,
    LibraryDocument,
    fingerprint as doc_fingerprint,
)
from khohoc.models import (
    Attempt,
    AuditEvent,
    ContentQuestion,
    Exam,
    LearningSession,
    LearningUser,
    TeacherExam,
)
from khohoc.question_versions import QuestionRevision
from khohoc.schemas import ExamInput, Question

ROOT = Path(__file__).resolve().parents[3]
PRIVATE = "PRIVATE_STUDENT_SECRET_MUST_NOT_BE_EXPORTED"


@pytest.fixture(params=["sqlite", "postgresql"])
def content_target(request, tmp_path):
    admin = None
    if request.param == "postgresql":
        connection_url = os.environ.get("KHOHOC_TEST_POSTGRES_URL")
        if not connection_url:
            pytest.skip("Run with the disposable PostgreSQL test service")
        admin = make_engine(connection_url)
        schema = "content_" + uuid.uuid4().hex
        with admin.begin() as connection:
            connection.execute(text(f"CREATE SCHEMA {schema}"))
        connection_url = (
            make_url(connection_url)
            .update_query_dict({"options": "-csearch_path=" + schema})
            .render_as_string(hide_password=False)
        )
    else:
        connection_url = "sqlite:///" + str(tmp_path / "destination.db")
    engine = make_engine(connection_url)
    migrate(engine)
    try:
        yield engine
    finally:
        engine.dispose()
        if admin:
            with admin.begin() as connection:
                connection.execute(text(f"DROP SCHEMA {schema} CASCADE"))
            admin.dispose()


@pytest.fixture
def public_archive(tmp_path):
    source_path = tmp_path / "contains-private-state.db"
    engine = make_engine("sqlite:///" + str(source_path))
    migrate(engine)
    q = Question.model_validate(
        json.loads((ROOT / "data/seeds/practice_questions.json").read_text())[
            "questions"
        ][0]
    )
    exam = ExamInput.model_validate(
        dict(
            id="public-exam",
            title="Đề tự luyện công khai",
            grade=q.grade,
            subject=q.subject,
            question_ids=[q.id],
            duration_minutes=15,
        )
    ).model_dump(mode="json")
    doc = DocumentInput.model_validate(
        dict(
            id="public-guide",
            title="Hướng dẫn tự luyện",
            grade=q.grade,
            subject=q.subject,
            topic=q.topic,
            summary="Ghi chú tự biên soạn.",
            author="Nhóm nội dung",
            source_name="Nội dung ứng dụng",
            source_type="original",
            license="original_content",
            rights_evidence="Tự biên soạn nội dung luyện tập dùng trong thử nghiệm.",
            distribution_allowed=True,
            sections=[
                {"heading": "Lời giải", "text": "Trình bày từng bước rồi ghi đáp số."}
            ],
        )
    )
    with Session(engine) as db:
        db.add(
            ContentQuestion(
                id=q.id,
                payload=q.model_dump(mode="json"),
                fingerprint=fingerprint(q),
                state="published",
                rights_confirmed=True,
                version=3,
            )
        )
        for ident, state, rights in [
            ("unapproved", "draft", True),
            ("no-rights", "published", False),
        ]:
            payload = q.model_dump(mode="json") | {"id": ident, "question": ident}
            db.add(
                ContentQuestion(
                    id=ident,
                    payload=payload,
                    fingerprint=fingerprint(Question.model_validate(payload)),
                    state=state,
                    rights_confirmed=rights,
                )
            )
        db.add(Exam(id=exam["id"], payload=exam, state="published"))
        private_exam = exam | {"id": "private-exam", "title": PRIVATE}
        db.add(Exam(id="private-exam", payload=private_exam, state="published"))
        db.add(TeacherExam(exam_id="private-exam", owner_id=PRIVATE, group_id=PRIVATE))
        db.add(
            Exam(
                id="custom_generated",
                payload=exam | {"id": "custom_generated", "title": PRIVATE},
                state="published",
            )
        )
        db.add(
            LibraryDocument(
                id=doc.id,
                payload=doc.model_dump(mode="json"),
                fingerprint=doc_fingerprint(doc),
                state="published",
                rights_confirmed=True,
                version=2,
                updated_at=datetime(2026, 10, 15, tzinfo=timezone.utc),
            )
        )
        db.add(
            LearningUser(
                id="private-student",
                username=PRIVATE,
                display_name=PRIVATE,
                password_hash=PRIVATE,
                role="student",
            )
        )
        db.add(
            LearningSession(
                token_hash=PRIVATE,
                user_id="private-student",
                expires_at=datetime.now(timezone.utc),
            )
        )
        db.add(
            Attempt(
                id="private-attempt", token_hash=PRIVATE, snapshot={"private": PRIVATE}
            )
        )
        db.add(AuditEvent(actor=PRIVATE, action="private", target=PRIVATE))
        db.flush()
        db.add(
            QuestionRevision(
                question_id=q.id,
                version=3,
                payload=q.model_dump(mode="json"),
                operation="edit",
                actor=PRIVATE,
                note=PRIVATE,
            )
        )
        db.commit()
    archive_path = tmp_path / "public-content.json"
    result = export_published_content(source_path, archive_path)
    try:
        yield archive_path, result, engine, source_path
    finally:
        engine.dispose()


def count(engine, model):
    with Session(engine) as db:
        return db.scalar(select(func.count()).select_from(model))


def test_export_whitelists_only_published_content_and_never_private_state(
    public_archive,
):
    path, result, engine, source_path = public_archive
    payload = path.read_bytes()
    assert PRIVATE.encode() not in payload
    assert str(source_path).encode() not in payload
    assert result["counts"] == {"questions": 1, "exams": 1, "documents": 1}
    assert digest(payload) == result["archive_sha256"]
    assert count(engine, LearningUser) == 1  # Read-only source remains untouched.
    assert count(engine, LearningSession) == 1
    with pytest.raises(FileExistsError):
        export_published_content(source_path, path)


def test_dry_run_apply_and_exact_repeat_preserve_existing_learner_state(
    content_target, public_archive
):
    path, exported, _, _ = public_archive
    with Session(content_target) as db:
        db.add(
            LearningUser(
                id="existing-student",
                username="existing-student",
                display_name="Học viên",
                password_hash="unchanged-hash",
                role="student",
            )
        )
        db.add(
            Attempt(
                id="existing-result",
                token_hash="unchanged-token",
                snapshot={"exam": "unchanged"},
                answers={"q": ["answer"]},
                result={"score": "5"},
            )
        )
        db.commit()
    dry_run = import_published_content(content_target, path)
    assert dry_run["mode"] == "dry-run"
    assert dry_run["inserted"] == exported["counts"]
    assert count(content_target, ContentQuestion) == 0
    with pytest.raises(ValueError, match="exact reviewed"):
        import_published_content(content_target, path, apply=True)
    with pytest.raises(ValueError, match="exact reviewed"):
        import_published_content(
            content_target, path, apply=True, expected_sha256="0" * 64
        )
    applied = import_published_content(
        content_target, path, apply=True, expected_sha256=exported["archive_sha256"]
    )
    assert applied["inserted"] == exported["counts"]
    assert (
        import_published_content(
            content_target, path, apply=True, expected_sha256=exported["archive_sha256"]
        )["skipped"]
        == exported["counts"]
    )
    with Session(content_target) as db:
        student = db.get(LearningUser, "existing-student")
        assert student.password_hash == "unchanged-hash"
        result = db.get(Attempt, "existing-result")
        assert (result.token_hash, result.snapshot, result.answers, result.result) == (
            "unchanged-token",
            {"exam": "unchanged"},
            {"q": ["answer"]},
            {"score": "5"},
        )
        revision = db.scalar(select(QuestionRevision))
        assert revision.version == 3
        assert revision.actor == "content-transfer"
        assert db.get(ContentQuestion, revision.question_id).payload == revision.payload
        assert db.scalar(select(func.count()).select_from(LearningUser)) == 1
        assert db.scalar(select(func.count()).select_from(LearningSession)) == 0
        assert db.scalar(select(func.count()).select_from(AuditEvent)) == 0


def test_late_conflict_leaves_all_pending_content_unwritten(
    content_target, public_archive
):
    path, exported, _, _ = public_archive
    archive = json.loads(path.read_bytes())
    original = archive["content"]["exams"][0]["payload"]
    with Session(content_target) as db:
        db.add(
            Exam(
                id=original["id"],
                payload=original | {"title": "Đã được sửa tại máy chủ"},
                state="published",
            )
        )
        db.commit()
    for apply in [False, True]:
        with pytest.raises(ValueError, match="Destination content differs"):
            import_published_content(
                content_target,
                path,
                apply=apply,
                expected_sha256=exported["archive_sha256"],
            )
        assert count(content_target, ContentQuestion) == 0
        assert count(content_target, QuestionRevision) == 0
        assert count(content_target, LibraryDocument) == 0


def test_changed_approved_question_is_never_overwritten(content_target, public_archive):
    path, exported, _, _ = public_archive
    import_published_content(
        content_target, path, apply=True, expected_sha256=exported["archive_sha256"]
    )
    with Session(content_target) as db:
        question = db.scalar(select(ContentQuestion))
        # An answer-only change retains the stem fingerprint: payload/version checks still catch it.
        question.payload = question.payload | {"explanation": "Lời giải đã hiệu chỉnh"}
        db.commit()
    with pytest.raises(ValueError, match="Destination content differs"):
        import_published_content(
            content_target, path, apply=True, expected_sha256=exported["archive_sha256"]
        )
    with Session(content_target) as db:
        assert (
            db.scalar(select(ContentQuestion)).payload["explanation"]
            == "Lời giải đã hiệu chỉnh"
        )


def test_import_joins_an_existing_owner_transaction_and_its_rollback(
    content_target, public_archive
):
    path, exported, _, _ = public_archive
    with pytest.raises(RuntimeError, match="Abort setup"):
        with content_target.begin() as connection:
            connection.execute(
                LearningUser.__table__.insert().values(
                    id="owner-transaction",
                    username="owner-transaction",
                    display_name="Quản lý",
                    password_hash="unchanged",
                    role="manager",
                )
            )
            import_published_content(
                connection, path
            )  # Does not roll back the caller's work.
            assert (
                connection.execute(
                    select(func.count()).select_from(LearningUser)
                ).scalar_one()
                == 1
            )
            import_published_content(
                connection, path, apply=True, expected_sha256=exported["archive_sha256"]
            )
            assert (
                connection.execute(
                    select(func.count()).select_from(ContentQuestion)
                ).scalar_one()
                == 1
            )
            raise RuntimeError("Abort setup")
    assert count(content_target, LearningUser) == 0
    assert count(content_target, ContentQuestion) == 0
    assert count(content_target, QuestionRevision) == 0


@pytest.mark.parametrize("conflict", ["draft", "fingerprint", "teacher-exam"])
def test_destination_approval_or_private_content_conflicts_are_never_bypassed(
    content_target, public_archive, conflict
):
    path, exported, _, _ = public_archive
    archive = json.loads(path.read_bytes())
    question = archive["content"]["questions"][0]
    payload = question["payload"]
    with Session(content_target) as db:
        if conflict in {"draft", "fingerprint"}:
            ident = payload["id"] if conflict == "draft" else "another-question-id"
            db.add(
                ContentQuestion(
                    id=ident,
                    payload=payload | {"id": ident},
                    fingerprint=fingerprint(Question.model_validate(payload)),
                    state="draft" if conflict == "draft" else "published",
                    rights_confirmed=conflict != "draft",
                    version=question["version"],
                )
            )
        else:
            exam = archive["content"]["exams"][0]["payload"]
            db.add(Exam(id=exam["id"], payload=exam, state="published"))
            db.add(
                TeacherExam(
                    exam_id=exam["id"], owner_id="teacher", group_id="private-group"
                )
            )
        db.commit()
    with pytest.raises(ValueError, match="Destination"):
        import_published_content(
            content_target, path, apply=True, expected_sha256=exported["archive_sha256"]
        )
    assert count(content_target, LibraryDocument) == 0
    assert count(content_target, QuestionRevision) == 0


def test_export_resolves_withdrawn_question_references_like_public_api(
    public_archive, tmp_path
):
    _, _, source, source_path = public_archive
    old_id, replacement_id = next(iter(QUESTION_REPLACEMENTS.items()))
    with Session(source) as db:
        original = db.scalar(
            select(ContentQuestion).where(
                ContentQuestion.state == "published",
                ContentQuestion.rights_confirmed.is_(True),
            )
        )
        for ident in [old_id, replacement_id]:
            payload = original.payload | {"id": ident, "question": "Câu hỏi: " + ident}
            db.add(
                ContentQuestion(
                    id=ident,
                    payload=payload,
                    fingerprint=fingerprint(Question.model_validate(payload)),
                    state="published",
                    rights_confirmed=True,
                )
            )
        exam = db.get(Exam, "public-exam")
        exam.payload = exam.payload | {"question_ids": [old_id]}
        db.commit()
    exported = tmp_path / "resolved-content.json"
    export_published_content(source_path, exported)
    archive = json.loads(exported.read_bytes())
    ids = {row["payload"]["id"] for row in archive["content"]["questions"]}
    assert old_id not in ids
    assert replacement_id in ids
    assert archive["content"]["exams"][0]["payload"]["question_ids"] == [replacement_id]


@pytest.mark.parametrize(
    "mutation",
    ["private-table", "private-field", "wrong-question", "checksum", "duplicate-json"],
)
def test_archive_rejects_tampering_even_with_recomputed_content_hash(
    public_archive, mutation
):
    path, _, _, _ = public_archive
    archive = json.loads(path.read_bytes())
    if mutation == "private-table":
        archive["content"]["learning_users"] = [{"password_hash": PRIVATE}]
    elif mutation == "private-field":
        archive["content"]["questions"][0]["payload"]["password_hash"] = PRIVATE
    elif mutation == "wrong-question":
        archive["content"]["exams"][0]["payload"]["question_ids"] = ["missing-question"]
    elif mutation == "checksum":
        archive["content"]["questions"][0]["payload"]["explanation"] = "Altered"
    if mutation != "checksum":
        archive["manifest"]["content_sha256"] = digest(
            canonical_bytes(archive["content"])
        )
    payload = canonical_bytes(archive)
    if mutation == "duplicate-json":
        payload = payload.replace(
            b'"schema_version":1', b'"schema_version":1,"schema_version":1'
        )
    with pytest.raises(ValueError):
        validate_archive(payload)


def test_receiver_requires_identical_safe_public_pdf_before_any_import(
    content_target, public_archive, tmp_path
):
    path, exported, source, source_path = public_archive
    files = tmp_path / "pdfs"
    files.mkdir()
    pdf = files / "notes.pdf"
    pdf.write_bytes(b"%PDF-1.4\n% public test document\n%%EOF\n")
    with Session(source) as db:
        doc = db.get(LibraryDocument, "public-guide")
        doc.payload = doc.payload | {"pdf_filename": pdf.name, "download_allowed": True}
        db.commit()
    pdf_archive = tmp_path / "with-public-pdf.json"
    export_published_content(source_path, pdf_archive, library_root=files)
    pdf.write_bytes(b"%PDF-1.4\n% unexpected different version\n%%EOF\n")
    with pytest.raises(ValueError, match="PDF checksum mismatch"):
        import_published_content(content_target, pdf_archive, library_root=files)
    assert count(content_target, ContentQuestion) == 0
    pdf.unlink()
    with pytest.raises(ValueError, match="PDF unavailable"):
        import_published_content(content_target, pdf_archive, library_root=files)
