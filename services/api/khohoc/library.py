"""Local document library. Imports are metadata only; never fetch remote files."""

import hashlib
import json
from functools import lru_cache
import re
import unicodedata
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Callable, Literal
from urllib.parse import urlsplit

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlalchemy import JSON, DateTime, Integer, String, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Mapped, Session, mapped_column

from .catalog import subjects_for_grade
from .models import Base

MAX_PDF_BYTES = 10 * 1024 * 1024
DEFAULT_LIBRARY_ROOT = Path(__file__).resolve().parents[3] / "data/library/files"
DocumentKind = Literal["study_notes", "worksheet", "reference", "exam"]
Textbook = Literal[
    "independent",
    "ket_noi_tri_thuc",
    "chan_troi_sang_tao",
    "canh_dieu",
    "national_common",
]


@lru_cache(maxsize=1)
def textbook_unit_pairs() -> dict[str, tuple[int, str]]:
    """Secondary-source mapping, not publisher or pedagogical approval."""
    path = Path(__file__).resolve().parents[3] / "data/seeds/textbook_units.json"
    books = json.loads(path.read_text(encoding="utf-8"))["books"]
    return {
        unit["id"]: (book["grade"], book["subject"])
        for book in books
        for unit in book.get("units", [])
    }


def is_textbook_lesson(item: dict) -> bool:
    """Apply the same SGK mapping requirement to every grade and subject."""
    if (
        item.get("textbook") != "ket_noi_tri_thuc"
        or item.get("source_type") == "link_only"
        or item.get("kind") not in ("study_notes", "worksheet")
        or item.get("assessment_period") not in (None, "review")
        or textbook_unit_pairs().get(item.get("curriculum_unit_id"))
        != (item.get("grade"), item.get("subject"))
    ):
        return False
    headings = [
        s.get("heading", "")
        for s in item.get("sections", [])
        if s.get("text", "").strip()
    ]
    return all(
        any(required in heading for heading in headings)
        for required in (
            "Kiến thức và cách làm",
            "Ví dụ từng bước",
            "Bài tập tự luyện",
            "Lời giải bài tập",
        )
    )


def search_key(value: str) -> str:
    """Vietnamese search: Unicode decomposition, case folding, and đ → d."""
    decomposed = unicodedata.normalize("NFD", value.casefold().replace("đ", "d"))
    return " ".join(
        "".join(c for c in decomposed if not unicodedata.combining(c)).split()
    )


AssessmentPeriod = Literal[
    "midterm_1", "final_1", "midterm_2", "final_2", "graduation", "review"
]


class DocumentSection(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    heading: str = Field(min_length=1, max_length=150)
    text: str = Field(min_length=1, max_length=10000)


class DocumentInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    id: str = Field(pattern=r"^[a-zA-Z0-9_-]{1,80}$")
    title: str = Field(min_length=1, max_length=200)
    grade: int = Field(ge=1, le=12)
    subject: str = Field(min_length=1, max_length=60)
    semester: Literal[1, 2] | None = None
    topic: str = Field(min_length=1, max_length=100)
    chapter: str | None = Field(default=None, max_length=300)
    lesson_order: int | None = Field(default=None, ge=1, le=10000)
    curriculum_unit_id: str | None = Field(default=None, pattern=r"^unit_[a-f0-9]{20}$")
    textbook: Textbook = "independent"
    kind: DocumentKind = "study_notes"
    summary: str = Field(min_length=1, max_length=2000)
    author: str = Field(min_length=1, max_length=200)
    source_name: str = Field(min_length=1, max_length=200)
    source_url: str | None = Field(default=None, max_length=2000)
    assessment_period: AssessmentPeriod | None = None
    exam_year: int | None = Field(default=None, ge=2000, le=2100)
    source_verified_on: date | None = None
    resource_scope: Literal["single_paper", "collection", "study_guide"] = "study_guide"
    access_notice: str = Field(default="", max_length=500)
    source_type: Literal["original", "licensed", "link_only"] = "original"
    license: Literal[
        "original_content",
        "CC-BY-4.0",
        "CC-BY-SA-4.0",
        "written_permission",
        "link_only",
    ]
    rights_evidence: str = Field(min_length=10, max_length=5000)
    distribution_allowed: bool = False
    download_allowed: bool = False
    pdf_filename: str | None = Field(
        default=None, pattern=r"^[a-zA-Z0-9][a-zA-Z0-9_-]{0,99}\.pdf$"
    )
    sections: list[DocumentSection] = Field(default_factory=list, max_length=30)

    @model_validator(mode="after")
    def validate_permissions(self):
        if (
            self.assessment_period == "graduation"
            and self.textbook != "national_common"
        ):
            raise ValueError(
                "National graduation exams must use national_common, not a textbook label"
            )
        if self.textbook == "national_common" and self.grade != 12:
            raise ValueError("National graduation resources belong to grade 12")
        if (
            self.assessment_period == "graduation"
            and self.resource_scope == "single_paper"
            and self.exam_year is None
        ):
            raise ValueError("An individual national exam must identify its year")
        if self.subject not in {s["id"] for s in subjects_for_grade(self.grade)}:
            raise ValueError("Subject not available for grade")
        if self.source_url:
            parsed = urlsplit(self.source_url)
            if (
                parsed.scheme != "https"
                or not parsed.hostname
                or parsed.username
                or parsed.password
                or any(ord(c) < 33 for c in self.source_url)
            ):
                raise ValueError("Source URL must be HTTPS without credentials")
        if self.source_type == "link_only":
            if (
                not self.source_url
                or self.license != "link_only"
                or self.distribution_allowed
                or self.download_allowed
                or self.pdf_filename
                or self.sections
            ):
                raise ValueError(
                    "Link-only sources allow metadata and source link only"
                )
        else:
            if not self.pdf_filename and not self.sections:
                raise ValueError("Distributed document requires content or a local PDF")
            if self.source_type == "original" and self.license != "original_content":
                raise ValueError("Original content must identify its own provenance")
            if self.source_type == "licensed" and self.license in (
                "original_content",
                "link_only",
            ):
                raise ValueError("Licensed source requires an appropriate license")
            if self.download_allowed and (
                not self.distribution_allowed or not self.pdf_filename
            ):
                raise ValueError("Downloads require a PDF and redistribution rights")
        return self


class DocumentBatch(BaseModel):
    model_config = ConfigDict(extra="forbid")
    documents: list[DocumentInput] = Field(min_length=1, max_length=100)


class LibraryDocument(Base):
    __tablename__ = "local_documents"
    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    payload: Mapped[dict] = mapped_column(JSON)
    fingerprint: Mapped[str] = mapped_column(String(64), unique=True)
    state: Mapped[str] = mapped_column(String(30), default="draft")
    rights_confirmed: Mapped[bool] = mapped_column(default=False)
    version: Mapped[int] = mapped_column(Integer, default=1)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


def fingerprint(document: DocumentInput) -> str:
    text = "|".join(
        [str(document.grade), document.subject, search_key(document.title)]
        + [search_key(section.text) for section in document.sections]
    )
    return hashlib.sha256(text.encode()).hexdigest()


def read_pdf(root: Path, filename: str) -> bytes:
    """Bounded read of one plain filename, with symlink and path escape checks."""
    if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_-]{0,99}\.pdf", filename):
        raise HTTPException(422, "Invalid local PDF filename")
    resolved_root = root.resolve()
    path = resolved_root / filename
    if (
        path.is_symlink()
        or not path.is_file()
        or path.resolve().parent != resolved_root
    ):
        raise HTTPException(422, "Local PDF unavailable")
    try:
        with path.open("rb") as handle:
            payload = handle.read(MAX_PDF_BYTES + 1)
    except OSError:
        raise HTTPException(422, "Local PDF unavailable") from None
    if len(payload) > MAX_PDF_BYTES:
        raise HTTPException(422, "PDF exceeds 10 MiB limit")
    if not payload.startswith(b"%PDF-") or not payload.rstrip().endswith(b"%%EOF"):
        raise HTTPException(422, "Invalid PDF signature")
    # A conservative guard for this small local library, not a general PDF sanitizer.
    if re.search(rb"/(?:JavaScript|JS|Launch|OpenAction|EmbeddedFile)\b", payload):
        raise HTTPException(422, "Active PDF content is not accepted")
    return payload


@lru_cache(maxsize=1)
def source_practice_pairs():
    path = Path(__file__).resolve().parents[3] / "data/seeds/source_practice_map.json"
    return (
        json.loads(path.read_text(encoding="utf-8"))["papers"] if path.exists() else {}
    )


def public_document(row: LibraryDocument, *, detail: bool = False) -> dict:
    body = row.payload
    metadata = {
        key: body[key]
        for key in (
            "id",
            "title",
            "grade",
            "subject",
            "semester",
            "topic",
            "textbook",
            "kind",
            "summary",
            "author",
            "source_name",
            "source_url",
            "source_type",
            "license",
        )
    }
    view = bool(body.get("pdf_filename") and body["distribution_allowed"])
    metadata.update(
        {
            key: body.get(key)
            for key in (
                "assessment_period",
                "chapter",
                "lesson_order",
                "curriculum_unit_id",
                "exam_year",
                "source_verified_on",
                "resource_scope",
                "access_notice",
            )
        }
    )
    metadata.update(
        state=row.state,
        version=row.version,
        updated_at=row.updated_at.isoformat()
        + ("Z" if row.updated_at.tzinfo is None else ""),
        can_view_pdf=view,
        can_download=view and body["download_allowed"],
        can_open_source=bool(body["source_url"]),
        file_url=f"/documents/{row.id}/file" if view else None,
    )
    if detail:
        metadata["sections"] = body["sections"]
    pair = source_practice_pairs().get(row.id)
    if pair:
        metadata.update(
            reference_title=metadata["title"],
            title=pair["title"],
            practice_exam_id=pair["exam_id"],
            practice_notice=pair["notice"],
            summary=f"{pair['question_count']} câu · Làm và chấm trong app. {pair['notice']} Nguồn tham khảo: {body['title']}",
        )
    return metadata


def create_library_router(
    db: Callable, admin: Callable, audit: Callable, *, library_root: Path | None = None
) -> APIRouter:
    router = APIRouter()
    root = library_root or DEFAULT_LIBRARY_ROOT

    def eligible(row: LibraryDocument) -> bool:
        return bool(
            row.state == "published"
            and row.rights_confirmed
            and (
                row.payload["source_type"] == "link_only"
                or row.payload["distribution_allowed"]
            )
        )

    def visible(session: Session, document_id: str) -> LibraryDocument:
        row = session.get(LibraryDocument, document_id)
        if row is None or not eligible(row):
            raise HTTPException(404, "Document not found")
        return row

    @router.get("/documents")
    def documents(
        grade: int | None = Query(default=None, ge=1, le=12),
        subject: str | None = Query(default=None, max_length=60),
        semester: int | None = Query(default=None, ge=1, le=2),
        topic: str = Query(default="", max_length=100),
        textbook: Textbook | None = None,
        kind: DocumentKind | None = None,
        section: Literal["lessons", "exams", "references"] | None = None,
        assessment_period: AssessmentPeriod | None = None,
        exam_year: int | None = Query(default=None, ge=2000, le=2100),
        search: str = Query(default="", max_length=100),
        limit: int = Query(default=50, ge=1, le=100),
        offset: int = Query(default=0, ge=0, le=10000),
        session: Session = Depends(db),
    ):
        found = []
        for row in session.scalars(
            select(LibraryDocument)
            .where(LibraryDocument.state == "published")
            .order_by(LibraryDocument.updated_at.desc(), LibraryDocument.id)
        ):
            if not eligible(row):
                continue
            item = row.payload
            is_exam = item["kind"] == "exam" or item.get("assessment_period") in (
                "midterm_1",
                "final_1",
                "midterm_2",
                "final_2",
                "graduation",
            )
            is_lesson = is_textbook_lesson(item)
            if section == "lessons" and not is_lesson:
                continue
            if section == "exams" and not is_exam:
                continue
            if section == "references" and (is_lesson or is_exam):
                continue
            if any(
                expected is not None and item.get(field) != expected
                for field, expected in (
                    ("grade", grade),
                    ("subject", subject),
                    ("semester", semester),
                    ("textbook", textbook),
                    ("kind", kind),
                    ("assessment_period", assessment_period),
                    ("exam_year", exam_year),
                )
            ):
                continue
            if search_key(topic) not in search_key(item["topic"]):
                continue
            haystack = search_key(
                " ".join(
                    [item["title"], item["topic"], item["summary"], item["author"]]
                    + [s["heading"] + " " + s["text"] for s in item["sections"]]
                )
            )
            if not all(term in haystack for term in search_key(search).split()):
                continue
            found.append(public_document(row))
        terms = search_key(search).split()

        def rank(item):
            if not terms:
                return 0
            title = search_key(item["title"])
            if all(term in title for term in terms):
                return 0
            metadata = search_key(
                " ".join([item["title"], item["topic"], item["summary"]])
            )
            return 1 if all(term in metadata for term in terms) else 2

        if section == "lessons":
            found.sort(
                key=lambda d: (
                    rank(d),
                    d.get("lesson_order") is None,
                    d.get("lesson_order") or 0,
                    d["title"],
                )
            )
        elif terms:
            found.sort(key=rank)
        return found[offset : offset + limit]

    @router.get("/documents/{document_id}")
    def detail(document_id: str, session: Session = Depends(db)):
        return public_document(visible(session, document_id), detail=True)

    @router.get("/documents/{document_id}/file")
    def pdf(
        document_id: str,
        download: bool = False,
        session: Session = Depends(db),
    ):
        row = visible(session, document_id)
        body = row.payload
        if (
            body["source_type"] == "link_only"
            or not body["distribution_allowed"]
            or not body["pdf_filename"]
            or (download and not body["download_allowed"])
        ):
            raise HTTPException(403, "PDF viewing or download not permitted")
        payload = read_pdf(root, body["pdf_filename"])
        disposition = "attachment" if download else "inline"
        return Response(
            payload,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'{disposition}; filename="{row.id}.pdf"',
                "X-Content-Type-Options": "nosniff",
                "Content-Security-Policy": "sandbox",
            },
        )

    @router.get("/admin/documents", dependencies=[Depends(admin)])
    def admin_list(session: Session = Depends(db)):
        return [
            {
                "document": row.payload,
                "state": row.state,
                "rights_confirmed": row.rights_confirmed,
                "version": row.version,
            }
            for row in session.scalars(
                select(LibraryDocument).order_by(LibraryDocument.id)
            )
        ]

    @router.post("/admin/documents/import", dependencies=[Depends(admin)])
    def import_documents(batch: DocumentBatch, session: Session = Depends(db)):
        hashes = [fingerprint(document) for document in batch.documents]
        if len(set(hashes)) != len(hashes) or len(
            {document.id for document in batch.documents}
        ) != len(hashes):
            raise HTTPException(409, "Duplicate in batch; nothing imported")
        for document, digest in zip(batch.documents, hashes, strict=True):
            if session.get(LibraryDocument, document.id) or session.scalar(
                select(LibraryDocument).where(LibraryDocument.fingerprint == digest)
            ):
                raise HTTPException(
                    409, "Duplicate existing document; nothing imported"
                )
            if document.pdf_filename:
                read_pdf(root, document.pdf_filename)
        for document, digest in zip(batch.documents, hashes, strict=True):
            session.add(
                LibraryDocument(
                    id=document.id,
                    payload=document.model_dump(mode="json"),
                    fingerprint=digest,
                    state="draft",
                    rights_confirmed=False,
                )
            )
        audit(session, "import-documents", str(len(batch.documents)))
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise HTTPException(409, "Concurrent duplicate import") from None
        return {"imported": len(batch.documents), "state": "draft"}

    @router.post(
        "/admin/documents/{document_id}/approve", dependencies=[Depends(admin)]
    )
    def approve(
        document_id: str,
        rights_confirmed: bool = Query(),
        session: Session = Depends(db),
    ):
        row = session.get(LibraryDocument, document_id)
        if row is None:
            raise HTTPException(404, "Document not found")
        document = DocumentInput.model_validate(row.payload)
        if not rights_confirmed or (
            document.source_type != "link_only" and not document.distribution_allowed
        ):
            raise HTTPException(422, "Document or linking rights must be verified")
        if document.pdf_filename:
            read_pdf(root, document.pdf_filename)
        row.state, row.rights_confirmed = "approved", True
        row.updated_at = datetime.now(timezone.utc)
        audit(session, "approve-document", document_id)
        session.commit()
        return {"state": row.state}

    @router.post(
        "/admin/documents/{document_id}/publish", dependencies=[Depends(admin)]
    )
    def publish(document_id: str, session: Session = Depends(db)):
        row = session.get(LibraryDocument, document_id)
        if row is None or row.state != "approved" or not row.rights_confirmed:
            raise HTTPException(409, "Requires approved document and rights")
        document = DocumentInput.model_validate(row.payload)
        if document.source_type != "link_only" and not document.distribution_allowed:
            raise HTTPException(409, "Redistribution not permitted")
        if document.pdf_filename:
            read_pdf(root, document.pdf_filename)
        row.state = "published"
        row.updated_at = datetime.now(timezone.utc)
        audit(session, "publish-document", document_id)
        session.commit()
        return {"state": row.state}

    return router
