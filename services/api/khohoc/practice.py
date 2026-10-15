"""Guest practice assembled exclusively from published, rights-cleared questions."""

import json
import secrets
import uuid
import unicodedata
from collections import Counter
from functools import lru_cache
from pathlib import Path
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlalchemy import select
from sqlalchemy.orm import Session

from .catalog import subjects_for_grade
from .models import ContentQuestion, LearningRecord, Exam, TeacherExam, ClassroomGroup
from .content_fixes import QUESTION_REPLACEMENTS

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


LOCALIZED_TOPICS = {
    "toc_do": "Tốc độ",
    "khoi_luong_rieng": "Khối lượng riêng",
    "dinh_luat_ohm": "Định luật Ohm",
    "dinh_luat_newton": "Định luật Newton",
    "cong_dien": "Công của lực điện",
    "dinh_luat_boyle": "Định luật Boyle",
    "do_khoi_luong": "Đo và đổi đơn vị khối lượng",
    "am_van": "Âm và vần",
    "bai_toan": "Bài toán",
    "bien_phap_tu_tu": "Biện pháp tu từ",
    "cau_tao_so": "Cấu tạo số",
    "dai_so": "Đại số",
    "danh_gia_bang_chung": "Đánh giá bằng chứng",
    "dau_cau": "Dấu câu",
    "day_so": "Dãy số",
    "doc_hieu": "Đọc hiểu",
    "doc_tieng": "Đọc tiếng",
    "lap_luan": "Lập luận",
    "lien_ket_lap_luan": "Liên kết lập luận",
    "loi_dan": "Lời dẫn",
    "luan_cu": "Luận cứ",
    "luan_de": "Luận đề",
    "mu_logarit": "Mũ và logarit",
    "ngoi_ke": "Ngôi kể",
    "nguyen_ham": "Nguyên hàm",
    "phan_biet_y_kien_su_kien": "Phân biệt ý kiến và sự kiện",
    "phep_cong": "Phép cộng",
    "phep_lien_ket": "Phép liên kết",
    "phep_tru": "Phép trừ",
    "quan_he_tu": "Quan hệ từ",
    "so_tu_nhien": "Số tự nhiên",
    "suy_luan": "Suy luận",
    "thanh_phan_cau": "Thành phần câu",
    "thoi_gian": "Thời gian",
    "thong_ke": "Thống kê",
    "toa_do": "Tọa độ",
    "tu_trai_nghia": "Từ trái nghĩa",
    "ATP": "ATP",
    "DNA": "DNA",
    "pH": "pH",
    "academic_reading": "Đọc hiểu học thuật",
    "reading": "Đọc hiểu tiếng Anh",
    "reading_evidence": "Đọc hiểu: dẫn chứng",
    "reading_inference": "Đọc hiểu: suy luận",
    "reading_main_idea": "Đọc hiểu: ý chính",
    "reading_scope": "Đọc hiểu: phạm vi",
    "vocabulary": "Từ vựng",
    "be": "Động từ to be",
    "be_verb": "Động từ to be",
    "greetings": "Chào hỏi",
    "numbers": "Số đếm",
    "past_simple": "Thì quá khứ đơn",
    "present_simple": "Thì hiện tại đơn",
    "present_perfect": "Thì hiện tại hoàn thành",
    "past_perfect": "Thì quá khứ hoàn thành",
    "plural_nouns": "Danh từ số nhiều",
    "possessive_adjectives": "Tính từ sở hữu",
    "prepositions": "Giới từ",
    "comparatives": "So sánh hơn",
    "conditionals": "Câu điều kiện",
    "first_conditional": "Câu điều kiện loại 1",
    "second_conditional": "Câu điều kiện loại 2",
    "third_conditional": "Câu điều kiện loại 3",
    "passive_voice": "Câu bị động",
    "relative_clauses": "Mệnh đề quan hệ",
    "reported_speech": "Câu tường thuật",
    "modals": "Động từ khuyết thiếu",
    "concession": "Mệnh đề nhượng bộ",
    "cohesion": "Liên kết văn bản",
}


MATH5_ALIASES = {
    "chuyen_dong": "speed",
    "van_toc": "speed",
    "cong_thap_phan": "add_decimal",
    "nhan_thap_phan": "multiply_decimal",
    "ti_so_phan_tram": "ratio",
    "phan_tram": "ratio",
    "dien_tich_tam_giac": "triangle",
    "the_tich_hop": "box_volume",
    "phan_so": "fraction_ops",
    "dien_tich": "plane",
    "hinh_hoc": "plane",
    "so_thap_phan": "decimal",
    "do_dai": "measure_decimal",
    "thong_ke": "data",
}


def canonical_topic(grade, subject, topic):
    if grade == 1 and subject == "toan":
        topic = {
            "cau_tao_so": "chuc_don_vi",
            "phep_cong": "cong_trong_20",
            "phep_tru": "tru_trong_20",
            "so_tu_nhien": "dem_so",
        }.get(topic, topic)
    if subject == "tieng_anh":
        topic = topic.replace(" ", "_").lower()
        if topic == "be_verb":
            topic = "be"
    return (
        MATH5_ALIASES.get(topic, topic) if grade == 5 and subject == "toan" else topic
    )


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
    topic = canonical_topic(grade, subject, topic)
    if topic in LOCALIZED_TOPICS:
        return LOCALIZED_TOPICS[topic]
    if subject == "toan" and topic in MATH_TOPICS:
        return MATH_TOPICS[topic]
    legacy = {
        "chuyen_dong": "Chuyển động",
        "hinh_hoc": "Hình học",
        "so_hoc": "Số học",
        "phan_so": "Phân số",
        "ham_so": "Hàm số",
        "dao_ham": "Đạo hàm",
        "tich_phan": "Tích phân",
        "phuong_trinh": "Phương trình",
        "xac_suat": "Xác suất",
        "tong_hop": "Ôn tổng hợp",
        "kien_thuc_nen": "Kiến thức nền",
    }
    if topic in legacy:
        return legacy[topic]
    return topic_names().get(
        (grade, subject, topic), topic.replace("_", " ").capitalize()
    )


class PracticeInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    grade: int = Field(ge=1, le=12)
    subject: str = Field(min_length=1, max_length=60)
    count: int = Field(default=10, ge=1, le=50)
    topic: str | None = Field(default=None, min_length=1, max_length=100)
    topics: list[str] = Field(default_factory=list, max_length=20)
    textbook: (
        Literal["independent", "ket_noi_tri_thuc", "chan_troi_sang_tao", "canh_dieu"]
        | None
    ) = None
    difficulty: Literal["easy", "medium", "hard"] | None = None
    group_id: str | None = Field(default=None, min_length=1, max_length=36)
    question_ids: list[str] | None = Field(default=None, min_length=1, max_length=50)

    @model_validator(mode="after")
    def validate_selection(self):
        if self.subject not in {s["id"] for s in subjects_for_grade(self.grade)}:
            raise ValueError("Subject does not belong to grade")
        if self.topic is not None and self.topics:
            raise ValueError("Use topic or topics, not both")
        if len(set(self.topics)) != len(self.topics) or any(
            not 1 <= len(t) <= 100 for t in self.topics
        ):
            raise ValueError("Topics must be unique and valid")
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
        and row.id not in QUESTION_REPLACEMENTS
    ]


def create_practice_router(*, db, create_attempt, accounts):
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
        topics = Counter(canonical_topic(grade, subject, q["topic"]) for q in questions)
        groups = Counter(
            (
                canonical_topic(grade, subject, q["topic"]),
                q["difficulty"],
                q.get("textbook", "independent"),
            )
            for q in questions
        )
        return dict(
            grade=grade,
            subject=subject,
            total=len(questions),
            topics=[
                dict(id=key, name=topic_name(grade, subject, key), count=count)
                for key, count in sorted(
                    topics.items(),
                    key=lambda pair: "".join(
                        c
                        for c in unicodedata.normalize(
                            "NFD",
                            topic_name(grade, subject, pair[0])
                            .lower()
                            .replace("đ", "d"),
                        )
                        if not unicodedata.combining(c)
                    ),
                )
            ],
            groups=[
                dict(topic=t, difficulty=d, textbook=b, count=count)
                for (t, d, b), count in sorted(groups.items())
            ],
        )

    @router.post("/practice-attempts", status_code=201)
    def start(body: PracticeInput, request: Request, session: Session = Depends(db)):
        user = accounts.required(request, session)
        if user.role not in {"teacher", "manager"}:
            if body.question_ids is None:
                raise HTTPException(
                    403, "Học sinh làm đề có sẵn; chỉ giáo viên được tạo đề."
                )
            # Explicit IDs are only a student's own previously missed questions.
            # This must not become a way to bypass the teacher-only generator.
            eligible = set()
            for record in session.scalars(
                select(LearningRecord).where(LearningRecord.user_id == user.id)
            ):
                for detail in record.payload.get("result", {}).get("details", []):
                    if (
                        detail.get("score") is not None
                        and detail["score"] < detail["max_score"]
                    ):
                        eligible.add(detail["question_id"])
            if not set(body.question_ids).issubset(eligible):
                raise HTTPException(
                    403, "Chỉ được ôn lại câu chưa đúng trong kết quả của chính bạn."
                )
        if body.group_id:
            group = session.get(ClassroomGroup, body.group_id)
            if (
                user.role not in {"teacher", "manager"}
                or not group
                or group.owner_id != user.id
            ):
                raise HTTPException(404, "Không tìm thấy nhóm của bạn.")
        requested_topics = list(
            dict.fromkeys(
                canonical_topic(body.grade, body.subject, t)
                for t in (body.topics or ([body.topic] if body.topic else []))
            )
        )
        candidates = [
            q
            for q in available_questions(session, body.grade, body.subject)
            if (
                not requested_topics
                or canonical_topic(body.grade, body.subject, q["topic"])
                in requested_topics
            )
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
            rng = secrets.SystemRandom()
            if requested_topics and body.count < len(requested_topics):
                raise HTTPException(
                    422, "Choose at least one question per selected topic"
                )
            pools = {
                t: [
                    q
                    for q in candidates
                    if canonical_topic(body.grade, body.subject, q["topic"]) == t
                ]
                for t in requested_topics
            }
            if any(not pool for pool in pools.values()):
                raise HTTPException(422, "A selected topic has no matching questions")
            selected = []
            for pool in pools.values():
                rng.shuffle(pool)
            # Round-robin keeps every chosen topic represented when possible.
            if pools:
                while len(selected) < body.count:
                    for pool in pools.values():
                        if pool and len(selected) < body.count:
                            selected.append(pool.pop())
                rng.shuffle(selected)
            else:
                selected = rng.sample(candidates, body.count)
        subject_name = next(
            s["name"] for s in subjects_for_grade(body.grade) if s["id"] == body.subject
        )
        label = "Ôn câu chưa đúng" if body.question_ids is not None else "Đề tự tạo"
        title = f"{subject_name} {body.grade} · {label}"
        if body.topics:
            title += f" · {len(body.topics)} chủ đề"
        elif body.topic:
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
        if body.group_id and body.question_ids is None:
            exam["title"] = (
                f"{subject_name} {body.grade} · Đề của {user.display_name} · {group.name}"
            )
            session.add(Exam(id=exam["id"], payload=exam, state="published"))
            session.add(
                TeacherExam(exam_id=exam["id"], owner_id=user.id, group_id=group.id)
            )
            # The following create_attempt commits the exam and attempt atomically.
        return create_attempt(
            session,
            exam,
            selected,
            body.model_dump(mode="json"),
            user_id=user.id if user else None,
        )

    return router
