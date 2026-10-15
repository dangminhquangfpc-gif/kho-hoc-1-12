import json
import secrets
import unicodedata
from contextlib import asynccontextmanager
from pathlib import Path

import pytest
from fastapi import FastAPI, Header, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from khohoc.library import (
    MAX_PDF_BYTES,
    DocumentInput,
    LibraryDocument,
    create_library_router,
    read_pdf,
)
from khohoc.models import AuditEvent, Base

ROOT = Path(__file__).resolve().parents[3]
ADMIN = {"Authorization": "Bearer library-test-token"}
PDF = b"%PDF-1.4\n% inert local test payload\n%%EOF\n"


@pytest.fixture
def client(tmp_path):
    engine = create_engine(
        f"sqlite:///{tmp_path}/library.db", connect_args={"check_same_thread": False}
    )
    files = tmp_path / "pdfs"
    files.mkdir()
    (files / "notes.pdf").write_bytes(PDF)

    def db():
        with Session(engine) as session:
            yield session

    def admin(authorization: str = Header(default="")):
        if not secrets.compare_digest(authorization, ADMIN["Authorization"]):
            raise HTTPException(403, "Admin authorization required")

    def audit(session, action, target):
        session.add(AuditEvent(actor="local-admin", action=action, target=target))

    @asynccontextmanager
    async def lifespan(app):
        Base.metadata.create_all(engine)
        yield
        engine.dispose()

    app = FastAPI(lifespan=lifespan)
    app.include_router(create_library_router(db, admin, audit, library_root=files))
    with TestClient(app) as test:
        test.engine, test.files = engine, files
        yield test


def document(**overrides):
    return {
        "id": "original-notes",
        "title": "Cộng và trừ: ôn tập",
        "grade": 1,
        "subject": "toan",
        "semester": 1,
        "topic": "Số và phép tính",
        "textbook": "independent",
        "kind": "study_notes",
        "summary": "Ghi chú tự biên soạn về phép cộng và phép trừ.",
        "author": "Nhóm thử nghiệm",
        "source_name": "Kho Học · mẫu tự biên soạn",
        "source_type": "original",
        "license": "original_content",
        "rights_evidence": "Tài liệu kiểm thử tự biên soạn, không lấy từ nguồn bên ngoài.",
        "distribution_allowed": True,
        "download_allowed": True,
        "pdf_filename": "notes.pdf",
        "sections": [
            {"heading": "Đếm tiếp", "text": "Có 3 bút và thêm 2 bút: 3 + 2 = 5."}
        ],
    } | overrides


def publish(client, payload=None):
    payload = payload or document()
    response = client.post(
        "/admin/documents/import", headers=ADMIN, json={"documents": [payload]}
    )
    assert response.status_code == 200, response.text
    url = f"/admin/documents/{payload['id']}"
    response = client.post(url + "/approve?rights_confirmed=true", headers=ADMIN)
    assert response.status_code == 200, response.text
    response = client.post(url + "/publish", headers=ADMIN)
    assert response.status_code == 200, response.text


def test_review_visibility_admin_auth_and_audit(client):
    payload = {"documents": [document()]}
    url = "/admin/documents/original-notes"
    assert client.post("/admin/documents/import", json=payload).status_code == 403
    assert client.get("/admin/documents").status_code == 403
    assert (
        client.post("/admin/documents/import", json=payload, headers=ADMIN).status_code
        == 200
    )
    assert client.get("/documents").json() == []
    assert client.get("/documents/original-notes").status_code == 404
    assert client.get("/documents/original-notes/file").status_code == 404
    assert client.post(url + "/publish", headers=ADMIN).status_code == 409
    assert (
        client.post(url + "/approve?rights_confirmed=false", headers=ADMIN).status_code
        == 422
    )
    assert (
        client.post(url + "/approve?rights_confirmed=true", headers=ADMIN).status_code
        == 200
    )
    assert client.get("/documents").json() == []
    assert client.post(url + "/publish", headers=ADMIN).status_code == 200
    public = client.get("/documents/original-notes").json()
    assert public["state"] == "published"
    assert public["sections"][0]["heading"] == "Đếm tiếp"
    assert public["can_download"] is True
    assert "pdf_filename" not in public
    assert "rights_evidence" not in public
    assert client.get(public["file_url"]).content == PDF
    assert (
        client.get(public["file_url"] + "?download=true")
        .headers["content-disposition"]
        .startswith("attachment;")
    )
    with Session(client.engine) as session:
        assert {event.action for event in session.scalars(select(AuditEvent))} == {
            "import-documents",
            "approve-document",
            "publish-document",
        }


def test_vietnamese_search_filters_and_paging(client):
    publish(client)
    publish(
        client,
        document(
            id="derivative",
            grade=12,
            semester=2,
            title="Đạo hàm và chiều biến thiên",
            topic="Ứng dụng đạo hàm",
            summary="Ghi chú đạo hàm tự biên soạn.",
            kind="reference",
            textbook="canh_dieu",
            sections=[
                {"heading": "Dấu của đạo hàm", "text": "Đạo hàm dương: hàm đồng biến."}
            ],
        ),
    )
    for term in ["cong va tru", "CỘNG VÀ TRỪ", unicodedata.normalize("NFD", "cộng")]:
        result = client.get("/documents", params={"search": term}).json()
        assert [r["id"] for r in result] == ["original-notes"]
    assert client.get("/documents?search=dao%20ham").json()[0]["id"] == "derivative"
    assert client.get("/documents?search=ham%20dao").json()[0]["id"] == "derivative"
    assert (
        client.get(
            "/documents?grade=1&subject=toan&semester=1&topic=so&textbook=independent&kind=study_notes"
        ).json()[0]["id"]
        == "original-notes"
    )
    assert (
        client.get("/documents?grade=12&textbook=canh_dieu&kind=reference").json()[0][
            "id"
        ]
        == "derivative"
    )
    assert client.get("/documents?subject=tieng_viet").json() == []
    assert client.get("/documents?semester=2&grade=1").json() == []
    assert len(client.get("/documents?limit=1").json()) == 1
    assert len(client.get("/documents?limit=1&offset=1").json()) == 1
    assert client.get("/documents?offset=2").json() == []
    for query in [
        "grade=13",
        "semester=3",
        "limit=101",
        "offset=-1",
        "textbook=unknown",
    ]:
        assert client.get("/documents?" + query).status_code == 422


def test_link_only_and_view_without_download(client):
    publish(client, document(download_allowed=False))
    assert client.get("/documents/original-notes/file").status_code == 200
    assert client.get("/documents/original-notes/file?download=true").status_code == 403
    publish(
        client,
        document(
            id="source-link",
            title="Trang nguồn tham khảo",
            source_type="link_only",
            license="link_only",
            source_url="https://example.edu.vn/reference",
            distribution_allowed=False,
            download_allowed=False,
            pdf_filename=None,
            sections=[],
        ),
    )
    link = client.get("/documents/source-link").json()
    assert link["can_open_source"] is True
    assert link["can_download"] is False
    assert link["can_view_pdf"] is False
    assert link["file_url"] is None
    assert client.get("/documents/source-link/file").status_code == 403


@pytest.mark.parametrize(
    "overrides",
    [
        {"grade": 13},
        {"subject": "vat_ly"},
        {"source_url": "javascript:alert(1)"},
        {"source_url": "https://user:password@example.org/"},
        {"source_url": "https://example.org/\npath"},
        {"source_type": "licensed", "license": "original_content"},
        {"source_type": "original", "license": "CC-BY-4.0"},
        {"source_type": "link_only", "license": "link_only"},
        {"rights_evidence": ""},
        {"distribution_allowed": False, "download_allowed": True},
        {"pdf_filename": "../private.pdf"},
        {"pdf_filename": "/etc/passwd"},
        {"pdf_filename": "https://example.org/file.pdf"},
        {"pdf_filename": "notes.PDF"},
        {"state": "published"},
        {"sections": [{"heading": "", "text": "Empty heading"}]},
    ],
)
def test_metadata_and_permission_validation(client, overrides):
    response = client.post(
        "/admin/documents/import",
        headers=ADMIN,
        json={"documents": [document(**overrides)]},
    )
    assert response.status_code == 422, response.text
    assert client.get("/admin/documents", headers=ADMIN).json() == []


def test_unlicensed_and_revoked_rights_remain_hidden(client):
    response = client.post(
        "/admin/documents/import",
        headers=ADMIN,
        json={
            "documents": [document(distribution_allowed=False, download_allowed=False)]
        },
    )
    assert response.status_code == 200
    assert (
        client.post(
            "/admin/documents/original-notes/approve?rights_confirmed=true",
            headers=ADMIN,
        ).status_code
        == 422
    )
    assert client.get("/documents").json() == []
    with Session(client.engine) as session:
        row = session.get(LibraryDocument, "original-notes")
        row.state = "published"
        row.rights_confirmed = True
        session.commit()
    assert client.get("/documents/original-notes").status_code == 404


def test_duplicate_and_file_validation_keep_import_atomic(client):
    invalid = document(id="missing-pdf", title="Thiếu PDF", pdf_filename="missing.pdf")
    response = client.post(
        "/admin/documents/import",
        headers=ADMIN,
        json={"documents": [document(), invalid]},
    )
    assert response.status_code == 422
    assert client.get("/admin/documents", headers=ADMIN).json() == []
    duplicate = document(id="another-id", title="Cong va tru: on tap")
    response = client.post(
        "/admin/documents/import",
        headers=ADMIN,
        json={"documents": [document(), duplicate]},
    )
    assert response.status_code == 409
    assert client.get("/admin/documents", headers=ADMIN).json() == []
    publish(client)
    assert (
        client.post(
            "/admin/documents/import",
            headers=ADMIN,
            json={
                "documents": [document(id="new-one", title="Ghi chú mới"), document()]
            },
        ).status_code
        == 409
    )
    assert len(client.get("/admin/documents", headers=ADMIN).json()) == 1


def test_local_pdf_traversal_symlink_and_bounded_content(client, tmp_path):
    outside = tmp_path / "private.pdf"
    outside.write_bytes(PDF)
    (client.files / "linked.pdf").symlink_to(outside)
    response = client.post(
        "/admin/documents/import",
        headers=ADMIN,
        json={"documents": [document(pdf_filename="linked.pdf")]},
    )
    assert response.status_code == 422
    for filename, body in [
        ("active.pdf", b"%PDF-1.4\n/JavaScript (bad)\n%%EOF"),
        ("html.pdf", b"<html>not a PDF</html>"),
        ("huge.pdf", b"%PDF-1.4\n" + b" " * MAX_PDF_BYTES + b"\n%%EOF"),
    ]:
        (client.files / filename).write_bytes(body)
        response = client.post(
            "/admin/documents/import",
            headers=ADMIN,
            json={"documents": [document(pdf_filename=filename)]},
        )
        assert response.status_code == 422
    publish(client)
    with Session(client.engine) as session:
        row = session.get(LibraryDocument, "original-notes")
        row.payload = row.payload | {"pdf_filename": "../private.pdf"}
        session.commit()
    assert client.get("/documents/original-notes/file").status_code == 422


def test_real_original_notes_have_valid_metadata_and_inert_local_pdf():
    notes = json.loads((ROOT / "data/library/documents.json").read_text())["documents"]
    assert len(notes) >= 3
    assert {n["grade"] for n in notes} == set(range(1, 13))
    for payload in notes:
        document = DocumentInput.model_validate(payload)
        assert document.source_type == "original"
        assert document.license == "original_content"
        assert document.sections
        if document.pdf_filename:
            assert (
                len(read_pdf(ROOT / "data/library/files", document.pdf_filename)) > 1000
            )
        else:
            assert document.download_allowed is False
