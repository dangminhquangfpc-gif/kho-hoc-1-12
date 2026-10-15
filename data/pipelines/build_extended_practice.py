"""Additional authored numeric variants, preserving every previous fixture ID."""

import json
from decimal import Decimal
from pathlib import Path
from build_math5_practice import task
from build_math5_lessons import SKILLS

ROOT = Path(__file__).resolve().parents[2]


def build():
    questions = []
    for key in SKILLS:
        for n in range(9, 26):
            prompt, answer, explanation = task(key, n)
            if key == "natural":
                number = 20000 + n * 137
                power = n % 4 + 1
                place = 10**power
                label = {1: "chục", 2: "trăm", 3: "nghìn", 4: "chục nghìn"}[power]
                digit = number // place % 10
                answer = digit * place
                prompt = (
                    f"Trong số {number}, chữ số ở hàng {label} có giá trị bao nhiêu?"
                )
                explanation = f"Chữ số hàng {label} là {digit}; giá trị là {digit} × {place} = {answer}."
            if key == "compare_decimal":
                explanation = "So sánh phần nguyên trước, rồi lần lượt các hàng thập phân; chọn số lớn hơn."
            if key == "pie":
                a = n % 9 + 3
                b = n % 7 + 2
                answer = 100 - a * 3 - b * 2
                prompt = f"Hai phần biểu đồ hình quạt chiếm {a * 3}% và {b * 2}%. Phần còn lại chiếm bao nhiêu phần trăm? Chỉ nhập số trước dấu %."
                explanation = f"Phần còn lại = 100 − {a * 3} − {b * 2} = {answer}%."
            if key == "time_units":
                hours = n + 3
                minutes = (n % 10 + 1) * 5
                answer = hours * 60 + minutes
                prompt = f"Đổi {hours} giờ {minutes} phút thành phút. Chỉ nhập số phút."
                explanation = f"{hours} × 60 + {minutes} = {answer} phút."
            questions.append(
                dict(
                    id=f"extended_math5_{key}_{n:02d}",
                    grade=5,
                    subject="toan",
                    topic=key,
                    textbook="ket_noi_tri_thuc",
                    type="numeric",
                    difficulty="medium",
                    question=prompt + "\nNhập số hoặc phân số, không kèm đơn vị.",
                    correct_answer=[
                        format(answer, "f")
                        if isinstance(answer, Decimal)
                        else str(answer)
                    ],
                    max_score=1,
                    explanation=explanation,
                    source_type="original",
                    license="original_content",
                    rights_evidence="Biến thể số liệu tự biên soạn cho nhóm kỹ năng Toán 5, không sao chép đề Internet. Chưa thẩm định sư phạm độc lập.",
                )
            )
    path = ROOT / "data/seeds/extended_practice_questions.json"
    path.write_text(
        json.dumps({"questions": questions}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(len(questions), "additional authored questions; 43 skill families")


if __name__ == "__main__":
    build()
