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
        "docs/OCR.md",
        "docs/OFFLINE_STUDY.md",
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
    guide = """TỰ HỌC 111 — BẢN THỬ .19 — WINDOWS 64-BIT

CÁCH CHẠY
1. Giải nén toàn bộ ZIP (Extract All), không chạy trực tiếp trong ZIP.
2. Nhấp đúp start-demo.bat trong thư mục vừa giải nén.
3. Giữ cửa sổ mở; đợi DEMO READY. Trình duyệt tự mở http://localhost:8080.
Gói kèm Python 3.12.10 chính thức của PSF và thư viện Windows khóa phiên bản;
khởi động không tải thư viện từ Internet. Không cần cài Flutter/Node/Python.
Dừng bằng Ctrl+C. Nếu cổng bận, mở CMD và chạy:
start-demo.bat --api-port 8011 --port 8091
Log ở state/api.log và state/demo.log.

NÂNG CẤP GIỮ DỮ LIỆU
Dừng bản cũ, sao lưu rồi chép nguyên thư mục state từ bản cũ sang thư mục mới
trước khi chạy. Giữ cùng cổng localhost để giữ lịch sử trong trình duyệt.
Không chia sẻ state vì chứa dữ liệu riêng. Không xóa dữ liệu khi gặp lỗi.
Cấu hình/khóa AI cũ trong state được giữ nguyên nhưng bản .18 không đọc/dùng.

HỌC VÀ QUẢN LÝ
Luyện đề: làm đề có sẵn, nộp và xem lời giải; Tiến độ: lịch sử, ôn câu chưa đúng.
Tài liệu: chọn lớp/môn để đọc kiến thức, cách làm, ví dụ, bài tập và lời giải.
Học viên tự đăng ký hoặc được cấp tài khoản. Giáo viên/quản lý tạo đề nhiều
chủ đề, tạo nhóm, giao bài, xem tiến độ và xuất CSV. Học sinh không tạo đề.
Tài khoản quản lý ban đầu ở state/TAI-KHOAN-QUAN-LY.txt: mở riêng trên máy
của bạn rồi đổi mật khẩu lần đầu. Không chia sẻ tệp này.
Có báo lỗi nội dung, tự xóa tài khoản bằng mật khẩu xác nhận và bản nháp
bài đang làm. Các bài khách vẫn gửi tới backend local để chấm điểm.
Giám sát học viên/đồng bộ giữa nhiều máy cần cùng backend HTTPS; gói này
chạy backend trên máy Windows, chưa triển khai máy chủ Internet dùng chung.

HỌC NGOẠI TUYẾN
Trang chủ/Cá nhân có Học trên thiết bị: đọc bài, luyện và lưu điểm từ dữ liệu
đóng gói mà không gọi máy chủ. Lịch sử tự luyện được giữ riêng, không tự gửi
cho giáo viên hoặc chuyển thành điểm giám sát. Tài khoản/nhóm vẫn cần máy chủ.
Đáp án có trong gói phục vụ tự học; đề giám sát cần ngân hàng riêng nếu phải
giữ bí mật đáp án. Xem docs/OFFLINE_STUDY.md.

OCR MIỄN PHÍ
Cá nhân > Nhận chữ từ ảnh: chọn ảnh chữ in tiếng Việt/Anh, kiểm tra và sửa,
đánh dấu đã kiểm tra rồi sao chép. Câu trả lời dạng gõ có Nhập từ ảnh hoặc
văn bản; nhận chữ không tự nộp bài. Web/Windows dùng Tesseract kèm gói,
ảnh không tải lên backend. Android/iOS dùng ML Kit chạy trên thiết bị,
SDK có dữ liệu chẩn đoán cần khai quyền riêng tư. Bản .18 đã gỡ trợ lý AI
trả phí, không yêu cầu khóa API và không gọi dịch vụ AI. Xem docs/OCR.md.

PHẠM VI BẢN THỬ
7.886 câu đang hoạt động, 1.461 đề làm trực tiếp; 733 hướng dẫn Toán 1–12.
Nội dung tự biên soạn hướng tới Kết nối tri thức, chưa thẩm định độc lập
hoặc bảo đảm phủ đủ mọi môn/trang/ấn bản. Đề gắn thẻ nguồn dùng câu tự soạn;
525 nguồn còn là tham khảo, chưa sao chép nguyên đề PDF. Liên kết Internet
cần mạng. Bản Windows không phải gói Android/iOS hay bản đã duyệt Google Play.
Runtime/batch Windows chưa nghiệm thu trên máy Windows vật lý.
"""
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
