"""Guest practice assembled exclusively from published, rights-cleared questions."""

import json
import secrets
import uuid
from collections import Counter
from functools import lru_cache
from pathlib import Path
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlalchemy import select
from sqlalchemy.orm import Session

from .catalog import subjects_for_grade
from .models import ContentQuestion

MATH_TOPICS = {
    "natural": "Số tự nhiên",
    "operations": "Thứ tự thực hiện phép tính",
    "fraction": "Rút gọn phân số",
    "decimal_fraction": "Phân số thập phân",
    "fraction_ops": "Phép tính với phân số",
    "unlike_fraction": "Phân số khác mẫu",
    "mixed": "Hỗn số",
    "plane": "Chu vi và diện tích",
    "decimal": "Số thập phân",
    "compare_decimal": "So sánh số thập phân",
    "measure_decimal": "Số đo thập phân",
    "round": "Làm tròn số",
    "land_area": "Đơn vị đo diện tích đất",
    "area_units": "Đổi đơn vị diện tích",
    "add_decimal": "Cộng số thập phân",
    "subtract_decimal": "Trừ số thập phân",
    "multiply_decimal": "Nhân số thập phân",
    "divide_decimal": "Chia số thập phân",
    "powers_ten": "Nhân chia với lũy thừa của 10",
    "triangle": "Diện tích tam giác",
    "trapezoid": "Diện tích hình thang",
    "circle": "Hình tròn",
    "drawing": "Vẽ và ghép hình",
    "ratio": "Tỉ số phần trăm",
    "map": "Tỉ lệ bản đồ",
    "sum_ratio": "Tìm hai số biết tổng và tỉ số",
    "difference_ratio": "Tìm hai số biết hiệu và tỉ số",
    "percentage_value": "Giá trị phần trăm",
    "calculator": "Sử dụng máy tính",
    "volume": "Thể tích",
    "volume_units": "Đơn vị thể tích",
    "nets": "Hình khai triển",
    "box_area": "Diện tích hình hộp chữ nhật",
    "cube_area": "Diện tích hình lập phương",
    "box_volume": "Thể tích hình hộp chữ nhật",
    "cube_volume": "Thể tích hình lập phương",
    "time_units": "Đơn vị thời gian",
    "time_add": "Cộng trừ thời gian",
    "time_multiply": "Nhân chia thời gian",
    "speed": "Quãng đường và vận tốc",
    "data": "Thu thập số liệu",
    "pie": "Biểu đồ hình quạt",
    "frequency": "Tỉ số số lần xuất hiện",
}


@lru_cache(maxsize=1)
def topic_names():
    root = Path(__file__).resolve().parents[3] / "data/seeds"
    names = {}
    for name in (
        "exams.json",
        "language_exams.json",
        "curriculum_exams.json",
        "subject_exams.json",
    ):
        path = root / name
        if not path.exists():
            continue
        for exam in json.loads(path.read_text(encoding="utf-8")):
            parts = exam["title"].split(" · ")
            if len(parts) > 1:
                names[
                    (exam["grade"], exam["subject"], exam.get("topic", "tong_hop"))
                ] = parts[1]
    return names


def topic_name(grade, subject, topic):
    if subject == "toan" and topic in MATH_TOPICS:
        return MATH_TOPICS[topic]
    return topic_names().get(
        (grade, subject, topic), topic.replace("_", " ").capitalize()
    )


class PracticeInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    grade: int = Field(ge=1, le=12)
    subject: str = Field(min_length=1, max_length=60)
    count: int = Field(default=10, ge=1, le=50)
    topic: str | None = Field(default=None, min_length=1, max_length=100)
    textbook: (
        Literal["independent", "ket_noi_tri_thuc", "chan_troi_sang_tao", "canh_dieu"]
        | None
    ) = None
    difficulty: Literal["easy", "medium", "hard"] | None = None
    question_ids: list[str] | None = Field(default=None, min_length=1, max_length=50)

    @model_validator(mode="after")
    def validate_selection(self):
        if self.subject not in {s["id"] for s in subjects_for_grade(self.grade)}:
            raise ValueError("Subject does not belong to grade")
        if self.question_ids is not None:
            if (
                len(set(self.question_ids)) != len(self.question_ids)
                or len(self.question_ids) != self.count
            ):
                raise ValueError("Selected IDs must be unique and match count")
            if any(not 1 <= len(qid) <= 80 for qid in self.question_ids):
                raise ValueError("Invalid question ID")
        return self


def available_questions(session, grade, subject):
    return [
        row.payload
        for row in session.scalars(
            select(ContentQuestion).where(
                ContentQuestion.state == "published",
                ContentQuestion.rights_confirmed.is_(True),
            )
        )
        if row.payload["grade"] == grade
        and row.payload["subject"] == subject
        and row.payload["type"] != "essay"
        and row.payload.get("source_type") != "link_only"
    ]


def create_practice_router(*, db, create_attempt):
    router = APIRouter()

    @router.get("/practice-options")
    def options(
        grade: int = Query(ge=1, le=12),
        subject: str = Query(min_length=1, max_length=60),
        session: Session = Depends(db),
    ):
        if subject not in {s["id"] for s in subjects_for_grade(grade)}:
            raise HTTPException(422, "Subject does not belong to grade")
        questions = available_questions(session, grade, subject)
        topics = Counter(q["topic"] for q in questions)
        groups = Counter(
            (q["topic"], q["difficulty"], q.get("textbook", "independent"))
            for q in questions
        )
        return dict(
            grade=grade,
            subject=subject,
            total=len(questions),
            topics=[
                dict(id=key, name=topic_name(grade, subject, key), count=count)
                for key, count in sorted(topics.items())
            ],
            groups=[
                dict(topic=t, difficulty=d, textbook=b, count=count)
                for (t, d, b), count in sorted(groups.items())
            ],
        )

    @router.post("/practice-attempts", status_code=201)
    def start(body: PracticeInput, session: Session = Depends(db)):
        candidates = [
            q
            for q in available_questions(session, body.grade, body.subject)
            if (body.topic is None or q["topic"] == body.topic)
            and (
                body.textbook is None
                or q.get("textbook", "independent") == body.textbook
            )
            and (body.difficulty is None or q["difficulty"] == body.difficulty)
        ]
        if body.question_ids is not None:
            by_id = {q["id"]: q for q in candidates}
            if any(qid not in by_id for qid in body.question_ids):
                raise HTTPException(
                    409,
                    "Selected questions are no longer available; choose another practice set",
                )
            selected = [by_id[qid] for qid in body.question_ids]
        else:
            if len(candidates) < body.count:
                raise HTTPException(
                    422, f"Only {len(candidates)} matching questions are available"
                )
            selected = secrets.SystemRandom().sample(candidates, body.count)
        subject_name = next(
            s["name"] for s in subjects_for_grade(body.grade) if s["id"] == body.subject
        )
        label = "Ôn câu chưa đúng" if body.question_ids is not None else "Đề tự tạo"
        title = f"{subject_name} {body.grade} · {label}"
        if body.topic:
            title += " · " + topic_name(body.grade, body.subject, body.topic)
        selected_books = {q.get("textbook", "independent") for q in selected}
        book = body.textbook or (
            next(iter(selected_books)) if len(selected_books) == 1 else "independent"
        )
        exam = dict(
            id="custom_" + uuid.uuid4().hex,
            title=title,
            grade=body.grade,
            subject=body.subject,
            textbook=book,
            topic=body.topic or "tong_hop",
            duration_minutes=min(120, max(10, body.count * 2)),
            question_ids=[q["id"] for q in selected],
        )
        return create_attempt(session, exam, selected, body.model_dump(mode="json"))

    return router
