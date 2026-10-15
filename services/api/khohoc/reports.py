"""Account-owned content feedback; review never changes answers or historic grades."""

import hashlib
import uuid
from datetime import datetime, timedelta, timezone
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select, func, update, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .models import (
    ContentReport,
    LearningUser,
    AccountAttempt,
    Attempt,
    GroupMember,
    ClassroomGroup,
    AuditEvent,
)
from .library import LibraryDocument

Status = Literal["open", "in_review", "resolved", "dismissed"]


class ReportInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    target_kind: Literal["question", "document"]
    target_id: str = Field(min_length=1, max_length=80)
    attempt_id: str | None = Field(default=None, min_length=1, max_length=36)
    category: Literal["wrong_answer", "unclear", "typo", "other"]
    message: str = Field(min_length=5, max_length=1500)


class ReviewInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    revision: int = Field(ge=1, le=2147483646)
    status: Literal["in_review", "resolved", "dismissed"]
    response: str = Field(min_length=5, max_length=2000)


def timestamp(value):
    return value.isoformat() + ("Z" if value.tzinfo is None else "")


def public_report(row, reporter=None):
    result = {
        k: getattr(row, k)
        for k in (
            "id",
            "target_kind",
            "target_id",
            "target_title",
            "excerpt",
            "category",
            "message",
            "status",
            "response",
            "revision",
        )
    }
    result.update(
        created_at=timestamp(row.created_at), updated_at=timestamp(row.updated_at)
    )
    if reporter is not None:
        result["reporter"] = {
            "username": reporter.username,
            "display_name": reporter.display_name,
        }
    return result


def reviewer_ids(owner):
    # Membership gives the same current access as the existing student-results view.
    member_ids = (
        select(GroupMember.user_id)
        .join(ClassroomGroup, GroupMember.group_id == ClassroomGroup.id)
        .where(ClassroomGroup.owner_id == owner.id)
    )
    scope = (LearningUser.manager_id == owner.id) | LearningUser.id.in_(member_ids)
    if owner.role == "manager":
        teachers = select(LearningUser.id).where(
            LearningUser.role == "teacher", LearningUser.manager_id == owner.id
        )
        scope = scope | LearningUser.manager_id.in_(teachers)
    return select(LearningUser.id).where(
        LearningUser.id != owner.id,
        LearningUser.role.in_(
            ["student", "teacher"] if owner.role == "manager" else ["student"]
        ),
        scope,
    )


def remove_account_reports(db, user_id):
    db.execute(delete(ContentReport).where(ContentReport.reporter_id == user_id))
    # A deleted reviewer leaves no authored feedback or identity in other users' tickets.
    db.execute(
        update(ContentReport)
        .where(ContentReport.reviewed_by == user_id)
        .values(
            reviewed_by=None,
            response="Người xử lý đã xóa tài khoản. Liên hệ quản lý nếu cần xem xét lại.",
            revision=ContentReport.revision + 1,
            updated_at=datetime.now(timezone.utc),
        )
    )


def create_reports_router(db, accounts):
    router = APIRouter()

    @router.post("/content-reports", status_code=201)
    def create(body: ReportInput, request: Request, session: Session = Depends(db)):
        user = accounts.required(request, session)
        # Serialize quota/duplicate decisions for a user across PostgreSQL workers.
        session.scalar(
            select(LearningUser).where(LearningUser.id == user.id).with_for_update()
        )
        now = datetime.now(timezone.utc)
        count = session.scalar(
            select(func.count())
            .select_from(ContentReport)
            .where(
                ContentReport.reporter_id == user.id,
                ContentReport.created_at >= now - timedelta(days=1),
            )
        )
        if count >= 20:
            raise HTTPException(
                429, "Bạn đã gửi 20 phản hồi trong 24 giờ. Vui lòng thử lại sau."
            )
        if body.target_kind == "question":
            owner = (
                session.get(AccountAttempt, body.attempt_id)
                if body.attempt_id
                else None
            )
            attempt = (
                session.get(Attempt, body.attempt_id)
                if owner and owner.user_id == user.id
                else None
            )
            question = (
                next(
                    (
                        q
                        for q in attempt.snapshot["questions"]
                        if q["id"] == body.target_id
                    ),
                    None,
                )
                if attempt
                else None
            )
            if not question:
                raise HTTPException(
                    404, "Không tìm thấy câu hỏi trong bài làm của bạn."
                )
            title = attempt.snapshot["exam"]["title"]
            excerpt = question["question"]
        else:
            document = session.get(LibraryDocument, body.target_id)
            if (
                not document
                or document.state != "published"
                or not document.rights_confirmed
            ):
                raise HTTPException(404, "Không tìm thấy tài liệu.")
            title = document.payload["title"]
            excerpt = document.payload.get("summary", "")
        active_key = hashlib.sha256(
            f"{user.id}:{body.target_kind}:{body.target_id}".encode()
        ).hexdigest()
        report = ContentReport(
            id=str(uuid.uuid4()),
            reporter_id=user.id,
            target_kind=body.target_kind,
            target_id=body.target_id,
            target_title=title[:300],
            excerpt=excerpt[:1200],
            category=body.category,
            message=body.message,
            active_key=active_key,
        )
        session.add(report)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise HTTPException(
                409, "Bạn đã có phản hồi đang chờ xử lý cho nội dung này."
            ) from None
        return public_report(report)

    @router.get("/content-reports")
    def mine(
        request: Request,
        status: Status | None = None,
        offset: int = Query(0, ge=0),
        limit: int = Query(30, ge=1, le=100),
        session: Session = Depends(db),
    ):
        user = accounts.required(request, session)
        query = select(ContentReport).where(ContentReport.reporter_id == user.id)
        if status:
            query = query.where(ContentReport.status == status)
        return [
            public_report(row)
            for row in session.scalars(
                query.order_by(ContentReport.created_at.desc(), ContentReport.id)
                .offset(offset)
                .limit(limit)
            )
        ]

    @router.get("/classroom/content-reports")
    def inbox(
        request: Request,
        status: Status | None = None,
        offset: int = Query(0, ge=0),
        limit: int = Query(30, ge=1, le=100),
        session: Session = Depends(db),
    ):
        owner = accounts.manager(request, session)
        query = (
            select(ContentReport, LearningUser)
            .join(LearningUser, LearningUser.id == ContentReport.reporter_id)
            .where(ContentReport.reporter_id.in_(reviewer_ids(owner)))
        )
        if status:
            query = query.where(ContentReport.status == status)
        return [
            public_report(row, reporter)
            for row, reporter in session.execute(
                query.order_by(ContentReport.created_at.desc(), ContentReport.id)
                .offset(offset)
                .limit(limit)
            )
        ]

    @router.post("/classroom/content-reports/{report_id}/review")
    def review(
        report_id: str,
        body: ReviewInput,
        request: Request,
        session: Session = Depends(db),
    ):
        owner = accounts.manager(request, session)
        row = session.scalar(
            select(ContentReport).where(
                ContentReport.id == report_id,
                ContentReport.reporter_id.in_(reviewer_ids(owner)),
            )
        )
        if not row:
            raise HTTPException(404, "Không tìm thấy phản hồi.")
        if row.status in ("resolved", "dismissed"):
            raise HTTPException(409, "Phản hồi đã đóng. Hãy tải lại danh sách.")
        changed = session.execute(
            update(ContentReport)
            .where(
                ContentReport.id == row.id,
                ContentReport.revision == body.revision,
                ContentReport.status.in_(["open", "in_review"]),
            )
            .values(
                status=body.status,
                response=body.response,
                reviewed_by=owner.id,
                active_key=None
                if body.status in ("resolved", "dismissed")
                else row.active_key,
                revision=ContentReport.revision + 1,
                updated_at=datetime.now(timezone.utc),
            )
        ).rowcount
        if not changed:
            session.rollback()
            raise HTTPException(
                409, "Phản hồi đã thay đổi trên thiết bị khác. Hãy tải lại."
            )
        session.add(
            AuditEvent(
                actor=owner.id, action="content_report." + body.status, target=row.id
            )
        )
        session.commit()
        session.refresh(row)
        return public_report(row)

    return router
