"""Reviewed transitions for authored fixtures; never overwrite unknown admin edits."""

import hashlib
import json
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path

from sqlalchemy.orm import Session

from .library import DocumentInput, LibraryDocument, fingerprint
from .models import AuditEvent


def payload_hash(payload):
    canonical = DocumentInput.model_validate(payload).model_dump(mode="json")
    return hashlib.sha256(
        json.dumps(
            canonical, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode()
    ).hexdigest()


@lru_cache(maxsize=1)
def transitions():
    path = Path(__file__).resolve().parents[3] / "data/library/document_upgrades.json"
    return json.loads(path.read_text(encoding="utf-8"))["transitions"]


def reviewed_transition(previous, current):
    return previous["id"] == current["id"] and any(
        item["id"] == previous["id"]
        and item["from_sha256"] == payload_hash(previous)
        and item["to_sha256"] == payload_hash(current)
        for item in transitions()
    )


def upgrade_documents(engine, existing, expected):
    """All fixture kinds have been preflighted before this atomic update."""
    with Session(engine) as db:
        for did, old in existing.items():
            if did not in expected:
                continue
            canonical_old = DocumentInput.model_validate(old["document"]).model_dump(
                mode="json"
            )
            if canonical_old == expected[did]:
                continue
            row = db.get(LibraryDocument, did)
            new = expected[did]
            if (
                not row
                or row.state != "published"
                or not row.rights_confirmed
                or not reviewed_transition(row.payload, new)
            ):
                raise RuntimeError("Refusing changed document fixture: " + did)
            before = row.payload
            document = DocumentInput.model_validate(new)
            row.payload = document.model_dump(mode="json")
            row.fingerprint = fingerprint(document)
            row.version += 1
            row.updated_at = datetime.now(timezone.utc)
            db.add(
                AuditEvent(
                    actor="local-fixture",
                    action="upgrade-document",
                    target=json.dumps(
                        {
                            "id": did,
                            "from_sha256": payload_hash(before),
                            "to_sha256": payload_hash(new),
                            "previous_document": before,
                        },
                        ensure_ascii=False,
                    ),
                )
            )
        db.commit()
