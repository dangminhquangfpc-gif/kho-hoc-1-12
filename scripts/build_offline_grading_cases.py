"""Generate device-grader golden cases using the actual Python grading service.

This is a development fixture, not an additional answer bank shipped in the app.
The all-question oracle refers to authored content already in content.json so it
can verify every active question without duplicating its text or explanation.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "services/api"))
sys.path.insert(0, str(ROOT / "scripts"))

from build_offline_bundle import QUESTION_FILES, canonical_records  # noqa: E402
from khohoc.content_fixes import QUESTION_REPLACEMENTS  # noqa: E402
from khohoc.grading import grade  # noqa: E402
from khohoc.schemas import Question  # noqa: E402

DEFAULT_OUTPUT = ROOT / "data/offline/grading_cases.json"


def question(kind: str, **overrides) -> Question:
    payload = {
        "id": "parity_" + kind,
        "grade": 5,
        "subject": "toan",
        "topic": "kiem_thu",
        "type": kind,
        "question": "Câu hỏi kiểm tra sự nhất quán của bộ chấm ngoại tuyến.",
        "max_score": "1",
        "correct_answer": ["12"],
        "explanation": "Dữ liệu kiểm thử, không phải nội dung cho học sinh.",
        "license": "original_content",
        "rights_evidence": "Tự biên soạn để kiểm thử bộ chấm điểm.",
    }
    payload.update(overrides)
    return Question.model_validate(payload)


def edge_cases() -> list[dict]:
    cases = []

    def add(name: str, q: Question, answer: list[str]):
        cases.append(
            {
                "name": name,
                "question": q.model_dump(mode="json"),
                "answer": answer,
                "expected": grade(q, answer),
            }
        )

    integer = question("numeric")
    for label, value in (
        ("plain", "12"),
        ("explicit_plus", "+12"),
        ("surrounding_space", " \t12\n"),
        ("decimal_comma", "12,0"),
        ("decimal_dot", "12.000"),
        ("fraction", "24/2"),
        ("positive_denominator", "24/+2"),
        ("double_negative_fraction", "-24/-2"),
        ("zero_prefix", "00012"),
        ("arabic_indic_digits", "١٢"),
        ("fullwidth_digits", "１２"),
        ("unicode_nbsp", "\u00a012\u00a0"),
        ("wrong", "13"),
        ("negative", "-12"),
        ("unicode_minus_invalid", "−12"),
        ("empty", ""),
        ("spaces_only", " \t\n"),
        ("exponent_invalid", "12e0"),
        ("grouping_space_invalid", "1 2"),
        ("leading_decimal_invalid", ".12"),
        ("trailing_decimal_invalid", "12."),
        ("mixed_separator_invalid", "1,2.0"),
        ("zero_denominator", "12/0"),
        ("decimal_fraction_numerator_invalid", "24.0/2"),
        ("decimal_fraction_denominator_invalid", "24/2.0"),
        ("internal_fraction_space_invalid", "24 / 2"),
        ("expression_invalid", "6+6"),
        ("nan_invalid", "NaN"),
        ("infinite_invalid", "Infinity"),
        ("unsupported_suffix", "12kg"),
        ("unrequested_unit", "12m"),
    ):
        add("numeric_" + label, integer, [value])
    add("numeric_no_answer", integer, [])
    add("numeric_two_answers", integer, ["12", "12"])
    add("numeric_python_integer_digit_limit", integer, ["0" * 5000 + "12"])

    tolerant = question("numeric", correct_answer=["1"], tolerance="0.1")
    for label, value in (
        ("lower_boundary", "0.9"),
        ("upper_boundary", "1,1"),
        ("inside", "1.099999999999999999"),
        ("above_boundary", "1.100000000000000001"),
        ("below_boundary", "0.899999999999999999"),
        ("fraction_boundary", "11/10"),
    ):
        add("tolerance_" + label, tolerant, [value])
    add(
        "numeric_multiple_expected_answers",
        question("numeric", correct_answer=["1", "2"]),
        ["2"],
    )
    add(
        "numeric_fraction_canonical",
        question("numeric", correct_answer=["1/3"], tolerance="0.000001"),
        ["0,333333"],
    )
    add(
        "numeric_noninteger_max_score",
        question("numeric", max_score="2.75"),
        ["12"],
    )
    add(
        "numeric_internal_scientific_tolerance",
        question("numeric", correct_answer=["1"], tolerance="0.0000001"),
        ["1.0000001"],
    )
    for label, expected, actual in (
        ("third_rounded_28", "1/3", "0.3333333333333333333333333333"),
        ("two_thirds_rounded_28", "2/3", "0.6666666666666666666666666667"),
        ("third_longer_input", "1/3", "0.333333333333333333333333333333333333"),
        (
            "integer_rounded_28",
            "12345678901234567890123456789",
            "12345678901234567890123456790",
        ),
        (
            "half_even_integer_down",
            "10000000000000000000000000005",
            "10000000000000000000000000000",
        ),
        (
            "half_even_integer_up",
            "10000000000000000000000000015",
            "10000000000000000000000000020",
        ),
    ):
        add(
            "decimal_context_" + label,
            question("numeric", correct_answer=[expected]),
            [actual],
        )

    length_answers = {"m": "1000", "cm": "100000", "km": "1"}
    area_answers = {"m2": "10000", "ha": "1", "km2": "0.01"}
    for dimensions in (length_answers, area_answers):
        for unit, expected in dimensions.items():
            q = question("numeric", unit=unit, correct_answer=[expected])
            add("unit_" + unit + "_implicit", q, [expected])
            for actual_unit, actual in dimensions.items():
                add("unit_" + actual_unit + "_to_" + unit, q, [actual + actual_unit])
                add(
                    "unit_upper_" + actual_unit + "_to_" + unit,
                    q,
                    [actual + " " + actual_unit.upper()],
                )
            add(
                "unit_incompatible_" + unit,
                q,
                ["1000ha" if unit in length_answers else "1000m"],
            )
            add("unit_unknown_" + unit, q, [expected + "kg"])
    add(
        "unit_superscript_square",
        question("numeric", unit="ha", correct_answer=["1"]),
        ["10000 m²"],
    )
    add(
        "unit_canonical_suffix",
        question("numeric", unit="m", correct_answer=["1km"]),
        ["100000cm"],
    )

    options = [
        {"id": "A", "text": "Một"},
        {"id": "B", "text": "Hai"},
        {"id": "C", "text": "Ba"},
    ]
    single = question("single_choice", options=options, correct_answer=["A"])
    for label, answer in (
        ("correct", ["A"]),
        ("wrong", ["B"]),
        ("duplicate", ["A", "A"]),
        ("extra", ["A", "B"]),
        ("missing", []),
        ("unknown", ["D"]),
        ("case_sensitive", ["a"]),
    ):
        add("single_" + label, single, answer)
    multiple = question("multiple_choice", options=options, correct_answer=["A", "C"])
    for label, answer in (
        ("correct", ["A", "C"]),
        ("reordered", ["C", "A"]),
        ("duplicate", ["A", "C", "C"]),
        ("subset", ["A"]),
        ("extra", ["A", "B", "C"]),
        ("unknown", ["A", "D"]),
        ("missing", []),
    ):
        add("multiple_" + label, multiple, answer)

    true_false = question(
        "true_false", options=options, correct_answer=["true", "false", "true"]
    )
    for label, answer in (
        ("correct", ["true", "false", "true"]),
        ("one_correct", ["true", "true", "false"]),
        ("two_correct", ["true", "false", "false"]),
        ("none_correct", ["false", "true", "false"]),
        ("short", ["true", "false"]),
        ("long", ["true", "false", "true", "false"]),
        ("missing", []),
        ("uppercase", ["TRUE", "FALSE", "TRUE"]),
        ("invalid_token", ["true", "invalid", "true"]),
    ):
        add("true_false_" + label, true_false, answer)

    short = question("short_answer", correct_answer=["Hồ Chí Minh", "Bác Hồ"])
    for label, answer in (
        ("canonical", ["Hồ Chí Minh"]),
        ("case", ["hỒ cHÍ mINH"]),
        ("nfd", [unicodedata.normalize("NFD", "Hồ Chí Minh")]),
        ("space", [" \tHồ   Chí\nMinh\u00a0"]),
        ("control_space", ["Hồ\u001cChí\u001fMinh"]),
        ("alternate", ["BÁC HỒ"]),
        ("accent_required", ["Ho Chi Minh"]),
        ("punctuation_required", ["Hồ Chí Minh."]),
        ("missing", []),
        ("extra_answer", ["Hồ Chí Minh", "Bác Hồ"]),
    ):
        add("short_" + label, short, answer)
    for label, expected, answer in (
        ("german_sharp_s", "Straße", "STRASSE"),
        ("greek_final_sigma", "ΟΣ", "ος"),
        ("latin_ligature", "oﬃce", "OFFICE"),
        ("dotted_capital_i", "İ", "i\u0307"),
        ("dotless_i_distinct", "ı", "I"),
        ("kelvin", "K", "k"),
        ("long_s", "ſ", "S"),
        ("zero_width_is_not_space", "ab", "a\u200bb"),
        ("bom_is_not_space", "ab", "\ufeffab\ufeff"),
    ):
        add(
            "casefold_" + label,
            question("short_answer", correct_answer=[expected]),
            [answer],
        )

    essay = question(
        "essay",
        correct_answer=[],
        max_score="3",
        rubric=[{"description": "Trình bày đủ ý.", "points": "3"}],
    )
    add("essay_has_text_manual", essay, ["Bài giải tự viết."])
    add("essay_empty_manual", essay, [])
    add("essay_multiple_text_manual", essay, ["Ý một", "Ý hai"])
    return cases


def build_cases() -> dict:
    all_questions = canonical_records(QUESTION_FILES, "seeds", "questions", Question)
    questions = {
        qid: Question.model_validate(raw)
        for qid, raw in all_questions.items()
        if qid not in QUESTION_REPLACEMENTS
    }
    bank = {}
    for qid, q in sorted(questions.items()):
        answer = (
            q.correct_answer[:1]
            if q.type in ("numeric", "short_answer")
            else q.correct_answer
        )
        correct = grade(q, answer)
        empty = grade(q, [])
        bank[qid] = {
            "score": correct["score"],
            "empty_score": empty["score"],
            "max_score": correct["max_score"],
            "status": correct["status"],
        }
    paths = [
        ROOT / "services/api/khohoc/grading.py",
        ROOT / "services/api/khohoc/schemas.py",
        ROOT / "services/api/khohoc/content_fixes.py",
        *(ROOT / "data/seeds" / name for name in QUESTION_FILES),
    ]
    return {
        "schema_version": 1,
        "oracle": "services/api/khohoc/grading.py:grade + schemas.py:Question",
        "source_sha256": {
            str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(paths)
        },
        "question_count": len(questions),
        "question_types": dict(
            sorted(Counter(q.type for q in questions.values()).items())
        ),
        "cases": edge_cases(),
        "bank_correct_answers": bank,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build_cases()
    payload = (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    if args.check:
        if not args.output.is_file() or args.output.read_bytes() != payload:
            print("Offline grading golden fixture is stale", file=sys.stderr)
            return 1
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(payload)
    print(
        f"Grading oracle: {len(value['cases'])} edge cases, {value['question_count']} active questions; {len(payload)} bytes"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
