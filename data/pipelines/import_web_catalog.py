"""Build link-only catalog from checked page metadata; never import page bodies/PDFs."""

import argparse
import hashlib
import json
import re
import unicodedata
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
ALLOWED_HOSTS = {"loigiaihay.com", "vietjack.com", "khoahoc.vietjack.com"}
PERIOD_NAMES = {
    "midterm_1": "Giữa học kỳ 1",
    "final_1": "Cuối học kỳ 1",
    "midterm_2": "Giữa học kỳ 2",
    "final_2": "Cuối học kỳ 2",
    "graduation": "Tốt nghiệp THPT",
    "review": "Ôn tập củng cố",
}


def plain(text):
    return "".join(
        c
        for c in unicodedata.normalize("NFD", text.casefold().replace("đ", "d"))
        if not unicodedata.combining(c)
    )


def classify(url, title):
    path = urlsplit(url).path
    m = re.search(
        r"(?:lop|toan|van|anh|hoa|sinh|li|ly|khtn|gdcd|nhac|thuat|hoc|nghe|duc|hoi|dia-li|lich-su|trai-nghiem|phap-luat)-(1[0-2]|[1-9])(?:-|[/.])",
        path,
    )
    if not m:
        m = re.search(r"lop\s*(1[0-2]|[1-9])\b", plain(title))
    grade = int(m.group(1)) if m else None
    tests = [
        ("tieng-viet", "tieng_viet"),
        ("tieng-anh", "tieng_anh"),
        ("mon-anh", "tieng_anh"),
        ("toan", "toan"),
        ("vat-li", "vat_li"),
        ("vat-ly", "vat_li"),
        ("mon-li", "vat_li"),
        ("hoa", "hoa_hoc"),
        ("sinh", "sinh_hoc"),
        ("khoa-hoc-tu-nhien", "khoa_hoc_tu_nhien"),
        ("khtn", "khoa_hoc_tu_nhien"),
        ("tu-nhien-va-xa-hoi", "tu_nhien_xa_hoi"),
        ("khoa-hoc", "khoa_hoc"),
        ("lich-su-va-dia-li", "lich_su_dia_li"),
        ("lich-su", "lich_su"),
        ("dia-li", "dia_li"),
        ("kinh-te", "kinh_te_phap_luat"),
        ("gdcd", "gdcd"),
        ("dao-duc", "dao_duc"),
        ("quoc-phong", "quoc_phong"),
        ("the-chat", "the_chat"),
        ("tin-hoc", "tin_hoc"),
        ("cong-nghe", "cong_nghe"),
        ("am-nhac", "am_nhac"),
        ("mi-thuat", "mi_thuat"),
        ("hoat-dong-trai-nghiem", "huong_nghiep"),
        ("ngu-van", "ngu_van"),
        ("van", "ngu_van"),
    ]
    subject = next(
        (
            sid
            for keyword, sid in tests
            if re.search(r"(?:^|/)" + re.escape(keyword) + r"(?:-|$)", path.lstrip("/"))
            or re.search(r"-" + re.escape(keyword) + r"(?:-|$)", path)
        ),
        None,
    )
    if grade:
        if subject in ("lich_su", "dia_li") and grade <= 9:
            subject = "lich_su_dia_li"
        if subject in ("tin_hoc", "cong_nghe") and grade <= 5:
            subject = "tin_hoc_cong_nghe"
        if subject in ("am_nhac", "mi_thuat") and grade <= 9:
            subject = "nghe_thuat"
        if subject == "huong_nghiep" and grade <= 5:
            subject = "trai_nghiem"
    return grade, subject


def period(url):
    for token, base in [
        ("giua-ki", "midterm"),
        ("giua-hoc-ki", "midterm"),
        ("cuoi-ki", "final"),
        ("hoc-ki", "final"),
        ("hoc-ky", "final"),
    ]:
        match = re.search(token + r"-([12])(?:-|\b)", url)
        if match:
            return base + "_" + match.group(1)
    return None


def build(evidence_dir):
    catalog = json.loads((ROOT / "data/seeds/catalog.json").read_text(encoding="utf-8"))
    valid = {(g["id"], s["id"]) for g in catalog["grades"] for s in g["subjects"]}
    evidence = []
    for name, scope in [
        ("verified_hubs.json", "collection"),
        ("verified_papers.json", "single_paper"),
    ]:
        for row in json.loads((evidence_dir / name).read_text(encoding="utf-8")):
            evidence.append((row, scope, False))
    national = json.loads(
        (evidence_dir / "verified_national.json").read_text(encoding="utf-8")
    )
    evidence.extend((r, "collection", True) for r in national["hubs"])
    evidence.extend((r, "single_paper", True) for r in national["papers"])
    extra = evidence_dir / "verified_national_archives.json"
    if extra.exists():
        evidence.extend(
            (r, "single_paper", True)
            for r in json.loads(extra.read_text(encoding="utf-8"))
        )
    documents, audit, rejected = [], [], []
    seen = set()
    seen_content = set()
    for row, scope, is_national in evidence:
        url = row["url"]
        parsed = urlsplit(url)
        title = " ".join(row.get("title", "").split())
        reason = None
        if row.get("http_status") != 200 or "error" in row:
            reason = "fetch_failed"
        elif (
            parsed.scheme != "https"
            or parsed.hostname not in ALLOWED_HOSTS
            or parsed.username
            or parsed.password
        ):
            reason = "untrusted_url"
        elif not title:
            reason = "missing_title"
        if reason:
            rejected.append(dict(url=url, reason=reason))
            continue
        if url in seen:
            continue
        grade, subject = classify(url, title)
        if grade is None or subject is None:
            parent_grade, parent_subject = classify(row.get("parent", url), title)
            grade = grade if grade is not None else parent_grade
            subject = subject if subject is not None else parent_subject
        if is_national:
            grade = 12
            if not subject:
                _, subject = classify(row.get("parent", url), title)
        if (grade, subject) not in valid:
            rejected.append(dict(url=url, reason="unmapped_grade_subject"))
            continue
        marker = plain(" ".join([title] + [h[1] for h in row.get("headings", [])]))
        if not is_national and not any(
            x in marker for x in ("ket noi tri thuc", "kntt", "global success")
        ):
            rejected.append(dict(url=url, reason="no_book_marker_in_page_title"))
            continue
        if is_national and not any(
            x in plain(title) for x in ("tot nghiep", "thpt", "quoc gia")
        ):
            rejected.append(dict(url=url, reason="no_national_exam_marker"))
            continue
        normalized_title = plain(title)
        if any(token in normalized_title for token in ("cau truc", "huong dan")):
            scope = "study_guide"
        elif re.search(
            r"(?:bo de|tong hop|tuyen tap|\d+ de (?:thi|kiem))", normalized_title
        ):
            scope = "collection"
        p = "graduation" if is_national else period(url)
        if not p and "de-thi" not in url and "de-kiem-tra" not in url:
            p = "review"
        year_match = (
            re.search(r"\b(20(?:0\d|1\d|2[0-6]))\b", title) if is_national else None
        )
        year = int(year_match.group(1)) if year_match else None
        if is_national and scope == "single_paper" and year is None:
            rejected.append(dict(url=url, reason="year_not_identified"))
            continue
        note = (
            "Đề quốc gia dùng chung các bộ sách. "
            if is_national
            else "Nguồn ghi rõ Kết nối tri thức / Global Success. "
        )
        if year and year < 2025:
            note += "Nguồn ghi năm trước 2025; chỉ dùng tham khảo và cần đối chiếu cấu trúc kỳ thi hiện hành. "
        note += "Chỉ mở trang nguồn, không sao chép PDF/câu hỏi vào app. Trang nguồn có thể có quảng cáo, đăng nhập hoặc phí; chưa xác nhận miễn phí toàn bộ."
        content_key = (grade, subject, " ".join(plain(title[:200]).split()))
        if content_key in seen_content:
            rejected.append(dict(url=url, reason="duplicate_title_grade_subject"))
            continue
        seen_content.add(content_key)
        doc = dict(
            id="web_" + hashlib.sha256(url.encode()).hexdigest()[:24],
            title=title[:200],
            grade=grade,
            subject=subject,
            semester=int(p[-1]) if p and p[-1] in "12" else None,
            topic=PERIOD_NAMES.get(p, "Kho đề kiểm tra"),
            textbook="national_common" if is_national else "ket_noi_tri_thuc",
            kind="exam"
            if (is_national or "de-thi" in url or "de-kiem-tra" in url)
            and scope != "study_guide"
            else "worksheet"
            if "sbt-" in url or "vbt-" in url
            else "reference",
            summary=note,
            author="Theo thông tin tại trang nguồn",
            source_name=parsed.hostname,
            source_url=url,
            assessment_period=p,
            exam_year=year,
            source_verified_on=date(2026, 10, 15).isoformat(),
            resource_scope=scope,
            access_notice=note,
            source_type="link_only",
            license="link_only",
            rights_evidence="Chỉ lưu metadata nhận diện và liên kết HTTPS tới trang công khai đã kiểm tra HTTP 200; không sao chép hoặc phân phối nội dung nguồn.",
            distribution_allowed=False,
            download_allowed=False,
            sections=[],
        )
        documents.append(doc)
        seen.add(url)
        audit.append(
            dict(
                id=doc["id"],
                url=url,
                title=title,
                http_status=200,
                html_sha256=row["sha256"],
                verified_on="2026-10-15",
                evidence_type="national_title"
                if is_national
                else "book_marker_in_heading_or_html_title",
                book_evidence=marker if not is_national else None,
                parent_url=row.get("parent"),
                resource_scope=scope,
            )
        )
    output = ROOT / "data/library/external_documents.json"
    # Existing verified records stay immutable so upgrades preserve user databases.
    if output.exists():
        existing = json.loads(output.read_text(encoding="utf-8"))["documents"]
        by_url = {document["source_url"]: document for document in existing}
        # Preserve published fixture payloads; rechecks live in the audit report.
        documents = [
            by_url.get(document["source_url"], document) for document in documents
        ]
        found_urls = {document["source_url"] for document in documents}
        documents.extend(
            document
            for document in existing
            if document["source_url"] not in found_urls
        )
    output.write_text(
        json.dumps(dict(documents=documents), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (ROOT / "data/library/source_checks.json").write_text(
        json.dumps(
            dict(verified=audit, rejected=rejected), ensure_ascii=False, indent=2
        )
        + "\n",
        encoding="utf-8",
    )
    print(
        "Catalog records",
        len(documents),
        "single papers",
        sum(d["resource_scope"] == "single_paper" for d in documents),
        "national",
        sum(d["textbook"] == "national_common" for d in documents),
        "rejected",
        len(rejected),
    )
    return documents


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", type=Path, required=True)
    build(parser.parse_args().evidence)
