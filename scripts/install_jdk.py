"""Install pinned Temurin 21 from the official release with its SHA-256."""

import hashlib
from pathlib import Path
import tarfile
import tempfile
from urllib.request import urlretrieve

jdk_root = Path("/workspace/toolchains/jdk-21")
expected = "ce79869e1307ed8ee1e2baa86a412b1eb5b75d10a01006d788a6f968bcfaee94"
if not (jdk_root / "bin/javac").exists():
    with tempfile.TemporaryDirectory(dir="/workspace/scratch") as directory:
        archive = Path(directory) / "jdk.tar.gz"
        urlretrieve(
            "https://github.com/adoptium/temurin21-binaries/releases/download/jdk-21.0.12.1%2B1/OpenJDK21U-jdk_x64_linux_hotspot_21.0.12.1_1.tar.gz",
            archive,
        )
        if hashlib.sha256(archive.read_bytes()).hexdigest() != expected:
            raise SystemExit("Official Temurin checksum mismatch")
        with tarfile.open(archive) as bundle:
            bundle.extractall(directory, filter="data")
        next(Path(directory).glob("jdk-*")).rename(jdk_root)
