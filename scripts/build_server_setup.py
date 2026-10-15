"""Package a Windows maintenance kit from authored public fixtures, never live state."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
METADATA = (
    "textbook_units.json",
    "source_practice_map.json",
    "exams.json",
    "language_exams.json",
    "curriculum_exams.json",
    "subject_exams.json",
)


def sha256(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def build(output):
    output = Path(output).resolve()
    report = output.with_suffix(".manifest.json")
    checksum = Path(str(output) + ".sha256")
    if any(p.exists() or p.is_symlink() for p in (output, report, checksum)):
        raise ValueError("Refusing to overwrite an existing kit or manifest")
    with tempfile.TemporaryDirectory(prefix="tuhoc-server-kit-") as directory:
        temporary = Path(directory)
        stage = temporary / "kit"
        stage.mkdir()
        content = stage / "content/published-content.json"
        content.parent.mkdir()
        source = temporary / "authored-preview.sqlite"
        environment = os.environ.copy()
        for name in ("KHOHOC_MANAGER_CREDENTIALS_FILE", "KHOHOC_DATABASE_PASSWORD_FILE"):
            environment.pop(name, None)
        environment.update(
            PYTHONPATH=str(ROOT / "services/api"),
            KHOHOC_MODE="development",
            KHOHOC_DATABASE_URL="sqlite:///" + str(source),
        )
        # Only this throwaway database is ever opened. The publication procedure
        # is the existing authored-preview workflow, not an export of live users.
        command = """
import json, sys
from khohoc.phone_preview import create_preview
from khohoc.content_transfer import export_published_content
app = create_preview()
app.state.engine.dispose()
summary = export_published_content(sys.argv[1], sys.argv[2])
assert summary['counts'] == {'questions': 7886, 'exams': 1461, 'documents': 2866}
print(json.dumps(summary, ensure_ascii=False))
"""
        result = subprocess.run(
            [sys.executable, "-c", command, str(source), str(content)],
            cwd=ROOT,
            env=environment,
            check=True,
            capture_output=True,
            text=True,
        )
        content_summary = json.loads(result.stdout.strip().splitlines()[-1])

        def copy(relative):
            destination = stage / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, destination)

        for path in sorted((ROOT / "services/api/khohoc").rglob("*.py")):
            copy(path.relative_to(ROOT))
        for name in ("requirements.txt", "requirements.lock.txt"):
            copy(Path("services/api") / name)
        for name in METADATA:
            copy(Path("data/seeds") / name)
        for path in sorted((ROOT / "data/library/files").glob("*.pdf")):
            copy(path.relative_to(ROOT))
        for name in (
            "scripts/prepare_free_server.py",
            "prepare-free-server.bat",
            "docs/FREE_HOSTING.md",
            "docs/CONTENT_TRANSFER.md",
        ):
            copy(Path(name))

        digest = content_summary["archive_sha256"]
        for name, apply in (("1-KIEM-TRA.bat", False), ("2-KHOI-TAO.bat", True)):
            arguments = " --apply" if apply else ""
            launcher = (
                '@echo off\nsetlocal\ncd /d "%~dp0"\n'
                'call prepare-free-server.bat --content-archive '
                '"%~dp0content\\published-content.json" '
                f'--content-sha256 {digest}{arguments} %*\n'
                'set "SETUP_RESULT=%errorlevel%"\n'
                'echo.\npause\nexit /b %SETUP_RESULT%\n'
            )
            (stage / name).write_bytes(launcher.replace("\n", "\r\n").encode())
        instructions = """TỰ HỌC 111 — CHUẨN BỊ MÁY CHỦ THỬ MIỄN PHÍ

1. Giải nén toàn bộ ZIP ra một thư mục trên máy Windows của bạn.
2. Cần Python 3.12: https://www.python.org/downloads/
   Chọn Add Python to PATH khi cài. Công cụ cài các thư viện đã khóa phiên bản.
3. Tạo Neon Free, PostgreSQL 17, AWS Singapore. Giữ chuỗi kết nối DIRECT
   của chủ database riêng tư. Không gửi mật khẩu/chuỗi kết nối qua chat.
4. Mở 1-KIEM-TRA.bat. Dán chuỗi kết nối khi công cụ hỏi ẩn; bước này chỉ
   kiểm tra, không tạo bảng/tài khoản hoặc ghi dữ liệu.
5. Sau khi xem kết quả kiểm tra, mở 2-KHOI-TAO.bat để tạo hệ thống mới.
   Công cụ yêu cầu đích mới, không ghi đè role/cấu hình/tài khoản cũ.
   Tệp cấu hình Render và tài khoản quản lý được lưu trong thư mục riêng.
   Không gửi thư mục state, tệp tài khoản hoặc tệp cấu hình lên Git/chat.
6. Làm theo docs/FREE_HOSTING.md để tạo Render Free từ nhánh được ghi rõ
   trong hướng dẫn. Chỉ nhập URL database của role API vào cấu hình Render;
   URL chủ database chỉ dùng ở máy vận hành. Sao chép địa chỉ HTTPS Render
   vào Cá nhân → Cài đặt → Máy chủ trong app, rồi đăng nhập tài khoản quản lý.

Render Free có thời gian ngủ/khởi động và hạn mức; Neon Free có hạn mức
lưu trữ/tính toán. Chọn gói Free; công cụ không tạo tài khoản nhà cung cấp,
không thanh toán hoặc nâng cấp gói. Cần sao lưu riêng dữ liệu thực tế.

Gói chỉ có mã công cụ và nội dung công khai đã có trong bản thử:
7.886 câu, 1.461 đề, 2.866 mục tài liệu/nguồn. Không có tài khoản, phiên,
bài làm, kết quả, database học viên hoặc khóa ký. JSON có đáp án tự luyện;
không dùng như ngân hàng đề bí mật. Các liên kết/PDF bên ngoài không được
sao chép toàn bộ. Nội dung chưa được thẩm định chuyên môn toàn bộ.
"""
        (stage / "DOC-TRUOC.txt").write_text(instructions, encoding="utf-8-sig")
        manifest = {
            "kind": "tuhoc111.free-server-setup",
            "version": "2026.10.15.20",
            "content": content_summary,
            "contains_learner_data": False,
            "files": {
                str(path.relative_to(stage)).replace(os.sep, "/"): sha256(path)
                for path in sorted(stage.rglob("*"))
                if path.is_file()
            },
        }
        (stage / "MANIFEST.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        output.parent.mkdir(parents=True, exist_ok=True)
        with ZipFile(output, "x", compression=ZIP_DEFLATED, compresslevel=9) as archive:
            for path in sorted(stage.rglob("*")):
                if path.is_file():
                    archive.write(path, str(path.relative_to(stage)))
        with ZipFile(output) as archive:
            if archive.testzip() is not None:
                raise RuntimeError("Kit ZIP CRC verification failed")
        manifest["zip_sha256"] = sha256(output)
        manifest["zip_bytes"] = output.stat().st_size
        report.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
        checksum.write_text(manifest["zip_sha256"] + "  " + output.name + "\n")
        return {k: v for k, v in manifest.items() if k != "files"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(build(args.output), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
