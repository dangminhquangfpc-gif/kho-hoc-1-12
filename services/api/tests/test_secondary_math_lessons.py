"""Secondary index scope, real lesson content and arithmetic regressions."""

import importlib.util
import json
from pathlib import Path
import re

from khohoc.library import DocumentInput, fingerprint, is_textbook_lesson
from test_worked_lessons import exact_expression

ROOT = Path(__file__).resolve().parents[3]
COUNTS = {6: 74, 7: 69, 8: 75, 9: 62, 10: 39, 11: 43, 12: 29}
NUMBERED = {6: 43, 7: 37, 8: 39, 9: 32, 10: 27, 11: 33, 12: 19}


def documents():
    return json.loads(
        (ROOT / "data/library/secondary_math_documents.json").read_text()
    )["documents"]


def test_secondary_guides_cover_recorded_units_and_all_numbered_lessons():
    rows = documents()
    books = json.loads((ROOT / "data/seeds/textbook_units.json").read_text())["books"]
    assert len(rows) == len({d["id"] for d in rows}) == 391
    assert len({fingerprint(DocumentInput.model_validate(d)) for d in rows}) == 391
    for grade, count in COUNTS.items():
        book = next(b for b in books if b["grade"] == grade and b["subject"] == "toan")
        guides = [d for d in rows if d["grade"] == grade]
        assert len(guides) == len(book["units"]) == count
        by_id = {d["curriculum_unit_id"]: d for d in guides}
        assert set(by_id) == {u["id"] for u in book["units"]}
        assert sorted(
            u["lesson_number"] for u in book["units"] if u["unit_kind"] == "lesson"
        ) == list(range(1, NUMBERED[grade] + 1))
        for unit in book["units"]:
            d = by_id[unit["id"]]
            assert is_textbook_lesson(d)
            assert d["title"] == unit["title"] and d["source_url"] == unit["source_url"]
            assert d["chapter"] == unit["chapter"] and d["semester"] == unit["semester"]


def test_all_secondary_examples_and_exercises_have_working_and_final_answer():
    examples = exercises = 0
    for d in documents():
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
                a = d["sections"][i + 1]
                assert "Lời giải bài tập" in a["heading"]
                assert (
                    a["text"].count("Lời giải\n")
                    == a["text"].count("Đáp số: ")
                    == n
                    == 2
                )
                exercises += n
    assert (examples, exercises) == (610, 1220)


def test_secondary_conditions_and_distinct_grade_topics():
    def text(grade, number):
        books = json.loads((ROOT / "data/seeds/textbook_units.json").read_text())[
            "books"
        ]
        book = next(b for b in books if b["grade"] == grade and b["subject"] == "toan")
        unit = next(u for u in book["units"] if u["lesson_number"] == number)
        d = next(d for d in documents() if d["curriculum_unit_id"] == unit["id"])
        return "\n".join(s["text"] for s in d["sections"])

    assert "duy nhất một đường" in text(7, 10)
    assert "x≠1" in text(8, 21)
    assert "chia hai vế với số âm phải đổi chiều" in text(9, 6)
    assert "x≥1" in text(10, 18)
    assert "|A−a|/|a|" in text(10, 12) and "1/49" in text(10, 12)
    assert "x>1" in text(11, 21)
    assert "thể tích" in text(12, 13) and "1/6" in text(12, 13)
    assert "3/7" in text(12, 19) and "P(A)>0" in text(12, 19)


def test_secondary_computable_equalities_are_exact():
    checked = 0
    for d in documents():
        for section in d["sections"]:
            for line in section["text"].splitlines():
                value = line.strip().rstrip(".").replace(" ", "").replace(",", ".")
                if (
                    not re.fullmatch(r"[\d.+×*/():=−\-]+", value)
                    or "=" not in value
                    or value.startswith("=")
                ):
                    continue
                value = (
                    re.sub(r"(?<![\d/])(\d+/\d+)(?![\d/])", r"(\1)", value)
                    .replace("×", "*")
                    .replace(":", "/")
                    .replace("−", "-")
                )
                parts = [exact_expression(x) for x in value.split("=")]
                assert all(v == parts[0] for v in parts), (d["id"], line)
                checked += 1
    assert checked > 100


def test_new_toc_layout_excludes_sidebar_book_and_chapter_links():
    spec = importlib.util.spec_from_file_location(
        "toc_check", ROOT / "data/pipelines/textbook_index.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    parser = module.StructuredMathToc()
    parser.feed("""<div id="sidebar"><a href="/bad-e1.html">Bài sai</a></div>
    <div id="event_1_columns"><h2><a href="/book-e2.html">Toán 12 tập 1 - Kết nối tri thức</a></h2>
    <a href="/chapter-e3.html">Chương 1. Đạo hàm</a>
    <ul><li><a href="/lesson-e4.html"><b>Bài 1. Tính đơn điệu</b></a></li></ul>
    <a href="/review-e5.html">Bài tập cuối chương 1</a></div>
    <div><a href="/advert-e6.html">Bài quảng cáo</a></div>""")
    assert [e["title"] for e in parser.entries] == [
        "Bài 1. Tính đơn điệu",
        "Bài tập cuối chương 1",
    ]
    assert all(
        e["chapter"] == "Chương 1. Đạo hàm" and e["semester"] == 1
        for e in parser.entries
    )
