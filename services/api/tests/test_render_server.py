"""Provider ingress/configuration tests; no real provider credentials or network."""

import json

import pytest
from starlette.responses import JSONResponse
from starlette.testclient import TestClient

from khohoc.render_server import (
    FORWARDING_HEADERS,
    RenderIngress,
    SYSTEM_CA,
    create_render_app,
    main,
    render_origin,
    render_settings,
)

ORIGIN = "https://tuhoc-synthetic.onrender.com"
RUNTIME_URL = (
    "postgresql+psycopg://tuhoc_app:Synthetic-Test-Password-Only@"
    "ep-synthetic.ap-southeast-1.aws.neon.tech/neondb?sslmode=verify-full"
)


@pytest.fixture
def render_environment(monkeypatch):
    import os

    for key in os.environ:
        if key.startswith(("KHOHOC_", "RENDER_")) or key in {
            "RENDER",
            "PGSSLROOTCERT",
            "FORWARDED_ALLOW_IPS",
            "PORT",
        }:
            monkeypatch.delenv(key)
    values = {
        "RENDER": "true",
        "RENDER_SERVICE_TYPE": "web",
        "RENDER_SERVICE_ID": "srv-synthetic-test",
        "RENDER_EXTERNAL_HOSTNAME": "tuhoc-synthetic.onrender.com",
        "RENDER_EXTERNAL_URL": ORIGIN,
        "KHOHOC_MODE": "shared",
        "KHOHOC_DATABASE_URL": RUNTIME_URL,
        "PGSSLROOTCERT": SYSTEM_CA,
        "FORWARDED_ALLOW_IPS": "*",
    }
    for key, value in values.items():
        monkeypatch.setenv(key, value)
    return values


def test_provider_configuration_is_shared_without_development_credentials(
    render_environment,
):
    settings = render_settings()
    assert settings.mode == "shared"
    assert settings.public_origin == ORIGIN
    assert settings.cors_origins == [ORIGIN]
    assert settings.database_url == RUNTIME_URL
    assert not settings.admin_token and not settings.manager_credentials_file
    # Factory creates an engine only; lifespan is responsible for checking the
    # pre-existing schema. This construction performs no DDL or remote query.
    app = create_render_app()
    assert app.app.state.engine.dialect.name == "postgresql"
    assert app.app.docs_url is None
    app.app.state.engine.dispose()


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("RENDER", "false"),
        ("RENDER_SERVICE_TYPE", "pserv"),
        ("RENDER_SERVICE_ID", ""),
        ("RENDER_EXTERNAL_URL", "http://tuhoc-synthetic.onrender.com"),
        ("RENDER_EXTERNAL_URL", ORIGIN + "/api"),
        ("RENDER_EXTERNAL_URL", ORIGIN + "/"),
        ("RENDER_EXTERNAL_URL", ORIGIN + ":443"),
        ("RENDER_EXTERNAL_URL", ORIGIN + ":broken"),
        ("RENDER_EXTERNAL_URL", "https://someone-else.onrender.com"),
        ("RENDER_EXTERNAL_URL", "https://secret@tuhoc-synthetic.onrender.com"),
        ("RENDER_EXTERNAL_HOSTNAME", "evil.onrender.com.attacker.example"),
    ],
)
def test_origin_requires_actual_canonical_provider_identity(
    render_environment, key, value
):
    with pytest.raises(ValueError):
        render_origin(render_environment | {key: value})


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("KHOHOC_MODE", "development"),
        ("KHOHOC_MODE", "production"),
        ("KHOHOC_PUBLIC_ORIGIN", "https://somewhere.example.org"),
        ("KHOHOC_CORS_ORIGINS", '["https://somewhere.example.org"]'),
        ("KHOHOC_ADMIN_TOKEN", "Synthetic-Admin-Token-Not-Allowed"),
        ("KHOHOC_MANAGER_CREDENTIALS_FILE", "/tmp/not-a-manager-credential"),
        ("PGSSLROOTCERT", "/tmp/untrusted-root-ca"),
        ("KHOHOC_DATABASE_URL", "sqlite:////tmp/unsafe-local.db"),
        ("KHOHOC_DATABASE_URL", RUNTIME_URL.replace("tuhoc_app:", "neondb_owner:")),
        ("KHOHOC_DATABASE_URL", RUNTIME_URL.replace("tuhoc_app:", "neon_superuser:")),
        ("KHOHOC_DATABASE_URL", RUNTIME_URL.replace(".aws.neon.tech", ".evil.example")),
        (
            "KHOHOC_DATABASE_URL",
            RUNTIME_URL.replace("ep-synthetic.", "ep-synthetic-pooler."),
        ),
        ("KHOHOC_DATABASE_URL", RUNTIME_URL.replace("verify-full", "require")),
        ("KHOHOC_DATABASE_URL", RUNTIME_URL.replace("?sslmode=verify-full", "")),
        ("KHOHOC_DATABASE_URL", RUNTIME_URL + "&sslrootcert=/tmp/untrusted-ca"),
    ],
)
def test_runtime_configuration_rejects_unsafe_or_ambiguous_settings(
    render_environment, monkeypatch, key, value
):
    monkeypatch.setenv(key, value)
    with pytest.raises(ValueError) as failure:
        render_settings()
    assert "Synthetic-Test-Password-Only" not in str(failure.value)
    assert "Synthetic-Admin-Token-Not-Allowed" not in str(failure.value)


def test_explicit_matching_origin_and_cors_are_accepted(
    render_environment, monkeypatch
):
    monkeypatch.setenv("KHOHOC_PUBLIC_ORIGIN", ORIGIN)
    monkeypatch.setenv("KHOHOC_CORS_ORIGINS", json.dumps([ORIGIN]))
    assert render_settings().cors_origins == [ORIGIN]


def test_ingress_strips_prefix_preserves_peer_and_ignores_spoofed_headers():
    received = []

    async def capture(scope, receive, send):
        received.append(scope)
        await JSONResponse(
            {
                "path": scope["path"],
                "scheme": scope["scheme"],
                "client": scope["client"],
                "server": scope["server"],
                "query": scope["query_string"].decode(),
            }
        )(scope, receive, send)

    client = TestClient(
        RenderIngress(capture, "tuhoc-synthetic.onrender.com"),
        base_url="http://tuhoc-synthetic.onrender.com",
        client=("10.1.2.3", 4321),
    )
    headers = {key.decode(): "198.51.100.99" for key in FORWARDING_HEADERS}
    headers.update(
        {
            "X-Forwarded-For": "198.51.100.99, 203.0.113.1",
            "X-Forwarded-Proto": "http",
            "X-Forwarded-Host": "attacker.example",
            "X-Forwarded-Unknown": "ignored",
            "Authorization": "Bearer synthetic-session",
            "Origin": ORIGIN,
        }
    )
    response = client.post("/api/auth/login?synthetic=1", headers=headers)
    assert response.status_code == 200
    assert response.json() == {
        "path": "/auth/login",
        "scheme": "https",
        "client": ["10.1.2.3", 4321],
        "server": ["tuhoc-synthetic.onrender.com", 443],
        "query": "synthetic=1",
    }
    forwarded = received[0]
    assert forwarded["root_path"] == ""
    assert forwarded["raw_path"] == b"/auth/login"
    actual = dict(forwarded["headers"])
    assert not FORWARDING_HEADERS.intersection(actual)
    assert not any(key.startswith(b"x-forwarded-") for key in actual)
    assert actual[b"authorization"] == b"Bearer synthetic-session"
    assert actual[b"origin"] == ORIGIN.encode()


def test_api_paths_only_and_strict_host():
    async def capture(scope, receive, send):
        await JSONResponse({"path": scope["path"]})(scope, receive, send)

    client = TestClient(
        RenderIngress(capture, "tuhoc-synthetic.onrender.com"), base_url=ORIGIN
    )
    for path in ("/", "/ready", "/docs", "/openapi.json", "/api", "/api-other/ready"):
        assert client.get(path).status_code == 404
    assert client.get("/api/ready").json() == {"path": "/ready"}
    assert client.get("/api/admin/questions").json() == {"path": "/admin/questions"}
    for host in ("localhost", "attacker.example", "tuhoc-synthetic.onrender.com:80"):
        assert client.get("/api/ready", headers={"Host": host}).status_code == 400
    assert (
        client.get(
            "/api/ready", headers={"Host": "tuhoc-synthetic.onrender.com:443"}
        ).status_code
        == 200
    )
    assert (
        client.get(
            "/api/ready",
            headers=[
                ("Host", "tuhoc-synthetic.onrender.com"),
                ("Host", "attacker.example"),
            ],
        ).status_code
        == 400
    )


def test_main_does_not_inherit_render_wildcard_forwarding(
    render_environment, monkeypatch
):
    called = []
    monkeypatch.setenv("PORT", "10042")
    monkeypatch.setattr(
        "khohoc.render_server.uvicorn.run",
        lambda *args, **kwargs: called.append((args, kwargs)),
    )
    main()
    args, kwargs = called[0]
    assert args == ("khohoc.render_server:create_render_app",)
    assert kwargs["port"] == 10042 and kwargs["workers"] == 1
    assert kwargs["proxy_headers"] is False
    assert kwargs["forwarded_allow_ips"] == ""
    assert kwargs["access_log"] is False


@pytest.mark.parametrize("port", ["bad", "0", "443", "65536"])
def test_invalid_port_fails_before_listener(render_environment, monkeypatch, port):
    monkeypatch.setenv("PORT", port)
    with pytest.raises(ValueError):
        main()
