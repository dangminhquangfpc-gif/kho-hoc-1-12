"""Validate/import authorized JSON or CSV. Never publish automatically."""

import argparse
import csv
import hashlib
import json
import os
import sys
from pathlib import Path
import httpx

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "services/api"))
from khohoc.schemas import ImportBatch  # noqa: E402
from khohoc.grading import normalize  # noqa: E402


def load(path):
    if path.suffix.lower() == ".csv":
        with path.open(encoding="utf-8-sig", newline="") as file:
            records = list(csv.DictReader(file))
        for row in records:
            for field in ("options", "correct_answer", "rubric"):
                if row.get(field):
                    row[field] = json.loads(row[field])
        records = [{k: v for k, v in row.items() if v != ""} for row in records]
        return {"questions": records}
    return json.loads(path.read_text(encoding="utf-8"))


def validate(path):
    batch = ImportBatch.model_validate(load(path))
    hashes = [
        hashlib.sha256(normalize(q.question).encode()).hexdigest()
        for q in batch.questions
    ]
    if len(hashes) != len(set(hashes)) or len({q.id for q in batch.questions}) != len(
        batch.questions
    ):
        raise ValueError("Duplicate IDs/content")
    return batch


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=Path)
    parser.add_argument(
        "--api", help="Import as draft at this API URL; omit to validate only"
    )
    args = parser.parse_args()
    batch = validate(args.file)
    if args.api:
        token = os.environ.get("KHOHOC_ADMIN_TOKEN")
        if not token:
            raise SystemExit(
                "Set KHOHOC_ADMIN_TOKEN securely; do not pass it on the command line"
            )
        result = httpx.post(
            args.api.rstrip("/") + "/admin/import",
            json=batch.model_dump(mode="json"),
            headers={"Authorization": "Bearer " + token},
            timeout=30,
        )
        result.raise_for_status()
        print(result.json())
    else:
        print(
            f"Valid: {len(batch.questions)} original records; publication not performed"
        )
