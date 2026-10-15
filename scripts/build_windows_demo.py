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
    staging = artifacts / "kho-hoc-demo-windows"
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
        "start-demo.bat",
        "start-demo.sh",
        "LICENSE",
        "data/library/documents.json",
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
    guide = """KHO HỌC 1–12 — DEMO LOCAL WINDOWS 64-BIT\n\n1. Giải nén toàn bộ ZIP (Extract All), không chạy trực tiếp trong ZIP.\n2. Mở thư mục vừa giải nén, nhấp đúp start-demo.bat.\n3. Giữ cửa sổ đó mở; đợi dòng DEMO READY. Trình duyệt sẽ tự mở http://localhost:8080.\n\nĐã kèm Python 3.12.10 chính thức của Python Software Foundation và thư viện Windows đã khóa phiên bản. Không cần cài Python, Flutter, Node hoặc Supabase. Lần đầu chuẩn bị môi trường có thể mất vài phút; các lần sau nhanh hơn. Không tải thư viện từ Internet khi khởi động trên Windows.\n\nThử: chọn lớp/môn, làm và nộp đề; vào Tài liệu đọc ghi chú/mở PDF; xem Tiến độ/Lịch sử. Có108 câu/12 đề và4 tài liệu tự biên soạn.\n\nĐể dừng, quay lại cửa sổ khởi động và nhấn Ctrl+C. Dữ liệu bài làm lưu trong state/demo.sqlite và trong trình duyệt trên máy này. Không chạy admin/Supabase/AI/OCR.\n\nNếu cổng đã được chương trình khác sử dụng, launcher sẽ thông báo. Có thể mở CMD trong thư mục gói và chạy: start-demo.bat --api-port8011 --port8091 (thêm khoảng trắng: --api-port 8011 --port 8091).\n\nNếu có lỗi, giữ nội dung lỗi trong cửa sổ; log ở state/api.log và state/demo.log. Không xóa dữ liệu state khi muốn giữ bài làm.\n\nGói Windows dùng runtime/wheel Windows64-bit; không dùng Python Windows trong gói này trên macOS/Linux. Backend và giao diện đã kiểm tra trên môi trường Linux; file.bat/runtime Windows chưa chạy trên máy Windows thực tế. Đây là bản thử, chưa phát hành Google Play hoặc nội dung được thẩm định chuyên môn.\n"""
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
    document_count = len(
        json.loads((ROOT / "data/library/documents.json").read_text(encoding="utf-8"))[
            "documents"
        ]
    )
    guide = guide.replace(
        "Có 108 câu/12 đề và 4 tài liệu",
        f"Có {question_count} câu/{exam_count} đề và {document_count} tài liệu",
    )
    guide += "\nDữ liệu mở rộng hướng tới Kết nối tri thức: 720 biến thể Toán từ 72 dạng; các môn khác có bộ ôn kiến thức nền, một số câu dùng lại giữa các lớp. Chưa đối chiếu từng bài/ấn bản SGK hiện hành.\n"
    (staging / "HUONG-DAN.txt").write_text(guide, encoding="utf-8-sig")
    for bat in [staging / "start-demo.bat"]:
        content = (
            bat.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\n", "\r\n")
        )
        bat.write_bytes(content.encode("utf-8"))
    output = artifacts / "kho-hoc-demo-windows.zip"
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
    (artifacts / "kho-hoc-demo-windows.zip.sha256").write_text(
        digest + "  " + output.name + "\n"
    )
    print(
        f"Built {output}: {output.stat().st_size:,} bytes; Windows wheel dependency closure verified"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifacts", type=Path, default=Path("/workspace/artifacts"))
    build(parser.parse_args().artifacts)
