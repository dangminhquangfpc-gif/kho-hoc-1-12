import hashlib
import secrets
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import create_engine, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .catalog import subjects_for_grade
from .grading import grade, normalize
from .models import (
    Attempt,
    AuditEvent,
    Base,
    ContentQuestion,
    Exam,
    AccountAttempt,
    LearningRecord,
)
from .accounts import AccountService, ensure_manager
from .content_fixes import QUESTION_REPLACEMENTS
from .schemas import ExamInput, ImportBatch, Question, Submission
from .practice import create_practice_router, topic_name, canonical_topic


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="KHOHOC_")
    database_url: str = "sqlite:////workspace/state/khohoc.db"
    admin_token: str = ""
    mode: str = "development"
    manager_credentials_file: str | None = None
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ]


def public_question(payload: dict) -> dict:
    return {
        k: payload[k]
        for k in (
            "id",
            "grade",
            "subject",
            "topic",
            "type",
            "question",
            "options",
            "max_score",
        )
    } | {
        "topic": canonical_topic(
            payload["grade"], payload["subject"], payload["topic"]
        ),
        "topic_name": topic_name(
            payload["grade"], payload["subject"], payload["topic"]
        ),
    }


def fingerprint(question: Question) -> str:
    return hashlib.sha256(normalize(question.question).encode()).hexdigest()


def create_app(settings: Settings | None = None) -> FastAPI:
    config = settings or Settings()
    if config.mode != "development":
        raise RuntimeError(
            "Production adapter/JWT authentication are not implemented; refusing to start"
        )
    if config.database_url.startswith("sqlite:////"):
        Path(config.database_url.removeprefix("sqlite:///")).parent.mkdir(
            parents=True, exist_ok=True
        )
    engine = create_engine(
        config.database_url,
        connect_args={"check_same_thread": False}
        if config.database_url.startswith("sqlite")
        else {},
    )

    @asynccontextmanager
    async def lifespan(app):
        Base.metadata.create_all(engine)
        ensure_manager(engine, config.manager_credentials_file)
        yield
        engine.dispose()

    app = FastAPI(title="Kho Học 1–12 — local MVP", lifespan=lifespan)
    app.state.engine = engine
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_origins,
        allow_methods=["GET", "POST", "DELETE"],
        allow_headers=["Content-Type", "Authorization", "X-Attempt-Token"],
    )

    # Reject oversized bodies before JSON parsing. Public deployment also needs gateway rate limiting.
    @app.middleware("http")
    async def limits(request: Request, call_next):
        from fastapi.responses import JSONResponse

        if request.method in ("POST", "PUT", "PATCH"):
            body = bytearray()
            async for chunk in request.stream():
                body.extend(chunk)
                if len(body) > 2_000_000:
                    return JSONResponse(
                        {"detail": "Request too large"}, status_code=413
                    )
            request._body = bytes(body)
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        return response

    def db():
        with Session(engine) as session:
            yield session

    accounts = AccountService(db)
    app.include_router(accounts.router)

    def admin(authorization: str = Header(default="")):
        if not config.admin_token or not secrets.compare_digest(
            authorization, "Bearer " + config.admin_token
        ):
            raise HTTPException(403, "Admin authorization required")
        return "local-admin"

    def audit(session, action, target):
        session.add(AuditEvent(actor="local-admin", action=action, target=target))

    def owned_attempt(session, attempt_id, token):
        attempt = session.get(Attempt, attempt_id)
        if not attempt or not secrets.compare_digest(
            attempt.token_hash, hashlib.sha256(token.encode()).hexdigest()
        ):
            raise HTTPException(404, "Attempt not found")
        return attempt

    def published_exam(session, exam_id):
        exam = session.get(Exam, exam_id)
        if not exam or exam.state != "published":
            raise HTTPException(404, "Exam not found")
        questions = [
            session.get(ContentQuestion, QUESTION_REPLACEMENTS.get(qid, qid))
            for qid in exam.payload["question_ids"]
        ]
        if any(
            q is None or q.state != "published" or not q.rights_confirmed
            for q in questions
        ):
            raise HTTPException(404, "Exam unavailable")
        return exam, questions

    from .question_versions import create_question_versions_router

    app.include_router(
        create_question_versions_router(
            db=db, admin=admin, audit=audit, fingerprint=fingerprint
        )
    )

    from .library import create_library_router, search_key

    app.include_router(create_library_router(db, admin, audit))

    @app.get("/health")
    def health(session: Session = Depends(db)):
        session.execute(select(1))
        return {"status": "ok", "mode": config.mode}

    @app.get("/grades")
    def grades():
        return [{"id": n, "name": f"Lớp {n}"} for n in range(1, 13)]

    @app.get("/grades/{grade_id}/subjects")
    def subjects(grade_id: int):
        if not 1 <= grade_id <= 12:
            raise HTTPException(404, "Grade not found")
        return subjects_for_grade(grade_id)

    @app.get("/curriculum")
    def curriculum(
        grade: int = Query(ge=1, le=12),
        subject: str = "toan",
        session: Session = Depends(db),
    ):
        import json
        from .library import LibraryDocument, is_textbook_lesson

        path = Path(__file__).resolve().parents[3] / "data/seeds/textbook_units.json"
        books = json.loads(path.read_text(encoding="utf-8"))["books"]
        book = next(
            (
                book
                for book in books
                if book["grade"] == grade and book["subject"] == subject
            ),
            None,
        )
        if not book or not book.get("units"):
            return {
                "status": "index_not_verified",
                "units": [],
                "unit_count": None,
                "authored_count": 0,
            }
        authored = {
            row.payload.get("curriculum_unit_id"): row.id
            for row in session.scalars(
                select(LibraryDocument).where(
                    LibraryDocument.state == "published",
                    LibraryDocument.rights_confirmed.is_(True),
                )
            )
            if row.payload["grade"] == grade
            and row.payload["subject"] == subject
            and is_textbook_lesson(row.payload)
        }
        units = [
            unit
            | {
                "document_id": authored.get(unit["id"]),
                "content_status": "authored_pending_review"
                if unit["id"] in authored
                else "missing",
            }
            for unit in book["units"]
        ]
        return {
            "status": "secondary_index_pending_publisher_review",
            "source_url": book["source_url"],
            "edition": book["edition"],
            "unit_count": len(units),
            "authored_count": sum(unit["document_id"] is not None for unit in units),
            "units": units,
        }

    @app.get("/coverage")
    def coverage(grade: int = Query(ge=1, le=12), session: Session = Depends(db)):
        from .library import LibraryDocument

        questions = [
            row.payload
            for row in session.scalars(
                select(ContentQuestion).where(
                    ContentQuestion.state == "published",
                    ContentQuestion.rights_confirmed.is_(True),
                )
            )
            if row.payload["grade"] == grade
        ]
        exams = [
            row.payload
            for row in session.scalars(select(Exam).where(Exam.state == "published"))
            if row.payload["grade"] == grade
        ]
        documents = [
            row.payload
            for row in session.scalars(
                select(LibraryDocument).where(
                    LibraryDocument.state == "published",
                    LibraryDocument.rights_confirmed.is_(True),
                )
            )
            if row.payload["grade"] == grade
        ]
        return [
            {
                "subject": subject["id"],
                "name": subject["name"],
                "question_count": sum(q["subject"] == subject["id"] for q in questions),
                "exam_count": sum(e["subject"] == subject["id"] for e in exams),
                "document_count": sum(d["subject"] == subject["id"] for d in documents),
                "external_document_count": sum(
                    d["subject"] == subject["id"] and d["source_type"] == "link_only"
                    for d in documents
                ),
                "external_paper_count": sum(
                    d["subject"] == subject["id"]
                    and d["source_type"] == "link_only"
                    and d.get("resource_scope") == "single_paper"
                    for d in documents
                ),
                "topic_count": len(
                    {q["topic"] for q in questions if q["subject"] == subject["id"]}
                ),
            }
            for subject in subjects_for_grade(grade)
        ]

    @app.get("/exams")
    def exams(
        grade: int = Query(ge=1, le=12),
        subject: str = "toan",
        search: str = Query(default="", max_length=100),
        session: Session = Depends(db),
    ):
        output = []
        for exam in session.scalars(select(Exam).where(Exam.state == "published")):
            if (
                exam.payload["grade"] == grade
                and exam.payload["subject"] == subject
                and search_key(search) in search_key(exam.payload["title"])
            ):
                try:
                    published_exam(session, exam.id)
                except HTTPException:
                    continue
                output.append(
                    {k: v for k, v in exam.payload.items() if k != "question_ids"}
                    | {"question_count": len(exam.payload["question_ids"])}
                )
        return output

    @app.get("/exams/{exam_id}")
    def exam_detail(exam_id: str, session: Session = Depends(db)):
        exam, questions = published_exam(session, exam_id)
        return {k: v for k, v in exam.payload.items() if k != "question_ids"} | {
            "questions": [public_question(q.payload) for q in questions]
        }

    def create_attempt(
        session, exam_payload, questions, practice_filter=None, user_id=None
    ):
        exam_payload = {**exam_payload, "question_ids": [q["id"] for q in questions]}
        token = secrets.token_urlsafe(32)
        attempt = Attempt(
            id=str(uuid.uuid4()),
            token_hash=hashlib.sha256(token.encode()).hexdigest(),
            snapshot={"exam": exam_payload, "questions": questions},
        )
        if practice_filter is not None:
            attempt.snapshot["practice_filter"] = practice_filter
        session.add(attempt)
        if user_id:
            session.add(AccountAttempt(attempt_id=attempt.id, user_id=user_id))
        session.commit()
        response = {
            "id": attempt.id,
            "token": token,
            "exam": {k: v for k, v in exam_payload.items() if k != "question_ids"},
            "questions": [public_question(q) for q in questions],
            "created_at": attempt.created_at.isoformat()
            + ("Z" if attempt.created_at.tzinfo is None else ""),
        }
        if practice_filter is not None:
            response["practice_filter"] = practice_filter
        if user_id:
            response["account_id"] = user_id
        return response

    app.include_router(
        create_practice_router(db=db, create_attempt=create_attempt, accounts=accounts)
    )

    @app.post("/exams/{exam_id}/attempts", status_code=201)
    def start(exam_id: str, request: Request, session: Session = Depends(db)):
        user = accounts.optional_user(request, session)
        exam, questions = published_exam(session, exam_id)
        return create_attempt(
            session,
            exam.payload,
            [q.payload for q in questions],
            user_id=user.id if user else None,
        )

    @app.post("/attempts/{attempt_id}/submit")
    def submit(
        attempt_id: str,
        body: Submission,
        request: Request,
        x_attempt_token: str = Header(default=""),
        session: Session = Depends(db),
    ):
        attempt = owned_attempt(session, attempt_id, x_attempt_token)
        accounts.authorize_attempt(request, session, attempt_id)
        if attempt.result is not None:
            if attempt.answers != body.answers:
                raise HTTPException(409, "Already submitted with different answers")
            return attempt.result
        questions = [Question.model_validate(q) for q in attempt.snapshot["questions"]]
        if not set(body.answers) <= {q.id for q in questions} or any(
            len(a) > 20 or any(len(v) > 10000 for v in a) for a in body.answers.values()
        ):
            raise HTTPException(422, "Invalid answers")
        created = (
            attempt.created_at.replace(tzinfo=timezone.utc)
            if attempt.created_at.tzinfo is None
            else attempt.created_at
        )
        # 24h transport grace allows offline submission; these are practice scores, not supervised exams.
        if datetime.now(timezone.utc) > created + timedelta(hours=24):
            raise HTTPException(
                410, "Practice attempt expired; answers remain on device"
            )
        details = []
        for q in questions:
            submitted = body.answers.get(q.id, [])
            choices = {option.id: option.text for option in q.options}
            displayed = [
                ("Đúng" if value == "true" else "Sai" if value == "false" else value)
                if q.type == "true_false"
                else choices.get(value, value)
                for value in submitted
            ]
            details.append(
                grade(q, submitted)
                | {"submitted_answer": submitted, "submitted_answer_display": displayed}
            )
        needs_review = any(d["score"] is None for d in details)
        result = {
            "attempt_id": attempt.id,
            "title": attempt.snapshot["exam"]["title"],
            "score": None if needs_review else sum(d["score"] for d in details),
            "graded_score": sum(d["score"] or 0 for d in details),
            "max_score": sum(d["max_score"] for d in details),
            "status": "needs_manual_review" if needs_review else "graded",
            "details": details,
        }
        # Compare-and-set makes concurrent retries idempotent on SQLite and PostgreSQL.
        changed = session.execute(
            update(Attempt)
            .where(Attempt.id == attempt.id, Attempt.result.is_(None))
            .values(answers=body.answers, result=result)
        ).rowcount
        owner = session.get(AccountAttempt, attempt_id)
        if changed and owner:
            session.add(
                LearningRecord(
                    attempt_id=attempt_id,
                    user_id=owner.user_id,
                    payload={
                        "exam": {
                            k: v
                            for k, v in attempt.snapshot["exam"].items()
                            if k != "question_ids"
                        },
                        "result": result,
                        "questions": [
                            public_question(q) for q in attempt.snapshot["questions"]
                        ],
                    },
                )
            )
        session.commit()
        if not changed:
            session.expire_all()
            saved = session.get(Attempt, attempt_id)
            if saved.answers != body.answers:
                raise HTTPException(409, "Already submitted")
            return saved.result
        return result

    @app.get("/attempts/{attempt_id}/result")
    def result(
        attempt_id: str,
        request: Request,
        x_attempt_token: str = Header(default=""),
        session: Session = Depends(db),
    ):
        attempt = owned_attempt(session, attempt_id, x_attempt_token)
        accounts.authorize_attempt(request, session, attempt_id)
        if attempt.result is None:
            raise HTTPException(409, "Not submitted")
        return attempt.result

    @app.delete("/attempts/{attempt_id}", status_code=204)
    def delete_attempt(
        attempt_id: str,
        request: Request,
        x_attempt_token: str = Header(default=""),
        session: Session = Depends(db),
    ):
        attempt = owned_attempt(session, attempt_id, x_attempt_token)
        accounts.authorize_attempt(request, session, attempt_id)
        session.delete(attempt)
        owner = session.get(AccountAttempt, attempt_id)
        if owner:
            session.delete(owner)
        session.commit()

    @app.get("/admin/questions", dependencies=[Depends(admin)])
    def admin_questions(session: Session = Depends(db)):
        return [
            {
                "question": q.payload,
                "state": q.state,
                "rights_confirmed": q.rights_confirmed,
                "version": q.version,
            }
            for q in session.scalars(
                select(ContentQuestion).order_by(ContentQuestion.id)
            )
        ]

    @app.post("/admin/import", dependencies=[Depends(admin)])
    def import_questions(batch: ImportBatch, session: Session = Depends(db)):
        if len({q.id for q in batch.questions}) != len(batch.questions) or len(
            {fingerprint(q) for q in batch.questions}
        ) != len(batch.questions):
            raise HTTPException(409, "Duplicate in batch; nothing imported")
        for q in batch.questions:
            if q.subject not in {s["id"] for s in subjects_for_grade(q.grade)}:
                raise HTTPException(422, "Subject not available for grade")
            if session.get(ContentQuestion, q.id) or session.scalar(
                select(ContentQuestion).where(
                    ContentQuestion.fingerprint == fingerprint(q)
                )
            ):
                raise HTTPException(
                    409, "Duplicate existing question; nothing imported"
                )
        for q in batch.questions:
            session.add(
                ContentQuestion(
                    id=q.id,
                    payload=q.model_dump(mode="json"),
                    fingerprint=fingerprint(q),
                    state="draft",
                    rights_confirmed=False,
                )
            )
        audit(session, "import", str(len(batch.questions)))
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise HTTPException(409, "Concurrent duplicate import") from None
        return {"imported": len(batch.questions), "state": "draft"}

    @app.post("/admin/questions/{question_id}/approve", dependencies=[Depends(admin)])
    def approve(
        question_id: str,
        rights_confirmed: bool = Query(),
        expected_version: int | None = Query(default=None, ge=1),
        session: Session = Depends(db),
    ):
        question = session.get(ContentQuestion, question_id)
        if not question:
            raise HTTPException(404, "Question not found")
        if expected_version is not None and question.version != expected_version:
            raise HTTPException(409, "Question version changed; review again")
        if not rights_confirmed or question.payload["source_type"] == "link_only":
            raise HTTPException(422, "Redistribution rights must be confirmed")
        changed = session.execute(
            update(ContentQuestion)
            .where(
                ContentQuestion.id == question_id,
                ContentQuestion.version == question.version,
            )
            .values(state="approved", rights_confirmed=True)
        ).rowcount
        if changed != 1:
            session.rollback()
            raise HTTPException(409, "Question version changed; review again")
        audit(session, "approve", question_id)
        session.commit()
        return {"state": question.state}

    @app.post("/admin/questions/{question_id}/publish", dependencies=[Depends(admin)])
    def publish_question(
        question_id: str,
        expected_version: int | None = Query(default=None, ge=1),
        session: Session = Depends(db),
    ):
        question = session.get(ContentQuestion, question_id)
        if (
            not question
            or question.state != "approved"
            or not question.rights_confirmed
        ):
            raise HTTPException(409, "Requires approved content and rights")
        if expected_version is not None and question.version != expected_version:
            raise HTTPException(409, "Question version changed; review again")
        changed = session.execute(
            update(ContentQuestion)
            .where(
                ContentQuestion.id == question_id,
                ContentQuestion.version == question.version,
                ContentQuestion.state == "approved",
                ContentQuestion.rights_confirmed.is_(True),
            )
            .values(state="published")
        ).rowcount
        if changed != 1:
            session.rollback()
            raise HTTPException(409, "Question changed; review again")
        audit(session, "publish-question", question_id)
        session.commit()
        return {"state": "published"}

    @app.get("/admin/exams", dependencies=[Depends(admin)])
    def list_admin_exams(session: Session = Depends(db)):
        return [
            {"exam": row.payload, "state": row.state}
            for row in session.scalars(select(Exam))
        ]

    @app.post("/admin/exams", dependencies=[Depends(admin)], status_code=201)
    def create_exam(body: ExamInput, session: Session = Depends(db)):
        if session.get(Exam, body.id):
            raise HTTPException(409, "Exam already exists")
        for qid in body.question_ids:
            question = session.get(ContentQuestion, qid)
            if (
                not question
                or question.payload["grade"] != body.grade
                or question.payload["subject"] != body.subject
            ):
                raise HTTPException(422, "Question grade/subject mismatch")
        session.add(
            Exam(id=body.id, payload=body.model_dump(mode="json"), state="draft")
        )
        audit(session, "create-exam", body.id)
        session.commit()
        return {"id": body.id, "state": "draft"}

    @app.post("/admin/exams/{exam_id}/publish", dependencies=[Depends(admin)])
    def publish_exam(exam_id: str, session: Session = Depends(db)):
        exam = session.get(Exam, exam_id)
        if not exam:
            raise HTTPException(404, "Exam not found")
        for qid in exam.payload["question_ids"]:
            q = session.get(ContentQuestion, QUESTION_REPLACEMENTS.get(qid, qid))
            if not q or q.state != "published" or not q.rights_confirmed:
                raise HTTPException(409, "All questions must be published")
        exam.state = "published"
        audit(session, "publish-exam", exam_id)
        session.commit()
        return {"state": "published"}

    return app
