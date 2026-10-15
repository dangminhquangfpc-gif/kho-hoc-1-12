"""Update only Math 6–12 indexes from saved source pages; keep existing IDs."""

import argparse
import hashlib
import json
import re
from pathlib import Path
from textbook_index import StructuredMathToc

ROOT = Path(__file__).resolve().parents[2]


def refresh(source_directory):
    path = ROOT / "data/seeds/textbook_units.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    for book in data["books"]:
        if book["subject"] != "toan" or not 6 <= book["grade"] <= 12:
            continue
        raw = (source_directory / f"math{book['grade']}.html").read_bytes()
        parser = StructuredMathToc()
        parser.feed(raw.decode("utf-8"))
        seen = set()
        units = []
        for e in parser.entries:
            if e["url"] in seen:
                continue
            seen.add(e["url"])
            match = re.match(r"Bài\s+(\d+)\.", e["title"], re.I)
            activity = e["chapter"].casefold().startswith("hoạt động")
            year = "cuối năm" in e["title"].casefold()
            kind = (
                "year_review"
                if year
                else "activity"
                if activity
                else "lesson"
                if match
                else "review"
            )
            units.append(
                dict(
                    id="unit_" + hashlib.sha256(e["url"].encode()).hexdigest()[:20],
                    title=e["title"],
                    chapter=e["chapter"] or "Ôn tập cuối năm",
                    source_url=e["url"],
                    semester=e["semester"],
                    order=len(units) + 1,
                    unit_kind=kind,
                    lesson_number=int(match.group(1))
                    if match and kind == "lesson"
                    else None,
                )
            )
        expected = {6: 43, 7: 37, 8: 39, 9: 32, 10: 27, 11: 33, 12: 19}[book["grade"]]
        numbers = [u["lesson_number"] for u in units if u["unit_kind"] == "lesson"]
        assert sorted(numbers) == list(range(1, expected + 1)), (book["grade"], numbers)
        assert all(u["semester"] in (1, 2) for u in units)
        book.update(
            units=units,
            source_html_sha256=hashlib.sha256(raw).hexdigest(),
            verified_on="2026-10-15",
        )
        print(book["grade"], len(units), "entries;", len(numbers), "numbered lessons")
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("source_directory", type=Path)
    refresh(p.parse_args().source_directory)
