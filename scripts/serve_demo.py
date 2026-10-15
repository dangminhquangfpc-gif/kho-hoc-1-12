"""One localhost origin for Flutter web and its public backend API."""

from pathlib import Path
import os
from urllib.parse import urlsplit
import re
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import Response, JSONResponse
from fastapi.staticfiles import StaticFiles

ROOT = Path(__file__).resolve().parents[1]
BACKEND_URL = os.environ.get("KHOHOC_DEMO_API_URL", "http://127.0.0.1:8000")
backend = urlsplit(BACKEND_URL)
if (
    backend.scheme != "http"
    or backend.hostname not in ("127.0.0.1", "localhost")
    or backend.username
    or backend.password
    or backend.query
    or backend.fragment
    or backend.path not in ("", "/")
):
    raise RuntimeError("Demo backend must be a loopback HTTP address")
BACKEND_URL = BACKEND_URL.rstrip("/")
app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
PUBLIC = re.compile(
    r"(?:ai/status|ai/explain|content-reports|classroom/content-reports|classroom/content-reports/[^/]+/review|auth/(?:me|login|logout|register|password)|account/assignments|account/results|account/attempts|account/attempts/[^/]+|account/attempts/[^/]+/draft|account/delete|classroom/groups|classroom/groups/join|classroom/groups/[^/]+|classroom/groups/[^/]+/results\.csv|classroom/groups/[^/]+/assignments|classroom/groups/[^/]+/assignments/[^/]+|classroom/groups/[^/]+/assignments/[^/]+/results\.csv|classroom/groups/[^/]+/members|classroom/groups/[^/]+/members/[^/]+|classroom/students|classroom/students/bulk|classroom/students/[^/]+|classroom/students/[^/]+/(?:results|reset-password)|health|ready|coverage|curriculum|practice-options|practice-attempts|grades|grades/[0-9]+/subjects|exams|exams/[^/]+|exams/[^/]+/attempts|attempts/[^/]+|attempts/[^/]+/(?:submit|result)|documents|documents/[^/]+|documents/[^/]+/file)"
)


@app.middleware("http")
async def fresh_demo_assets(request: Request, call_next):
    response = await call_next(request)
    # Never serve a previous ZIP's app shell after a local demo upgrade.
    response.headers["Cache-Control"] = "no-store"
    return response


@app.get("/flutter_service_worker.js")
async def retire_legacy_worker():
    # Old Flutter bootstraps still request this URL. Retire their asset cache
    # without clearing localStorage, saved answers, history, or IndexedDB.
    return Response(
        """self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', event => event.waitUntil((async () => {
  for (const name of ['flutter-app-cache', 'flutter-temp-cache', 'flutter-app-manifest']) {
    await caches.delete(name);
  }
  await self.registration.unregister();
  const windows = await self.clients.matchAll({type: 'window'});
  await Promise.all(windows.map(client => client.navigate(client.url)));
})()));
""",
        media_type="application/javascript",
        headers={"Service-Worker-Allowed": "/"},
    )


@app.api_route("/api/{path:path}", methods=["GET", "POST", "DELETE", "OPTIONS"])
async def api(path: str, request: Request):
    if not PUBLIC.fullmatch(path):
        return JSONResponse({"detail": "Not found"}, 404)
    body = bytearray()
    async for chunk in request.stream():
        body.extend(chunk)
        if len(body) > 2_000_000:
            return JSONResponse({"detail": "Request too large"}, 413)
    headers = {
        k: v
        for k, v in request.headers.items()
        if k.lower() in ("content-type", "x-attempt-token")
    }
    headers["x-forwarded-proto"] = request.url.scheme
    cookie = request.cookies.get("khohoc_session")
    if cookie:
        headers["cookie"] = "khohoc_session=" + cookie
    authorization = request.headers.get("authorization", "")
    if authorization.startswith("Bearer khs_"):
        headers["authorization"] = authorization
    if (
        request.method in ("POST", "DELETE")
        and request.headers.get("sec-fetch-site") == "cross-site"
    ):
        return JSONResponse({"detail": "Cross-site request denied"}, 403)
    try:
        async with httpx.AsyncClient(timeout=30, trust_env=False) as client:
            result = await client.request(
                request.method,
                BACKEND_URL + "/" + path,
                params=request.query_params,
                headers=headers,
                content=bytes(body),
            )
        return Response(
            result.content,
            status_code=result.status_code,
            headers={
                k: v
                for k, v in result.headers.items()
                if k.lower()
                in (
                    "content-type",
                    "set-cookie",
                    "content-disposition",
                    "cache-control",
                    "x-content-type-options",
                )
            },
        )
    except httpx.HTTPError:
        return JSONResponse({"detail": "Backend temporarily unavailable"}, 503)


app.mount(
    "/", StaticFiles(directory=ROOT / "apps/mobile/build/web", html=True), name="demo"
)
