import json
from pathlib import Path
import importlib.util
from khohoc.library import DocumentInput, search_key

ROOT = Path(__file__).resolve().parents[3]


def test_external_sources_are_verified_link_only_and_book_specific():
    documents = json.loads(
        (ROOT / "data/library/external_documents.json").read_text(encoding="utf-8")
    )["documents"]
    evidence = {
        e["id"]: e
        for e in json.loads(
            (ROOT / "data/library/source_checks.json").read_text(encoding="utf-8")
        )["verified"]
    }
    assert len(documents) >= 1900
    assert len({d["id"] for d in documents}) == len(documents)
    assert len({d["source_url"] for d in documents}) == len(documents)
    periods = set()
    for raw in documents:
        d = DocumentInput.model_validate(raw)
        assert d.source_type == d.license == "link_only"
        assert (
            not d.sections
            and not d.pdf_filename
            and not d.distribution_allowed
            and not d.download_allowed
        )
        check = evidence[d.id]
        assert check["http_status"] == 200 and len(check["html_sha256"]) == 64
        if d.textbook == "ket_noi_tri_thuc":
            assert any(
                marker in search_key(check["book_evidence"])
                for marker in ["ket noi tri thuc", "kntt", "global success"]
            )
            if d.assessment_period:
                periods.add(d.assessment_period)
        else:
            assert d.textbook == "national_common" and d.grade == 12
            if d.resource_scope == "single_paper":
                assert d.exam_year is not None
    assert {"midterm_1", "final_1", "midterm_2", "final_2", "review"} <= periods


def test_period_numbers_do_not_become_grade_numbers():
    spec = importlib.util.spec_from_file_location(
        "web_import", ROOT / "data/pipelines/import_web_catalog.py"
    )
    pipeline = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pipeline)
    url = "https://loigiaihay.com/de-thi-giua-ki-1-toan-6-de-so-18-a176472.html"
    assert pipeline.classify(url, "") == (6, "toan")
    assert pipeline.period(url) == "midterm_1"
    assert pipeline.classify(
        "https://loigiaihay.com/de-thi-hoc-ki-2-van-12-kntt-a123.html", ""
    ) == (12, "ngu_van")


def test_period_and_year_filters_and_national_classification(tmp_path):
    from fastapi.testclient import TestClient
    from khohoc.app import Settings, create_app
    from pydantic import ValidationError
    import pytest

    base = dict(
        grade=12,
        subject="toan",
        topic="Đề kiểm tra",
        summary="Liên kết tài liệu đã xác minh",
        author="Nguồn",
        source_name="Trang nguồn",
        source_type="link_only",
        license="link_only",
        rights_evidence="Chỉ liên kết trang nguồn; không sao chép nội dung.",
        textbook="ket_noi_tri_thuc",
        kind="exam",
    )
    papers = [
        base
        | dict(
            id="midterm",
            title="Đề giữa kỳ",
            source_url="https://example.test/midterm",
            assessment_period="midterm_1",
        ),
        base
        | dict(
            id="final",
            title="Đề cuối kỳ",
            source_url="https://example.test/final",
            assessment_period="final_1",
        ),
        base
        | dict(
            id="national",
            title="Đề quốc gia năm 2025",
            source_url="https://example.test/national",
            assessment_period="graduation",
            textbook="national_common",
            exam_year=2025,
            resource_scope="single_paper",
            source_verified_on="2026-10-15",
        ),
    ]
    with pytest.raises(ValidationError):
        DocumentInput.model_validate(papers[-1] | {"textbook": "ket_noi_tri_thuc"})
    with pytest.raises(ValidationError):
        DocumentInput.model_validate(papers[-1] | {"exam_year": None})
    with TestClient(
        create_app(
            Settings(
                database_url=f"sqlite:///{tmp_path}/filters.db",
                admin_token="filters-test",
            )
        )
    ) as client:
        headers = {"Authorization": "Bearer filters-test"}
        assert (
            client.post(
                "/admin/documents/import", headers=headers, json={"documents": papers}
            ).status_code
            == 200
        )
        for paper in papers:
            assert (
                client.post(
                    f"/admin/documents/{paper['id']}/approve",
                    params={"rights_confirmed": True},
                    headers=headers,
                ).status_code
                == 200
            )
            assert (
                client.post(
                    f"/admin/documents/{paper['id']}/publish", headers=headers
                ).status_code
                == 200
            )
        response = client.get("/documents", params={"assessment_period": "midterm_1"})
        assert [d["id"] for d in response.json()] == ["midterm"]
        national = client.get(
            "/documents", params={"textbook": "national_common", "exam_year": 2025}
        ).json()
        assert [d["id"] for d in national] == ["national"]
        assert national[0]["source_verified_on"] == "2026-10-15"
        assert "rights_evidence" not in national[0] and not national[0]["can_download"]
        assert client.get("/documents", params={"exam_year": 2024}).json() == []
        assert client.get("/documents/national/file").status_code == 403
