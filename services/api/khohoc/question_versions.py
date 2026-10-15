"""Admin-only question revisions; moderation must run again after each change."""

from datetime import datetime, timezone
from typing import Callable

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Mapped, Session, mapped_column

from .catalog import subjects_for_grade
from .models import Base, ContentQuestion, Exam
from .schemas import Question


class QuestionRevision(Base):
    __tablename__ = "local_question_revisions"

    question_id: Mapped[str] = mapped_column(
        ForeignKey("local_questions.id"), primary_key=True
    )
    version: Mapped[int] = mapped_column(Integer, primary_key=True)
    payload: Mapped[dict] = mapped_column(JSON)
    operation: Mapped[str] = mapped_column(String(20))
    note: Mapped[str] = mapped_column(Text)
    restored_from: Mapped[int | None] = mapped_column(Integer, nullable=True)
    actor: Mapped[str] = mapped_column(String(80), default="local-admin")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class EditQuestion(BaseModel):
    model_config = ConfigDict(extra="forbid")
    expected_version: int = Field(ge=1)
    question: Question
    note: str = Field(min_length=1, max_length=1000)


class RollbackQuestion(BaseModel):
    model_config = ConfigDict(extra="forbid")
    expected_version: int = Field(ge=1)
    target_version: int = Field(ge=1)
    note: str = Field(min_length=1, max_length=1000)


def record_question_version(
    session: Session,
    question: ContentQuestion,
    *,
    operation: str = "initial",
    note: str = "Nội dung ban đầu",
    actor: str = "local-admin",
) -> None:
    """Snapshot an existing revision once, without committing the caller's transaction."""
    if session.get(QuestionRevision, (question.id, question.version)) is None:
        session.add(
            QuestionRevision(
                question_id=question.id,
                version=question.version,
                payload=question.payload,
                operation=operation,
                note=note,
                actor=actor,
            )
        )


def create_question_versions_router(
    *, db: Callable, admin: Callable, audit: Callable, fingerprint: Callable
) -> APIRouter:
    router = APIRouter(prefix="/admin/questions", dependencies=[Depends(admin)])

    def get_question(session: Session, question_id: str) -> ContentQuestion:
        question = session.get(ContentQuestion, question_id)
        if question is None:
            raise HTTPException(404, "Question not found")
        return question

    def save_revision(
        session: Session,
        current: ContentQuestion,
        body: Question,
        expected_version: int,
        note: str,
        operation: str,
        actor: str,
        restored_from: int | None = None,
    ) -> dict:
        if current.version != expected_version:
            raise HTTPException(409, "Question changed; reload before saving")
        if body.id != current.id:
            raise HTTPException(422, "Question ID cannot be changed")
        if body.subject not in {s["id"] for s in subjects_for_grade(body.grade)}:
            raise HTTPException(422, "Subject not available for grade")
        related = [
            exam
            for exam in session.scalars(select(Exam))
            if current.id in exam.payload["question_ids"]
        ]
        if related and (
            body.grade != current.payload["grade"]
            or body.subject != current.payload["subject"]
        ):
            raise HTTPException(
                409, "Cannot change grade/subject of a question used by an exam"
            )
        digest = fingerprint(body)
        if session.scalar(
            select(ContentQuestion.id).where(
                ContentQuestion.fingerprint == digest,
                ContentQuestion.id != current.id,
            )
        ):
            raise HTTPException(409, "Duplicate existing question")
        payload = body.model_dump(mode="json")
        if payload == current.payload and operation == "edit":
            raise HTTPException(409, "Question content has not changed")
        next_version = expected_version + 1
        # A compare-and-set prevents stale forms from overwriting another editor.
        # Both payload and answer keys are replaced together in one transaction.
        try:
            changed = session.execute(
                update(ContentQuestion)
                .where(
                    ContentQuestion.id == current.id,
                    ContentQuestion.version == expected_version,
                )
                .values(
                    payload=payload,
                    fingerprint=digest,
                    version=next_version,
                    state="draft",
                    rights_confirmed=False,
                )
                .execution_options(synchronize_session=False)
            ).rowcount
        except IntegrityError:
            session.rollback()
            raise HTTPException(409, "Concurrent duplicate question") from None
        if changed != 1:
            session.rollback()
            raise HTTPException(409, "Question changed; reload before saving")
        record_question_version(session, current, actor=actor)
        session.add(
            QuestionRevision(
                question_id=current.id,
                version=next_version,
                payload=payload,
                operation=operation,
                note=note.strip(),
                actor=actor,
                restored_from=restored_from,
            )
        )
        # Existing attempts keep their immutable snapshots. Future attempts stop
        # until the changed content and its exams have been approved/published again.
        for exam in related:
            exam.state = "draft"
        audit(
            session,
            "question-" + operation,
            f"{current.id}:v{next_version}"
            + (f":from-v{restored_from}" if restored_from is not None else ""),
        )
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise HTTPException(
                409, "Concurrent change or duplicate question"
            ) from None
        return {
            "id": body.id,
            "version": next_version,
            "state": "draft",
            "rights_confirmed": False,
            "exams_reset_to_draft": [exam.id for exam in related],
        }

    @router.get("/{question_id}")
    def detail(question_id: str, session: Session = Depends(db)):
        question = get_question(session, question_id)
        return {
            "question": question.payload,
            "version": question.version,
            "state": question.state,
            "rights_confirmed": question.rights_confirmed,
            "exam_ids": [
                exam.id
                for exam in session.scalars(select(Exam))
                if question.id in exam.payload["question_ids"]
            ],
        }

    @router.get("/{question_id}/versions")
    def history(question_id: str, session: Session = Depends(db)):
        current = get_question(session, question_id)
        versions = [
            {
                "version": revision.version,
                "question": revision.payload,
                "operation": revision.operation,
                "note": revision.note,
                "actor": revision.actor,
                "restored_from": revision.restored_from,
                "created_at": revision.created_at.isoformat()
                + ("Z" if revision.created_at.tzinfo is None else ""),
            }
            for revision in session.scalars(
                select(QuestionRevision)
                .where(QuestionRevision.question_id == question_id)
                .order_by(QuestionRevision.version.desc())
            )
        ]
        if not versions:
            versions = [
                {
                    "version": current.version,
                    "question": current.payload,
                    "operation": "initial",
                    "note": "Nội dung ban đầu",
                    "actor": "local-admin",
                    "restored_from": None,
                    "created_at": None,
                }
            ]
        return {"current_version": current.version, "versions": versions}

    @router.post("/{question_id}/edit")
    def edit(
        question_id: str,
        body: EditQuestion,
        session: Session = Depends(db),
        actor: str = Depends(admin),
    ):
        if not body.note.strip():
            raise HTTPException(422, "Change note is required")
        return save_revision(
            session,
            get_question(session, question_id),
            body.question,
            body.expected_version,
            body.note,
            "edit",
            actor,
        )

    @router.post("/{question_id}/rollback")
    def rollback(
        question_id: str,
        body: RollbackQuestion,
        session: Session = Depends(db),
        actor: str = Depends(admin),
    ):
        current = get_question(session, question_id)
        if body.target_version == current.version:
            raise HTTPException(409, "Already at this version")
        revision = session.get(QuestionRevision, (question_id, body.target_version))
        if revision is None:
            raise HTTPException(404, "Question version not found")
        if not body.note.strip():
            raise HTTPException(422, "Rollback note is required")
        return save_revision(
            session,
            current,
            Question.model_validate(revision.payload),
            body.expected_version,
            body.note,
            "rollback",
            actor,
            body.target_version,
        )

    return router
