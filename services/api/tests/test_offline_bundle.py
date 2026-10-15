"""The installed practice data must match the published classroom preview."""

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from khohoc.content_fixes import QUESTION_REPLACEMENTS
from khohoc.library import LibraryDocument, is_textbook_lesson
from khohoc.models import ContentQuestion, Exam
from khohoc.phone_preview import create_preview

ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location(
    "offline_bundle_export", ROOT / "scripts/build_offline_bundle.py"
)
export = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(export)


@pytest.fixture(scope="module")
def bundle():
    return export.build_bundle()


def test_committed_bundle_is_reproducible_and_check_detects_stale_asset(
    bundle, tmp_path
):
    expected = export.serialized_bundle(bundle)
    assert export.DEFAULT_OUTPUT.read_bytes() == expected
    assert export.serialized_bundle(export.build_bundle()) == expected
    assert json.loads(expected)["content_version"] == "2026.10.15.19"
    path = tmp_path / "content.json"
    path.write_bytes(expected)
    command = [
        sys.executable,
        str(ROOT / "scripts/build_offline_bundle.py"),
        "--output",
        str(path),
        "--check",
    ]
    assert subprocess.run(command, capture_output=True).returncode == 0
    path.write_bytes(expected + b" ")
    stale = subprocess.run(command, capture_output=True)
    assert stale.returncode == 1
    assert b"stale" in stale.stderr


def test_bundle_matches_actual_preview_publication(bundle, tmp_path, monkeypatch):
    monkeypatch.setenv("KHOHOC_MODE", "development")
    monkeypatch.setenv("KHOHOC_DATABASE_URL", f"sqlite:///{tmp_path}/preview.sqlite")
    app = create_preview()
    with Session(app.state.engine) as session:
        active = {
            row.id: row.payload
            for row in session.scalars(select(ContentQuestion))
            if row.state == "published" and row.rights_confirmed
        }
        assert {q["id"]: q for q in bundle["questions"]} == active
        exams = {
            row.id: row.payload
            | {
                "question_ids": [
                    QUESTION_REPLACEMENTS.get(qid, qid)
                    for qid in row.payload["question_ids"]
                ]
            }
            for row in session.scalars(select(Exam))
            if row.state == "published"
        }
        assert {e["id"]: e for e in bundle["exams"]} == exams
        documents = {
            row.id: row.payload
            for row in session.scalars(select(LibraryDocument))
            if row.state == "published"
            and row.rights_confirmed
            and (
                row.payload["source_type"] == "link_only"
                or row.payload["distribution_allowed"]
            )
        }
        assert {d["id"]: d for d in bundle["documents"]} == documents
    app.state.engine.dispose()


def test_replacements_exam_references_and_lesson_classification(bundle):
    questions = {q["id"]: q for q in bundle["questions"]}
    assert not questions.keys() & QUESTION_REPLACEMENTS.keys()
    assert set(QUESTION_REPLACEMENTS.values()) <= questions.keys()
    for exam in bundle["exams"]:
        assert len(exam["question_ids"]) == len(set(exam["question_ids"]))
        assert all(
            (questions[qid]["grade"], questions[qid]["subject"])
            == (exam["grade"], exam["subject"])
            for qid in exam["question_ids"]
        )
    assert set(bundle["question_public_metadata"]) == questions.keys()
    assert set(bundle["lesson_document_ids"]) == {
        d["id"] for d in bundle["documents"] if is_textbook_lesson(d)
    }
    assert len(bundle["lesson_document_ids"]) == 733
    assert {q["grade"] for q in questions.values()} == set(range(1, 13))


def test_only_redistributable_authored_content_and_reference_metadata(bundle):
    assert all(
        q["source_type"] == "original" and q["license"] == "original_content"
        for q in bundle["questions"]
    )
    for document in bundle["documents"]:
        if document["source_type"] == "link_only":
            assert not document["sections"]
            assert not document["distribution_allowed"]
            assert not document["download_allowed"]
            assert not document["pdf_filename"]
        else:
            assert document["source_type"] == "original"
            assert document["license"] == "original_content"
            assert document["distribution_allowed"] and document["sections"]
    metadata = bundle["metadata"]
    assert metadata["contains_answer_keys"] and metadata["practice_only"]
    assert not metadata["pdf_files_included"]
    assert metadata["question_count"] == len(bundle["questions"])
    assert metadata["exam_count"] == len(bundle["exams"])
    assert metadata["document_count"] == len(bundle["documents"])
    assert metadata["external_reference_count"] == 1934
    assert "chưa đầy đủ" in metadata["scope_notice"]


def test_fixed_source_manifest_contains_no_private_or_live_state(bundle):
    expected = {
        "data/seeds/" + name
        for name in export.QUESTION_FILES + export.EXAM_FILES + export.METADATA_FILES
    } | {"data/library/" + name for name in export.DOCUMENT_FILES}
    manifest = bundle["metadata"]["source_sha256"]
    assert set(manifest) == expected
    for name, digest in manifest.items():
        assert digest == hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
    private_keys = {
        "token",
        "token_hash",
        "password",
        "password_hash",
        "api_key",
        "session_id",
        "user_id",
        "username",
        "database_url",
        "answers",
        "attempt_id",
    }

    def assert_no_private_keys(value):
        if isinstance(value, dict):
            assert not value.keys() & private_keys
            for child in value.values():
                assert_no_private_keys(child)
        elif isinstance(value, list):
            for child in value:
                assert_no_private_keys(child)

    assert_no_private_keys(bundle)


def test_export_fails_closed_for_new_unreviewed_redistribution(monkeypatch):
    original = export.canonical_records

    def changed_questions(names, directory, key, model):
        records = original(names, directory, key, model)
        if names == export.QUESTION_FILES:
            records = copy.deepcopy(records)
            question = next(
                q for qid, q in records.items() if qid not in QUESTION_REPLACEMENTS
            )
            question["source_type"] = "licensed"
            question["license"] = "unreviewed"
        return records

    monkeypatch.setattr(export, "canonical_records", changed_questions)
    with pytest.raises(ValueError, match="redistribution needs explicit review"):
        export.build_bundle()
