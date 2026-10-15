"""Package the web demo, PSF runtime, and pinned Windows wheels without user state."""

from pathlib import Path, PurePosixPath
import argparse
import base64
import hashlib
import json
import shutil
import struct
from zipfile import ZipFile, ZIP_DEFLATED, ZIP_STORED
from packaging.requirements import Requirement
from packaging.markers import default_environment
from packaging.utils import canonicalize_name
from email.parser import Parser

ROOT = Path(__file__).resolve().parents[1]


def build(artifacts: Path):
    # The shipped OCR worker must match its pinned source assets and licenses.
    ocr_source = ROOT / "apps/mobile/web/ocr"
    ocr_built = ROOT / "apps/mobile/build/web/ocr"
    for line in (ocr_source / "SHA256SUMS").read_text(encoding="ascii").splitlines():
        ocr_digest, name = line.split("  ", 1)
        relative = PurePosixPath(name)
        assert not relative.is_absolute() and ".." not in relative.parts
        for directory in (ocr_source, ocr_built):
            asset = directory / name
            assert not asset.is_symlink()
            assert hashlib.sha256(asset.read_bytes()).hexdigest() == ocr_digest, name
    runtime = artifacts / "python.3.12.10.nupkg"
    metadata = json.loads(
        (artifacts / "python-runtime-provenance.json").read_text(encoding="utf-8")
    )
    assert metadata["id"] == "python" and metadata["version"] == "3.12.10"
    assert metadata["packageHashAlgorithm"] == "SHA512"
    assert (
        base64.b64encode(hashlib.sha512(runtime.read_bytes()).digest()).decode()
        == metadata["packageHash"]
    )
    wheels = artifacts / "windows-wheels"
    hashes = json.loads((wheels / "SHA256SUMS.json").read_text())
    packages = {}
    requirements = []
    for file in wheels.glob("*.whl"):
        assert hashes[file.name] == hashlib.sha256(file.read_bytes()).hexdigest()
        with ZipFile(file) as z:
            message = Parser().parsestr(
                z.read(
                    next(n for n in z.namelist() if n.endswith(".dist-info/METADATA"))
                ).decode()
            )
            packages[canonicalize_name(message["Name"])] = message["Version"]
            requirements.extend(message.get_all("Requires-Dist", []))
    assert set(hashes) == {f.name for f in wheels.glob("*.whl")}
    windows = default_environment()
    windows.update(
        sys_platform="win32",
        platform_system="Windows",
        os_name="nt",
        platform_machine="AMD64",
        python_version="3.12",
        python_full_version="3.12.10",
        extra="",
    )
    for raw in requirements:
        requirement = Requirement(raw)
        if requirement.marker is None or requirement.marker.evaluate(windows):
            assert requirement.url is None
            assert requirement.specifier.contains(
                packages[canonicalize_name(requirement.name)], prereleases=True
            ), raw
    staging = artifacts / "tu-hoc-111-demo-windows"
    if staging.exists():
        raise RuntimeError(
            "Choose a clean artifact directory; existing staging is preserved"
        )
    staging.mkdir()
    directories = ["apps/mobile/build/web", "services/api/khohoc", "data/seeds"]
    for name in directories:
        shutil.copytree(
            ROOT / name,
            staging / name,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
        )
    for name in [
        "services/api/requirements.lock.txt",
        "scripts/serve_demo.py",
        "scripts/run_local_demo.py",
        "scripts/backup_local.py",
        "docs/BACKUP_RECOVERY.md",
        "docs/SHARED_SERVER.md",
        "docs/CONTENT_REPORTS.md",
        "docs/CLASSROOM_REPORTS.md",
        "docs/EVENING_CHECKLIST.md",
        "docs/GROUP_ASSIGNMENTS.md",
        "docs/AI_OCR.md",
        "start-demo.bat",
        "start-demo.sh",
        "LICENSE",
        "data/library/documents.json",
        "data/library/external_documents.json",
        "data/library/curriculum_documents.json",
        "data/library/primary_math_documents.json",
        "data/library/secondary_math_documents.json",
        "data/library/document_upgrades.json",
    ]:
        target = staging / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / name, target)
    shutil.copytree(ROOT / "data/library/files", staging / "data/library/files")
    shutil.copytree(wheels, staging / "wheelhouse")
    with ZipFile(runtime) as z:
        for name in z.namelist():
            if not name.startswith("tools/") or name.endswith("/"):
                continue
            relative = PurePosixPath(name).relative_to("tools")
            assert ".." not in relative.parts and not relative.is_absolute()
            target = staging / "runtime/python" / str(relative)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(z.read(name))
        (staging / "runtime/python.nuspec").write_bytes(z.read("python.nuspec"))
    exe = (staging / "runtime/python/python.exe").read_bytes()
    assert exe[:2] == b"MZ"
    pe = struct.unpack_from("<I", exe, 0x3C)[0]
    assert (
        exe[pe : pe + 4] == b"PE\x00\x00"
        and struct.unpack_from("<H", exe, pe + 4)[0] == 0x8664
    )
    assert (staging / "runtime/python/Lib/ensurepip/__init__.py").exists()
    (staging / "runtime/provenance.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    guide = """TỰ HỌC 111 — DEMO LOCAL WINDOWS 64-BIT\n\n1. Giải nén toàn bộ ZIP (Extract All), không chạy trực tiếp trong ZIP.\n2. Mở thư mục vừa giải nén, nhấp đúp start-demo.bat.\n3. Giữ cửa sổ đó mở; đợi dòng DEMO READY. Trình duyệt sẽ tự mở http://localhost:8080.\n\nĐã kèm Python 3.12.10 chính thức của Python Software Foundation và thư viện Windows đã khóa phiên bản. Không cần cài Python, Flutter, Node hoặc Supabase. Lần đầu chuẩn bị môi trường có thể mất vài phút; các lần sau nhanh hơn. Không tải thư viện từ Internet khi khởi động trên Windows.\n\nThử: chọn lớp/môn, làm và nộp đề; vào Tài liệu đọc ghi chú/mở PDF; xem Tiến độ/Lịch sử. Có108 câu/12 đề và4 tài liệu tự biên soạn.\n\nĐể dừng, quay lại cửa sổ khởi động và nhấn Ctrl+C. Dữ liệu bài làm lưu trong state/demo.sqlite và trong trình duyệt trên máy này. Không chạy admin/Supabase; OCR xử lý trong trình duyệt, AI mặc định chưa kết nối.\n\nNếu cổng đã được chương trình khác sử dụng, launcher sẽ thông báo. Có thể mở CMD trong thư mục gói và chạy: start-demo.bat --api-port8011 --port8091 (thêm khoảng trắng: --api-port 8011 --port 8091).\n\nNếu có lỗi, giữ nội dung lỗi trong cửa sổ; log ở state/api.log và state/demo.log. Không xóa dữ liệu state khi muốn giữ bài làm.\n\nGói Windows dùng runtime/wheel Windows64-bit; không dùng Python Windows trong gói này trên macOS/Linux. Backend và giao diện đã kiểm tra trên môi trường Linux; file.bat/runtime Windows chưa chạy trên máy Windows thực tế. Đây là bản thử, chưa phát hành Google Play hoặc nội dung được thẩm định chuyên môn.\n"""
    guide = (
        guide.replace("Có108 câu/12 đề và4", "Có 108 câu/12 đề và 4")
        .replace(
            "start-demo.bat --api-port8011 --port8091 (thêm khoảng trắng: --api-port 8011 --port 8091)",
            "start-demo.bat --api-port 8011 --port 8091",
        )
        .replace("file.bat/runtime", "file .bat/runtime")
        .replace("Windows64-bit", "Windows 64-bit")
    )
    question_count = sum(
        len(json.loads(path.read_text(encoding="utf-8"))["questions"])
        for path in (ROOT / "data/seeds").glob("*questions.json")
    )
    exam_count = sum(
        len(json.loads(path.read_text(encoding="utf-8")))
        for path in (ROOT / "data/seeds").glob("*exams.json")
    )
    document_count = sum(
        len(
            json.loads((ROOT / "data/library" / name).read_text(encoding="utf-8"))[
                "documents"
            ]
        )
        for name in (
            "documents.json",
            "external_documents.json",
            "curriculum_documents.json",
            "primary_math_documents.json",
            "secondary_math_documents.json",
        )
    )
    guide = guide.replace(
        "Có 108 câu/12 đề và 4 tài liệu",
        f"Có {question_count} bản ghi câu hỏi (gồm câu cũ đã rút/thay thế)/{exam_count} đề và {document_count} tài liệu/liên kết",
    )
    guide += "\nBản thử 2026.10.15.16. Nếu bài lưu quá hạn hoặc thuộc máy chủ cũ, dùng Khôi phục bài đã lưu; app chỉ giữ đáp án cho câu không đổi. Đã tránh cache giao diện của bản ZIP cũ, không xóa bài làm trong trình duyệt.\n"
    guide += "\nMới: Luyện đề > Tạo đề theo chủ đề và độ khó (1–50 câu tùy ngân hàng); Tiến độ > Ôn các câu chưa đúng. Thống kê chủ đề chỉ tính lần làm mới nhất của mỗi câu, không phải đánh giá năng lực chính thức. Có thể luyện khách hoặc đăng nhập để lưu kết quả tập trung; AI cần cấu hình dịch vụ thật như hướng dẫn AI_OCR.md.\n"
    guide += "\nTài liệu chỉ hiển thị bài gắn đúng mục lục SGK. Đề kiểm tra Internet ở Luyện đề > Đề giữa kỳ, cuối kỳ và tốt nghiệp từ Internet. 87 bộ luyện Toán 5 mới dùng 344 câu tự biên soạn; các bộ ôn tổng hợp dùng lại câu của bộ luyện theo bài. Chưa chuyển nguyên đề PDF của nguồn Internet vào app.\n"
    guide += "\nTài liệu Internet được liên kết tới trang nguồn, cần mạng để mở. Có bộ lọc giữa/cuối kỳ và năm đề tốt nghiệp; đề quốc gia dùng chung các bộ sách.\n"
    guide += "\nDữ liệu mở rộng hướng tới Kết nối tri thức: 720 biến thể Toán từ 72 dạng; các môn khác có bộ ôn kiến thức nền, một số câu dùng lại giữa các lớp. Chưa đối chiếu từng bài/ấn bản SGK hiện hành.\n"
    guide += "\nMới ở bản .6: chọn nhiều chủ đề cùng lúc (tối đa 20), phân bổ câu giữa các chủ đề; thêm 731 câu Toán 5 tự biên soạn, chuẩn hóa tên chủ đề tiếng Việt.\n"
    guide += "\nTÀI KHOẢN: chạy start-demo.bat rồi mở state/TAI-KHOAN-QUAN-LY.txt trên chính máy bạn để lấy tài khoản quanly và mật khẩu ban đầu; đổi mật khẩu khi đăng nhập lần đầu. Trong Cá nhân > Tài khoản > Quản lý học viên có tạo hàng loạt, cấp lại mật khẩu và xem kết quả. Học viên cũng có thể tự đăng ký. Không chia sẻ tệp mật khẩu quản lý.\n"
    guide += "\nMỚI Ở BẢN .12: lưu bản nháp lên backend theo tài khoản; vào Tài khoản để tiếp tục bài trên thiết bị khác, làm mới điểm và xem trạng thái đồng bộ. Khi có xung đột, app giữ câu trả lời local và yêu cầu tải lại bản máy chủ. Để dùng trên nhiều máy/điện thoại cần cùng backend HTTPS; gói ZIP vẫn chạy local. Hỗ trợ cấu hình HTTPS kết thúc bằng /api.\n"
    guide += "\nNÂNG CẤP: dừng bản cũ, sao lưu và chép toàn bộ thư mục state từ bản cũ sang bản mới trước khi chạy để giữ tài khoản và kết quả. Không chép state từ người khác. Mỗi bản chạy riêng có cơ sở dữ liệu riêng. Để giám sát học viên trên máy khác, cần triển khai một backend HTTPS dùng chung; bản ZIP hiện chạy local.\n"
    guide += "\nBản .7: 75 tài liệu Toán 5 có kiến thức bằng lời, hướng dẫn từng bước, ví dụ và bài tập kèm Lời giải đầy đủ, phép tính có đơn vị, Đáp số ở cuối. Đặt tính cộng/trừ thập phân hiển thị thẳng cột. Đây là nội dung tự biên soạn theo mục lục nguồn thứ cấp, chưa xác minh nguyên mẫu mọi trang SGK. Bản mới nâng cấp đúng dữ liệu gốc cũ; nếu tài liệu đã sửa riêng, giữ bản sao state và liên hệ để xử lý, không xóa dữ liệu.\n"
    guide += "\nBản .8: thêm 267 bài hướng dẫn Toán 1–4 theo các mục đã ghi nhận từ nguồn mục lục, gồm 476 ví dụ và 952 bài luyện có lời giải, đáp số. Vào Tài liệu chọn lớp 1–4, môn Toán. Các bài chưa có nguồn hoặc các môn/lớp khác vẫn cần bổ sung, chưa tuyên bố đủ mọi SGK.\n"
    guide += "\nBản .9: thêm 391 hướng dẫn Toán 6–12, gồm 230 bài đánh số và các phần ôn tập/thực hành đã có nguồn. Mỗi lớp 6–12 có thể mở tài liệu trong app. Thêm 610 ví dụ và 1 220 bài luyện có lời giải; các phần ôn tập dùng lại kỹ năng. Nội dung cơ bản tự biên soạn, chưa xác nhận nguyên mẫu hoặc đủ mọi dạng bài SGK; các môn ngoài Toán vẫn còn thiếu.\n"
    guide += "\nBản .10: thêm 5.246 câu và 164 đề tự biên soạn làm trực tiếp. Đăng ký có vai trò học sinh/giáo viên. Học sinh làm đề có sẵn, ôn câu đã sai; giáo viên và quản lý được tạo đề. Giáo viên tạo nhóm, thêm tài khoản đã cấp hoặc gửi mã nhóm cho học sinh tự tham gia; chỉ xem học viên trong phạm vi quản lý. Các liên kết Internet chưa nhập không được tính là đề làm trực tiếp. Nội dung bổ sung chưa được xác minh đầy đủ từng bài SGK. Nâng cấp: dừng bản cũ, sao lưu và chép toàn bộ thư mục state vào bản mới trước khi chạy.\n"
    guide += "\nBản .11 — Tự học 111: bỏ mệnh đề thừa ở 12 câu bằng phiên bản mới; có 991 đề tự biên soạn gắn từ thẻ tham khảo, mỗi đề 20–24 câu, không phải bản sao đề nguồn. 525 thẻ chưa đủ câu vẫn là tham khảo. Tổng 1.461 đề làm trực tiếp và 7.886 câu đang hoạt động. Có xóa tài khoản trong app bằng mật khẩu xác nhận. Đã chuẩn bị khung iOS/cấu hình ký Android; chưa đưa lên cửa hàng vì chưa có tài khoản nhà phát hành/backend HTTPS production và các bước thẩm định.\n"
    guide += "\nBản .14: Báo lỗi nội dung trong câu hỏi và tài liệu; theo dõi ở Cá nhân > Tài khoản > Phản hồi của tôi. Giáo viên/quản lý có Xử lý phản hồi nội dung; trả lời không sửa điểm cũ. Có CSV bảng điểm theo nhóm. Đọc docs/EVENING_CHECKLIST.md để kiểm tra toàn bộ và docs/CONTENT_REPORTS.md để xem quyền, cách nâng cấp schema.\n"
    guide += "\nBản .15: nhóm có Bài giao và tiến độ > Giao đề có sẵn; học sinh mở Bài được giao ở Tài khoản. Có trạng thái chưa nộp/đang làm/đã nộp và CSV từng đề; điểm lấy lần nộp gần nhất. Giữ bài chưa đồng bộ khi mở đề khác. Xem docs/GROUP_ASSIGNMENTS.md.\n"
    guide += "\nBản .16: Ảnh và trợ lý học tập có OCR tiếng Việt local, xem ảnh/sửa chữ/xác nhận trước khi dùng. Có nút nhập OCR ở câu trả lời dạng gõ. AI mặc định tắt vì chưa có dịch vụ; chỉ gửi văn bản sau xác nhận, không gửi ảnh. Xem docs/AI_OCR.md; OCR ảnh hiện chạy web/Windows, chưa native Android/iOS.\n"
    (staging / "HUONG-DAN.txt").write_text(guide, encoding="utf-8-sig")
    for bat in [staging / "start-demo.bat"]:
        content = (
            bat.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\n", "\r\n")
        )
        bat.write_bytes(content.encode("utf-8"))
    output = artifacts / "tu-hoc-111-demo-windows.zip"
    with ZipFile(output, "w", compression=ZIP_DEFLATED, compresslevel=6) as z:
        for file in sorted(staging.rglob("*")):
            if file.is_file():
                assert not file.is_symlink()
                name = file.relative_to(artifacts).as_posix()
                assert ".env" not in file.name and "__pycache__" not in file.parts
                z.write(
                    file,
                    name,
                    compress_type=ZIP_STORED if file.suffix == ".whl" else ZIP_DEFLATED,
                )
    with ZipFile(output) as z:
        assert z.testzip() is None
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    (artifacts / "tu-hoc-111-demo-windows.zip.sha256").write_text(
        digest + "  " + output.name + "\n"
    )
    print(
        f"Built {output}: {output.stat().st_size:,} bytes; Windows wheel dependency closure verified"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifacts", type=Path, default=Path("/workspace/artifacts"))
    build(parser.parse_args().artifacts)
