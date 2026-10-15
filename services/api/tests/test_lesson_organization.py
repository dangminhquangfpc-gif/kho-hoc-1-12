import json
from pathlib import Path
from khohoc.library import DocumentInput, fingerprint

ROOT = Path(__file__).resolve().parents[3]


def test_math5_index_has_all_numbered_lessons_and_real_practice_sections():
    books = json.loads(
        (ROOT / "data/seeds/textbook_units.json").read_text(encoding="utf-8")
    )["books"]
    book = next(b for b in books if b["grade"] == 5 and b["subject"] == "toan")
    documents = [
        DocumentInput.model_validate(d)
        for d in json.loads(
            (ROOT / "data/library/curriculum_documents.json").read_text(
                encoding="utf-8"
            )
        )["documents"]
    ]
    assert len(book["units"]) == len(documents) == 75
    assert {d.lesson_order for d in documents} == set(range(1, 76))
    assert {d.curriculum_unit_id for d in documents} == {u["id"] for u in book["units"]}
    assert len({fingerprint(d) for d in documents}) == 75
    for d in documents:
        headings = [s.heading for s in d.sections]
        assert any("Kiến thức và cách làm" in h for h in headings)
        assert any("Ví dụ từng bước" in h for h in headings)
        assert any("Bài tập tự luyện" in h for h in headings)
        assert any("Lời giải bài tập" in h for h in headings)
        assert d.source_type == "original" and d.license == "original_content"


def test_lesson_mapping_rejects_wrong_class_subject_or_missing_instruction():
    from copy import deepcopy
    from khohoc.library import is_textbook_lesson

    document = json.loads(
        (ROOT / "data/library/curriculum_documents.json").read_text(encoding="utf-8")
    )["documents"][0]
    assert is_textbook_lesson(document)
    for changes in (
        {"grade": 6},
        {"subject": "tieng_viet"},
        {"curriculum_unit_id": "unit_" + "0" * 20},
        {"textbook": "independent"},
        {"kind": "exam"},
        {"assessment_period": "final_1"},
        {"sections": []},
        {"sections": document["sections"][:3]},
    ):
        candidate = deepcopy(document)
        candidate.update(changes)
        assert not is_textbook_lesson(candidate)
