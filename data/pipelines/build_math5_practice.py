"""Original numeric practice linked to the secondary Math 5 lesson index.

These are authored practice sets, not copied school examination papers.
"""

import json
from decimal import Decimal
from fractions import Fraction
from pathlib import Path
from build_math5_lessons import MAP, SKILLS

ROOT = Path(__file__).resolve().parents[2]


def task(key, n):
    a, b, c = n + 3, n + 2, n + 1
    d = Decimal
    if key == "natural":
        return (
            f"Trong số {a * 1000 + 700 + n * 10 + 2}, chữ số 7 có giá trị bao nhiêu?",
            700,
            "Chữ số 7 ở hàng trăm: 7 × 100 = 700.",
        )
    if key == "operations":
        return (
            f"Tính {a} × {b} + {c}.",
            a * b + c,
            f"Nhân trước: {a} × {b} = {a * b}; cộng {c} được {a * b + c}.",
        )
    if key == "fraction":
        return (
            f"Rút gọn phân số {a * 3}/{b * 3}. Nhập một phân số tối giản.",
            Fraction(a, b),
            f"Chia tử và mẫu cho 3 rồi rút gọn tiếp nếu cần: {Fraction(a, b)}.",
        )
    if key == "decimal_fraction":
        return (
            f"Viết {a}/20 dưới dạng phân số có mẫu số 100. Tử số mới là bao nhiêu?",
            a * 5,
            f"Nhân cả tử và mẫu với 5: {a * 5}/100.",
        )
    if key == "fraction_ops":
        return (
            f"Tính {a}/{b} × {b}/{c}.",
            Fraction(a, c),
            f"Nhân tử với tử, mẫu với mẫu, rút gọn: {Fraction(a, c)}.",
        )
    if key == "unlike_fraction":
        return (
            f"Tính 1/{a} + 1/{b}. Nhập phân số tối giản.",
            Fraction(1, a) + Fraction(1, b),
            f"Quy đồng mẫu {a * b}, tử là {a + b}; rút gọn được {Fraction(1, a) + Fraction(1, b)}.",
        )
    if key == "mixed":
        return (
            f"Đổi hỗn số {c} và 1/{a} thành phân số. Tử số khi giữ mẫu {a} là bao nhiêu?",
            c * a + 1,
            f"Tử số = {c} × {a} + 1 = {c * a + 1}.",
        )
    if key == "plane":
        return (
            f"Hình chữ nhật dài {a} m, rộng {b} m. Chu vi bằng bao nhiêu mét?",
            2 * (a + b),
            f"Chu vi = ({a} + {b}) × 2 = {2 * (a + b)} m.",
        )
    if key == "decimal":
        return (
            f"Viết {a} + {b}/10 + {c}/100 dưới dạng số thập phân.",
            d(a) + d(b) / 10 + d(c) / 100,
            "Cộng phần nguyên, phần mười và phần trăm theo đúng giá trị hàng.",
        )
    if key == "compare_decimal":
        x, y = d(a) + d(c) / 100, d(a) + d(b) / 10
        return (
            f"Số lớn hơn trong hai số {x} và {y} là số nào?",
            max(x, y),
            "Phần nguyên bằng nhau; so sánh phần thập phân theo từng hàng.",
        )
    if key == "measure_decimal":
        return (
            f"Đổi {a} m {b * 5} cm thành mét. Chỉ nhập số đo theo m.",
            d(a) + d(b * 5) / 100,
            f"{b * 5} cm = {d(b * 5) / 100} m; cộng thêm {a} m.",
        )
    if key == "round":
        x = d(a) + d(b) / 10 + d(6) / 100
        return (
            f"Làm tròn {x} đến hàng phần mười.",
            x.quantize(d("0.1")),
            "Chữ số hàng phần trăm là 6 nên tăng hàng phần mười lên 1.",
        )
    if key == "land_area":
        return (
            f"Đổi {a} km² thành ha. Chỉ nhập số đo theo ha.",
            a * 100,
            "1 km² = 100 ha; nhân số đo với 100.",
        )
    if key == "area_units":
        return (
            f"Đổi {a * 100 + b * 10} cm² thành dm². Chỉ nhập số đo theo dm².",
            d(a) + d(b) / 10,
            "1 dm² = 100 cm²; chia số đo cm² cho 100.",
        )
    if key in ("add_decimal", "subtract_decimal", "multiply_decimal", "divide_decimal"):
        x, y = d(a) + d(25) / 100, d(b) / 10
        if key == "divide_decimal":
            x, y = d(a * b) / 10, d(b) / 10
        if key == "subtract_decimal":
            x, y = d(a) + d(25) / 100, d(b) + d(5) / 100
        symbol = {
            "add_decimal": "+",
            "subtract_decimal": "−",
            "multiply_decimal": "×",
            "divide_decimal": ":",
        }[key]
        result = {
            "add_decimal": lambda: x + y,
            "subtract_decimal": lambda: x - y,
            "multiply_decimal": lambda: x * y,
            "divide_decimal": lambda: x / y,
        }[key]()
        return (
            f"Tính {x} {symbol} {y}.",
            result,
            f"Tính đúng theo hàng thập phân: {x} {symbol} {y} = {result}.",
        )
    if key == "powers_ten":
        x = d(a) + d(b) / 10
        return (
            f"Tính {x} : 100.",
            x / 100,
            "Chia cho 100: dịch dấu phẩy sang trái hai hàng.",
        )
    if key == "drawing":
        return (
            f"Ghép hai tam giác bằng nhau, mỗi tam giác có đáy {2 * a} cm và chiều cao {b} cm, thành hình chữ nhật không chồng lấn. Diện tích hình ghép bằng bao nhiêu cm²?",
            2 * a * b,
            f"Mỗi tam giác có diện tích {a * b} cm²; hình ghép có diện tích {2 * a * b} cm².",
        )
    if key == "triangle":
        return (
            f"Tam giác có đáy {2 * a} cm, chiều cao vuông góc {b} cm. Diện tích bằng bao nhiêu cm²?",
            a * b,
            f"S = đáy × chiều cao : 2 = {2 * a} × {b} : 2 = {a * b} cm².",
        )
    if key == "trapezoid":
        return (
            f"Hình thang có hai đáy {2 * a} m và {2 * b} m, cao {c} m. Diện tích bằng bao nhiêu m²?",
            (a + b) * c,
            f"S = ({2 * a} + {2 * b}) × {c} : 2 = {(a + b) * c} m².",
        )
    if key == "circle":
        return (
            f"Đường tròn bán kính {a} cm. Lấy π = 3,14. Chu vi bằng bao nhiêu cm?",
            d("6.28") * a,
            f"C = 2 × {a} × 3,14 = {d('6.28') * a} cm.",
        )
    if key == "ratio":
        return (
            f"Tìm tỉ số phần trăm của {a} và 25. Chỉ nhập số trước dấu %.",
            a * 4,
            f"{a} : 25 × 100 = {a * 4}%.",
        )
    if key == "map":
        return (
            f"Bản đồ tỉ lệ 1:10 000, đoạn trên bản đồ dài {a} cm. Khoảng cách thực bằng bao nhiêu mét?",
            a * 100,
            f"{a} × 10 000 cm = {a * 100} m.",
        )
    if key == "sum_ratio":
        total = (a + b) * c
        return (
            f"Hai số có tổng {total}, tỉ số số bé:số lớn = {b}:{a}. Số bé bằng bao nhiêu?",
            b * c,
            f"Tổng số phần = {a + b}; mỗi phần = {c}; số bé = {b} × {c} = {b * c}.",
        )
    if key == "difference_ratio":
        return (
            f"Hai số có hiệu {2 * c}, tỉ số số bé:số lớn = {b}:{b + 2}. Số bé bằng bao nhiêu?",
            b * c,
            f"Hiệu số phần = 2; mỗi phần = {c}; số bé = {b * c}.",
        )
    if key == "calculator":
        return (
            f"Dùng máy tính kiểm tra: món hàng giá {b * 10000} đồng giảm {a}%. Số tiền được giảm là bao nhiêu đồng?",
            a * b * 100,
            f"{b * 10000} × {a} : 100 = {a * b * 100} đồng.",
        )
    if key == "percentage_value":
        return (
            f"Tìm {a}% của {b * 100}. Chỉ nhập kết quả bằng số.",
            a * b,
            f"{b * 100} × {a} : 100 = {a * b}.",
        )
    if key == "volume":
        return (
            f"Một khối xếp từ {a} hàng, mỗi hàng {b} khối đơn vị, có {c} lớp. Tổng cộng bao nhiêu khối đơn vị?",
            a * b * c,
            f"Số khối = {a} × {b} × {c} = {a * b * c}.",
        )
    if key == "volume_units":
        return (
            f"Đổi {a * 1000 + b * 100} cm³ thành dm³. Chỉ nhập số đo theo dm³.",
            d(a) + d(b) / 10,
            "1 dm³ = 1 000 cm³; chia cho 1 000.",
        )
    if key == "nets":
        return (
            f"Có {a} hình lập phương tách rời. Khi khai triển từng hình, tổng cộng có bao nhiêu mặt vuông?",
            a * 6,
            f"Mỗi hình lập phương có 6 mặt; {a} × 6 = {a * 6}.",
        )
    if key == "box_area":
        return (
            f"Hình hộp chữ nhật dài {a} cm, rộng {b} cm, cao {c} cm. Diện tích xung quanh bằng bao nhiêu cm²?",
            2 * (a + b) * c,
            f"Sxq = ({a} + {b}) × 2 × {c} = {2 * (a + b) * c} cm².",
        )
    if key == "cube_area":
        return (
            f"Hình lập phương cạnh {a} cm. Diện tích toàn phần bằng bao nhiêu cm²?",
            6 * a * a,
            f"Stp = 6 × {a} × {a} = {6 * a * a} cm².",
        )
    if key == "box_volume":
        return (
            f"Hình hộp chữ nhật dài {a} cm, rộng {b} cm, cao {c} cm. Thể tích bằng bao nhiêu cm³?",
            a * b * c,
            f"V = {a} × {b} × {c} = {a * b * c} cm³.",
        )
    if key == "cube_volume":
        return (
            f"Hình lập phương cạnh {a} cm. Thể tích bằng bao nhiêu cm³?",
            a**3,
            f"V = {a} × {a} × {a} = {a**3} cm³.",
        )
    if key == "time_units":
        return (
            f"Đổi {a} giờ {b * 5} phút thành phút. Chỉ nhập số phút.",
            a * 60 + b * 5,
            f"{a} giờ = {a * 60} phút; cộng {b * 5} phút được {a * 60 + b * 5} phút.",
        )
    if key == "time_add":
        return (
            f"Tính {a} giờ 45 phút + {b} giờ 35 phút. Kết quả có tổng cộng bao nhiêu phút?",
            (a + b) * 60 + 80,
            "Đổi cả hai số đo sang phút rồi cộng; cần nhớ 60 phút = 1 giờ.",
        )
    if key == "time_multiply":
        return (
            f"Tính {a} giờ 15 phút × {b}. Kết quả có tổng cộng bao nhiêu phút?",
            (a * 60 + 15) * b,
            f"Đổi thành {a * 60 + 15} phút, nhân {b} được {(a * 60 + 15) * b} phút.",
        )
    if key == "speed":
        return (
            f"Xe đi với vận tốc {a * 10} km/giờ trong {b} giờ. Quãng đường bằng bao nhiêu km?",
            a * 10 * b,
            f"s = v × t = {a * 10} × {b} = {a * 10 * b} km.",
        )
    if key == "data":
        return (
            f"Dãy số gồm {a} lần số 2, {b} lần số 3 và {c} lần số 4. Có tất cả bao nhiêu số liệu?",
            a + b + c,
            f"Cộng các tần số: {a} + {b} + {c} = {a + b + c}.",
        )
    if key == "pie":
        return (
            f"Hai phần biểu đồ hình quạt chiếm {a * 3}% và {b * 2}%. Phần còn lại chiếm bao nhiêu phần trăm? Chỉ nhập số trước dấu %.",
            100 - a * 3 - b * 2,
            f"Tổng là 100%; phần còn lại = 100 − {a * 3} − {b * 2} = {100 - a * 3 - b * 2}%.",
        )
    if key == "frequency":
        return (
            f"Thử 50 lần, sự kiện A xuất hiện {a} lần. Tỉ số số lần A xuất hiện so với tổng số lần thử bằng bao nhiêu phần trăm? Chỉ nhập số trước dấu %.",
            a * 2,
            f"{a} : 50 × 100 = {a * 2}%.",
        )
    raise ValueError(key)


def build():
    questions, by_skill = [], {}
    for key in SKILLS:
        by_skill[key] = []
        for n in range(1, 9):
            prompt, answer, explanation = task(key, n)
            qid = f"practice_math5_{key}_{n:02d}"
            by_skill[key].append(qid)
            questions.append(
                dict(
                    id=qid,
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
                    rights_evidence="Bài luyện tự biên soạn với số liệu mới; đối chiếu nhóm kỹ năng trong mục lục Toán 5 nguồn thứ cấp, không sao chép đề/PDF Internet. Chưa thẩm định sư phạm độc lập.",
                )
            )
    books = json.loads(
        (ROOT / "data/seeds/textbook_units.json").read_text(encoding="utf-8")
    )["books"]
    book = next(b for b in books if b["grade"] == 5 and b["subject"] == "toan")
    exams = []
    for unit in book["units"]:
        import re

        number = int(re.search(r"Bài\s+(\d+)", unit["title"]).group(1))
        ids = [qid for key in MAP[number] for qid in by_skill[key]]
        exams.append(
            dict(
                id=f"practice_math5_lesson_{number:02d}",
                grade=5,
                subject="toan",
                textbook="ket_noi_tri_thuc",
                topic=f"bai_{number:02d}",
                title=f"Toán 5 · {unit['title']} · Bài luyện tự biên soạn",
                duration_minutes=min(90, max(20, len(ids) * 2)),
                question_ids=ids,
            )
        )
    for semester, numbers in ((1, range(1, 36)), (2, range(36, 76))):
        skills = list(dict.fromkeys(key for number in numbers for key in MAP[number]))
        for version in range(1, 7):
            ids = [by_skill[key][(version + i - 1) % 8] for i, key in enumerate(skills)]
            exams.append(
                dict(
                    id=f"practice_math5_review_{semester}_{version}",
                    grade=5,
                    subject="toan",
                    textbook="ket_noi_tri_thuc",
                    topic=f"on_tap_hoc_ki_{semester}",
                    title=f"Toán 5 · Ôn các chủ đề học kỳ {semester} · Bộ {version} (tự biên soạn)",
                    duration_minutes=60,
                    question_ids=ids,
                )
            )
    (ROOT / "data/seeds/practice_questions.json").write_text(
        json.dumps({"questions": questions}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (ROOT / "data/seeds/practice_exams.json").write_text(
        json.dumps(exams, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"{len(questions)} new questions; {len(exams)} authored practice sets; questions reused across lesson/review sets"
    )


if __name__ == "__main__":
    build()
