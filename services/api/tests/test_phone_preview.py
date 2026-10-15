from fastapi.testclient import TestClient
from khohoc.phone_preview import create_preview


def test_phone_preview_seed_private_routes_and_rate_limit(tmp_path, monkeypatch):
    monkeypatch.setenv("KHOHOC_DATABASE_URL", f"sqlite:///{tmp_path}/preview.db")
    with TestClient(create_preview()) as client:
        assert client.get("/health").json()["status"] == "ok"
        assert all(
            len(client.get("/exams", params={"grade": n}).json()) == 8
            for n in [1, 5, 9, 12]
        )
        assert len(client.get("/documents", params={"limit": 100}).json()) == 100
        assert (
            len(client.get("/documents", params={"limit": 100, "offset": 100}).json())
            == 100
        )
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
