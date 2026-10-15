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
    r"(?:health|coverage|curriculum|grades|grades/[0-9]+/subjects|exams|exams/[^/]+|exams/[^/]+/attempts|attempts/[^/]+|attempts/[^/]+/(?:submit|result)|documents|documents/[^/]+|documents/[^/]+/file)"
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
