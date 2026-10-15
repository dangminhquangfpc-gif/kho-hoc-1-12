"""Disposable phone preview. No accounts, admin API, or production data."""

import json
import re
import secrets
import time
from collections import deque
from pathlib import Path

from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

from .app import Settings, create_app
from .library import DocumentInput
from .schemas import ExamInput, Question

PUBLIC = re.compile(
    r"/(?:health|coverage|grades|grades/[0-9]+/subjects|exams|exams/[^/]+|"
    r"exams/[^/]+/attempts|attempts/[^/]+/(?:submit|result)|attempts/[^/]+|documents|documents/[^/]+|documents/[^/]+/file)"
)


def canonical_fixture_map(records, model):
    """Apply API defaults before comparing authored fixtures with stored content."""
    fixtures = {}
    for raw in records:
        payload = model.model_validate(raw).model_dump(mode="json")
        if payload["id"] in fixtures:
            raise RuntimeError("Duplicate fixture ID: " + payload["id"])
        fixtures[payload["id"]] = payload
    return fixtures


def checked_fixture_rows(rows, fixtures, model, payload_key):
    """Never interpret a reused fixture ID as approval of changed content."""
    existing = {}
    for row in rows:
        payload = row[payload_key]
        record_id = payload["id"]
        existing[record_id] = row
        if record_id not in fixtures:
            continue
        try:
            canonical = model.model_validate(payload).model_dump(mode="json")
        except ValueError:
            raise RuntimeError(
                f"Refusing invalid stored {payload_key} fixture: {record_id}"
            ) from None
        if canonical != fixtures[record_id]:
            raise RuntimeError(
                f"Refusing changed {payload_key} fixture: {record_id}; "
                "review it through admin instead of fixture publication"
            )
    return existing


def create_preview():
    config = Settings()
    if config.mode != "development":
        raise RuntimeError("Preview cannot run as production")
    config.admin_token = secrets.token_urlsafe(32)
    app = create_app(config)
    root = Path(__file__).resolve().parents[3]
    questions = canonical_fixture_map(
        [
            question
            for name in (
                "questions.json",
                "language_questions.json",
                "curriculum_questions.json",
                "subject_questions.json",
            )
            for question in json.loads(
                (root / "data/seeds" / name).read_text(encoding="utf-8")
            )["questions"]
        ],
        Question,
    )
    exams = canonical_fixture_map(
        [
            exam
            for name in (
                "exams.json",
                "language_exams.json",
                "curriculum_exams.json",
                "subject_exams.json",
            )
            for exam in json.loads(
                (root / "data/seeds" / name).read_text(encoding="utf-8")
            )
        ],
        ExamInput,
    )
    notes = canonical_fixture_map(
        json.loads((root / "data/library/documents.json").read_text(encoding="utf-8"))[
            "documents"
        ],
        DocumentInput,
    )
    # Seed through the same validation/review routes, before the public gate exists.
    with TestClient(app) as client:
        headers = {"Authorization": "Bearer " + config.admin_token}
        # Preflight every fixture before making any moderation changes. This also
        # refuses edited fixtures that are already published, on repeated setup.
        existing = checked_fixture_rows(
            client.get("/admin/questions", headers=headers).raise_for_status().json(),
            questions,
            Question,
            "question",
        )
        existing_exams = checked_fixture_rows(
            client.get("/admin/exams", headers=headers).raise_for_status().json(),
            exams,
            ExamInput,
            "exam",
        )
        existing_docs = checked_fixture_rows(
            client.get("/admin/documents", headers=headers).raise_for_status().json(),
            notes,
            DocumentInput,
            "document",
        )
        pending = [q for qid, q in questions.items() if qid not in existing]
        for start in range(0, len(pending), 200):
            client.post(
                "/admin/import",
                headers=headers,
                json={"questions": pending[start : start + 200]},
            ).raise_for_status()
        rows = checked_fixture_rows(
            client.get("/admin/questions", headers=headers).raise_for_status().json(),
            questions,
            Question,
            "question",
        )
        for qid, row in rows.items():
            if qid not in questions:
                continue
            if row["state"] == "published":
                continue
            version = row["version"]
            client.post(
                f"/admin/questions/{qid}/approve",
                headers=headers,
                params={"rights_confirmed": "true", "expected_version": version},
            ).raise_for_status()
            client.post(
                f"/admin/questions/{qid}/publish",
                headers=headers,
                params={"expected_version": version},
            ).raise_for_status()
        for exam_id, exam in exams.items():
            if exam_id not in existing_exams:
                client.post(
                    "/admin/exams", headers=headers, json=exam
                ).raise_for_status()
            elif existing_exams[exam_id]["state"] == "published":
                continue
            client.post(
                f"/admin/exams/{exam_id}/publish", headers=headers
            ).raise_for_status()
        pending_docs = [d for did, d in notes.items() if did not in existing_docs]
        for start in range(0, len(pending_docs), 50):
            client.post(
                "/admin/documents/import",
                headers=headers,
                json={"documents": pending_docs[start : start + 50]},
            ).raise_for_status()
        document_rows = checked_fixture_rows(
            client.get("/admin/documents", headers=headers).raise_for_status().json(),
            notes,
            DocumentInput,
            "document",
        )
        for did, row in document_rows.items():
            if did not in notes or row["state"] == "published":
                continue
            client.post(
                f"/admin/documents/{did}/approve?rights_confirmed=true", headers=headers
            ).raise_for_status()
            client.post(
                f"/admin/documents/{did}/publish", headers=headers
            ).raise_for_status()
    config.admin_token = ""
    app = create_app(config)
    requests = deque()

    @app.middleware("http")
    async def preview_gate(request, call_next):
        if not PUBLIC.fullmatch(request.url.path):
            return JSONResponse({"detail": "Not available in phone preview"}, 404)
        now = time.monotonic()
        while requests and requests[0] <= now - 60:
            requests.popleft()
        # One process, global bound; does not trust client-supplied forwarding headers.
        if len(requests) >= 120 and request.url.path != "/health":
            return JSONResponse(
                {"detail": "Please retry later"}, 429, headers={"Retry-After": "60"}
            )
        if request.url.path != "/health":
            requests.append(now)
        return await call_next(request)

    return app
