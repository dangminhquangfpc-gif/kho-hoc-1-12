"""Export the repository's authored learning fixtures for device-only practice.

This command reads only the explicitly listed, versioned fixture files. It never
opens a live database, account state, environment configuration or remote source.
Answer keys are deliberately included: an offline practice bundle is not a secure
exam service, and its scores must not be treated as supervised assessment.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "services/api"))

from khohoc.catalog import subjects_for_grade  # noqa: E402
from khohoc.content_fixes import QUESTION_REPLACEMENTS  # noqa: E402
from khohoc.library import DocumentInput, is_textbook_lesson  # noqa: E402
from khohoc.practice import canonical_topic, topic_name  # noqa: E402
from khohoc.schemas import ExamInput, Question  # noqa: E402

CONTENT_VERSION = "2026.10.15.19"
DEFAULT_OUTPUT = ROOT / "apps/mobile/assets/offline/content.json"
QUESTION_FILES = (
    "questions.json",
    "language_questions.json",
    "curriculum_questions.json",
    "subject_questions.json",
    "practice_questions.json",
    "extended_practice_questions.json",
    "multigrade_questions.json",
    "subject_practice_questions.json",
    "clean_questions.json",
)
EXAM_FILES = (
    "exams.json",
    "language_exams.json",
    "curriculum_exams.json",
    "subject_exams.json",
    "practice_exams.json",
    "multigrade_exams.json",
    "subject_practice_exams.json",
    "source_practice_exams.json",
)
DOCUMENT_FILES = (
    "documents.json",
    "external_documents.json",
    "curriculum_documents.json",
    "primary_math_documents.json",
    "secondary_math_documents.json",
)
METADATA_FILES = ("catalog.json", "textbook_units.json", "source_practice_map.json")


def canonical_records(names: tuple[str, ...], directory: str, key: str | None, model):
    """Match preview validation and fail closed on reused IDs."""
    records = {}
    for name in names:
        value = json.loads((ROOT / "data" / directory / name).read_text("utf-8"))
        for raw in value[key] if key else value:
            record = model.model_validate(raw).model_dump(mode="json")
            if record["id"] in records:
                raise ValueError("Duplicate fixture ID: " + record["id"])
            records[record["id"]] = record
    return records


def build_bundle() -> dict:
    catalog, textbook_units, source_practice_map = (
        json.loads((ROOT / "data/seeds" / name).read_text("utf-8"))
        for name in METADATA_FILES
    )
    # Avoid a stale exported subject list after an API catalog change.
    for grade in catalog["grades"]:
        if grade["subjects"] != subjects_for_grade(grade["id"]):
            raise ValueError("Catalog differs from the current API")

    all_questions = canonical_records(QUESTION_FILES, "seeds", "questions", Question)
    questions = {
        qid: question
        for qid, question in all_questions.items()
        if qid not in QUESTION_REPLACEMENTS
    }
    for question in questions.values():
        if (
            question["source_type"] != "original"
            or question["license"] != "original_content"
        ):
            raise ValueError("Offline question redistribution needs explicit review")
    if not set(QUESTION_REPLACEMENTS.values()) <= questions.keys():
        raise ValueError("Missing replacement question")

    exams = canonical_records(EXAM_FILES, "seeds", None, ExamInput)
    for exam in exams.values():
        # The preview resolves replacements when reading and starting an exam;
        # normalize references here so a device never needs withdrawn questions.
        exam["question_ids"] = [
            QUESTION_REPLACEMENTS.get(qid, qid) for qid in exam["question_ids"]
        ]
        ExamInput.model_validate(exam)
        for qid in exam["question_ids"]:
            question = questions.get(qid)
            if not question or (question["grade"], question["subject"]) != (
                exam["grade"],
                exam["subject"],
            ):
                raise ValueError("Missing or mismatched question: " + qid)

    documents = canonical_records(DOCUMENT_FILES, "library", "documents", DocumentInput)
    for document in documents.values():
        if document["source_type"] == "link_only":
            if document["sections"] or document["distribution_allowed"]:
                raise ValueError("An external reference must contain metadata only")
        elif not (
            document["source_type"] == "original"
            and document["license"] == "original_content"
            and document["distribution_allowed"]
        ):
            raise ValueError("Offline document redistribution needs explicit review")

    for document_id, pair in source_practice_map["papers"].items():
        if document_id not in documents or pair["exam_id"] not in exams:
            raise ValueError("Broken source/practice mapping")
        if pair["question_count"] != len(exams[pair["exam_id"]]["question_ids"]):
            raise ValueError("Source practice question count mismatch")

    paths = [
        ROOT / "data/seeds" / name
        for name in QUESTION_FILES + EXAM_FILES + METADATA_FILES
    ] + [ROOT / "data/library" / name for name in DOCUMENT_FILES]
    lesson_ids = sorted(
        document_id
        for document_id, document in documents.items()
        if is_textbook_lesson(document)
    )
    return {
        "schema_version": 1,
        "content_version": CONTENT_VERSION,
        "catalog": catalog,
        "questions": [questions[qid] for qid in sorted(questions)],
        "exams": [exams[eid] for eid in sorted(exams)],
        "documents": [documents[did] for did in sorted(documents)],
        "textbook_units": textbook_units,
        "source_practice_map": source_practice_map,
        "question_public_metadata": {
            qid: {
                "topic": canonical_topic(q["grade"], q["subject"], q["topic"]),
                "topic_name": topic_name(q["grade"], q["subject"], q["topic"]),
            }
            for qid, q in sorted(questions.items())
        },
        "lesson_document_ids": lesson_ids,
        "metadata": {
            "question_count": len(questions),
            "exam_count": len(exams),
            "document_count": len(documents),
            "lesson_count": len(lesson_ids),
            "external_reference_count": sum(
                d["source_type"] == "link_only" for d in documents.values()
            ),
            "source_practice_count": len(source_practice_map["papers"]),
            "withdrawn_question_count": len(set(all_questions) - set(questions)),
            "contains_answer_keys": True,
            "practice_only": True,
            "pdf_files_included": False,
            "scope_notice": (
                "Nội dung tự biên soạn hướng tới Kết nối tri thức; chưa được nhà xuất bản "
                "hoặc giáo viên thẩm định toàn bộ. Hướng dẫn theo mục lục hiện có chủ yếu "
                "ở môn Toán; các môn khác chưa đầy đủ. Các đề ghép từ nguồn là đề tự "
                "biên soạn cùng lớp/môn, không phải bản chuyển nguyên văn đề Internet."
            ),
            "rights_notice": (
                "Chỉ đóng gói câu hỏi và ghi chú tự biên soạn được phép phân phối trong "
                "kho mã; nguồn Internet chỉ gồm thông tin và liên kết. Không chứa PDF "
                "hoặc toàn văn sách giáo khoa của bên thứ ba."
            ),
            "practice_notice": (
                "Đáp án nằm trong gói cài đặt để chấm ngoại tuyến và có thể được đọc "
                "trên thiết bị. Kết quả chỉ phục vụ tự luyện, không xác thực danh tính "
                "và không dùng như điểm kiểm tra có giám sát."
            ),
            "sync_notice": (
                "Bài làm ngoại tuyến lưu trên thiết bị; không tự đồng bộ thành kết quả "
                "tài khoản hoặc báo cáo cho giáo viên."
            ),
            "source_sha256": {
                str(path.relative_to(ROOT)): hashlib.sha256(
                    path.read_bytes()
                ).hexdigest()
                for path in sorted(paths)
            },
        },
    }


def serialized_bundle(bundle: dict) -> bytes:
    return (
        json.dumps(bundle, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--check", action="store_true", help="Fail if the asset is stale"
    )
    args = parser.parse_args()
    bundle = build_bundle()
    payload = serialized_bundle(bundle)
    if args.check:
        if not args.output.is_file() or args.output.read_bytes() != payload:
            print(
                "Offline content is stale; run scripts/build_offline_bundle.py",
                file=sys.stderr,
            )
            return 1
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(payload)
    print(
        f"Offline {CONTENT_VERSION}: {bundle['metadata']['question_count']} questions, "
        f"{bundle['metadata']['exam_count']} exams, "
        f"{bundle['metadata']['document_count']} documents; "
        f"{len(payload)} bytes; SHA256 {hashlib.sha256(payload).hexdigest()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
