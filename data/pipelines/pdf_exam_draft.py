"""Extract a rights-cleared text PDF into reviewable exam drafts, never publish.

Requires Poppler's pdftotext. Scans, diagrams, fractions and multi-part questions
need human review; no OCR or inferred answer keys are used here.
"""

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

QUESTIONS = re.compile(r"(?:^|\n)\s*Câu\s+(\d+)\s*[.:]\s*", re.I)
OPTIONS = re.compile(r"(?:^|\s)([ABCD])\s*[.)]\s*")


def parse_questions(text, answers):
    """Parse only explicit four-option questions with a supplied answer key."""
    body = re.split(
        r"(?:^|\n)\s*(?:ĐÁP ÁN|HƯỚNG DẪN GIẢI)\b", text, maxsplit=1, flags=re.I
    )[0]
    starts = list(QUESTIONS.finditer(body))
    questions, issues, seen = [], [], set()
    if not starts:
        return [], [
            "Không đọc được câu hỏi. PDF có thể là ảnh quét hoặc định dạng khác."
        ]
    for i, match in enumerate(starts):
        number = match.group(1)
        block = body[
            match.end() : starts[i + 1].start() if i + 1 < len(starts) else len(body)
        ].strip()
        options = list(OPTIONS.finditer(block))
        if number in seen:
            issues.append(f"Câu {number}: số câu trùng; cần tách phần đề.")
            continue
        seen.add(number)
        if [o.group(1) for o in options] != list("ABCD"):
            issues.append(
                f"Câu {number}: chưa tách được đúng bốn phương án; cần kiểm tra công thức/hình/tự luận."
            )
            continue
        if answers.get(number) not in list("ABCD"):
            issues.append(
                f"Câu {number}: thiếu đáp án đã kiểm tra, không suy đoán đáp án."
            )
            continue
        prompt = block[: options[0].start()].strip()
        choices = [
            dict(
                id=o.group(1),
                text=block[
                    o.end() : options[j + 1].start()
                    if j + 1 < len(options)
                    else len(block)
                ].strip(),
            )
            for j, o in enumerate(options)
        ]
        if not prompt or any(not o["text"] for o in choices):
            issues.append(f"Câu {number}: thiếu nội dung câu hoặc lựa chọn.")
            continue
        questions.append(
            dict(
                number=number,
                question=prompt,
                options=choices,
                correct_answer=[answers[number]],
            )
        )
    return questions, issues


def build(args):
    data = args.pdf.read_bytes()
    if len(data) > 10 * 1024 * 1024 or not data.startswith(b"%PDF-"):
        raise ValueError("Chỉ nhận PDF tối đa 10 MB.")
    evidence = args.rights_evidence.read_text(encoding="utf-8").strip()
    book_evidence = args.book_evidence.read_text(encoding="utf-8").strip()
    if len(evidence) < 20 or len(book_evidence) < 20:
        raise ValueError(
            "Cần bằng chứng quyền sử dụng và đối chiếu Kết nối tri thức rõ ràng."
        )
    answers = json.loads(args.answers.read_text(encoding="utf-8"))
    if not isinstance(answers, dict):
        raise ValueError('Đáp án phải là JSON dạng {"1":"A"}.')
    digest = hashlib.sha256(data).hexdigest()
    result = subprocess.run(
        ["pdftotext", "-layout", str(args.pdf.resolve()), "-"],
        capture_output=True,
        check=True,
        timeout=30,
    )
    text = result.stdout.decode("utf-8", "replace")
    parsed, issues = parse_questions(text, answers)
    records = []
    for item in parsed:
        number = item.pop("number")
        records.append(
            dict(
                id=f"pdf_{digest[:20]}_{number}",
                grade=args.grade,
                subject=args.subject,
                textbook="ket_noi_tri_thuc",
                topic="de_pdf_cho_tham_dinh",
                type="single_choice",
                max_score=1,
                explanation="Chưa có lời giải đã thẩm định; cần bổ sung trước khi phát hành.",
                source_type="licensed",
                license=args.license,
                rights_evidence=evidence,
                **item,
            )
        )
    args.output.mkdir(parents=True, exist_ok=False)
    payloads = {
        "questions.json": {"questions": records},
        "exam.json": dict(
            id=f"pdf_exam_{digest[:20]}",
            grade=args.grade,
            subject=args.subject,
            textbook="ket_noi_tri_thuc",
            title=args.title,
            duration_minutes=45,
            question_ids=[q["id"] for q in records],
        ),
        "review.json": dict(
            status="needs_human_review",
            publish_allowed=False,
            pdf_sha256=digest,
            source_url=args.source_url,
            book_evidence=book_evidence,
            parsed_count=len(records),
            issues=issues,
            required_review=[
                "Đủ mọi câu trong PDF",
                "Đúng thứ tự, công thức và hình",
                "Đúng đáp án, điểm từng câu và lời giải",
                "Đúng lớp, môn, học kỳ, bộ sách",
                "Quyền sao chép và phân phối được xác nhận",
            ],
        ),
    }
    for name, payload in payloads.items():
        (args.output / name).write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    (args.output / "extracted.txt").write_text(text, encoding="utf-8")
    print(
        f"Đã tách {len(records)} câu; {len(issues)} phần cần sửa. Chỉ tạo bản nháp riêng, chưa nhập hoặc phát hành."
    )


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("pdf", type=Path)
    p.add_argument("--answers", type=Path, required=True)
    p.add_argument("--rights-evidence", type=Path, required=True)
    p.add_argument("--book-evidence", type=Path, required=True)
    p.add_argument(
        "--license",
        choices=["CC-BY-4.0", "CC-BY-SA-4.0", "written_permission"],
        required=True,
    )
    p.add_argument("--grade", type=int, choices=range(1, 13), required=True)
    p.add_argument("--subject", required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--source-url", required=True)
    p.add_argument("--output", type=Path, required=True)
    build(p.parse_args())
