"""Validate language fixtures, their exam links, and cross-subject duplicates.

This validates development data only; it does not approve or publish questions.
"""

from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "services/api"))

from khohoc.grading import grade, normalize  # noqa: E402
from khohoc.schemas import ExamInput, ImportBatch  # noqa: E402


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate():
    seed_dir = ROOT / "data/seeds"
    batches = [
        ImportBatch.model_validate(read_json(seed_dir / name))
        for name in ("questions.json", "language_questions.json")
    ]
    all_questions = [q for batch in batches for q in batch.questions]
    questions_by_id = {q.id: q for q in all_questions}
    if len(questions_by_id) != len(all_questions):
        raise ValueError("Question IDs must be unique across math and language seeds")
    fingerprints = [
        hashlib.sha256(normalize(q.question).encode("utf-8")).hexdigest()
        for q in all_questions
    ]
    if len(set(fingerprints)) != len(fingerprints):
        raise ValueError("Normalized duplicate question text in combined seeds")

    catalog = read_json(seed_dir / "catalog.json")
    valid_pairs = {(g["id"], s["id"]) for g in catalog["grades"] for s in g["subjects"]}
    language_questions = batches[1].questions
    groups = Counter((q.grade, q.subject) for q in language_questions)
    expected_groups = {
        (1, "tieng_viet"),
        (5, "tieng_viet"),
        (9, "ngu_van"),
        (12, "ngu_van"),
        (3, "tieng_anh"),
        (5, "tieng_anh"),
        (9, "tieng_anh"),
        (12, "tieng_anh"),
    }
    if set(groups) != expected_groups or any(n < 5 for n in groups.values()):
        raise ValueError("Language coverage must include eight grade/subject groups")
    for q in language_questions:
        if (q.grade, q.subject) not in valid_pairs:
            raise ValueError(f"Subject not available for grade: {q.id}")
        if q.source_type != "original" or q.license != "original_content":
            raise ValueError(f"Unexpected rights declaration: {q.id}")
        if q.type == "essay":
            raise ValueError(
                f"Objective language fixtures cannot contain essays: {q.id}"
            )
        accepted = (
            q.correct_answer if q.type != "short_answer" else q.correct_answer[:1]
        )
        if grade(q, accepted)["score"] != float(q.max_score):
            raise ValueError(f"Canonical answer is not awarded full credit: {q.id}")
        if q.type == "true_false":
            rejected = ["false" if a == "true" else "true" for a in q.correct_answer]
        elif q.type in {"single_choice", "multiple_choice"}:
            rejected = [o.id for o in q.options if o.id not in q.correct_answer][:1]
        else:
            rejected = ["__incorrect_fixture_answer__"]
        if not rejected or grade(q, rejected)["score"] != 0:
            raise ValueError(f"Incorrect answer is not rejected: {q.id}")

    exams = [
        ExamInput.model_validate(raw)
        for name in ("exams.json", "language_exams.json")
        for raw in read_json(seed_dir / name)
    ]
    if len({e.id for e in exams}) != len(exams):
        raise ValueError("Duplicate exam IDs across math and language seeds")
    language_exam_ids = {e["id"] for e in read_json(seed_dir / "language_exams.json")}
    covered = set()
    for exam in exams:
        for question_id in exam.question_ids:
            q = questions_by_id.get(question_id)
            if q is None:
                raise ValueError(
                    f"Exam {exam.id} references missing question {question_id}"
                )
            if (q.grade, q.subject) != (exam.grade, exam.subject):
                raise ValueError(f"Grade/subject mismatch in {exam.id}: {q.id}")
            if q.type == "essay":
                raise ValueError(f"Objective exam {exam.id} references essay {q.id}")
            if exam.id in language_exam_ids:
                covered.add(q.id)
    if covered != {q.id for q in language_questions}:
        raise ValueError("All language questions must appear in a language exam")
    print(
        f"Valid: {len(language_questions)} original language questions, "
        f"{len(language_exam_ids)} objective exams, {len(all_questions)} combined "
        "math/language questions with unique IDs and normalized text."
    )
    return language_questions, exams


if __name__ == "__main__":
    validate()
