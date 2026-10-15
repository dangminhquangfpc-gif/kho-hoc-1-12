import json
import re
from fractions import Fraction
from pathlib import Path
from collections import Counter

from khohoc.schemas import Question, ExamInput
from khohoc.grading import normalize, grade

ROOT = Path(__file__).resolve().parents[3] / "data/seeds"


def expanded():
    return [
        q
        for file in ("multigrade_questions.json", "subject_practice_questions.json")
        for q in json.loads((ROOT / file).read_text())["questions"]
    ]


def test_expanded_bank_has_unique_prompts_valid_answers_and_choices():
    questions = expanded()
    assert len(questions) == 5246
    assert len({q["id"] for q in questions}) == len(questions)
    assert len({normalize(q["question"]) for q in questions}) == len(questions)
    old = {
        normalize(q["question"])
        for path in ROOT.glob("*questions.json")
        if path.name
        not in {"multigrade_questions.json", "subject_practice_questions.json"}
        for q in json.loads(path.read_text())["questions"]
    }
    for raw in questions:
        q = Question.model_validate(raw)
        assert normalize(q.question) not in old
        assert q.source_type == "original" and q.license == "original_content"
        assert grade(q, q.correct_answer)["score"] == 1
        if q.type == "single_choice":
            assert len({normalize(o.text) for o in q.options}) == 4
    counts = Counter(q["grade"] for q in questions if q["subject"] == "toan")
    assert set(counts) == set(range(1, 13)) - {5}
    assert min(counts.values()) >= 300


def test_new_complete_exams_reference_real_questions_in_same_grade_and_subject():
    bank = {q["id"]: q for q in expanded()}
    exams = [
        ExamInput.model_validate(e)
        for name in ("multigrade_exams.json", "subject_practice_exams.json")
        for e in json.loads((ROOT / name).read_text())
    ]
    assert len(exams) == 164
    assert len({tuple(e.question_ids) for e in exams}) == 164
    for e in exams:
        assert len(e.question_ids) >= 10
        assert len(set(e.question_ids)) == len(e.question_ids)
        for qid in e.question_ids:
            assert (bank[qid]["grade"], bank[qid]["subject"]) == (e.grade, e.subject)


def test_new_primary_arithmetic_and_probability_domains():
    checked = 0
    for q in expanded():
        if q["grade"] == 1 and q["topic"] in {"cong_trong_20", "tru_trong_20"}:
            a, op, b = re.fullmatch(
                r"Tính (\d+) ([+−]) (\d+)\.", q["question"]
            ).groups()
            a, b = int(a), int(b)
            expected = a + b if op == "+" else a - b
            assert 0 <= expected <= 20
            assert Fraction(q["correct_answer"][0]) == expected
            checked += 1
        if q["subject"] == "toan" and q["topic"] in {
            "bien_co_doc_lap",
            "xac_suat_co_dieu_kien",
            "xac_suat",
            "xac_suat_don_gian",
        }:
            assert 0 <= Fraction(q["correct_answer"][0]) <= 1
        if q["grade"] == 7 and q["topic"] == "goc_tam_giac":
            assert 0 < Fraction(q["correct_answer"][0]) < 180
    assert checked >= 100


def test_new_science_speed_and_density_answers_are_dimensionally_correct():
    checked = 0
    for q in expanded():
        if q["topic"] == "toc_do":
            distance, seconds = map(
                int, re.search(r"đi (\d+) m trong (\d+) s", q["question"]).groups()
            )
            assert Fraction(distance, seconds) == Fraction(q["correct_answer"][0])
            checked += 1
        if q["topic"] == "khoi_luong_rieng":
            mass, volume = map(
                int,
                re.search(
                    r"khối lượng (\d+) g, thể tích (\d+) cm", q["question"]
                ).groups(),
            )
            assert Fraction(mass, volume) == Fraction(q["correct_answer"][0])
            checked += 1
    assert checked == 80
