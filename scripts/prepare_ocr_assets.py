#!/usr/bin/env python3
"""Reproduce the offline browser OCR assets from SHA512-pinned npm tarballs.

No npm lifecycle scripts run. Only explicitly listed regular tar members are read.
Use --verify to check the checked-in SHA256 manifest without any network access.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import io
import json
from pathlib import Path
import tarfile
import urllib.request


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "apps/mobile/web/ocr"
PACKAGES = [
    {
        "name": "tesseract.js",
        "version": "6.0.1",
        "tarball": "https://registry.npmjs.org/tesseract.js/-/tesseract.js-6.0.1.tgz",
        "integrity": "sha512-/sPvMvrCtgxnNRCjbTYbr7BRu0yfWDsMZQ2a/T5aN/L1t8wUQN6tTWv6p6FwzpoEBA0jrN2UD2SX4QQFRdoDbA==",
        "license": "Apache-2.0",
        "members": {
            "package/dist/worker.min.js": "vendor/worker.min.js",
            "package/dist/worker.min.js.LICENSE.txt": "licenses/worker.min.js.LICENSE.txt",
            "package/LICENSE.md": "licenses/TESSERACT-JS-LICENSE.md",
        },
    },
    {
        "name": "tesseract.js-core",
        "version": "6.1.2",
        "tarball": "https://registry.npmjs.org/tesseract.js-core/-/tesseract.js-core-6.1.2.tgz",
        "integrity": "sha512-pv4GjmramjdObhDyR1q85Td8X60Puu/lGQn7Kw2id05LLgHhAcWgnz6xSdMCSxBMWjQDmMyDXPTC2aqADdpiow==",
        "license": "Apache-2.0",
        "members": {
            "package/tesseract-core-lstm.wasm.js": "vendor/tesseract-core-lstm.wasm.js",
            "package/tesseract-core-simd-lstm.wasm.js": "vendor/tesseract-core-simd-lstm.wasm.js",
            "package/LICENSE": "licenses/TESSERACT-CORE-LICENSE.txt",
        },
    },
    {
        "name": "@tesseract.js-data/vie",
        "version": "1.0.0",
        "tarball": "https://registry.npmjs.org/@tesseract.js-data/vie/-/vie-1.0.0.tgz",
        "integrity": "sha512-hFxBtxSiCw6+64uxf0psrlLvcYA5kQimYhTSx1RwjbD5jSxe1bWg3EmipAozkzELQIFAMkJC5vu+ONGRem7YLA==",
        "license": "MIT (npm metadata); traineddata repository Apache-2.0",
        "members": {
            "package/4.0.0_best_int/vie.traineddata.gz": "lang/vie.traineddata.gz",
            "package/package.json": "licenses/vie-package.json",
        },
    },
    {
        "name": "@tesseract.js-data/eng",
        "version": "1.0.0",
        "tarball": "https://registry.npmjs.org/@tesseract.js-data/eng/-/eng-1.0.0.tgz",
        "integrity": "sha512-mbTumm6KQPUHyzTPQaF3ObXYnx0SqqfV2nabqFVQBwD6Kl7PhGSLSzOlfFTWy0P3BjghaSKA2W9GB19Jk+ZcTg==",
        "license": "MIT (npm metadata); traineddata repository Apache-2.0",
        "members": {
            "package/4.0.0_best_int/eng.traineddata.gz": "lang/eng.traineddata.gz",
            "package/package.json": "licenses/eng-package.json",
        },
    },
]
TESSDATA_LICENSE_URL = (
    "https://api.github.com/repos/naptha/tessdata/git/blobs/"
    "261eeb9e9f8b2b4b0d119366dda99c6fd7d35c64"
)
TESSDATA_LICENSE_BLOB = "261eeb9e9f8b2b4b0d119366dda99c6fd7d35c64"


def download(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=90) as response:
        data = response.read(40 * 1024 * 1024 + 1)
    if len(data) > 40 * 1024 * 1024:
        raise ValueError("Upstream package exceeds download limit")
    return data


def prepare() -> None:
    for package in PACKAGES:
        data = download(package["tarball"])
        actual = "sha512-" + base64.b64encode(hashlib.sha512(data).digest()).decode()
        if actual != package["integrity"]:
            raise ValueError(f"Integrity mismatch: {package['name']}")
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
            for member, destination in package["members"].items():
                info = archive.getmember(member)
                if not info.isfile() or info.size > 8 * 1024 * 1024:
                    raise ValueError("Unexpected tar member")
                target = ASSETS / destination
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(archive.extractfile(info).read())
    license_json = json.loads(download(TESSDATA_LICENSE_URL))
    license_bytes = base64.b64decode(license_json["content"])
    git_blob = b"blob " + str(len(license_bytes)).encode() + b"\0" + license_bytes
    if hashlib.sha1(git_blob).hexdigest() != TESSDATA_LICENSE_BLOB:
        raise ValueError("Tessdata license Git blob mismatch")
    (ASSETS / "licenses/TESSDATA-LICENSE.txt").write_bytes(license_bytes)
    provenance = {
        "schema_version": 1,
        "packages": PACKAGES,
        "tessdata_license": {
            "url": TESSDATA_LICENSE_URL,
            "git_blob_sha1": TESSDATA_LICENSE_BLOB,
        },
        "notes": [
            "Official npm tarball SHA512 SRI verified before extracting named members.",
            "Upstream JavaScript and traineddata are unmodified.",
            "LSTM wasm.js files embed WASM; separate .wasm files are unnecessary.",
            "No upstream source maps are needed at runtime.",
            "Tessdata npm metadata says MIT; upstream repository supplies Apache-2.0 license, retained here.",
        ],
    }
    (ASSETS / "PROVENANCE.json").write_text(
        json.dumps(provenance, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    members = [
        path for path in ASSETS.rglob("*") if path.is_file() and path.name != "SHA256SUMS"
    ]
    (ASSETS / "SHA256SUMS").write_text(
        "".join(
            f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.relative_to(ASSETS).as_posix()}\n"
            for path in sorted(members)
        ),
        encoding="ascii",
    )
    verify()


def verify() -> None:
    manifest = ASSETS / "SHA256SUMS"
    expected = set()
    for line in manifest.read_text(encoding="ascii").splitlines():
        digest, relative = line.split("  ", 1)
        path = ASSETS / relative
        if path.resolve().parent != ASSETS and ASSETS not in path.resolve().parents:
            raise ValueError("Unsafe manifest path")
        if path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError(f"Asset SHA256 mismatch: {relative}")
        expected.add(relative)
    actual = {
        path.relative_to(ASSETS).as_posix()
        for path in ASSETS.rglob("*")
        if path.is_file() and path.name != "SHA256SUMS"
    }
    if actual != expected:
        raise ValueError("Asset manifest file set differs")
    print(f"Verified {len(expected)} local OCR files; no network needed for --verify.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", action="store_true")
    arguments = parser.parse_args()
    verify() if arguments.verify else prepare()
