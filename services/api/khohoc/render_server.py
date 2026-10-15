"""Render-only shared pilot entrypoint; migrations and credentials stay offline.

Render terminates TLS before forwarding to the service's otherwise non-public
HTTP port. This deployment contract, never a request header, establishes HTTPS.
Do not use this entrypoint behind an arbitrary proxy or on a public local port.
"""

import os
import re
from collections.abc import Mapping
from pathlib import Path
from urllib.parse import urlsplit

import uvicorn
from sqlalchemy.engine import make_url
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from .app import Settings, create_app
from .server_security import validate_shared

SYSTEM_CA = "/etc/ssl/certs/ca-certificates.crt"
FORWARDING_HEADERS = {
    b"forwarded",
    b"x-real-ip",
    b"cf-connecting-ip",
    b"true-client-ip",
    b"x-client-ip",
    b"x-envoy-external-address",
}


def render_origin(environment: Mapping[str, str]) -> str:
    """Validate non-secret provider identity without accepting arbitrary origins."""
    if (
        environment.get("RENDER") != "true"
        or environment.get("RENDER_SERVICE_TYPE") != "web"
        or not environment.get("RENDER_SERVICE_ID", "").startswith("srv-")
    ):
        raise ValueError("This entrypoint requires a Render web service")
    origin = environment.get("RENDER_EXTERNAL_URL", "")
    hostname = environment.get("RENDER_EXTERNAL_HOSTNAME", "")
    try:
        parsed = urlsplit(origin)
        valid = (
            re.fullmatch(
                r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.onrender\.com", hostname
            )
            and parsed.scheme == "https"
            and parsed.hostname == hostname
            and not parsed.username
            and not parsed.password
            and parsed.port is None
            and not parsed.path
            and not parsed.query
            and not parsed.fragment
            and origin == "https://" + hostname
        )
    except ValueError:
        valid = False
    if not valid:
        raise ValueError("Render must supply its canonical HTTPS onrender.com origin")
    return origin


def render_settings() -> Settings:
    """Fail closed before opening a listener or creating a database engine."""
    origin = render_origin(os.environ)
    if os.environ.get("KHOHOC_MODE") != "shared":
        raise ValueError("Render pilot requires KHOHOC_MODE=shared")
    configured_origin = os.environ.get("KHOHOC_PUBLIC_ORIGIN")
    if configured_origin is not None and configured_origin != origin:
        raise ValueError("Public origin must match the Render HTTPS origin")
    configured_cors = os.environ.get("KHOHOC_CORS_ORIGINS")
    if configured_cors is not None:
        # Settings validates its JSON list; do not silently override operator input.
        candidate = Settings(mode="shared", public_origin=origin)
        if candidate.cors_origins != [origin]:
            raise ValueError("CORS must contain only the Render HTTPS origin")
    settings = Settings(mode="shared", public_origin=origin, cors_origins=[origin])
    validate_shared(settings)
    try:
        database = make_url(settings.database_url)
    except Exception:
        raise ValueError(
            "Invalid runtime PostgreSQL connection configuration"
        ) from None
    if (
        database.username != "tuhoc_app"
        or not database.host
        or not database.host.endswith(".neon.tech")
        or "-pooler." in database.host
        or not database.database
        or (not database.password and not settings.database_password_file)
    ):
        raise ValueError(
            "Use the direct Neon connection for SQL runtime role tuhoc_app"
        )
    if database.query.get("sslmode") != "verify-full":
        raise ValueError("Neon runtime connection requires sslmode=verify-full")
    root_certificate = database.query.get("sslrootcert") or os.environ.get(
        "PGSSLROOTCERT"
    )
    if root_certificate != SYSTEM_CA or not Path(SYSTEM_CA).is_file():
        raise ValueError(
            "Neon runtime connection requires the system CA certificate bundle"
        )
    return settings


class RenderIngress:
    """Expose only /api, with canonical HTTPS and no request-header IP trust.

    The retained ASGI client is Render's ingress peer. Per-peer rate limits can
    therefore be shared by many learners. User-supplied XFF cannot mint budgets.
    """

    def __init__(self, app: ASGIApp, hostname: str):
        self.app = app
        self.hostname = hostname

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] == "lifespan":
            await self.app(scope, receive, send)
            return
        if scope["type"] == "websocket":
            await send({"type": "websocket.close", "code": 1008})
            return
        hosts = [value for key, value in scope["headers"] if key.lower() == b"host"]
        expected = self.hostname.encode("ascii")
        if len(hosts) != 1 or hosts[0].lower() not in {expected, expected + b":443"}:
            await JSONResponse({"detail": "Invalid host header"}, 400)(
                scope, receive, send
            )
            return
        if not scope["path"].startswith("/api/"):
            await JSONResponse({"detail": "Not found"}, 404)(scope, receive, send)
            return
        forwarded = dict(scope)
        forwarded["scheme"] = "https"
        forwarded["server"] = (self.hostname, 443)
        # Match the existing Caddy handle_path /api/* contract. The shared API's
        # auth budgets and administration checks inspect these stripped paths.
        forwarded["path"] = scope["path"][4:]
        forwarded["raw_path"] = forwarded["path"].encode("utf-8")
        forwarded["root_path"] = ""
        forwarded["headers"] = [
            (key, value)
            for key, value in scope["headers"]
            if key.lower() not in FORWARDING_HEADERS
            and not key.lower().startswith(b"x-forwarded-")
        ]
        await self.app(forwarded, receive, send)


def create_render_app() -> RenderIngress:
    settings = render_settings()
    # create_app(shared) verifies the existing schema during lifespan. It never
    # migrates, publishes fixtures, or creates a manager in this mode.
    return RenderIngress(
        create_app(settings), urlsplit(settings.public_origin).hostname
    )


def main():
    render_settings()
    try:
        port = int(os.environ.get("PORT", "10000"))
    except ValueError:
        raise ValueError("Render PORT must be an integer") from None
    if not 1024 <= port <= 65535:
        raise ValueError("Render PORT must be between 1024 and 65535")
    uvicorn.run(
        "khohoc.render_server:create_render_app",
        factory=True,
        host="0.0.0.0",
        port=port,
        workers=1,
        proxy_headers=False,
        forwarded_allow_ips="",
        access_log=False,
    )


if __name__ == "__main__":
    main()
