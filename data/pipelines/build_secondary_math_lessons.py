"""Build real worked guides for all recorded Math 6–12 units, including reviews."""

import json
from pathlib import Path
from secondary_math_content import MAPPING, YEAR, resolve, activity_keys

ROOT = Path(__file__).resolve().parents[2]


def chosen_activity(grade, title):
    if title == "Đại lượng tỉ lệ trong đời sống":
        return ["ratios"]
    if "gang tay" in title.casefold():
        return ["hand_measurement"]
    return activity_keys(grade, title)


def software_method(title):
    t = title.casefold()
    if "geog" in t:
        return "Thực hành với GeoGebra: nhập biểu thức bằng kí hiệu x^2, x^3 khi làm đại số; khi vẽ hình dùng các công cụ Điểm, Đoạn thẳng, Đa giác và Đo độ dài/góc. Đặt đúng giả thiết trước, đối chiếu kết quả với lời giải trên giấy; hình nhìn giống không thay cho chứng minh.\n"
    if "excel" in t:
        return "Thực hành bảng tính: mỗi quan sát ở một ô, giữ nhãn và đơn vị ở đầu cột. Lập bảng đếm theo giá trị, kiểm tra tổng số đếm bằng cỡ mẫu, rồi chọn bảng để chèn biểu đồ cột thích hợp. Với mô phỏng, ghi số lần thử và tần số quan sát, không khẳng định kết quả ngẫu nhiên phải đúng bằng xác suất lí thuyết.\n"
    return ""


def build():
    books = json.loads(
        (ROOT / "data/seeds/textbook_units.json").read_text(encoding="utf-8")
    )["books"]
    documents = []
    counts = {}
    examples = 0
    for grade in range(6, 13):
        book = next(b for b in books if b["grade"] == grade and b["subject"] == "toan")
        seen = set()
        history = {}
        for unit in book["units"]:
            kind = unit["unit_kind"]
            number = unit["lesson_number"]
            if kind == "lesson":
                keys = MAPPING[grade][number]
                seen.add(number)
                history.setdefault(unit["chapter"], []).extend(keys)
            elif kind == "activity":
                keys = chosen_activity(grade, unit["title"])
            elif kind == "year_review":
                title = unit["title"].casefold()
                keys = (
                    ["quadrilateral_area", "symmetry", "p:midpoint"]
                    if grade == 6 and "hình học" in title
                    else ["p:data", "probability"]
                    if grade == 6 and "thống kê" in title
                    else [
                        "integers",
                        "signed_fractions",
                        "decimal_signed",
                        "fraction_problems",
                    ]
                    if grade == 6 and "phần số" in title
                    else YEAR[grade]
                )
            else:
                keys = list(dict.fromkeys(history.get(unit["chapter"], [])))
                if not keys:
                    raise ValueError(
                        "Review without explicit chapter topics: " + unit["title"]
                    )
                keys = keys[-5:]
            skills = [resolve(k, grade) for k in keys]
            examples += len(skills)
            sections = [
                dict(
                    heading="Mục tiêu và phạm vi",
                    text=f"Hướng dẫn cơ bản cho {unit['title']} – Toán {grade}, Kết nối tri thức. Nội dung tự biên soạn theo mục lục nguồn thứ cấp, chưa xác minh nguyên mẫu từng trang/ấn bản hoặc đầy đủ mọi dạng bài SGK. Các bài ôn tập dùng lại kỹ năng có liên quan; ví dụ thực tế có dữ liệu giả định sẽ được ghi rõ.",
                )
            ]
            for i, s in enumerate(skills, 1):
                prefix = f"{i}. " if len(skills) > 1 else ""
                sections.extend(
                    [
                        dict(
                            heading=prefix + "Kiến thức và cách làm",
                            text=s["rule"]
                            + "\n\nCách làm:\n"
                            + (
                                software_method(unit["title"])
                                if kind == "activity"
                                else ""
                            )
                            + s["method"],
                        ),
                        dict(
                            heading=prefix + "Ví dụ từng bước",
                            text="Đề bài: " + s["example"] + "\n\n" + s["worked"],
                        ),
                        dict(
                            heading=prefix + "Bài tập tự luyện",
                            text="\n".join(
                                f"{j}. {t}" for j, t in enumerate(s["tasks"], 1)
                            ),
                        ),
                        dict(
                            heading=prefix + "Lời giải bài tập",
                            text="\n\n".join(
                                f"Bài {j}.\n{a}" for j, a in enumerate(s["answers"], 1)
                            ),
                        ),
                        dict(heading=prefix + "Lỗi cần tránh", text=s["mistake"]),
                    ]
                )
            documents.append(
                dict(
                    id=f"kntt_math{grade}_unit_{unit['id'][5:]}",
                    grade=grade,
                    subject="toan",
                    title=unit["title"],
                    topic=unit["chapter"],
                    chapter=unit["chapter"],
                    lesson_order=unit["order"],
                    curriculum_unit_id=unit["id"],
                    semester=unit["semester"],
                    textbook="ket_noi_tri_thuc",
                    kind="study_notes",
                    summary=f"Kiến thức, cách làm; {len(skills)} ví dụ và {2 * len(skills)} bài tự luyện có lời giải, đáp số. Nội dung cơ bản, chờ thẩm định.",
                    sections=sections,
                    author="Kho Học 1–12",
                    source_name="Bài hướng dẫn tự biên soạn; mục lục tham khảo Loigiaihay",
                    source_url=unit["source_url"],
                    source_type="original",
                    license="original_content",
                    rights_evidence="Tự biên soạn kiến thức, ví dụ và lời giải; tên bài/chương/URL chỉ nhận diện mục lục Kết nối tri thức. Không sao chép nguyên bài giải hoặc sách PDF. Chưa thẩm định sư phạm độc lập.",
                    distribution_allowed=True,
                    download_allowed=False,
                )
            )
        assert seen == set(MAPPING[grade]), (grade, seen ^ set(MAPPING[grade]))
        counts[grade] = len(book["units"])
    (ROOT / "data/library/secondary_math_documents.json").write_text(
        json.dumps({"documents": documents}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        "Authored",
        len(documents),
        "Math 6–12 guides;",
        examples,
        "examples;",
        2 * examples,
        "practice tasks;",
        counts,
    )


if __name__ == "__main__":
    build()
