"""Editorial completeness, exact arithmetic, and trusted fixture upgrades."""

import ast
from copy import deepcopy
from fractions import Fraction
import importlib.util
import json
from pathlib import Path
import re

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from khohoc.document_upgrades import reviewed_transition, upgrade_documents
from khohoc.library import DocumentInput, LibraryDocument, fingerprint
from khohoc.models import Base, AuditEvent
from khohoc.phone_preview import checked_fixture_rows

ROOT = Path(__file__).resolve().parents[3]


def lessons():
    return json.loads((ROOT / "data/library/curriculum_documents.json").read_text())[
        "documents"
    ]


def test_each_example_and_exercise_has_full_working_then_final_answer():
    example_count = practice_count = 0
    for document in lessons():
        sections = document["sections"]
        for i, section in enumerate(sections):
            if "Ví dụ từng bước" in section["heading"]:
                text = section["text"]
                assert text.startswith("Đề bài: ")
                assert "\n\nLời giải\n" in text
                assert text.count("Đáp số: ") == 1
                assert (
                    len(text.split("Lời giải\n")[1].split("\nĐáp số: ")[0].splitlines())
                    >= 2
                )
                example_count += 1
            if "Bài tập tự luyện" in section["heading"]:
                count = len(re.findall(r"^\d+\. ", section["text"], re.M))
                answers = sections[i + 1]["text"]
                assert "Lời giải bài tập" in sections[i + 1]["heading"]
                assert answers.count("Lời giải\n") == answers.count("Đáp số: ") == count
                for block in answers.split("\n\n"):
                    assert re.match(r"^Bài \d+\.\nLời giải\n", block)
                    working, final = block.split("\nĐáp số: ")
                    assert len(working.splitlines()) >= 4 and final.strip()
                practice_count += count
    assert (example_count, practice_count) == (139, 278)


def exact_expression(expression):
    def read(node):
        if isinstance(node, ast.Constant):
            return Fraction(ast.get_source_segment(expression, node))
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return -read(node.operand)
        assert isinstance(node, ast.BinOp)
        a, b = read(node.left), read(node.right)
        if isinstance(node.op, ast.Add):
            return a + b
        if isinstance(node.op, ast.Sub):
            return a - b
        if isinstance(node.op, ast.Mult):
            return a * b
        assert isinstance(node.op, ast.Div)
        return a / b

    return read(ast.parse(expression, mode="eval").body)


def test_authored_working_numeric_equalities_are_exact():
    path = ROOT / "data/pipelines/math5_worked_solutions.py"
    spec = importlib.util.spec_from_file_location("worked_solutions", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    checked = 0
    for key, solutions in module.WORKED.items():
        for text in solutions:
            for line in text.splitlines():
                line = re.sub(
                    r"\((?:cm²|cm³|m²|m³|cm|m|km|km/giờ|giờ|phút|đồng|bạn|khối|phần|lần|đơn vị khối)\)",
                    "",
                    line,
                )
                line = line.strip().rstrip(".").replace(" ", "").replace(",", ".")
                line = re.sub(r"(?<![\d/])(\d+/\d+)(?![\d/])", r"(\1)", line)
                line = line.replace("×", "*").replace(":", "/").replace("−", "-")
                if (
                    line.startswith("=")
                    or "=" not in line
                    or not re.fullmatch(r"[\d.+*/()=\-]+", line)
                ):
                    continue
                parts = [exact_expression(part) for part in line.split("=")]
                assert all(value == parts[0] for value in parts), (key, line)
                checked += 1
    assert checked >= 100


def test_circle_is_grade_appropriate_and_solves_radius_before_area():
    document = next(d for d in lessons() if d["lesson_order"] == 27)
    text = "\n".join(s["text"] for s in document["sections"])
    assert "π" not in text
    assert "bán kính nhân với bán kính" in text
    assert "3 × 3 × 3,14 = 28,26 (cm²)" in text
    assert "5 × 2 × 3,14 = 31,4 (cm)" in text
    assert text.index("4 : 2 = 2 (cm)") < text.index("2 × 2 × 3,14 = 12,56 (cm²)")
    assert "Đáp số: 12,56 cm²." in text


def test_only_reviewed_exact_document_transition_can_upgrade(tmp_path):
    previous = json.loads(
        (Path(__file__).parent / "fixtures/math5_circle_v6.json").read_text()
    )
    current = next(d for d in lessons() if d["id"] == previous["id"])
    before = DocumentInput.model_validate(previous).model_dump(mode="json")
    after = DocumentInput.model_validate(current).model_dump(mode="json")
    assert reviewed_transition(before, after)
    for field in ("summary", "source_url", "rights_evidence"):
        edited = deepcopy(before)
        edited[field] = (
            "https://example.org/unknown"
            if field == "source_url"
            else "Unknown editorial change"
        )
        assert not reviewed_transition(edited, after)
    bad_target = deepcopy(after)
    bad_target["sections"][0]["text"] = "Unexpected replacement"
    assert not reviewed_transition(before, bad_target)
    row = {"document": before, "state": "published", "rights_confirmed": True}
    expected = {current["id"]: after}
    assert checked_fixture_rows(
        [row], expected, DocumentInput, "document", allow_document_upgrades=True
    )
    with pytest.raises(RuntimeError, match="Refusing changed document fixture"):
        checked_fixture_rows(
            [row | {"state": "draft"}],
            expected,
            DocumentInput,
            "document",
            allow_document_upgrades=True,
        )
    engine = create_engine(f"sqlite:///{tmp_path}/upgrade.db")
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        db.add(
            LibraryDocument(
                id=before["id"],
                payload=before,
                fingerprint=fingerprint(DocumentInput.model_validate(before)),
                state="published",
                rights_confirmed=True,
            )
        )
        db.commit()
    upgrade_documents(engine, {before["id"]: row}, expected)
    # A repeated start leaves the new version and audit history unchanged.
    upgrade_documents(engine, {after["id"]: row | {"document": after}}, expected)
    with Session(engine) as db:
        stored = db.get(LibraryDocument, before["id"])
        assert stored.payload == after and stored.version == 2
        assert stored.state == "published" and stored.rights_confirmed
        events = list(db.scalars(select(AuditEvent)))
        assert len(events) == 1
        assert json.loads(events[0].target)["previous_document"] == before


def test_missing_legacy_defaults_do_not_trigger_an_unreviewed_upgrade():
    before = DocumentInput.model_validate(lessons()[0]).model_dump(mode="json")
    legacy = deepcopy(before)
    del legacy["access_notice"]
    assert legacy != before
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        db.add(
            LibraryDocument(
                id=legacy["id"],
                payload=legacy,
                fingerprint=fingerprint(DocumentInput.model_validate(before)),
                state="draft",
                rights_confirmed=False,
            )
        )
        db.commit()
    upgrade_documents(
        engine, {legacy["id"]: {"document": legacy}}, {before["id"]: before}
    )
    with Session(engine) as db:
        row = db.get(LibraryDocument, legacy["id"])
        assert row.state == "draft" and row.version == 1 and not row.rights_confirmed
        assert list(db.scalars(select(AuditEvent))) == []
