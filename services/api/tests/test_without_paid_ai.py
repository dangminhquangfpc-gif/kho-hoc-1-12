"""Old environment configuration cannot expose or call a paid AI provider."""

from fastapi.testclient import TestClient
import httpx

from khohoc.app import Settings, create_app


def test_paid_ai_routes_removed_even_with_legacy_environment(tmp_path, monkeypatch):
    secret = tmp_path / "ai-secret.api-key"
    secret.write_text("synthetic-private-test-key-only")
    original = secret.read_bytes()
    for name, value in {
        "KHOHOC_AI_ENABLED": "true",
        "KHOHOC_AI_BASE_URL": "https://api.example.com/v1",
        "KHOHOC_AI_MODEL": "legacy-paid-model",
        "KHOHOC_AI_API_KEY_FILE": str(secret),
        "KHOHOC_AI_API_KEY": "synthetic-environment-key-only",
        "KHOHOC_AI_DAILY_USER_LIMIT": "invalid old setting",
    }.items():
        monkeypatch.setenv(name, value)

    def reject_external_client(*args, **kwargs):
        raise AssertionError("No remote AI client may be created")

    monkeypatch.setattr(httpx, "AsyncClient", reject_external_client)
    app = create_app(Settings(database_url=f"sqlite:///{tmp_path}/test.sqlite"))
    with TestClient(app) as client:
        assert client.get("/health").status_code == 200
        for headers in ({}, {"Authorization": "Bearer khs_legacy-session"}):
            assert client.get("/ai/status", headers=headers).status_code == 404
            assert (
                client.post(
                    "/ai/explain",
                    headers=headers,
                    json={"text": "Giải bài tập này", "consent": True},
                ).status_code
                == 404
            )
        assert not any(
            path.startswith("/ai/")
            for path in client.get("/openapi.json").json()["paths"]
        )
    assert secret.read_bytes() == original
