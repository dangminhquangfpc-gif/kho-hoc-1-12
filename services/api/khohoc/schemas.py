from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, Field, model_validator

QuestionType = Literal[
    "single_choice", "multiple_choice", "true_false", "short_answer", "numeric", "essay"
]


class Option(BaseModel):
    id: str = Field(min_length=1, max_length=20)
    text: str = Field(min_length=1, max_length=2000)


class RubricCriterion(BaseModel):
    description: str = Field(min_length=1)
    points: Decimal = Field(gt=0, le=100)


class Question(BaseModel):
    id: str = Field(pattern=r"^[a-zA-Z0-9_-]{1,80}$")
    grade: int = Field(ge=1, le=12)
    subject: str = Field(min_length=1, max_length=60)
    topic: str = Field(min_length=1, max_length=100)
    textbook: Literal[
        "independent", "ket_noi_tri_thuc", "chan_troi_sang_tao", "canh_dieu"
    ] = "independent"
    type: QuestionType
    difficulty: Literal["easy", "medium", "hard"] = "easy"
    question: str = Field(min_length=1, max_length=10000)
    options: list[Option] = Field(default_factory=list, max_length=20)
    correct_answer: list[str] = Field(default_factory=list, max_length=20)
    max_score: Decimal = Field(gt=0, le=100)
    explanation: str = Field(min_length=1, max_length=10000)
    tolerance: Decimal = Field(default=Decimal(0), ge=0, le=100)
    unit: Literal["m", "cm", "km", "m2", "ha", "km2"] | None = None
    rubric: list[RubricCriterion] = Field(default_factory=list)
    source_type: Literal["original", "licensed", "link_only"] = "original"
    license: str = Field(min_length=1)
    rights_evidence: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_answers(self):
        ids = [o.id for o in self.options]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate option IDs")
        if self.type in ("single_choice", "multiple_choice"):
            if (
                len(ids) < 2
                or not self.correct_answer
                or not set(self.correct_answer) <= set(ids)
            ):
                raise ValueError("Choice answers must reference options")
            if self.type == "single_choice" and len(self.correct_answer) != 1:
                raise ValueError("Single choice requires one answer")
        elif self.type == "true_false":
            if (
                not ids
                or len(self.correct_answer) != len(ids)
                or any(a not in ("true", "false") for a in self.correct_answer)
            ):
                raise ValueError("True/false requires one boolean answer per statement")
        elif self.type == "essay":
            if not self.rubric or sum(r.points for r in self.rubric) != self.max_score:
                raise ValueError("Essay rubric must sum to max_score")
        elif not self.correct_answer:
            raise ValueError("Answer required")
        if (
            len(self.correct_answer) != len(set(self.correct_answer))
            and self.type != "true_false"
        ):
            raise ValueError("Duplicate answers")
        if self.type == "numeric":
            from .grading import number

            for expected in self.correct_answer:
                try:
                    number(expected, self.unit)
                except (ValueError, ZeroDivisionError, ArithmeticError) as exc:
                    raise ValueError("Invalid canonical numeric answer") from exc
        return self


class ImportBatch(BaseModel):
    questions: list[Question] = Field(min_length=1, max_length=500)


class Submission(BaseModel):
    draft_revision: int | None = Field(default=None, ge=0, le=2147483646)
    answers: dict[str, list[str]] = Field(max_length=100)


class ExamInput(BaseModel):
    id: str = Field(pattern=r"^[a-zA-Z0-9_-]{1,80}$")
    title: str = Field(min_length=1, max_length=200)
    grade: int = Field(ge=1, le=12)
    subject: str = Field(min_length=1, max_length=60)
    textbook: Literal[
        "independent", "ket_noi_tri_thuc", "chan_troi_sang_tao", "canh_dieu"
    ] = "independent"
    topic: str = Field(default="tong_hop", min_length=1, max_length=100)
    question_ids: list[str] = Field(min_length=1, max_length=100)
    duration_minutes: int = Field(ge=1, le=180)

    @model_validator(mode="after")
    def unique_questions(self):
        if len(self.question_ids) != len(set(self.question_ids)):
            raise ValueError("Duplicate questions")
        return self
