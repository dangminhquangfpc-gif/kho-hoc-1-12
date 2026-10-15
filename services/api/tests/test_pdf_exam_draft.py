import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location(
    "pdf_draft", ROOT / "data/pipelines/pdf_exam_draft.py"
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_pdf_parser_preserves_choices_and_does_not_parse_solution_as_question():
    text = "Câu 1. Tính 2 + 3.\nA. 4    B. 5    C. 6    D. 7\nĐÁP ÁN\nCâu 1. Lời giải ở đây."
    rows, issues = module.parse_questions(text, {"1": "B"})
    assert not issues and len(rows) == 1
    assert rows[0]["question"] == "Tính 2 + 3."
    assert rows[0]["options"] == [
        {"id": k, "text": str(v)} for k, v in zip("ABCD", range(4, 8))
    ]
    assert rows[0]["correct_answer"] == ["B"]


def test_pdf_parser_never_guesses_missing_answers_or_part_questions():
    text = "Câu 1. Tính 2 + 3.\nA. 4 B. 5 C. 6 D. 7\nCâu 2. Vẽ hình và giải thích."
    rows, issues = module.parse_questions(text, {})
    assert not rows and len(issues) == 2
    rows, issues = module.parse_questions(
        "Câu 1. x\nA. a B. b C. c D. d\nCâu 1. y\nA. a B. b C. c D. d", {"1": "A"}
    )
    assert len(rows) == 1 and any("trùng" in issue for issue in issues)
    assert module.parse_questions("", {})[1]
