"""Private group assignments and progress computed from server-owned submissions."""

import csv
import io
import math
import uuid
from collections import defaultdict
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from sqlalchemy import String, cast, or_, select
from sqlalchemy.orm import Session

from .content_fixes import QUESTION_REPLACEMENTS
from .models import (
    AccountAttempt,
    Attempt,
    ClassroomGroup,
    ContentQuestion,
    Exam,
    GroupMember,
    LearningRecord,
    LearningUser,
    TeacherExam,
)
from .schemas import ExamInput, Question


class AssignmentInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    exam_id: str = Field(min_length=1, max_length=80)


def timestamp(value):
    return value.isoformat() + ("Z" if value.tzinfo is None else "")


def normalized_percent(payload):
    result = payload.get("result", {})
    score, maximum = result.get("score"), result.get("max_score")
    if (
        isinstance(score, bool)
        or isinstance(maximum, bool)
        or not isinstance(score, (int, float))
        or not isinstance(maximum, (int, float))
        or not math.isfinite(score)
        or not math.isfinite(maximum)
        or maximum <= 0
    ):
        return None
    return round(100 * score / maximum, 2)


def progress_for(db, exams, user_ids):
    """Two batched queries regardless of the number of members or assignments."""
    progress = defaultdict(dict)
    if not exams or not user_ids:
        return progress
    exam_ids = [exam.id for exam in exams]
    for record in db.scalars(
        select(LearningRecord)
        .where(
            LearningRecord.user_id.in_(user_ids),
            LearningRecord.payload["exam"]["id"].as_string().in_(exam_ids),
        )
        .order_by(LearningRecord.submitted_at.desc(), LearningRecord.attempt_id.desc())
    ):
        exam_id = record.payload["exam"]["id"]
        current = progress[exam_id].get(record.user_id)
        if current:
            current["attempts_count"] += 1
        else:
            progress[exam_id][record.user_id] = dict(
                status="submitted",
                attempts_count=1,
                latest_percent=normalized_percent(record.payload),
                latest_submitted_at=timestamp(record.submitted_at),
            )
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    for user_id, exam_id in db.execute(
        select(AccountAttempt.user_id, Attempt.snapshot["exam"]["id"].as_string())
        .join(Attempt, Attempt.id == AccountAttempt.attempt_id)
        .where(
            AccountAttempt.user_id.in_(user_ids),
            Attempt.snapshot["exam"]["id"].as_string().in_(exam_ids),
            or_(Attempt.result.is_(None), cast(Attempt.result, String) == "null"),
            Attempt.created_at >= cutoff,
        )
        .distinct()
    ):
        if user_id not in progress[exam_id]:
            progress[exam_id][user_id] = dict(
                status="in_progress",
                attempts_count=0,
                latest_percent=None,
                latest_submitted_at=None,
            )
    return progress


def student_progress(progress, exam_id, user_id):
    return progress.get(exam_id, {}).get(
        user_id,
        dict(
            status="not_started",
            attempts_count=0,
            latest_percent=None,
            latest_submitted_at=None,
        ),
    )


def exam_fields(exam, group):
    return dict(
        exam_id=exam.id,
        title=exam.payload["title"],
        grade=exam.payload["grade"],
        subject=exam.payload["subject"],
        duration_minutes=exam.payload["duration_minutes"],
        group_id=group.id,
        group_name=group.name,
    )


def summary(exam, group, members, progress):
    statuses = [
        student_progress(progress, exam.id, user.id)["status"] for user in members
    ]
    return dict(
        **exam_fields(exam, group),
        member_count=len(members),
        submitted_count=statuses.count("submitted"),
        in_progress_count=statuses.count("in_progress"),
        not_started_count=statuses.count("not_started"),
    )


def csv_cell(value):
    value = str(value)
    return (
        "'" + value
        if value.lstrip().startswith(("=", "+", "-", "@"))
        or value.startswith(("\t", "\r", "\n"))
        else value
    )


def create_assignments_router(*, db, accounts):
    router = APIRouter()

    def owned_group(group_id, request, session):
        owner = accounts.manager(request, session)
        group = session.get(ClassroomGroup, group_id)
        if not group or group.owner_id != owner.id:
            raise HTTPException(404, "Không tìm thấy nhóm của bạn.")
        return group

    def group_members(session, group):
        return list(
            session.scalars(
                select(LearningUser)
                .join(GroupMember, GroupMember.user_id == LearningUser.id)
                .where(GroupMember.group_id == group.id, LearningUser.role == "student")
                .order_by(LearningUser.username)
            )
        )

    def group_exam_query(group):
        return (
            select(Exam)
            .join(TeacherExam, TeacherExam.exam_id == Exam.id)
            .where(
                TeacherExam.group_id == group.id,
                TeacherExam.owner_id == group.owner_id,
                Exam.state == "published",
            )
        )

    def assignment_detail(group_id, exam_id, request, session):
        group = owned_group(group_id, request, session)
        exam = session.scalar(group_exam_query(group).where(Exam.id == exam_id))
        if not exam:
            raise HTTPException(404, "Không tìm thấy đề giao cho nhóm.")
        members = group_members(session, group)
        progress = progress_for(session, [exam], [user.id for user in members])
        result = summary(exam, group, members, progress)
        result["students"] = [
            dict(
                id=user.id,
                username=user.username,
                display_name=user.display_name,
                grade=user.grade,
                **student_progress(progress, exam.id, user.id),
            )
            for user in members
        ]
        return result

    @router.post("/classroom/groups/{group_id}/assignments", status_code=201)
    def assign(
        group_id: str,
        body: AssignmentInput,
        request: Request,
        session: Session = Depends(db),
    ):
        group = owned_group(group_id, request, session)
        source = session.get(Exam, body.exam_id)
        if (
            not source
            or source.state != "published"
            or not accounts.can_access_exam(request, session, source.id)
        ):
            raise HTTPException(404, "Không tìm thấy đề nguồn được phép sử dụng.")
        try:
            payload = ExamInput.model_validate(source.payload).model_dump(mode="json")
            question_ids = list(
                dict.fromkeys(
                    QUESTION_REPLACEMENTS.get(qid, qid)
                    for qid in payload["question_ids"]
                )
            )
            questions = {
                row.id: row
                for row in session.scalars(
                    select(ContentQuestion).where(ContentQuestion.id.in_(question_ids))
                )
            }
            for question_id in question_ids:
                row = questions.get(question_id)
                if not row or row.state != "published" or not row.rights_confirmed:
                    raise ValueError("Question unavailable")
                question = Question.model_validate(row.payload)
                if (
                    question.id != question_id
                    or question.source_type == "link_only"
                    or question.grade != payload["grade"]
                    or question.subject != payload["subject"]
                ):
                    raise ValueError("Question does not belong to exam")
        except (ValidationError, ValueError, KeyError, TypeError):
            raise HTTPException(
                409, "Đề nguồn có câu hỏi chưa sẵn sàng. Hãy chọn đề khác."
            ) from None
        payload.update(id=str(uuid.uuid4()), question_ids=question_ids)
        exam = Exam(id=payload["id"], payload=payload, state="published")
        session.add(exam)
        session.add(
            TeacherExam(exam_id=exam.id, owner_id=group.owner_id, group_id=group.id)
        )
        session.commit()
        members = group_members(session, group)
        return summary(exam, group, members, {})

    @router.get("/classroom/groups/{group_id}/assignments")
    def list_group(
        group_id: str,
        request: Request,
        offset: int = Query(default=0, ge=0),
        limit: int = Query(default=30, ge=1, le=100),
        session: Session = Depends(db),
    ):
        group = owned_group(group_id, request, session)
        exams = list(
            session.scalars(
                group_exam_query(group).order_by(Exam.id).offset(offset).limit(limit)
            )
        )
        members = group_members(session, group)
        progress = progress_for(session, exams, [user.id for user in members])
        return [summary(exam, group, members, progress) for exam in exams]

    @router.get("/classroom/groups/{group_id}/assignments/{exam_id}")
    def detail(
        group_id: str,
        exam_id: str,
        request: Request,
        session: Session = Depends(db),
    ):
        return assignment_detail(group_id, exam_id, request, session)

    @router.get("/classroom/groups/{group_id}/assignments/{exam_id}/results.csv")
    def download(
        group_id: str,
        exam_id: str,
        request: Request,
        session: Session = Depends(db),
    ):
        result = assignment_detail(group_id, exam_id, request, session)
        output = io.StringIO(newline="")
        writer = csv.writer(output)
        writer.writerow(
            [
                "Nhóm",
                "Đề được giao",
                "Tên đăng nhập",
                "Họ và tên",
                "Lớp",
                "Trạng thái",
                "Số lần nộp",
                "Điểm gần nhất (%)",
                "Nộp gần nhất (UTC)",
            ]
        )
        labels = {
            "submitted": "Đã nộp",
            "in_progress": "Đang làm",
            "not_started": "Chưa có bài đang làm",
        }
        for student in result["students"]:
            writer.writerow(
                [
                    csv_cell(result["group_name"]),
                    csv_cell(result["title"]),
                    csv_cell(student["username"]),
                    csv_cell(student["display_name"]),
                    student["grade"] or "",
                    labels[student["status"]],
                    student["attempts_count"],
                    ""
                    if student["latest_percent"] is None
                    else student["latest_percent"],
                    student["latest_submitted_at"] or "",
                ]
            )
        return Response(
            content="\ufeff" + output.getvalue(),
            media_type="text/csv; charset=utf-8",
            headers={
                "Content-Disposition": 'attachment; filename="tu-hoc-111-ket-qua-de-giao.csv"',
                "Cache-Control": "no-store",
                "X-Content-Type-Options": "nosniff",
            },
        )

    @router.get("/account/assignments")
    def mine(
        request: Request,
        offset: int = Query(default=0, ge=0),
        limit: int = Query(default=30, ge=1, le=100),
        session: Session = Depends(db),
    ):
        user = accounts.required(request, session)
        if user.role != "student":
            raise HTTPException(403, "Mục này dành cho học sinh trong nhóm.")
        rows = list(
            session.execute(
                select(Exam, ClassroomGroup)
                .join(TeacherExam, TeacherExam.exam_id == Exam.id)
                .join(ClassroomGroup, ClassroomGroup.id == TeacherExam.group_id)
                .join(GroupMember, GroupMember.group_id == ClassroomGroup.id)
                .where(
                    GroupMember.user_id == user.id,
                    TeacherExam.owner_id == ClassroomGroup.owner_id,
                    Exam.state == "published",
                )
                .order_by(Exam.id)
                .offset(offset)
                .limit(limit)
            )
        )
        progress = progress_for(session, [exam for exam, group in rows], [user.id])
        return [
            dict(
                **exam_fields(exam, group),
                **student_progress(progress, exam.id, user.id),
            )
            for exam, group in rows
        ]

    return router
