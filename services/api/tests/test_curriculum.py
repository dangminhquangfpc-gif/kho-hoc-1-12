"""Content integrity and grading checks for the expanded practice bank."""

import json
from collections import Counter
from fractions import Fraction
from pathlib import Path

from khohoc.grading import grade, normalize
from khohoc.schemas import ExamInput, Question
from khohoc.library import DocumentInput

ROOT = Path(__file__).resolve().parents[3]


def load(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def test_bank_integrity_catalog_coverage_and_answer_keys():
    questions = [
        Question.model_validate(q)
        for filename in (
            "questions.json",
            "language_questions.json",
            "curriculum_questions.json",
            "subject_questions.json",
        )
        for q in load("data/seeds/" + filename)["questions"]
    ]
    by_id = {q.id: q for q in questions}
    assert len(by_id) == len(questions) == 1566
    assert len({normalize(q.question) for q in questions}) == len(questions)
    catalog = load("data/seeds/catalog.json")
    pairs = {(g["id"], s["id"]) for g in catalog["grades"] for s in g["subjects"]}
    assert {(q.grade, q.subject) for q in questions} == pairs
    exams = [
        ExamInput.model_validate(e)
        for filename in (
            "exams.json",
            "language_exams.json",
            "curriculum_exams.json",
            "subject_exams.json",
        )
        for e in load("data/seeds/" + filename)
    ]
    assert len(exams) == len({e.id for e in exams}) == 219
    assert {(e.grade, e.subject) for e in exams} == pairs
    used = set()
    for exam in exams:
        for qid in exam.question_ids:
            q = by_id[qid]
            assert (q.grade, q.subject) == (exam.grade, exam.subject)
            used.add(qid)
    assert {qid for qid in by_id if qid.startswith("kntt_")} <= used
    documents = [
        DocumentInput.model_validate(d)
        for d in load("data/library/documents.json")["documents"]
    ]
    assert len(documents) == len({d.id for d in documents}) == 199
    assert {(d.grade, d.subject) for d in documents} == pairs
    for q in questions:
        if q.id.startswith("kntt_"):
            assert q.textbook == "ket_noi_tri_thuc"
            assert grade(q, q.correct_answer)["score"] == 1
            incorrect = (
                ["999999999"]
                if q.type == "numeric"
                else [next(o.id for o in q.options if o.id not in q.correct_answer)]
            )
            assert grade(q, incorrect)["score"] == 0
    positions = Counter(
        q.correct_answer[0] for q in questions if q.id.startswith("kntt_core_")
    )
    assert set(positions) == {"A", "B", "C", "D"}


def test_independent_math_examples_and_fraction_equivalence():
    by_id = {
        q["id"]: Question.model_validate(q)
        for q in load("data/seeds/curriculum_questions.json")["questions"]
    }
    # Independently calculated examples span primary, lower and upper secondary.
    examples = {
        "1_chuc_don_vi_10": "30",
        "2_cong_co_nho_01": "40",
        "3_gia_tri_chu_so_10": "0",
        "4_tim_so_10": "23",
        "5_cong_thap_phan_01": "3.75",
        "6_bcnn_10": "66",
        "7_ti_le_nghich_10": "44",
        "8_thales_10": "15",
        "9_he_phuong_trinh_10": "14",
        "10_to_hop_10": "78",
        "11_logarit_10": "10",
        "12_mau_ghep_nhom_10": "12",
        "12_xac_suat_co_dieu_kien_10": "5/6",
    }
    for suffix, answer in examples.items():
        q = by_id["kntt_math_" + suffix]
        assert Fraction(q.correct_answer[0]) == Fraction(answer)
        assert grade(q, [answer])["score"] == 1
    assert grade(by_id["kntt_math_5_cong_thap_phan_01"], ["3,75"])["score"] == 1
    assert grade(by_id["kntt_math_7_xac_suat_don_gian_01"], ["6/12"])["score"] == 1
