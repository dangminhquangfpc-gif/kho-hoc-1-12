"""Local classroom accounts. Opaque sessions, server grading, no hosted auth claims."""

import base64
import hashlib
import hmac
import secrets
import time
import uuid
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import delete, select, func, case
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .models import (
    AccountAttempt,
    AuditEvent,
    LearningRecord,
    LearningSession,
    LearningUser,
    Attempt,
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
    display_name: str = Field(min_length=1, max_length=80)
    grade: int | None = Field(default=None, ge=1, le=12)


class StudentInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    username: str = Field(pattern=r"^[a-zA-Z0-9_.-]{3,40}$")
    display_name: str = Field(min_length=1, max_length=80)
    grade: int | None = Field(default=None, ge=1, le=12)


class BulkInput(BaseModel):
    students: list[StudentInput] = Field(min_length=1, max_length=50)


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
        if user.role != "manager":
            raise HTTPException(403, "Chỉ người quản lý được dùng chức năng này.")
        return user

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
        if not student or student.role != "student" or student.manager_id != manager.id:
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
                role="student",
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
                        LearningUser.manager_id == owner.id,
                        LearningUser.role == "student",
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
            db.delete(student)
            db.commit()

        return router
