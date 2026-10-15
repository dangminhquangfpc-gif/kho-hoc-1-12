"""Import original study-note fixtures; never download or scrape external files."""

import argparse
import json
import os
from pathlib import Path
import sys

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "services/api"))
from khohoc.library import DocumentInput  # noqa: E402
from khohoc.phone_preview import (  # noqa: E402
    canonical_fixture_map,
    checked_fixture_rows,
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--api", default="http://127.0.0.1:8000")
    parser.add_argument(
        "--publish-fixtures",
        action="store_true",
        help="DEV ONLY: approve original sample notes for a local test",
    )
    args = parser.parse_args()
    if os.environ.get("KHOHOC_MODE", "development") != "development":
        raise SystemExit("Sample document publication only allowed in development")
    token = os.environ.get("KHOHOC_ADMIN_TOKEN")
    if not token:
        raise SystemExit("Configure KHOHOC_ADMIN_TOKEN in a local ignored file")
    fixtures = canonical_fixture_map(
        json.loads((ROOT / "data/library/documents.json").read_text())["documents"],
        DocumentInput,
    )
    with httpx.Client(
        base_url=args.api,
        headers={"Authorization": "Bearer " + token},
        timeout=30,
    ) as client:
        existing = checked_fixture_rows(
            client.get("/admin/documents").raise_for_status().json(),
            fixtures,
            DocumentInput,
            "document",
        )
        pending = [d for did, d in fixtures.items() if did not in existing]
        for start in range(0, len(pending), 50):
            client.post(
                "/admin/documents/import",
                json={"documents": pending[start : start + 50]},
            ).raise_for_status()
        if args.publish_fixtures:
            rows = checked_fixture_rows(
                client.get("/admin/documents").raise_for_status().json(),
                fixtures,
                DocumentInput,
                "document",
            )
            for document_id, row in rows.items():
                if document_id not in fixtures or row["state"] == "published":
                    continue
                client.post(
                    f"/admin/documents/{document_id}/approve",
                    params={"rights_confirmed": "true"},
                ).raise_for_status()
                client.post(
                    f"/admin/documents/{document_id}/publish"
                ).raise_for_status()
    print(f"Study-note fixtures prepared; publication={args.publish_fixtures}")


if __name__ == "__main__":
    main()
