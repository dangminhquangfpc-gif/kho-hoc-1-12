from fastapi.testclient import TestClient
from khohoc.phone_preview import create_preview


def test_phone_preview_seed_private_routes_and_rate_limit(tmp_path, monkeypatch):
    monkeypatch.setenv("KHOHOC_DATABASE_URL", f"sqlite:///{tmp_path}/preview.db")
    with TestClient(create_preview()) as client:
        assert client.get("/health").json()["status"] == "ok"
        assert all(
            len(client.get("/exams", params={"grade": n}).json())
            == (95 if n == 5 else 8)
            for n in [1, 5, 9, 12]
        )
        assert len(client.get("/documents", params={"limit": 100}).json()) == 100
        assert (
            len(client.get("/documents", params={"limit": 100, "offset": 100}).json())
            == 100
        )
        lessons = client.get(
            "/documents",
            params={"grade": 5, "subject": "toan", "section": "lessons", "limit": 100},
        ).json()
        assert len(lessons) == 75
        assert [d["lesson_order"] for d in lessons[:75]] == list(range(1, 76))
        assert all(
            d["kind"] != "exam" and d["source_type"] != "link_only" for d in lessons
        )
        assert (
            client.get(
                "/documents",
                params={"grade": 6, "subject": "toan", "section": "lessons"},
            ).json()
            == []
        )
        references = client.get(
            "/documents",
            params={"grade": 6, "subject": "toan", "section": "references"},
        ).json()
        assert any(d["source_type"] == "original" for d in references)
        exam_sources = client.get(
            "/documents",
            params={"grade": 6, "subject": "toan", "section": "exams", "limit": 100},
        ).json()
        assert exam_sources and all(d["kind"] == "exam" for d in exam_sources)
        curriculum = client.get(
            "/curriculum", params={"grade": 5, "subject": "toan"}
        ).json()
        assert curriculum["unit_count"] == curriculum["authored_count"] == 75
        assert all(u["document_id"] is not None for u in curriculum["units"])
        partial = client.get(
            "/curriculum", params={"grade": 6, "subject": "toan"}
        ).json()
        assert partial["authored_count"] == 0 and all(
            u["content_status"] == "missing" for u in partial["units"]
        )
        for grade, count in [(1, 41), (2, 74), (3, 79), (4, 73)]:
            guide_index = client.get(
                "/curriculum", params={"grade": grade, "subject": "toan"}
            ).json()
            assert guide_index["authored_count"] == guide_index["unit_count"] == count
            assert all(u["document_id"] for u in guide_index["units"])
            guides = client.get(
                "/documents",
                params={
                    "grade": grade,
                    "subject": "toan",
                    "section": "lessons",
                    "limit": 100,
                },
            ).json()
            assert len(guides) == count
        circle3 = client.get("/documents/kntt_math3_lesson_17").json()
        assert circle3["grade"] == 3 and circle3["sections"]
        assert "3,14" not in str(circle3["sections"])
        options = client.get(
            "/practice-options", params={"grade": 5, "subject": "toan"}
        )
        assert options.status_code == 200 and options.json()["total"] > 400
        custom = client.post(
            "/practice-attempts",
            json={"grade": 5, "subject": "toan", "topic": "add_decimal", "count": 3},
        )
        assert custom.status_code == 201 and len(custom.json()["questions"]) == 3
        coverage = client.get("/coverage", params={"grade": 2}).json()
        math = next(row for row in coverage if row["subject"] == "toan")
        assert math["question_count"] == 60 and math["exam_count"] == 7
        assert all(row["exam_count"] >= 1 for row in coverage)
        pdf = client.get("/documents/note_math_1_addition/file")
        assert pdf.status_code == 200 and pdf.content.startswith(b"%PDF-")
        assert (
            len(
                client.get(
                    "/exams", params={"grade": 1, "subject": "tieng_viet"}
                ).json()
            )
            == 2
        )
        for path in ["/admin/questions", "/docs", "/openapi.json"]:
            assert client.get(path).status_code == 404
        for _ in range(120):
            client.get("/grades")
        assert client.get("/grades").status_code == 429
        assert client.get("/health").status_code == 200
