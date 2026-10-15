"""Local-only fixture import; --publish-fixtures explicitly approves dev examples."""

import argparse
import json
import os
from pathlib import Path
import sys
import httpx

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / "services/api"))
from khohoc.phone_preview import (  # noqa: E402
    canonical_fixture_map,
    checked_fixture_rows,
)
from khohoc.schemas import ExamInput, Question  # noqa: E402

parser = argparse.ArgumentParser()
parser.add_argument("--api", default="http://127.0.0.1:8000")
parser.add_argument(
    "--publish-fixtures",
    action="store_true",
    help="DEV ONLY: publish authored fixtures, not professional approval",
)
args = parser.parse_args()
if os.environ.get("KHOHOC_MODE", "development") != "development":
    raise SystemExit("Fixture publication only allowed in development")
token = os.environ.get("KHOHOC_ADMIN_TOKEN")
if not token:
    raise SystemExit("Configure KHOHOC_ADMIN_TOKEN in a local ignored file")
questions = canonical_fixture_map(
    [
        q
        for name in (
            "questions.json",
            "language_questions.json",
            "curriculum_questions.json",
            "subject_questions.json",
            "practice_questions.json",
            "extended_practice_questions.json",
        )
        for q in json.loads((root / "data/seeds" / name).read_text(encoding="utf-8"))[
            "questions"
        ]
    ],
    Question,
)
exams = canonical_fixture_map(
    [
        exam
        for name in (
            "exams.json",
            "language_exams.json",
            "curriculum_exams.json",
            "subject_exams.json",
            "practice_exams.json",
        )
        for exam in json.loads((root / "data/seeds" / name).read_text(encoding="utf-8"))
    ],
    ExamInput,
)
with httpx.Client(
    base_url=args.api, headers={"Authorization": "Bearer " + token}, timeout=30
) as client:
    existing = checked_fixture_rows(
        client.get("/admin/questions").raise_for_status().json(),
        questions,
        Question,
        "question",
    )
    existing_exams = checked_fixture_rows(
        client.get("/admin/exams").raise_for_status().json(),
        exams,
        ExamInput,
        "exam",
    )
    pending = [q for qid, q in questions.items() if qid not in existing]
    for start in range(0, len(pending), 200):
        client.post(
            "/admin/import", json={"questions": pending[start : start + 200]}
        ).raise_for_status()
    if args.publish_fixtures:
        rows = checked_fixture_rows(
            client.get("/admin/questions").raise_for_status().json(),
            questions,
            Question,
            "question",
        )
        for qid, q in rows.items():
            # Only fixture IDs from repository, not other users' imports.
            if qid not in questions:
                continue
            if q["state"] == "published":
                continue
            version = q["version"]
            client.post(
                f"/admin/questions/{qid}/approve",
                params={"rights_confirmed": "true", "expected_version": version},
            ).raise_for_status()
            client.post(
                f"/admin/questions/{qid}/publish",
                params={"expected_version": version},
            ).raise_for_status()
        for exam_id, exam in exams.items():
            if exam_id not in existing_exams:
                client.post("/admin/exams", json=exam).raise_for_status()
            elif existing_exams[exam_id]["state"] == "published":
                continue
            client.post(f"/admin/exams/{exam_id}/publish").raise_for_status()
print("Fixtures prepared; publication=" + str(args.publish_fixtures))
