"""Validate concrete store prerequisites without reading/printing signing secrets."""

import argparse
import json
import subprocess
from pathlib import Path
from urllib.parse import urlsplit
import ipaddress

ROOT = Path(__file__).resolve().parents[1]


def secure_public_url(value):
    u = urlsplit(value)
    if (
        u.scheme != "https"
        or not u.hostname
        or u.username
        or u.password
        or u.query
        or u.fragment
    ):
        raise ValueError(
            "Backend phải là URL HTTPS công khai, không chứa tài khoản/query/fragment."
        )
    host = u.hostname.lower()
    if host in {"localhost", "backend.invalid"} or host.endswith(
        (".localhost", ".invalid", ".test", ".local")
    ):
        raise ValueError("Không dùng địa chỉ local hoặc minh họa để phát hành.")
    try:
        if not ipaddress.ip_address(host).is_global:
            raise ValueError("Backend không được là IP nội bộ.")
    except ValueError as e:
        if "Backend" in str(e):
            raise
        if "." not in host:
            raise ValueError("Backend cần tên miền công khai.") from None
    return value.rstrip("/")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--platform", choices=["android", "ios"], required=True)
    parser.add_argument("--api-base-url", required=True)
    parser.add_argument("--publisher-config", type=Path, required=True)
    parser.add_argument("--build", action="store_true")
    args = parser.parse_args()
    api = secure_public_url(args.api_base_url)
    config = json.loads(args.publisher_config.read_text())
    for name in [
        "publisher_name",
        "support_email",
        "privacy_policy_url",
        "account_deletion_url",
    ]:
        value = config.get(name, "").strip()
        if not value or "CHUA_" in value:
            raise ValueError("Chưa thiết lập " + name)
        if name.endswith("_url"):
            secure_public_url(value)
    if not config.get("content_review_complete") or not config.get(
        "child_privacy_review_complete"
    ):
        raise ValueError(
            "Cần hoàn tất thẩm định nội dung và dữ liệu trẻ em trước phát hành."
        )
    import urllib.request

    with urllib.request.urlopen(api + "/health", timeout=15) as response:
        health = json.load(response)
        if health.get("status") != "ok":
            raise ValueError("Backend health chưa đạt.")
        if health.get("mode") != "production":
            raise ValueError("Backend vẫn là development; chưa được đưa lên cửa hàng.")
    if args.platform == "android":
        if not (ROOT / "apps/mobile/android/key.properties").is_file():
            raise ValueError(
                "Chưa thiết lập Android upload signing ở key.properties riêng tư."
            )
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
    print(
        "Prerequisites checked; store account verification, device testing and store review remain external steps."
    )
    if args.build:
        subprocess.run(command, cwd=ROOT / "apps/mobile", check=True)


if __name__ == "__main__":
    main()
