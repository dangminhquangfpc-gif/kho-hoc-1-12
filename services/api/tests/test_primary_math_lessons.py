"""Coverage of actual index entries, lesson structure and independent arithmetic."""

import importlib.util
import json
from pathlib import Path
import re

from khohoc.library import DocumentInput, fingerprint, is_textbook_lesson
from test_worked_lessons import exact_expression

ROOT = Path(__file__).resolve().parents[3]


def load_documents():
    return json.loads((ROOT / "data/library/primary_math_documents.json").read_text())[
        "documents"
    ]


def test_primary_guides_match_each_recorded_lesson_not_just_book_titles():
    documents = load_documents()
    books = json.loads((ROOT / "data/seeds/textbook_units.json").read_text())["books"]
    assert len(documents) == len({d["id"] for d in documents}) == 267
    assert len({fingerprint(DocumentInput.model_validate(d)) for d in documents}) == 267
    for grade, count in [(1, 41), (2, 74), (3, 79), (4, 73)]:
        rows = [d for d in documents if d["grade"] == grade]
        book = next(b for b in books if b["grade"] == grade and b["subject"] == "toan")
        assert len(rows) == len(book["units"]) == count
        assert {d["curriculum_unit_id"] for d in rows} == {
            u["id"] for u in book["units"]
        }
        by_unit = {u["id"]: u for u in book["units"]}
        for d in rows:
            assert is_textbook_lesson(d)
            assert d["source_url"] == by_unit[d["curriculum_unit_id"]]["source_url"]
            assert d["title"] == by_unit[d["curriculum_unit_id"]]["title"]
            assert d["license"] == "original_content" and d["semester"] in (1, 2)


def test_every_primary_example_and_task_has_working_and_final_answer():
    examples = tasks = 0
    for d in load_documents():
        for i, s in enumerate(d["sections"]):
            if "Ví dụ từng bước" in s["heading"]:
                assert s["text"].startswith("Đề bài: ")
                assert "\n\nLời giải\n" in s["text"]
                assert s["text"].count("Đáp số: ") == 1
                assert (
                    len(
                        s["text"]
                        .split("Lời giải\n")[1]
                        .split("\nĐáp số: ")[0]
                        .splitlines()
                    )
                    >= 2
                )
                examples += 1
            if "Bài tập tự luyện" in s["heading"]:
                n = len(re.findall(r"^\d+\. ", s["text"], re.M))
                solution = d["sections"][i + 1]
                assert "Lời giải bài tập" in solution["heading"]
                assert (
                    solution["text"].count("Lời giải\n")
                    == solution["text"].count("Đáp số: ")
                    == n
                    == 2
                )
                tasks += n
    assert examples == 476 and tasks == 952


def test_primary_computable_equalities_are_exact():
    checked = 0
    for d in load_documents():
        for s in d["sections"]:
            for line in s["text"].splitlines():
                # Isolate independent arithmetic sentences and table entries.
                for part in re.split(r";|(?<=\d)\.\s+", line):
                    part = re.sub(
                        r"\((?:cm²|cm³|m²|cm|m|km|mm|kg|g|l|ml|°C|giây|năm|đồng|bạn|quyển|bút|quả|học sinh|cây|viên|nhóm|bông|que|ngày|nhãn vở|phần|lần)\)",
                        "",
                        part,
                    )
                    value = part.strip().rstrip(".").replace(" ", "").replace(",", ".")
                    if (
                        not re.fullmatch(r"[\d.+×*/():=−\-]+", value)
                        or "=" not in value
                        or value.startswith("=")
                    ):
                        continue
                    value = re.sub(r"(?<![\d/])(\d+/\d+)(?![\d/])", r"(\1)", value)
                    value = value.replace("×", "*").replace(":", "/").replace("−", "-")
                    parts = [exact_expression(x) for x in value.split("=")]
                    assert all(x == parts[0] for x in parts), (d["id"], line)
                    checked += 1
    assert checked > 1000


def test_grade3_circle_and_midpoint_are_not_grade5_area_lessons():
    rows = {d["id"]: d for d in load_documents()}
    for n in (13, 14, 16, 17, 18, 19, 21):
        d = rows[f"kntt_math3_lesson_{n:02d}"]
        assert len(d["sections"]) >= 6
    text = "\n".join(s["text"] for s in rows["kntt_math3_lesson_17"]["sections"])
    assert "đường kính" in text and "bán kính" in text
    assert "3,14" not in text and "r × r" not in text
    middle = "\n".join(s["text"] for s in rows["kntt_math3_lesson_16"]["sections"])
    assert "Điểm ở giữa chưa chắc là trung điểm" in middle
    assert "4 cm" in middle


def test_authored_arithmetic_respects_grade_and_digit_ranges():
    import sys
    from unittest.mock import patch

    with patch.object(sys, "path", [str(ROOT / "data/pipelines"), *sys.path]):
        spec = importlib.util.spec_from_file_location(
            "primary_content_check", ROOT / "data/pipelines/primary_math_content.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    for grade, mapping in module.GRADE_MAP.items():
        for number, keys in mapping.items():
            for key in keys:
                if not re.fullmatch(r"(?:add|sub|mul|div)\d+", key):
                    continue
                skill = module.resolve(key, grade, number)
                for text in [skill["example"], *skill["tasks"]]:
                    match = re.fullmatch(r"Tính (\d+) ([+−×:]) (\d+)\.", text)
                    assert match
                    a, op, b = match.groups()
                    a, b = int(a), int(b)
                    if grade == 1:
                        assert max(a, b, a + b if op == "+" else a - b) <= 100
                    if grade == 2:
                        assert max(a, b, a + b if op == "+" else a - b) <= 1000
                    if grade == 3:
                        assert (
                            max(a, b, a * b if op == "×" else a + b if op == "+" else a)
                            <= 100000
                        )
                        if key in ("mul2", "mul3", "mul4", "mul5"):
                            assert len(str(a)) == int(key[-1])
                        if key in ("div2", "div3", "div4", "div5"):
                            assert len(str(a)) == int(key[-1])
