"""Create substantive original Math 1–4 lessons for verified index entries only."""

import json
import re
from pathlib import Path
from primary_math_content import GRADE_MAP, resolve

ROOT = Path(__file__).resolve().parents[2]


def build():
    books = json.loads(
        (ROOT / "data/seeds/textbook_units.json").read_text(encoding="utf-8")
    )["books"]
    documents = []
    for grade in (1, 2, 3, 4):
        book = next(b for b in books if b["grade"] == grade and b["subject"] == "toan")
        seen = set()
        for unit in book["units"]:
            number = int(re.match(r"Bài\s*(\d+)", unit["title"]).group(1))
            seen.add(number)
            keys = GRADE_MAP[grade][number]
            skills = [resolve(key, grade, number) for key in keys]
            sections = [
                dict(
                    heading="Mục tiêu và phạm vi",
                    text=f"Hướng dẫn và luyện tập cơ bản cho {unit['title']} (Toán {grade}, Kết nối tri thức). Nội dung tự biên soạn theo mục lục nguồn thứ cấp; chưa xác minh nguyên mẫu từng trang/ấn bản SGK hoặc đủ mọi dạng bài. Các nội dung ôn tập dùng lại kỹ năng đã học có liên quan.",
                )
            ]
            for i, skill in enumerate(skills, 1):
                prefix = f"{i}. " if len(skills) > 1 else ""
                sections.extend(
                    [
                        dict(
                            heading=prefix + "Kiến thức và cách làm",
                            text=skill["name"]
                            + "\n"
                            + skill["rule"]
                            + "\n\nCách làm:\n"
                            + skill["method"],
                        ),
                        dict(
                            heading=prefix + "Ví dụ từng bước",
                            text="Đề bài: "
                            + skill["example"]
                            + "\n\n"
                            + skill["worked"],
                        ),
                        dict(
                            heading=prefix + "Bài tập tự luyện",
                            text="\n".join(
                                f"{j}. {task}"
                                for j, task in enumerate(skill["tasks"], 1)
                            ),
                        ),
                        dict(
                            heading=prefix + "Lời giải bài tập",
                            text="\n\n".join(
                                f"Bài {j}.\n{answer}"
                                for j, answer in enumerate(skill["answers"], 1)
                            ),
                        ),
                        dict(heading=prefix + "Lỗi cần tránh", text=skill["mistake"]),
                    ]
                )
            documents.append(
                dict(
                    id=f"kntt_math{grade}_lesson_{number:02d}",
                    grade=grade,
                    subject="toan",
                    title=unit["title"],
                    topic=unit["chapter"],
                    chapter=unit["chapter"],
                    lesson_order=number,
                    curriculum_unit_id=unit["id"],
                    semester=1 if number <= {1: 20, 2: 36, 3: 44, 4: 37}[grade] else 2,
                    textbook="ket_noi_tri_thuc",
                    kind="study_notes",
                    summary=f"Hướng dẫn {', '.join(s['name'].lower() for s in skills)}; {len(skills)} ví dụ và {2 * len(skills)} bài tự luyện có lời giải, đáp số.",
                    sections=sections,
                    author="Kho Học 1–12",
                    source_name="Bài hướng dẫn tự biên soạn; mục lục tham khảo Loigiaihay",
                    source_url=unit["source_url"],
                    source_type="original",
                    license="original_content",
                    rights_evidence="Kiến thức, ví dụ và lời giải được soạn riêng. Chỉ tên bài, chương và URL nguồn dùng đối chiếu mục lục; không sao chép nguyên bài giải của nguồn. Chưa thẩm định sư phạm độc lập.",
                    distribution_allowed=True,
                    download_allowed=False,
                )
            )
        assert seen == set(GRADE_MAP[grade]), (grade, seen ^ set(GRADE_MAP[grade]))
    output = ROOT / "data/library/primary_math_documents.json"
    output.write_text(
        json.dumps({"documents": documents}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        "Authored",
        len(documents),
        "new Math 1–4 lesson guides; examples",
        sum(len(GRADE_MAP[d["grade"]][d["lesson_order"]]) for d in documents),
    )


if __name__ == "__main__":
    build()
