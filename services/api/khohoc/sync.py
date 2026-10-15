"""Account-owned draft synchronization with optimistic concurrency."""

from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .models import Attempt, AccountAttempt, AttemptDraft


class DraftInput(BaseModel):
    revision: int = Field(ge=0, le=2147483646)
    answers: dict[str, list[str]] = Field(max_length=100)


def create_sync_router(db_dependency, accounts, public_question):
    router = APIRouter()

    def owned(request, db, attempt_id):
        user = accounts.required(request, db)
        owner = db.get(AccountAttempt, attempt_id)
        attempt = db.get(Attempt, attempt_id)
        if not owner or owner.user_id != user.id or not attempt:
            raise HTTPException(404, "Không tìm thấy bài làm.")
        return attempt, user

    def deadline(attempt):
        created = attempt.created_at
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        return created + timedelta(
            minutes=attempt.snapshot["exam"]["duration_minutes"], hours=24
        )

    @router.get("/account/attempts")
    def pending(request: Request, db: Session = Depends(db_dependency)):
        user = accounts.required(request, db)
        rows = db.scalars(
            select(Attempt)
            .join(AccountAttempt, AccountAttempt.attempt_id == Attempt.id)
            .where(AccountAttempt.user_id == user.id)
            .order_by(Attempt.created_at.desc())
            .limit(100)
        )
        return [
            dict(
                id=row.id,
                title=row.snapshot["exam"]["title"],
                created_at=row.created_at.isoformat(),
            )
            for row in rows
            if row.result is None and deadline(row) >= datetime.now(timezone.utc)
        ]

    @router.get("/account/attempts/{attempt_id}")
    def resume(attempt_id: str, request: Request, db: Session = Depends(db_dependency)):
        attempt, user = owned(request, db, attempt_id)
        if attempt.result is not None:
            raise HTTPException(409, "Bài đã nộp. Hãy xem kết quả đã lưu.")
        if deadline(attempt) < datetime.now(timezone.utc):
            raise HTTPException(410, "Phiên làm bài đã hết hạn.")
        draft = db.get(AttemptDraft, attempt_id)
        return dict(
            id=attempt.id,
            token="",
            account_id=user.id,
            exam={
                k: v for k, v in attempt.snapshot["exam"].items() if k != "question_ids"
            },
            questions=[public_question(q) for q in attempt.snapshot["questions"]],
            created_at=attempt.created_at.isoformat()
            + ("Z" if attempt.created_at.tzinfo is None else ""),
            answers=draft.answers if draft else {},
            draft_revision=draft.revision if draft else 0,
            **(
                {"practice_filter": attempt.snapshot["practice_filter"]}
                if "practice_filter" in attempt.snapshot
                else {}
            ),
        )

    @router.post("/account/attempts/{attempt_id}/draft")
    def save(
        attempt_id: str,
        body: DraftInput,
        request: Request,
        db: Session = Depends(db_dependency),
    ):
        attempt, _ = owned(request, db, attempt_id)
        # Serialize save vs submit on PostgreSQL; stale clients cannot overwrite drafts.
        attempt = db.scalar(
            select(Attempt)
            .where(Attempt.id == attempt_id)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        if attempt.result is not None:
            raise HTTPException(409, "Bài đã nộp.")
        if deadline(attempt) < datetime.now(timezone.utc):
            raise HTTPException(410, "Phiên làm bài đã hết hạn.")
        question_ids = {q["id"] for q in attempt.snapshot["questions"]}
        if not set(body.answers) <= question_ids or any(
            len(v) > 20 or any(len(x) > 10000 for x in v) for v in body.answers.values()
        ):
            raise HTTPException(422, "Câu trả lời không hợp lệ.")
        draft = db.get(AttemptDraft, attempt_id)
        now = datetime.now(timezone.utc)
        if draft is None and body.revision == 0:
            db.add(
                AttemptDraft(
                    attempt_id=attempt_id,
                    answers=body.answers,
                    revision=1,
                    updated_at=now,
                )
            )
        else:
            changed = db.execute(
                update(AttemptDraft)
                .where(
                    AttemptDraft.attempt_id == attempt_id,
                    AttemptDraft.revision == body.revision,
                )
                .values(
                    answers=body.answers, revision=body.revision + 1, updated_at=now
                )
            ).rowcount
            if changed != 1:
                raise HTTPException(
                    409,
                    "Bài đã thay đổi trên thiết bị khác. Tải lại trước khi tiếp tục.",
                )
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                409, "Bài đã thay đổi trên thiết bị khác. Tải lại trước khi tiếp tục."
            ) from None
        return {"revision": body.revision + 1, "updated_at": now.isoformat()}

    return router
