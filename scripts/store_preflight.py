"""Check store prerequisites, or build an explicitly unsigned engineering AAB.

Engineering checks do not approve a store submission or contact a backend.
Signing passwords and key material are never printed or put in the report.
"""

import argparse
import hashlib
import ipaddress
import json
import os
from pathlib import Path
import re
import socket
import struct
import subprocess
import sys
from urllib.parse import urlsplit
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
ENGINEERING_API = "https://backend.invalid/api"


def secure_public_url(value):
    if not isinstance(value, str) or re.search(r"[\s\x00-\x1f\x7f\\]", value):
        raise ValueError(
            "URL HTTPS không được chứa khoảng trắng hoặc ký tự điều khiển."
        )
    try:
        u = urlsplit(value)
        host = (u.hostname or "").lower().rstrip(".")
        port = u.port
    except ValueError:
        raise ValueError("URL HTTPS không hợp lệ.") from None
    if (
        u.scheme != "https"
        or not host
        or u.username
        or u.password
        or u.query
        or u.fragment
        or port == 0
    ):
        raise ValueError(
            "Cần URL HTTPS công khai, không chứa tài khoản/query/fragment."
        )
    if (
        host == "localhost"
        or host.endswith((".localhost", ".invalid", ".test", ".local", ".example"))
        or any(
            host == d or host.endswith("." + d)
            for d in ("example.com", "example.net", "example.org")
        )
    ):
        raise ValueError("Không dùng địa chỉ local hoặc minh họa để phát hành.")
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        try:
            labels = host.encode("idna").decode("ascii").split(".")
        except UnicodeError:
            raise ValueError("Tên miền không hợp lệ.") from None
        if (
            len(labels) < 2
            or len(host) > 253
            or not all(
                re.fullmatch(r"[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?", label)
                for label in labels
            )
        ):
            raise ValueError("Cần tên miền công khai hợp lệ.")
    else:
        if not address.is_global:
            raise ValueError("URL không được là IP nội bộ.")
    if any(part in {".", ".."} for part in u.path.split("/")):
        raise ValueError("Đường dẫn URL không hợp lệ.")
    return value.rstrip("/")


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError(
            "Endpoint phải trả lời trực tiếp qua HTTPS, không chuyển hướng."
        )


def check_endpoint(url, *, json_response=False):
    """Use normal TLS/proxy trust, reject private DNS answers and redirects."""
    secure_public_url(url)
    host = urlsplit(url).hostname
    addresses = socket.getaddrinfo(
        host, urlsplit(url).port or 443, type=socket.SOCK_STREAM
    )
    if not addresses or any(
        not ipaddress.ip_address(a[4][0]).is_global for a in addresses
    ):
        raise ValueError("DNS của endpoint phải trỏ hoàn toàn tới địa chỉ công khai.")
    request = urllib.request.Request(
        url, headers={"User-Agent": "TuHoc111-store-preflight"}
    )
    with urllib.request.build_opener(NoRedirect()).open(
        request, timeout=15
    ) as response:
        if response.status != 200:
            raise ValueError("Endpoint chưa trả HTTP 200.")
        content_type = response.headers.get_content_type()
        if json_response:
            if content_type != "application/json":
                raise ValueError("Backend probe phải trả JSON.")
            payload = response.read(65_537)
            if len(payload) > 65_536:
                raise ValueError("Phản hồi backend probe vượt giới hạn.")
            result = json.loads(payload)
            if not isinstance(result, dict):
                raise ValueError("Phản hồi backend probe không hợp lệ.")
            return result
        if (
            content_type not in {"text/html", "text/plain"}
            or not response.read(4096).strip()
        ):
            raise ValueError(
                "Trang chính sách/xóa tài khoản phải có nội dung đọc được."
            )
    return None


def validate_publisher(config):
    if not isinstance(config, dict):
        raise ValueError("Metadata nhà phát hành phải là JSON object.")
    for name in (
        "publisher_name",
        "support_email",
        "privacy_policy_url",
        "account_deletion_url",
    ):
        value = config.get(name)
        if not isinstance(value, str) or not value.strip() or "CHUA_" in value:
            raise ValueError("Chưa thiết lập " + name)
        if value != value.strip() or re.search(r"[\x00-\x1f\x7f]", value):
            raise ValueError("Giá trị metadata không hợp lệ: " + name)
        if name.endswith("_url"):
            secure_public_url(value)
    email = config["support_email"]
    if not re.fullmatch(r"[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+", email):
        raise ValueError("Email hỗ trợ không hợp lệ.")
    secure_public_url("https://" + email.rsplit("@", 1)[1])
    for name in (
        "content_review_complete",
        "child_privacy_review_complete",
        "data_safety_review_complete",
        "device_testing_complete",
        "store_account_verified",
    ):
        if config.get(name) is not True:
            raise ValueError("Cần xác nhận đã hoàn tất " + name)


def _protobuf_fields(data):
    """Read the few wire fields needed from public BundleConfig (no protobuf dependency)."""

    def varint(position):
        result = 0
        for shift in range(0, 70, 7):
            if position >= len(data):
                break
            byte = data[position]
            position += 1
            result |= (byte & 127) << shift
            if byte < 128:
                return result, position
        raise ValueError("BundleConfig protobuf không hợp lệ.")

    position = 0
    result = {}
    while position < len(data):
        tag, position = varint(position)
        number, wire = tag >> 3, tag & 7
        if number == 0:
            raise ValueError("BundleConfig protobuf không hợp lệ.")
        if wire == 0:
            value, position = varint(position)
        elif wire in {1, 2, 5}:
            size, position = (
                varint(position) if wire == 2 else (8 if wire == 1 else 4, position)
            )
            if position + size > len(data):
                raise ValueError("BundleConfig protobuf bị cắt ngắn.")
            value = data[position : position + size]
            position += size
        else:
            raise ValueError("BundleConfig protobuf có wire type không hỗ trợ.")
        result[number] = value
    return result


def _elf_alignment(data):
    if len(data) < 64 or data[:4] != b"\x7fELF" or data[4] != 2 or data[5] != 1:
        raise ValueError("Thư viện native 64-bit không phải ELF little-endian hợp lệ.")
    offset = struct.unpack_from("<Q", data, 32)[0]
    entry_size, count = struct.unpack_from("<HH", data, 54)
    if entry_size < 56 or not count or offset + entry_size * count > len(data):
        raise ValueError("Bảng ELF program header không hợp lệ.")
    alignments = []
    for index in range(count):
        start = offset + index * entry_size
        kind = struct.unpack_from("<I", data, start)[0]
        if kind == 1:  # PT_LOAD
            file_offset, virtual_address = struct.unpack_from("<QQ", data, start + 8)
            alignment = struct.unpack_from("<Q", data, start + 48)[0]
            if (
                alignment < 16_384
                or alignment & (alignment - 1)
                or (file_offset - virtual_address) % 16_384
            ):
                raise ValueError("ELF PT_LOAD chưa hỗ trợ page size 16 KB.")
            alignments.append(alignment)
    if not alignments:
        raise ValueError("ELF không có PT_LOAD.")
    return min(alignments)


def inspect_android_bundle(path, *, require_unsigned=False):
    """Check the AAB's 64-bit ELF and generated-APK page alignment, not device behavior.

    BundleConfig fields follow google/bundletool src/main/proto/config.proto:
    BundleConfig.optimizations=2, UncompressNativeLibraries=2, alignment=2 (16K=2).
    """
    path = Path(path)
    libraries = []
    with zipfile.ZipFile(path) as bundle:
        names = bundle.namelist()
        if len(names) != len(set(names)) or "BundleConfig.pb" not in names:
            raise ValueError("AAB không hợp lệ hoặc có entry trùng.")
        signed = any(
            re.fullmatch(r"META-INF/[^/]+\.(?:RSA|DSA|EC|SF)", n, re.I) for n in names
        )
        if require_unsigned and signed:
            raise ValueError(
                "Engineering AAB phải không ký; phát hiện chữ ký trong gói."
            )
        config_entry = bundle.getinfo("BundleConfig.pb")
        if config_entry.file_size > 65_536:
            raise ValueError("BundleConfig quá lớn.")
        config = _protobuf_fields(bundle.read(config_entry))
        optimizations = _protobuf_fields(config.get(2, b""))
        native = _protobuf_fields(optimizations.get(2, b""))
        alignment = native.get(2, 0)
        if native.get(1) == 1 and alignment not in {2, 3}:
            raise ValueError("AAB chưa yêu cầu căn ZIP 16 KB cho thư viện không nén.")
        for entry in bundle.infolist():
            if re.fullmatch(
                r"[^/]+/lib/(?:arm64-v8a|x86_64)/[^/]+\.so", entry.filename
            ):
                if entry.file_size > 200 * 1024 * 1024:
                    raise ValueError("Thư viện native vượt giới hạn kiểm tra.")
                try:
                    minimum = _elf_alignment(bundle.read(entry))
                except ValueError as error:
                    raise ValueError(entry.filename + ": " + str(error)) from None
                libraries.append(
                    {"path": entry.filename, "minimum_load_alignment": minimum}
                )
    if not libraries:
        raise ValueError("AAB không có thư viện 64-bit để kiểm tra.")
    with path.open("rb") as source:
        digest = hashlib.file_digest(source, "sha256").hexdigest()
    return {
        "artifact": str(path.resolve()),
        "size_bytes": path.stat().st_size,
        "sha256": digest,
        "signed": signed,
        "signature_verified": False,
        "signature_check": "ZIP signature markers only; cryptographic verification remains required",
        "page_size_check": "16 KB ELF and bundle packaging passed",
        "bundle_native_libraries_uncompressed": native.get(1) == 1,
        "bundle_page_alignment": {2: 16_384, 3: 65_536}.get(alignment),
        "native_libraries": libraries,
        "device_16kb_runtime_tested": False,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--platform", choices=["android", "ios"], required=True)
    parser.add_argument("--api-base-url")
    parser.add_argument("--publisher-config", type=Path)
    parser.add_argument(
        "--engineering",
        action="store_true",
        help="Android unsigned only; never approves store submission",
    )
    parser.add_argument(
        "--inspect-aab",
        type=Path,
        help="Check a previously built Android AAB without rebuilding",
    )
    parser.add_argument(
        "--report", type=Path, help="Write a non-secret JSON readiness/artifact report"
    )
    parser.add_argument("--build", action="store_true")
    args = parser.parse_args(argv)
    if args.engineering and args.platform != "android":
        parser.error("--engineering chỉ hỗ trợ Android; iOS dùng workflow macOS riêng.")
    if args.inspect_aab and (args.platform != "android" or args.build):
        parser.error("--inspect-aab chỉ dùng Android và không dùng cùng --build.")
    report = {
        "platform": args.platform,
        "engineering": args.engineering,
        "store_ready": False,
    }
    api = args.api_base_url or (ENGINEERING_API if args.engineering else None)
    if not api:
        parser.error("Bản phát hành cần --api-base-url HTTPS thật.")
    if args.engineering:
        if api != ENGINEERING_API:
            secure_public_url(api)
        report["remaining"] = [
            "Chưa xác minh tài khoản Play Console, backend HTTPS production hoặc ký upload.",
            "Còn thẩm định nội dung, dữ liệu trẻ em/Data Safety và thử nghiệm thiết bị/cửa hàng.",
            "AAB engineering không được tải lên Google Play.",
        ]
    else:
        secure_public_url(api)
        if not args.publisher_config:
            parser.error("Bản phát hành cần --publisher-config đã hoàn tất.")
        config = json.loads(args.publisher_config.read_text(encoding="utf-8"))
        validate_publisher(config)
        for field in ("privacy_policy_url", "account_deletion_url"):
            check_endpoint(config[field])
        for endpoint in ("health", "ready"):
            health = check_endpoint(api + "/" + endpoint, json_response=True)
            if health.get("status") != "ok" or health.get("mode") != "production":
                raise ValueError("Backend " + endpoint + " chưa đạt chế độ production.")
        if (
            args.platform == "android"
            and not (ROOT / "apps/mobile/android/key.properties").is_file()
        ):
            raise ValueError(
                "Chưa thiết lập Android upload signing ở key.properties riêng tư."
            )
        report["prerequisites_checked"] = True
        report["remaining"] = [
            "Còn xác minh gói đã ký, thử nghiệm nội bộ/kín và xét duyệt của cửa hàng."
        ]
    if args.platform == "android":
        command = [
            "flutter",
            "build",
            "appbundle",
            "--release",
            "--dart-define=API_BASE_URL=" + api,
        ]
    else:
        import platform

        if platform.system() != "Darwin":
            raise ValueError("Build iOS archive cần macOS và Xcode.")
        command = [
            "flutter",
            "build",
            "ipa",
            "--release",
            "--dart-define=API_BASE_URL=" + api,
        ]
    if args.build:
        environment = os.environ.copy()
        environment["ORG_GRADLE_PROJECT_tuhocEngineering"] = str(
            args.engineering
        ).lower()
        environment["ORG_GRADLE_PROJECT_tuhocRequireUploadSigning"] = str(
            not args.engineering
        ).lower()
        # Enforce the reviewed dependency lock first. Do not use --no-pub on
        # the build: Flutter 3.35.7 must regenerate the release registrant to
        # exclude dev-only plugins left behind by debug/integration builds.
        subprocess.run(
            ["flutter", "pub", "get", "--enforce-lockfile"],
            cwd=ROOT / "apps/mobile",
            env=environment,
            check=True,
        )
        subprocess.run(command, cwd=ROOT / "apps/mobile", env=environment, check=True)
    artifact = args.inspect_aab
    if args.platform == "android" and args.build:
        artifact = ROOT / "apps/mobile/build/app/outputs/bundle/release/app-release.aab"
    if artifact:
        report["bundle"] = inspect_android_bundle(
            artifact, require_unsigned=args.engineering
        )
        if not args.engineering and not report["bundle"]["signed"]:
            raise ValueError("Bản phát hành chưa có chữ ký upload.")
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (
        ValueError,
        OSError,
        subprocess.CalledProcessError,
        zipfile.BadZipFile,
    ) as error:
        # Do not include a response body, config contents or signing material in errors.
        print("Preflight không đạt: " + str(error), file=sys.stderr)
        sys.exit(1)
