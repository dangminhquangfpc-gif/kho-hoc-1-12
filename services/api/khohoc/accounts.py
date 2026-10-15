"""Local classroom accounts. Opaque sessions, server grading, no hosted auth claims."""

import base64
import csv
import io
import hashlib
import hmac
import secrets
import time
import uuid
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import delete, select, func, case
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .models import (
    ClassroomGroup,
    TeacherExam,
    Exam,
    GroupMember,
    AccountAttempt,
    AuditEvent,
    LearningRecord,
    LearningSession,
    LearningUser,
    Attempt,
    AttemptDraft,
)

COOKIE = "khohoc_session"


def password_hash(password):
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(
        password.encode(),
        salt=salt,
        n=16384,
        r=8,
        p=1,
        dklen=32,
        maxmem=64 * 1024 * 1024,
    )
    return base64.b64encode(salt + digest).decode()


def password_valid(password, stored):
    try:
        value = base64.b64decode(stored, validate=True)
        if len(value) != 48:
            return False
        actual = hashlib.scrypt(
            password.encode(),
            salt=value[:16],
            n=16384,
            r=8,
            p=1,
            dklen=32,
            maxmem=64 * 1024 * 1024,
        )
        return hmac.compare_digest(actual, value[16:])
    except (ValueError, TypeError):
        return False


def public_user(user):
    return dict(
        id=user.id,
        username=user.username,
        display_name=user.display_name,
        role=user.role,
        grade=user.grade,
        active=user.active,
        must_change_password=user.must_change_password,
    )


def ensure_manager(engine, credential_file):
    """Called only by the local launcher; never bootstrap via an HTTP request."""
    if not credential_file:
        return
    with Session(engine) as db:
        if db.scalar(select(LearningUser).where(LearningUser.role == "manager")):
            return
        path = Path(credential_file)
        password = secrets.token_urlsafe(15)
        user = LearningUser(
            id=str(uuid.uuid4()),
            username="quanly",
            display_name="Người quản lý",
            role="manager",
            password_hash=password_hash(password),
            must_change_password=True,
        )
        db.add(user)
        db.flush()
        path.parent.mkdir(parents=True, exist_ok=True)
        # Preserve existing user files. The DB/file pair is created once.
        with path.open("x", encoding="utf-8-sig") as file:
            file.write(
                "KHO HỌC — TÀI KHOẢN QUẢN LÝ LOCAL\nTên đăng nhập: quanly\nMật khẩu tạm: "
                + password
                + "\nĐổi mật khẩu ngay lần đăng nhập đầu. Không gửi tệp này lên GitHub hoặc qua chat.\n"
            )
        try:
            path.chmod(0o600)
        except OSError:
            pass
        db.commit()


class LoginInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    username: str = Field(pattern=r"^[a-zA-Z0-9_.-]{3,40}$")
    password: str = Field(min_length=10, max_length=128)
    mobile: bool = False


class Registration(LoginInput):
    role: Literal["student", "teacher"] = "student"
    display_name: str = Field(min_length=1, max_length=80)
    grade: int | None = Field(default=None, ge=1, le=12)


class StudentInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    username: str = Field(pattern=r"^[a-zA-Z0-9_.-]{3,40}$")
    display_name: str = Field(min_length=1, max_length=80)
    grade: int | None = Field(default=None, ge=1, le=12)


class BulkInput(BaseModel):
    students: list[StudentInput] = Field(min_length=1, max_length=50)


class GroupInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    name: str = Field(min_length=1, max_length=100)


class JoinGroupInput(BaseModel):
    code: str = Field(min_length=8, max_length=30)


class MemberInput(BaseModel):
    username: str = Field(pattern=r"^[a-zA-Z0-9_.-]{3,40}$")


class DeleteAccountInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    password: str = Field(min_length=10, max_length=128)


class PasswordInput(BaseModel):
    current_password: str = Field(min_length=10, max_length=128)
    new_password: str = Field(min_length=10, max_length=128)


class AccountService:
    def __init__(self, db):
        self.db = db
        self.failures = defaultdict(deque)
        self.dummy = password_hash(secrets.token_urlsafe(20))
        self.router = self.routes()

    def token(self, request):
        authorization = request.headers.get("authorization", "")
        if authorization:
            if not authorization.startswith("Bearer khs_"):
                raise HTTPException(401, "Phiên đăng nhập không hợp lệ.")
            return authorization[7:]
        return request.cookies.get(COOKIE)

    def optional_user(self, request, db, allow_temporary=False):
        token = self.token(request)
        if not token:
            return None
        session = db.get(LearningSession, hashlib.sha256(token.encode()).hexdigest())
        if not session:
            raise HTTPException(401, "Phiên đăng nhập đã hết hạn. Hãy đăng nhập lại.")
        expiry = (
            session.expires_at.replace(tzinfo=timezone.utc)
            if session.expires_at.tzinfo is None
            else session.expires_at
        )
        user = db.get(LearningUser, session.user_id)
        if expiry < datetime.now(timezone.utc) or not user or not user.active:
            raise HTTPException(401, "Phiên đăng nhập đã hết hạn. Hãy đăng nhập lại.")
        if user.must_change_password and not allow_temporary:
            raise HTTPException(403, "Hãy đổi mật khẩu tạm trước khi tiếp tục.")
        return user

    def required(self, request, db, allow_temporary=False):
        user = self.optional_user(request, db, allow_temporary)
        if not user:
            raise HTTPException(401, "Bạn cần đăng nhập.")
        return user

    def manager(self, request, db):
        user = self.required(request, db)
        if user.role not in {"manager", "teacher"}:
            raise HTTPException(
                403, "Chỉ giáo viên hoặc người quản lý được dùng chức năng này."
            )
        return user

    def can_access_exam(self, request, db, exam_id):
        scope = db.get(TeacherExam, exam_id)
        if not scope:
            return True
        user = self.optional_user(request, db)
        if not user:
            return False
        return (
            user.id == scope.owner_id
            or db.get(GroupMember, (scope.group_id, user.id)) is not None
        )

    def authorize_attempt(self, request, db, attempt_id):
        owner = db.get(AccountAttempt, attempt_id)
        if owner:
            user = self.optional_user(request, db)
            if not user or owner.user_id != user.id:
                raise HTTPException(404, "Attempt not found")

    def login_rate(self, request, username, action="login"):
        now = time.monotonic()
        key = (action, request.client.host if request.client else "", username.lower())
        if len(self.failures) > 5000:
            self.failures.clear()
        values = self.failures[key]
        while values and values[0] < now - 900:
            values.popleft()
        if len(values) >= 8:
            raise HTTPException(429, "Bạn đã thử nhiều lần. Vui lòng thử lại sau.")
        return values

    def issue(self, user, body, request, response, db):
        token = "khs_" + secrets.token_urlsafe(32)
        db.add(
            LearningSession(
                token_hash=hashlib.sha256(token.encode()).hexdigest(),
                user_id=user.id,
                expires_at=datetime.now(timezone.utc) + timedelta(hours=8),
            )
        )
        db.commit()
        response.set_cookie(
            COOKIE,
            token,
            max_age=8 * 3600,
            httponly=True,
            samesite="strict",
            secure=request.url.scheme == "https",
            path="/",
        )
        return dict(user=public_user(user), **({"token": token} if body.mobile else {}))

    def assigned(self, request, db, user_id):
        manager = self.manager(request, db)
        student = db.get(LearningUser, user_id)
        member = db.scalar(
            select(GroupMember)
            .join(ClassroomGroup, GroupMember.group_id == ClassroomGroup.id)
            .where(
                GroupMember.user_id == user_id, ClassroomGroup.owner_id == manager.id
            )
        )
        provisioner = (
            db.get(LearningUser, student.manager_id)
            if student and student.manager_id
            else None
        )
        overseen = (
            manager.role == "manager"
            and provisioner
            and provisioner.manager_id == manager.id
            and provisioner.role == "teacher"
        )
        if (
            not student
            or student.role != "student"
            or (student.manager_id != manager.id and not member and not overseen)
        ):
            raise HTTPException(404, "Không tìm thấy học viên.")
        return student

    def records(self, db, user_id):
        return [
            dict(
                id=row.attempt_id,
                submitted_at=row.submitted_at.isoformat()
                + ("Z" if row.submitted_at.tzinfo is None else ""),
                **row.payload,
            )
            for row in db.scalars(
                select(LearningRecord)
                .where(LearningRecord.user_id == user_id)
                .order_by(LearningRecord.submitted_at.desc())
                .limit(500)
            )
        ]

    def routes(self):
        router = APIRouter()
        db_dependency = self.db

        @router.get("/auth/me")
        def me(request: Request, db: Session = Depends(db_dependency)):
            return public_user(self.required(request, db, True))

        @router.post("/auth/login")
        def login(
            body: LoginInput,
            request: Request,
            response: Response,
            db: Session = Depends(db_dependency),
        ):
            failures = self.login_rate(request, body.username)
            user = db.scalar(
                select(LearningUser).where(
                    LearningUser.username == body.username.lower()
                )
            )
            valid = password_valid(
                body.password, user.password_hash if user else self.dummy
            )
            if not user or not valid or not user.active:
                failures.append(time.monotonic())
                raise HTTPException(401, "Tên đăng nhập hoặc mật khẩu không đúng.")
            failures.clear()
            return self.issue(user, body, request, response, db)

        @router.post("/auth/register", status_code=201)
        def register(
            body: Registration,
            request: Request,
            response: Response,
            db: Session = Depends(db_dependency),
        ):
            failures = self.login_rate(request, body.username, "register")
            failures.append(time.monotonic())
            managers = list(
                db.scalars(
                    select(LearningUser).where(
                        LearningUser.role == "manager", LearningUser.active.is_(True)
                    )
                )
            )
            if len(managers) != 1:
                raise HTTPException(409, "Người quản lý chưa thiết lập hệ thống.")
            user = LearningUser(
                id=str(uuid.uuid4()),
                username=body.username.lower(),
                display_name=body.display_name,
                grade=body.grade,
                role=body.role,
                manager_id=managers[0].id,
                password_hash=password_hash(body.password),
            )
            db.add(user)
            try:
                db.commit()
            except IntegrityError:
                db.rollback()
                raise HTTPException(409, "Tên đăng nhập đã được sử dụng.") from None
            return self.issue(user, body, request, response, db)

        @router.post("/auth/logout", status_code=204)
        def logout(
            request: Request, response: Response, db: Session = Depends(db_dependency)
        ):
            token = self.token(request)
            if token:
                db.execute(
                    delete(LearningSession).where(
                        LearningSession.token_hash
                        == hashlib.sha256(token.encode()).hexdigest()
                    )
                )
                db.commit()
            response.delete_cookie(COOKIE, path="/")

        @router.post("/auth/password")
        def change_password(
            body: PasswordInput, request: Request, db: Session = Depends(db_dependency)
        ):
            user = self.required(request, db, True)
            failures = self.login_rate(request, user.username)
            if not password_valid(body.current_password, user.password_hash):
                failures.append(time.monotonic())
                raise HTTPException(400, "Mật khẩu hiện tại không đúng.")
            if body.new_password == body.current_password:
                raise HTTPException(422, "Mật khẩu mới phải khác mật khẩu cũ.")
            user.password_hash = password_hash(body.new_password)
            user.must_change_password = False
            token = self.token(request)
            db.execute(
                delete(LearningSession).where(
                    LearningSession.user_id == user.id,
                    LearningSession.token_hash
                    != hashlib.sha256(token.encode()).hexdigest(),
                )
            )
            db.add(
                AuditEvent(
                    actor=user.id, action="account.password_changed", target=user.id
                )
            )
            db.commit()
            return public_user(user)

        @router.post("/account/delete", status_code=204)
        def delete_self(
            body: DeleteAccountInput,
            request: Request,
            response: Response,
            db: Session = Depends(db_dependency),
        ):
            user = self.required(request, db, True)
            if user.role == "manager":
                raise HTTPException(
                    403, "Tài khoản quản lý hệ thống cần được bàn giao trước khi xóa."
                )
            failures = self.login_rate(request, user.username, "delete")
            if not password_valid(body.password, user.password_hash):
                failures.append(time.monotonic())
                raise HTTPException(400, "Mật khẩu xác nhận không đúng.")
            # Deleting a teacher never deletes their pupils' accounts or immutable results.
            for student in db.scalars(
                select(LearningUser).where(LearningUser.manager_id == user.id)
            ):
                student.manager_id = user.manager_id
            for scope in db.scalars(
                select(TeacherExam).where(TeacherExam.owner_id == user.id)
            ):
                exam = db.get(Exam, scope.exam_id)
                if exam:
                    db.delete(exam)
                db.delete(scope)
            for group in db.scalars(
                select(ClassroomGroup).where(ClassroomGroup.owner_id == user.id)
            ):
                db.execute(delete(GroupMember).where(GroupMember.group_id == group.id))
                db.delete(group)
            db.execute(delete(GroupMember).where(GroupMember.user_id == user.id))
            db.execute(
                delete(AttemptDraft).where(
                    AttemptDraft.attempt_id.in_(
                        select(AccountAttempt.attempt_id).where(
                            AccountAttempt.user_id == user.id
                        )
                    )
                )
            )
            db.execute(
                delete(Attempt).where(
                    Attempt.id.in_(
                        select(AccountAttempt.attempt_id).where(
                            AccountAttempt.user_id == user.id
                        )
                    )
                )
            )
            db.execute(delete(AccountAttempt).where(AccountAttempt.user_id == user.id))
            db.execute(delete(LearningRecord).where(LearningRecord.user_id == user.id))
            db.execute(
                delete(LearningSession).where(LearningSession.user_id == user.id)
            )
            from .reports import remove_account_reports

            remove_account_reports(db, user.id)
            db.delete(user)
            # Keep no account name/password or deleted answers in the deletion event.
            db.add(
                AuditEvent(
                    actor="deleted-account",
                    action="account.self_deleted",
                    target="account-and-learning-records",
                )
            )
            db.commit()
            response.delete_cookie(COOKIE, path="/")

        @router.get("/account/results")
        def my_results(request: Request, db: Session = Depends(db_dependency)):
            return self.records(db, self.required(request, db).id)

        @router.get("/classroom/students")
        def students(request: Request, db: Session = Depends(db_dependency)):
            owner = self.manager(request, db)
            rows = list(
                db.scalars(
                    select(LearningUser)
                    .where(
                        LearningUser.role == "student",
                        (
                            (
                                LearningUser.manager_id.in_(
                                    select(LearningUser.id).where(
                                        LearningUser.manager_id == owner.id,
                                        LearningUser.role == "teacher",
                                    )
                                )
                            )
                            if owner.role == "manager"
                            else LearningUser.id.is_(None)
                        )
                        | (LearningUser.manager_id == owner.id)
                        | LearningUser.id.in_(
                            select(GroupMember.user_id)
                            .join(
                                ClassroomGroup,
                                GroupMember.group_id == ClassroomGroup.id,
                            )
                            .where(ClassroomGroup.owner_id == owner.id)
                        ),
                    )
                    .order_by(LearningUser.username)
                )
            )
            output = []
            for user in rows:
                score = LearningRecord.payload["result"]["score"].as_float()
                maximum = LearningRecord.payload["result"]["max_score"].as_float()
                completed, average = db.execute(
                    select(
                        func.count(LearningRecord.attempt_id),
                        func.avg(
                            case((maximum > 0, 100 * score / maximum), else_=None)
                        ),
                    ).where(LearningRecord.user_id == user.id)
                ).one()
                output.append(
                    {
                        **public_user(user),
                        "completed": completed,
                        "average_percent": average,
                    }
                )
            return output

        @router.post("/classroom/students/bulk", status_code=201)
        def bulk(
            body: BulkInput, request: Request, db: Session = Depends(db_dependency)
        ):
            owner = self.manager(request, db)
            names = [s.username.lower() for s in body.students]
            if len(set(names)) != len(names) or db.scalar(
                select(LearningUser.id).where(LearningUser.username.in_(names))
            ):
                raise HTTPException(
                    409, "Có tên đăng nhập trùng. Chưa tạo tài khoản nào."
                )
            created = []
            for item in body.students:
                password = secrets.token_urlsafe(12)
                user = LearningUser(
                    id=str(uuid.uuid4()),
                    username=item.username.lower(),
                    display_name=item.display_name,
                    grade=item.grade,
                    role="student",
                    manager_id=owner.id,
                    password_hash=password_hash(password),
                    must_change_password=True,
                    active=True,
                )
                db.add(user)
                created.append({**public_user(user), "temporary_password": password})
            db.add(
                AuditEvent(
                    actor=owner.id,
                    action="account.bulk_created",
                    target=str(len(created)),
                )
            )
            try:
                db.commit()
            except IntegrityError:
                db.rollback()
                raise HTTPException(
                    409, "Tên đăng nhập đã được dùng. Chưa tạo tài khoản nào."
                ) from None
            return created

        @router.get("/classroom/students/{user_id}/results")
        def student_results(
            user_id: str, request: Request, db: Session = Depends(db_dependency)
        ):
            student = self.assigned(request, db, user_id)
            return dict(
                student=public_user(student), records=self.records(db, student.id)
            )

        @router.post("/classroom/students/{user_id}/reset-password")
        def reset(user_id: str, request: Request, db: Session = Depends(db_dependency)):
            student = self.assigned(request, db, user_id)
            owner = self.manager(request, db)
            if owner.role != "manager" and student.manager_id != owner.id:
                raise HTTPException(
                    403, "Chỉ người cấp tài khoản được đặt lại mật khẩu."
                )
            password = secrets.token_urlsafe(12)
            student.password_hash = password_hash(password)
            student.must_change_password = True
            db.execute(
                delete(LearningSession).where(LearningSession.user_id == student.id)
            )
            db.add(
                AuditEvent(
                    actor=student.manager_id,
                    action="account.password_reset",
                    target=student.id,
                )
            )
            db.commit()
            return dict(username=student.username, temporary_password=password)

        @router.delete("/classroom/students/{user_id}", status_code=204)
        def remove_student(
            user_id: str, request: Request, db: Session = Depends(db_dependency)
        ):
            student = self.assigned(request, db, user_id)
            owner = self.manager(request, db)
            if owner.role != "manager" and student.manager_id != owner.id:
                raise HTTPException(403, "Chỉ người cấp tài khoản được xóa tài khoản.")
            db.execute(delete(GroupMember).where(GroupMember.user_id == student.id))
            db.execute(
                delete(AttemptDraft).where(
                    AttemptDraft.attempt_id.in_(
                        select(AccountAttempt.attempt_id).where(
                            AccountAttempt.user_id == student.id
                        )
                    )
                )
            )
            db.execute(
                delete(Attempt).where(
                    Attempt.id.in_(
                        select(AccountAttempt.attempt_id).where(
                            AccountAttempt.user_id == student.id
                        )
                    )
                )
            )
            db.execute(
                delete(AccountAttempt).where(AccountAttempt.user_id == student.id)
            )
            db.execute(
                delete(LearningRecord).where(LearningRecord.user_id == student.id)
            )
            db.execute(
                delete(LearningSession).where(LearningSession.user_id == student.id)
            )
            db.add(
                AuditEvent(
                    actor=student.manager_id,
                    action="account.deleted",
                    target=student.id,
                )
            )
            from .reports import remove_account_reports

            remove_account_reports(db, student.id)
            db.delete(student)
            db.commit()

        def owned_group(group_id, request, db):
            owner = self.manager(request, db)
            group = db.get(ClassroomGroup, group_id)
            if not group or group.owner_id != owner.id:
                raise HTTPException(404, "Không tìm thấy nhóm.")
            return group

        @router.get("/classroom/groups/{group_id}/results.csv")
        def group_results_csv(
            group_id: str, request: Request, db: Session = Depends(db_dependency)
        ):
            # Authorize before reading membership or results. A group code is not access.
            group = owned_group(group_id, request, db)
            score = LearningRecord.payload["result"]["score"].as_float()
            maximum = LearningRecord.payload["result"]["max_score"].as_float()
            statistics = (
                select(
                    LearningRecord.user_id.label("user_id"),
                    func.count().label("completed"),
                    func.avg(
                        case((maximum > 0, 100 * score / maximum), else_=None)
                    ).label("average"),
                    func.max(LearningRecord.submitted_at).label("latest"),
                )
                .group_by(LearningRecord.user_id)
                .subquery()
            )
            rows = db.execute(
                select(
                    LearningUser,
                    statistics.c.completed,
                    statistics.c.average,
                    statistics.c.latest,
                )
                .join(GroupMember, GroupMember.user_id == LearningUser.id)
                .outerjoin(statistics, statistics.c.user_id == LearningUser.id)
                .where(GroupMember.group_id == group.id, LearningUser.role == "student")
                .order_by(LearningUser.username)
            )
            output = io.StringIO(newline="")
            writer = csv.writer(output)
            writer.writerow(
                [
                    "Nhóm",
                    "Tên đăng nhập",
                    "Họ và tên",
                    "Lớp",
                    "Số bài đã nộp",
                    "Điểm trung bình (%)",
                    "Nộp gần nhất (UTC)",
                ]
            )

            def cell(value):
                value = str(value)
                # Quoting CSV alone does not stop spreadsheet formula injection.
                return (
                    "'" + value
                    if value.lstrip().startswith(("=", "+", "-", "@"))
                    or value.startswith(("\t", "\r", "\n"))
                    else value
                )

            for user, completed, average, latest in rows:
                writer.writerow(
                    [
                        cell(group.name),
                        cell(user.username),
                        cell(user.display_name),
                        user.grade or "",
                        completed or 0,
                        "" if average is None else round(average, 2),
                        ""
                        if latest is None
                        else latest.isoformat()
                        + ("Z" if latest.tzinfo is None else ""),
                    ]
                )
            return Response(
                content="\ufeff" + output.getvalue(),
                media_type="text/csv; charset=utf-8",
                headers={
                    "Content-Disposition": 'attachment; filename="tu-hoc-111-bang-diem.csv"',
                    "Cache-Control": "no-store",
                    "X-Content-Type-Options": "nosniff",
                },
            )

        @router.get("/classroom/groups")
        def groups(request: Request, db: Session = Depends(db_dependency)):
            owner = self.required(request, db)
            query = select(ClassroomGroup)
            if owner.role == "student":
                query = query.where(
                    ClassroomGroup.id.in_(
                        select(GroupMember.group_id).where(
                            GroupMember.user_id == owner.id
                        )
                    )
                )
            else:
                query = query.where(ClassroomGroup.owner_id == owner.id)
            return [
                dict(
                    id=g.id,
                    name=g.name,
                    **({"join_code": g.join_code} if owner.role != "student" else {}),
                    student_ids=(
                        []
                        if owner.role == "student"
                        else list(
                            db.scalars(
                                select(GroupMember.user_id).where(
                                    GroupMember.group_id == g.id
                                )
                            )
                        )
                    ),
                )
                for g in db.scalars(query.order_by(ClassroomGroup.name))
            ]

        @router.post("/classroom/groups", status_code=201)
        def create_group(
            body: GroupInput, request: Request, db: Session = Depends(db_dependency)
        ):
            owner = self.manager(request, db)
            group = ClassroomGroup(
                id=str(uuid.uuid4()),
                owner_id=owner.id,
                name=body.name,
                join_code=secrets.token_hex(8),
            )
            db.add(group)
            db.commit()
            return dict(
                id=group.id, name=group.name, join_code=group.join_code, student_ids=[]
            )

        @router.post("/classroom/groups/join")
        def join_group(
            body: JoinGroupInput, request: Request, db: Session = Depends(db_dependency)
        ):
            user = self.required(request, db)
            if user.role != "student":
                raise HTTPException(403, "Chức năng dành cho học sinh.")
            group = db.scalar(
                select(ClassroomGroup).where(
                    ClassroomGroup.join_code == body.code.strip()
                )
            )
            if not group:
                raise HTTPException(404, "Mã nhóm không đúng.")
            if not db.get(GroupMember, (group.id, user.id)):
                db.add(GroupMember(group_id=group.id, user_id=user.id))
                db.commit()
            return dict(id=group.id, name=group.name)

        @router.post("/classroom/groups/{group_id}/members")
        def add_member(
            group_id: str,
            body: MemberInput,
            request: Request,
            db: Session = Depends(db_dependency),
        ):
            group = owned_group(group_id, request, db)
            student = db.scalar(
                select(LearningUser).where(
                    LearningUser.username == body.username.lower()
                )
            )
            owner = self.manager(request, db)
            if (
                not student
                or student.role != "student"
                or (owner.role != "manager" and student.manager_id != owner.id)
            ):
                raise HTTPException(
                    404,
                    "Chỉ thêm tài khoản bạn đã cấp; học sinh tự đăng ký dùng mã nhóm để tham gia.",
                )
            if not db.get(GroupMember, (group.id, student.id)):
                db.add(GroupMember(group_id=group.id, user_id=student.id))
                db.commit()
            return dict(user_id=student.id)

        @router.delete(
            "/classroom/groups/{group_id}/members/{user_id}", status_code=204
        )
        def remove_member(
            group_id: str,
            user_id: str,
            request: Request,
            db: Session = Depends(db_dependency),
        ):
            owned_group(group_id, request, db)
            db.execute(
                delete(GroupMember).where(
                    GroupMember.group_id == group_id, GroupMember.user_id == user_id
                )
            )
            db.commit()

        @router.delete("/classroom/groups/{group_id}", status_code=204)
        def delete_group(
            group_id: str, request: Request, db: Session = Depends(db_dependency)
        ):
            group = owned_group(group_id, request, db)
            db.execute(delete(GroupMember).where(GroupMember.group_id == group.id))
            db.delete(group)
            db.commit()

        return router
