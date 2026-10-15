"""Offer original same-grade/subject practice from reference cards, without claiming web transcription."""

import hashlib
import json
import random
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[2]


def build():
    # Clean replacements supersede old IDs; content remains unchanged in stored attempts.
    replacements = {"practice_math5_natural_04"}
    cleaned = json.loads((ROOT / "data/seeds/clean_questions.json").read_text())[
        "questions"
    ]
    replacements.update(q["id"].removesuffix("_clean_v2") for q in cleaned)
    pools = defaultdict(dict)
    for path in sorted((ROOT / "data/seeds").glob("*questions.json")):
        for q in json.loads(path.read_text())["questions"]:
            if (
                q["type"] == "essay"
                or q["id"] in replacements
                or q.get("source_type") == "link_only"
            ):
                continue
            pools[(q["grade"], q["subject"])][q["id"]] = q
    names = {}
    import sys

    sys.path.insert(0, str(ROOT / "services/api"))
    from khohoc.catalog import subjects_for_grade

    for g in range(1, 13):
        for s in subjects_for_grade(g):
            names[g, s["id"]] = s["name"]
    sources = json.loads((ROOT / "data/library/external_documents.json").read_text())[
        "documents"
    ]
    exams = []
    mapping = {}
    unavailable = []
    for d in sources:
        if d["kind"] != "exam" or d["resource_scope"] != "single_paper":
            continue
        pool = list(pools[d["grade"], d["subject"]].values())
        # A complete set means at least 20 distinct questions; never duplicate to pad a small bank.
        if len(pool) < 20:
            unavailable.append(d["id"])
            continue
        by_topic = defaultdict(list)
        seed = int(hashlib.sha256(d["id"].encode()).hexdigest(), 16)
        rng = random.Random(seed)
        for q in pool:
            by_topic[q["topic"]].append(q)
        for values in by_topic.values():
            rng.shuffle(values)
        topics = list(by_topic)
        rng.shuffle(topics)
        selected = []
        count = min(24, len(pool))
        while len(selected) < count:
            for topic in topics:
                if by_topic[topic] and len(selected) < count:
                    selected.append(by_topic[topic].pop()["id"])
        title = f"{names[d['grade'], d['subject']]} {d['grade']} · Đề luyện {len(exams) + 1} · Tự biên soạn"
        eid = "source_practice_" + d["id"].removeprefix("web_")
        exams.append(
            dict(
                id=eid,
                title=title,
                grade=d["grade"],
                subject=d["subject"],
                textbook="ket_noi_tri_thuc",
                topic="tong_hop",
                duration_minutes=40,
                question_ids=selected,
            )
        )
        mapping[d["id"]] = dict(
            exam_id=eid,
            title=title,
            question_count=count,
            notice="Đề tự biên soạn cùng lớp/môn; không phải bản chuyển nguyên văn đề nguồn. Phạm vi chương và học kỳ chưa được đối chiếu đầy đủ với nguồn.",
        )
    (ROOT / "data/seeds/source_practice_exams.json").write_text(
        json.dumps(exams, ensure_ascii=False, indent=2) + "\n"
    )
    (ROOT / "data/seeds/source_practice_map.json").write_text(
        json.dumps(
            dict(
                version=1,
                kind="original_same_grade_subject",
                papers=mapping,
                unavailable=unavailable,
            ),
            ensure_ascii=False,
            indent=2,
        )
        + "\n"
    )
    print(
        len(exams),
        "complete original practice sets;",
        len(unavailable),
        "references still lack enough bank questions",
    )


if __name__ == "__main__":
    build()
