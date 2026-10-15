"""Explicit transfer of already-published public learning content, never learner data.

The archive is a JSON document, not a database backup. Publication/rights flags in
the source are prerequisites, not a claim of expert or publisher certification.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sqlite3
import tempfile

from fastapi import HTTPException
from sqlalchemy import inspect, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .app import fingerprint as question_fingerprint
from .catalog import subjects_for_grade
from .content_fixes import QUESTION_REPLACEMENTS
from .database import make_engine
from .library import (
    DEFAULT_LIBRARY_ROOT,
    DocumentInput,
    LibraryDocument,
    fingerprint as document_fingerprint,
    read_pdf,
)
from .models import ContentQuestion, Exam, TeacherExam
from .question_versions import QuestionRevision
from .schemas import ExamInput, Question

MAX_ARCHIVE_BYTES = 32 * 1024 * 1024
ARCHIVE_KIND = "tuhoc111.published-content"


def canonical_bytes(value):
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def digest(value):
    return hashlib.sha256(value).hexdigest()


def timestamp(value):
    if isinstance(value, str):
        value = datetime.fromisoformat(value)
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat()


def canonical_payload(raw, model):
    """Reject unknown fields instead of silently dropping private archive columns."""
    payload = model.model_validate(raw).model_dump(mode="json")
    if set(raw) - set(payload):
        raise ValueError("Unknown content payload fields")
    if model is Question:
        if (
            raw.get("options", []) != payload["options"]
            or raw.get("rubric", []) != payload["rubric"]
        ):
            raise ValueError("Question options/rubric must be canonical")
        if payload["subject"] not in {
            s["id"] for s in subjects_for_grade(payload["grade"])
        }:
            raise ValueError("Question subject unavailable for grade")
        if (
            payload["source_type"] == "link_only"
            or payload["id"] in QUESTION_REPLACEMENTS
        ):
            raise ValueError("Unpublishable or withdrawn question")
    return payload


def pdf_checksums(documents, library_root):
    files = {}
    for row in documents:
        name = row["payload"]["pdf_filename"]
        if name:
            try:
                files[name] = digest(read_pdf(Path(library_root), name))
            except HTTPException:
                raise ValueError(
                    "Required public library PDF unavailable: " + name
                ) from None
    return dict(sorted(files.items()))


def _stored_payload(row, model):
    payload = canonical_payload(row.payload, model)
    if row.id != payload["id"]:
        raise ValueError("Stored public content ID differs from payload")
    if model in (Question, DocumentInput):
        expected = (
            question_fingerprint(Question.model_validate(payload))
            if model is Question
            else document_fingerprint(DocumentInput.model_validate(payload))
        )
        if row.fingerprint != expected:
            raise ValueError("Stored public content fingerprint differs: " + row.id)
    return payload


def export_published_content(
    source_path, output_path, *, library_root=DEFAULT_LIBRARY_ROOT
):
    """Read a consistent SQLite backup; whitelist public content tables/columns only."""
    path, output = Path(source_path).resolve(), Path(output_path)
    if not path.is_file():
        raise ValueError("Missing SQLite source")
    with tempfile.TemporaryDirectory(prefix="tuhoc-public-content-") as directory:
        snapshot = Path(directory) / "snapshot.db"
        with sqlite3.connect(path.as_uri() + "?mode=ro", uri=True) as incoming:
            with sqlite3.connect(snapshot) as backup:
                incoming.backup(backup)
        source = make_engine("sqlite:///file:" + str(snapshot) + "?mode=ro&uri=true")
        try:
            with Session(source) as session:
                required = {
                    model.__tablename__
                    for model in (ContentQuestion, Exam, TeacherExam, LibraryDocument)
                }
                if not required <= set(inspect(source).get_table_names()):
                    raise ValueError("Source content schema incomplete")
                questions = [
                    {
                        "payload": _stored_payload(row, Question),
                        "version": row.version,
                    }
                    for row in session.scalars(
                        select(ContentQuestion)
                        .where(
                            ContentQuestion.state == "published",
                            ContentQuestion.rights_confirmed.is_(True),
                        )
                        .order_by(ContentQuestion.id)
                    )
                    if row.id not in QUESTION_REPLACEMENTS
                ]
                private_exams = set(session.scalars(select(TeacherExam.exam_id)))
                exams = []
                for row in session.scalars(
                    select(Exam).where(Exam.state == "published").order_by(Exam.id)
                ):
                    if row.id in private_exams or row.id.startswith("custom_"):
                        continue
                    payload = _stored_payload(row, ExamInput)
                    # Match the public API: withdrawn questions resolve to reviewed replacements.
                    payload["question_ids"] = [
                        QUESTION_REPLACEMENTS.get(qid, qid)
                        for qid in payload["question_ids"]
                    ]
                    exams.append({"payload": canonical_payload(payload, ExamInput)})
                documents = [
                    {
                        "payload": _stored_payload(row, DocumentInput),
                        "version": row.version,
                        "updated_at": timestamp(row.updated_at),
                    }
                    for row in session.scalars(
                        select(LibraryDocument)
                        .where(
                            LibraryDocument.state == "published",
                            LibraryDocument.rights_confirmed.is_(True),
                        )
                        .order_by(LibraryDocument.id)
                    )
                    if row.payload.get("source_type") == "link_only"
                    or row.payload.get("distribution_allowed")
                ]
        finally:
            source.dispose()
    content = {"questions": questions, "exams": exams, "documents": documents}
    archive = {
        "kind": ARCHIVE_KIND,
        "schema_version": 1,
        "manifest": {
            "content_sha256": digest(canonical_bytes(content)),
            "counts": {key: len(rows) for key, rows in content.items()},
            "pdf_sha256": pdf_checksums(documents, library_root),
        },
        "content": content,
    }
    payload = canonical_bytes(archive) + b"\n"
    # Validate our export using exactly the receiver's validation before writing it.
    validate_archive(payload, library_root=library_root)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("xb") as handle:
        handle.write(payload)
    return {"archive_sha256": digest(payload), **archive["manifest"]}


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON object key")
        result[key] = value
    return result


def validate_archive(payload, *, library_root=DEFAULT_LIBRARY_ROOT):
    if len(payload) > MAX_ARCHIVE_BYTES:
        raise ValueError("Content archive exceeds 32 MiB limit")
    archive = json.loads(payload, object_pairs_hook=_unique_object)
    if not isinstance(archive, dict) or set(archive) != {
        "kind",
        "schema_version",
        "manifest",
        "content",
    }:
        raise ValueError("Invalid content-only archive")
    if (
        archive["kind"] != ARCHIVE_KIND
        or type(archive["schema_version"]) is not int
        or archive["schema_version"] != 1
    ):
        raise ValueError("Unsupported content archive")
    content, manifest = archive["content"], archive["manifest"]
    if not isinstance(content, dict) or set(content) != {
        "questions",
        "exams",
        "documents",
    }:
        raise ValueError("Archive may contain only public content collections")
    if not isinstance(manifest, dict) or set(manifest) != {
        "content_sha256",
        "counts",
        "pdf_sha256",
    }:
        raise ValueError("Invalid content manifest")
    if manifest["content_sha256"] != digest(canonical_bytes(content)):
        raise ValueError("Content manifest checksum mismatch")
    ids = {}
    for key, model in (
        ("questions", Question),
        ("exams", ExamInput),
        ("documents", DocumentInput),
    ):
        rows = content[key]
        if not isinstance(rows, list) or len(rows) > 100000:
            raise ValueError("Invalid content collection")
        ids[key] = {}
        expected_keys = (
            {"payload"}
            | ({"version"} if key != "exams" else set())
            | ({"updated_at"} if key == "documents" else set())
        )
        for row in rows:
            if (
                not isinstance(row, dict)
                or set(row) != expected_keys
                or not isinstance(row["payload"], dict)
            ):
                raise ValueError("Unknown content record fields")
            canonical = canonical_payload(row["payload"], model)
            if canonical != row["payload"]:
                raise ValueError("Archive payload is not canonical")
            ident = canonical["id"]
            if ident in ids[key]:
                raise ValueError("Duplicate content ID: " + ident)
            ids[key][ident] = row
            if key != "exams" and (
                type(row["version"]) is not int or not 1 <= row["version"] <= 2147483647
            ):
                raise ValueError("Invalid content version")
            if key == "documents":
                if (
                    not isinstance(row["updated_at"], str)
                    or timestamp(row["updated_at"]) != row["updated_at"]
                ):
                    raise ValueError("Invalid document update timestamp")
                if (
                    canonical["source_type"] != "link_only"
                    and not canonical["distribution_allowed"]
                ):
                    raise ValueError("Document redistribution not allowed")
    if manifest["counts"] != {key: len(rows) for key, rows in content.items()}:
        raise ValueError("Content manifest counts mismatch")
    for row in content["exams"]:
        exam = row["payload"]
        if exam["id"].startswith("custom_"):
            raise ValueError("Private/custom exams cannot be transferred")
        for qid in exam["question_ids"]:
            question = ids["questions"].get(qid, {}).get("payload")
            if not question or (exam["grade"], exam["subject"]) != (
                question["grade"],
                question["subject"],
            ):
                raise ValueError(
                    "Missing or incompatible published exam question: " + qid
                )
    if manifest["pdf_sha256"] != pdf_checksums(content["documents"], library_root):
        raise ValueError("Required public library PDF checksum mismatch")
    return archive


def import_published_content(
    engine,
    archive_path,
    *,
    apply=False,
    expected_sha256=None,
    library_root=DEFAULT_LIBRARY_ROOT,
):
    """Default dry-run; insert-only transaction; exact matches skip, all conflicts abort."""
    with Path(archive_path).open("rb") as handle:
        payload = handle.read(MAX_ARCHIVE_BYTES + 1)
    archive = validate_archive(payload, library_root=library_root)
    actual_sha256 = digest(payload)
    if apply and expected_sha256 != actual_sha256:
        raise ValueError("Applying requires the exact reviewed --expected-sha256")
    if expected_sha256 is not None and expected_sha256 != actual_sha256:
        raise ValueError("Archive SHA256 differs from expected value")
    inserted = {key: 0 for key in archive["content"]}
    skipped = dict(inserted)
    try:
        with Session(engine) as session, session.begin():
            if engine.dialect.name == "postgresql":
                session.execute(text("SELECT pg_advisory_xact_lock(11120261016)"))
            private_exams = set(session.scalars(select(TeacherExam.exam_id)))
            pending = []
            for key, model in (
                ("questions", ContentQuestion),
                ("exams", Exam),
                ("documents", LibraryDocument),
            ):
                records = archive["content"][key]
                incoming_ids = [row["payload"]["id"] for row in records]
                # Batch reads: a remote free-tier database must not need two network
                # round-trips for each of several thousand questions/documents.
                existing_rows = {}
                for start in range(0, len(incoming_ids), 500):
                    existing_rows.update(
                        {
                            row.id: row
                            for row in session.scalars(
                                select(model).where(
                                    model.id.in_(incoming_ids[start : start + 500])
                                )
                            )
                        }
                    )
                incoming_fingerprints = {}
                owners = {}
                if key != "exams":
                    for record in records:
                        content = record["payload"]
                        incoming_fingerprints[content["id"]] = (
                            question_fingerprint(Question.model_validate(content))
                            if key == "questions"
                            else document_fingerprint(
                                DocumentInput.model_validate(content)
                            )
                        )
                    wanted = list(incoming_fingerprints.values())
                    for start in range(0, len(wanted), 500):
                        owners.update(
                            {
                                fingerprint: ident
                                for ident, fingerprint in session.execute(
                                    select(model.id, model.fingerprint).where(
                                        model.fingerprint.in_(
                                            wanted[start : start + 500]
                                        )
                                    )
                                )
                            }
                        )
                fingerprints = {}
                for record in records:
                    content = record["payload"]
                    ident = content["id"]
                    if key == "exams" and ident in private_exams:
                        raise ValueError(
                            "Destination contains a private exam ID: " + ident
                        )
                    values = {"id": ident, "payload": content, "state": "published"}
                    if key != "exams":
                        fingerprint = incoming_fingerprints[ident]
                        if fingerprint in fingerprints:
                            raise ValueError("Duplicate content fingerprint: " + ident)
                        fingerprints[fingerprint] = ident
                        values.update(
                            fingerprint=fingerprint,
                            rights_confirmed=True,
                            version=record["version"],
                        )
                        owner = owners.get(fingerprint)
                        if owner is not None and owner != ident:
                            raise ValueError(
                                "Destination fingerprint conflict: " + ident
                            )
                    if key == "documents":
                        values["updated_at"] = datetime.fromisoformat(
                            record["updated_at"]
                        )
                    existing = existing_rows.get(ident)
                    if existing is not None:
                        for field, expected in values.items():
                            actual = getattr(existing, field)
                            if field == "updated_at":
                                actual, expected = (
                                    timestamp(actual),
                                    timestamp(expected),
                                )
                            if actual != expected:
                                raise ValueError(
                                    "Destination content differs; review through admin instead: "
                                    + ident
                                )
                        skipped[key] += 1
                    else:
                        pending.append(model(**values))
                        inserted[key] += 1
                        if key == "questions":
                            pending.append(
                                QuestionRevision(
                                    question_id=ident,
                                    version=record["version"],
                                    payload=content,
                                    operation="initial",
                                    actor="content-transfer",
                                    note="Current published revision transferred; historical actors/revisions excluded.",
                                )
                            )
            if apply:
                # Explicit order also works on PostgreSQL with revision foreign keys.
                session.add_all(
                    [row for row in pending if not isinstance(row, QuestionRevision)]
                )
                session.flush()
                session.add_all(
                    [row for row in pending if isinstance(row, QuestionRevision)]
                )
    except IntegrityError:
        raise ValueError(
            "Concurrent content conflict; no archive changes committed"
        ) from None
    return {
        "archive_sha256": actual_sha256,
        "mode": "applied" if apply else "dry-run",
        "inserted": inserted,
        "skipped": skipped,
    }
