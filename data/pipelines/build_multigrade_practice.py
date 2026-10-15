"""Original numeric practice. Preserve old IDs; never relabel web links as exams."""

import json
import hashlib
from fractions import Fraction as F
from pathlib import Path
from build_curriculum_seeds import TOPICS

ROOT = Path(__file__).resolve().parents[2]


def primary(slug, i):
    a, b = (i - 1) // 9 + 1, (i - 1) % 9 + 1
    if slug == "dem_so":
        value = 20 + i
        return (
            f"Số liền trước {value} là số nào?",
            value - 1,
            f"Số liền trước là {value} − 1 = {value - 1}.",
        )
    if slug == "cong_trong_20":
        return f"Tính {a} + {b}.", a + b, f"Gộp {a} và {b} đơn vị: {a} + {b} = {a + b}."
    if slug == "tru_trong_20":
        return (
            f"Tính {a + b} − {b}.",
            a,
            f"{a + b} − {b} = {a}; kiểm tra: {a} + {b} = {a + b}.",
        )
    if slug == "so_sanh":
        return (
            f"Giữa {20 + i} và {19 + i}, số nào nhỏ hơn?",
            19 + i,
            f"{19 + i} đứng trước {20 + i}; số nhỏ hơn là {19 + i}.",
        )
    if slug == "chuc_don_vi":
        return (
            f"Số {a * 10 + b} gồm mấy chục? Chỉ nhập số chục.",
            a,
            f"{a * 10 + b} = {a} chục và {b} đơn vị. Đáp số: {a}.",
        )
    return (
        f"Hộp có {a} bút chì, thêm {b} bút chì. Có tất cả bao nhiêu bút chì?",
        a + b,
        f"Số bút chì là {a} + {b} = {a + b} (bút chì).",
    )


def variant(grade, slug, make, i):
    if grade == 1:
        return primary(slug, i)
    if grade == 2 and slug in {"nhan_2", "chia_2"}:
        a, b = (i - 1) // 9 + 1, (i - 1) % 9 + 1
        if slug == "nhan_2":
            return (
                f"Có {a} đôi tất đỏ và {b} đôi tất xanh. Mỗi đôi có 2 chiếc. Có tất cả bao nhiêu chiếc tất?",
                2 * (a + b),
                f"Tổng số đôi là {a} + {b} = {a + b}. Số chiếc tất: {a + b} × 2 = {2 * (a + b)}.",
            )
        return (
            f"Có {2 * a} bánh đậu và {2 * b} bánh gạo. Chia đều tất cả cho 2 bạn. Mỗi bạn được mấy cái bánh?",
            a + b,
            f"Tổng số bánh: {2 * a} + {2 * b} = {2 * (a + b)}. Mỗi bạn: {2 * (a + b)} : 2 = {a + b} (cái bánh).",
        )
    if grade == 2 and slug == "gio_phut":
        h, minutes = (i - 1) // 10 + 7, ((i - 1) % 10 + 1) * 5
        return (
            f"Bắt đầu lúc {h} giờ, học trong {minutes} phút. Khi kết thúc, số phút trên đồng hồ là bao nhiêu?",
            minutes,
            f"{minutes} < 60 nên kết thúc lúc {h} giờ {minutes} phút. Đáp số: {minutes}.",
        )
    if grade == 11 and slug == "bien_co_doc_lap":
        a, b = (i - 1) // 9 + 1, (i - 1) % 9 + 1
        value = F(a * b, 100)
        return (
            f"A, B độc lập; P(A) = {a}/10, P(B) = {b}/10. Tính P(A ∩ B).",
            value,
            f"Vì độc lập, P(A ∩ B) = ({a}/10) × ({b}/10) = {value}.",
        )
    if grade == 12 and slug == "xac_suat_co_dieu_kien":
        a, b = (i - 1) // 9 + 1, (i - 1) % 9 + 1
        return (
            f"P(B) = {a + b}/20 và P(A ∩ B) = {a}/20. Tính P(A|B).",
            F(a, a + b),
            f"P(B) > 0. P(A|B) = ({a}/20)/({a + b}/20) = {F(a, a + b)}.",
        )
    if grade == 11 and slug in {"logarit", "ham_mu"}:
        a, b = (i - 1) // 8 + 2, (i - 1) % 8 + 2
        if slug == "logarit":
            return (
                f"Tính log cơ số {a} của {a**b}.",
                b,
                f"{a} > 0, {a} ≠ 1 và {a**b} = {a}^{b}; log cơ số {a} của {a**b} bằng {b}.",
            )
        return (
            f"Giải {a}^(x + 1) = {a ** (b + 1)}. Nhập x.",
            b,
            f"Cơ số {a} dương và khác 1. Vế phải = {a}^{b + 1}; x + 1 = {b + 1}, nên x = {b}.",
        )
    return make(i + 10)


def build():
    seen = set()
    for path in (ROOT / "data/seeds").glob("*questions.json"):
        if path.name == "multigrade_questions.json":
            continue
        seen.update(
            hashlib.sha256(q["question"].strip().casefold().encode()).hexdigest()
            for q in json.loads(path.read_text())["questions"]
        )
    questions = []
    for grade, slug, name, rule, mistake, make in TOPICS:
        if grade == 5:
            continue
        for i in range(1, 61):
            prompt, answer, solution = variant(grade, slug, make, i)
            digest = hashlib.sha256(prompt.strip().casefold().encode()).hexdigest()
            if digest in seen:
                continue
            seen.add(digest)
            questions.append(
                dict(
                    id=f"multi_math{grade}_{slug.replace('ơ', 'o')}_{i:02d}",
                    grade=grade,
                    subject="toan",
                    topic=slug.replace("ơ", "o"),
                    textbook="ket_noi_tri_thuc",
                    type="numeric",
                    difficulty="easy" if grade <= 5 else "medium",
                    question=prompt,
                    correct_answer=[str(answer)],
                    max_score=1,
                    explanation="Lời giải\n"
                    + solution
                    + "\nĐáp số: "
                    + str(answer)
                    + ".",
                    source_type="original",
                    license="original_content",
                    rights_evidence="Biến thể tự biên soạn theo kỹ năng; không chép đề Internet. Ánh xạ mức chủ đề KNTT, chưa xác minh từng bài hoặc thẩm định sư phạm độc lập.",
                )
            )
    # Expand the original sparse Grade 1 topics too, rather than leaving one-question rows.
    weekdays = [
        "thứ Hai",
        "thứ Ba",
        "thứ Tư",
        "thứ Năm",
        "thứ Sáu",
        "thứ Bảy",
        "Chủ nhật",
    ]
    extra = []
    for i in range(1, 61):
        start = (i - 1) // 3 + 1
        step = (i - 1) % 3 + 1
        prompt = f"Điền số tiếp theo: {start}, {start + step}, {start + 2 * step}, …"
        answer = start + 3 * step
        extra.append(
            (
                "day_so",
                i,
                prompt,
                str(answer),
                f"Mỗi số sau hơn số trước {step} đơn vị. Số tiếp theo: {start + 2 * step} + {step} = {answer}.",
                None,
            )
        )
        a, b = (i - 1) // 9 + 1, (i - 1) % 9 + 1
        extra.append(
            (
                "bai_toan",
                i,
                f"Có {a + b} viên bi, lấy ra {b} viên bi. Còn lại bao nhiêu viên bi?",
                str(a),
                f"Số viên bi còn lại: {a + b} − {b} = {a} (viên bi).",
                None,
            )
        )
    for day in range(7):
        for offset in (1, 2, 3):
            correct = weekdays[(day + offset) % 7]
            choices = [correct] + [d for d in weekdays if d != correct][:3]
            shift = (day + offset) % 4
            choices = choices[shift:] + choices[:shift]
            options = [dict(id=k, text=v) for k, v in zip("ABCD", choices)]
            extra.append(
                (
                    "thoi_gian",
                    day * 3 + offset,
                    f"Hôm nay là {weekdays[day]}. Sau {offset} ngày nữa là ngày nào trong tuần?",
                    next(o["id"] for o in options if o["text"] == correct),
                    f"Đếm tiếp {offset} ngày từ {weekdays[day]} được {correct}.",
                    options,
                )
            )
    for slug, i, prompt, answer, solution, options in extra:
        assert (
            hashlib.sha256(prompt.strip().casefold().encode()).hexdigest() not in seen
        )
        questions.append(
            dict(
                id=f"multi_math1_{slug}_{i:02d}",
                grade=1,
                subject="toan",
                topic=slug,
                textbook="ket_noi_tri_thuc",
                type="single_choice" if options else "numeric",
                difficulty="easy",
                question=prompt,
                correct_answer=[answer],
                explanation="Lời giải\n"
                + solution
                + "\nĐáp số: "
                + (
                    next(o["text"] for o in options if o["id"] == answer)
                    if options
                    else answer
                )
                + ".",
                max_score=1,
                options=options or [],
                source_type="original",
                license="original_content",
                rights_evidence="Bài tự biên soạn theo kỹ năng lớp 1; chưa thẩm định độc lập, không chép nguồn Internet.",
            )
        )
    exams = []
    for grade in range(1, 13):
        if grade == 5:
            continue
        rows = [q for q in questions if q["grade"] == grade]
        for n in range(1, 9):
            # Different offsets per family produce distinct, reproducible complete practice sets.
            chosen = []
            topics = list(dict.fromkeys(q["topic"] for q in rows))
            for topic in topics:
                pool = [q["id"] for q in rows if q["topic"] == topic]
                chosen.extend(
                    pool[((n - 1) * 3) % len(pool) : ((n - 1) * 3) % len(pool) + 3]
                )
            exams.append(
                dict(
                    id=f"multi_math{grade}_set_{n}",
                    grade=grade,
                    subject="toan",
                    textbook="ket_noi_tri_thuc",
                    topic="tong_hop",
                    title=f"Toán {grade} · Đề luyện tổng hợp số {n} · Tự biên soạn",
                    duration_minutes=40,
                    question_ids=chosen,
                )
            )
    (ROOT / "data/seeds/multigrade_questions.json").write_text(
        json.dumps({"questions": questions}, ensure_ascii=False, indent=2) + "\n"
    )
    (ROOT / "data/seeds/multigrade_exams.json").write_text(
        json.dumps(exams, ensure_ascii=False, indent=2) + "\n"
    )
    print(len(questions), "new questions;", len(exams), "complete original exams")


if __name__ == "__main__":
    build()
