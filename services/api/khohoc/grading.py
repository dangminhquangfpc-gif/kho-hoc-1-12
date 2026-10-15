import re
import unicodedata
from decimal import Decimal, InvalidOperation
from fractions import Fraction
from .schemas import Question

# No eval, symbolic execution, or LLM for numeric answers.
FACTORS = {
    "m": ("length", Decimal(1)),
    "cm": ("length", Decimal(".01")),
    "km": ("length", Decimal(1000)),
    "m2": ("area", Decimal(1)),
    "ha": ("area", Decimal(10000)),
    "km2": ("area", Decimal(1000000)),
}


def normalize(text: str) -> str:
    return " ".join(unicodedata.normalize("NFC", text).casefold().split())


def number(text: str, expected_unit: str | None = None) -> Decimal:
    match = re.fullmatch(
        r"\s*([+-]?\d+(?:[.,]\d+)?(?:/[+-]?\d+)?)\s*([a-zA-Z²0-9]*)\s*", text
    )
    if not match:
        raise ValueError("Invalid number")
    raw, unit = match.groups()
    fraction = Fraction(raw.replace(",", "."))
    value = Decimal(fraction.numerator) / Decimal(fraction.denominator)
    unit = unit.replace("²", "2").lower()
    if unit:
        if not expected_unit or unit not in FACTORS or expected_unit not in FACTORS:
            raise ValueError("Unsupported unit")
        if FACTORS[unit][0] != FACTORS[expected_unit][0]:
            raise ValueError("Incompatible unit")
        value *= FACTORS[unit][1] / FACTORS[expected_unit][1]
    return value


def result_context(q: Question) -> dict:
    choices = {o.id: o.text for o in q.options}
    if q.type in ("single_choice", "multiple_choice"):
        display = [choices[a] for a in q.correct_answer]
    elif q.type == "true_false":
        display = ["Đúng" if a == "true" else "Sai" for a in q.correct_answer]
    else:
        display = q.correct_answer
    return {"question": q.question, "answer_display": display}


def grade(q: Question, answer: list[str]) -> dict:
    score = Decimal(0)
    status = "graded"
    if q.type == "essay":
        status = "needs_manual_review"
        return {
            **result_context(q),
            "question_id": q.id,
            "score": None,
            "max_score": float(q.max_score),
            "status": status,
            "explanation": q.explanation,
            "correct_answer": q.correct_answer,
        }
    if q.type in ("single_choice", "multiple_choice"):
        valid = len(answer) == len(set(answer)) and set(answer) == set(q.correct_answer)
        if q.type == "single_choice":
            valid = valid and len(answer) == 1
        score = q.max_score if valid else Decimal(0)
    elif q.type == "true_false":
        if len(answer) == len(q.correct_answer):
            score = (
                q.max_score
                * Decimal(sum(a == b for a, b in zip(answer, q.correct_answer)))
                / len(answer)
            )
    elif q.type == "short_answer":
        score = (
            q.max_score
            if len(answer) == 1
            and normalize(answer[0]) in {normalize(a) for a in q.correct_answer}
            else Decimal(0)
        )
    elif q.type == "numeric" and len(answer) == 1:
        try:
            actual = number(answer[0], q.unit)
            score = (
                q.max_score
                if any(
                    abs(actual - number(a, q.unit)) <= q.tolerance
                    for a in q.correct_answer
                )
                else Decimal(0)
            )
        except (ValueError, ZeroDivisionError, InvalidOperation):
            pass
    return {
        **result_context(q),
        "question_id": q.id,
        "score": float(score),
        "max_score": float(q.max_score),
        "status": status,
        "explanation": q.explanation,
        "correct_answer": q.correct_answer,
    }
