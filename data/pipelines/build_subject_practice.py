"""Original English and science practice; topic alignment only, not SGK transcriptions."""

import json
from pathlib import Path
from fractions import Fraction as F

ROOT = Path(__file__).resolve().parents[2]


def build():
    rows = []

    def add(grade, subject, topic, i, prompt, answer, reason, choices=None):
        q = dict(
            id=f"subplus_{grade}_{subject}_{topic}_{i:03d}",
            grade=grade,
            subject=subject,
            topic=topic,
            textbook="ket_noi_tri_thuc",
            type="single_choice" if choices else "numeric",
            difficulty="easy" if grade <= 5 else "medium",
            question=prompt,
            correct_answer=[str(answer)],
            explanation=reason,
            max_score=1,
            source_type="original",
            license="original_content",
            rights_evidence="Bài tập tự biên soạn theo kỹ năng chương trình; Tiếng Anh hướng tới Global Success. Chưa đối chiếu từng Unit/ấn bản hoặc thẩm định độc lập; không chép từ Internet.",
        )
        if choices:
            # Correct position varies and all alternatives are distinct.
            shift = i % 4
            labels = list("ABCD")
            opts = choices[shift:] + choices[:shift]
            q["options"] = [dict(id=k, text=v) for k, v in zip(labels, opts)]
            q["correct_answer"] = [labels[opts.index(choices[0])]]
        rows.append(q)

    names = [
        "An",
        "Binh",
        "Chi",
        "Dung",
        "Giang",
        "Ha",
        "Khanh",
        "Lan",
        "Minh",
        "Nam",
        "Phuong",
        "Quang",
    ]
    objects = [
        ("book", "books"),
        ("pencil", "pencils"),
        ("apple", "apples"),
        ("desk", "desks"),
        ("ruler", "rulers"),
        ("bag", "bags"),
        ("pen", "pens"),
        ("flower", "flowers"),
    ]
    for grade in range(3, 13):
        for i in range(1, 41):
            name = names[(i - 1) % 12]
            n = grade * 10 + i
            singular, plural = objects[(i - 1) % len(objects)]
            add(
                grade,
                "tieng_anh",
                "reading",
                i,
                f"Read: “In class {grade}A, {name} has {n} {plural} and gives {i} to a friend.” How many {plural} does {name} have left?",
                None,
                f"{n} − {i} = {grade * 10}. The phrase gives ... to a friend means subtraction.",
                [str(grade * 10), str(n + i), str(n), str(n + i + 1)],
            )
            if grade <= 5:
                add(
                    grade,
                    "tieng_anh",
                    "plural_nouns",
                    i,
                    f"Complete the label for shelf {grade}-{i}: “{n} ___”. Choose the plural of “{singular}”.",
                    None,
                    "For these regular nouns, add -s to form the plural.",
                    [plural, singular, singular + "'s", singular + "ing"],
                )
            elif grade <= 9:
                add(
                    grade,
                    "tieng_anh",
                    "past_simple",
                    i,
                    f"Complete: “Last Monday, {name} ___ {n} {plural} for the class.”",
                    None,
                    "Last Monday identifies a completed past time. Bought is the past form of buy.",
                    ["bought", "buy", "buys", "buying"],
                )
            else:
                add(
                    grade,
                    "tieng_anh",
                    "passive_voice",
                    i,
                    f"Complete: “The {n} {plural} ___ by {name} yesterday.”",
                    None,
                    "The plural subject receives the action; yesterday requires the past passive were collected.",
                    ["were collected", "was collected", "collects", "are collecting"],
                )
    # Numeric science tasks have explicit units and assumptions.
    for grade in range(7, 13):
        subject = "khoa_hoc_tu_nhien" if grade <= 9 else "vat_li"
        for i in range(1, 41):
            if grade == 7:
                speed = 2 + i % 9
                duration = 10 + i
                add(
                    grade,
                    subject,
                    "toc_do",
                    i,
                    f"Vật chuyển động đều đi {speed * duration} m trong {duration} s. Tốc độ bằng bao nhiêu m/s? Chỉ nhập số.",
                    speed,
                    f"v = s/t = {speed * duration}/{duration} = {speed} (m/s).",
                )
            elif grade == 8:
                density = 1 + i % 9
                volume = i + 2
                add(
                    grade,
                    subject,
                    "khoi_luong_rieng",
                    i,
                    f"Một vật đồng chất có khối lượng {density * volume} g, thể tích {volume} cm³. Khối lượng riêng bằng bao nhiêu g/cm³? Chỉ nhập số.",
                    density,
                    f"D = m/V = {density * volume}/{volume} = {density} (g/cm³).",
                )
            elif grade == 9:
                resistance = i + 2
                current = i % 5 + 1
                add(
                    grade,
                    subject,
                    "dinh_luat_ohm",
                    i,
                    f"Điện trở thuần R = {resistance} Ω có dòng điện I = {current} A chạy qua. Hiệu điện thế bằng bao nhiêu V? Chỉ nhập số.",
                    resistance * current,
                    f"U = IR = {current} × {resistance} = {current * resistance} (V).",
                )
            elif grade == 10:
                mass = i + 2
                acc = i % 7 + 1
                add(
                    grade,
                    subject,
                    "dinh_luat_newton",
                    i,
                    f"Vật khối lượng {mass} kg có gia tốc {acc} m/s² trong hệ quy chiếu quán tính. Độ lớn hợp lực bằng bao nhiêu N? Chỉ nhập số.",
                    mass * acc,
                    f"Theo định luật II Newton: F = ma = {mass} × {acc} = {mass * acc} (N).",
                )
            elif grade == 11:
                q = i + 1
                voltage = 10 + i
                add(
                    grade,
                    subject,
                    "cong_dien",
                    i,
                    f"Điện trường dịch chuyển điện tích dương q = {q} C từ M đến N; U_MN = {voltage} V. Công lực điện bằng bao nhiêu J? Chỉ nhập số.",
                    q * voltage,
                    f"A_MN = qU_MN = {q} × {voltage} = {q * voltage} (J).",
                )
            else:
                p = i + 1
                v = i + 3
                add(
                    grade,
                    subject,
                    "dinh_luat_boyle",
                    i,
                    f"Một lượng khí lí tưởng có áp suất {p} kPa, thể tích {v} lít. Nén đẳng nhiệt để thể tích còn {v}/2 lít. Áp suất mới bằng bao nhiêu kPa? Chỉ nhập số.",
                    2 * p,
                    f"Đẳng nhiệt: p₁V₁ = p₂V₂. p₂ = {p} × {v}/({v}/2) = {2 * p} (kPa).",
                )
    # Grade 6 measurements, grade 4–5 simple unit conversions, explicitly not chemistry calculations.
    for grade in (4, 5, 6):
        subject = "khoa_hoc" if grade <= 5 else "khoa_hoc_tu_nhien"
        for i in range(1, 41):
            value = grade * 50 + i
            add(
                grade,
                subject,
                "do_khoi_luong",
                i,
                f"Mẫu vật số {grade}-{i} có khối lượng {value} g. Đổi sang kg. Chỉ nhập số hoặc phân số.",
                F(value, 1000),
                f"1 kg = 1.000 g; {value} g = {value}/1.000 kg = {F(value, 1000)} kg.",
            )
    (ROOT / "data/seeds/subject_practice_questions.json").write_text(
        json.dumps({"questions": rows}, ensure_ascii=False, indent=2) + "\n"
    )
    exams = []
    groups = sorted({(q["grade"], q["subject"]) for q in rows})
    for grade, subject in groups:
        pool = [q["id"] for q in rows if (q["grade"], q["subject"]) == (grade, subject)]
        for n in range(4):
            exams.append(
                dict(
                    id=f"subplus_{grade}_{subject}_exam{n + 1}",
                    grade=grade,
                    subject=subject,
                    textbook="ket_noi_tri_thuc",
                    topic="tong_hop",
                    title=f"{'Tiếng Anh' if subject == 'tieng_anh' else 'Khoa học' if grade <= 6 else 'KHTN' if grade <= 9 else 'Vật lí'} {grade} · Ôn kỹ năng số {n + 1} · Tự biên soạn",
                    duration_minutes=20,
                    question_ids=pool[n * 10 : n * 10 + 10],
                )
            )
    (ROOT / "data/seeds/subject_practice_exams.json").write_text(
        json.dumps(exams, ensure_ascii=False, indent=2) + "\n"
    )
    print(len(rows), "original subject questions;", len(exams), "practice exams")


if __name__ == "__main__":
    build()
