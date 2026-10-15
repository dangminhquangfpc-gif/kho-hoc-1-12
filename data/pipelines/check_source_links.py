"""Recheck linked source pages; write a report without changing published fixtures."""

import argparse
import concurrent.futures
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request, build_opener, HTTPRedirectHandler

ALLOWED = {"loigiaihay.com", "vietjack.com", "khoahoc.vietjack.com"}


def allowed(url):
    parsed = urlsplit(url)
    return (
        parsed.scheme == "https"
        and parsed.hostname in ALLOWED
        and not parsed.username
        and not parsed.password
    )


class SourceRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not allowed(newurl):
            raise ValueError("Untrusted redirect destination")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def check(document):
    url = document["source_url"]
    result = {
        "id": document["id"],
        "url": url,
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }
    try:
        if not allowed(url):
            raise ValueError("Untrusted source")
        opener = build_opener(SourceRedirect())
        with opener.open(
            Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=15
        ) as response:
            raw = response.read(3_000_001)
            if len(raw) > 3_000_000:
                raise ValueError("Page exceeds bound")
            result.update(
                http_status=response.status,
                final_url=response.url,
                html_sha256=hashlib.sha256(raw).hexdigest(),
            )
    except Exception as exc:
        result["error"] = str(exc)[:200]
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--catalog", type=Path, default=Path("data/library/external_documents.json")
    )
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    documents = json.loads(args.catalog.read_text(encoding="utf-8"))["documents"]
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        results = list(pool.map(check, documents))
    args.report.write_text(
        json.dumps({"results": results}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        f"Checked {len(results)} URLs; {sum(r.get('http_status') == 200 for r in results)} HTTP 200; report {args.report}"
    )
