"""Pinned official Android tools; SHA1 is from Google's HTTPS repository manifest."""

import hashlib
import os
from pathlib import Path
import subprocess
import tempfile
from urllib.parse import urlparse
from urllib.request import urlretrieve
import zipfile

sdk = Path("/workspace/android-sdk")
tools = sdk / "cmdline-tools/19.0"
if not tools.exists():
    with tempfile.TemporaryDirectory(dir="/workspace/scratch") as temp:
        archive = Path(temp) / "tools.zip"
        urlretrieve(
            "https://dl.google.com/android/repository/commandlinetools-linux-13114758_latest.zip",
            archive,
        )
        if (
            hashlib.sha1(archive.read_bytes()).hexdigest()
            != "5fdcc763663eefb86a5b8879697aa6088b041e70"
        ):
            raise SystemExit("Official Android tools checksum mismatch")
        with zipfile.ZipFile(archive) as z:
            z.extractall(temp)
        tools.parent.mkdir(parents=True, exist_ok=True)
        (Path(temp) / "cmdline-tools").rename(tools)
        for f in (tools / "bin").iterdir():
            f.chmod(0o755)
env = os.environ.copy()
env["ANDROID_USER_HOME"] = "/workspace/cache/android"
env["JAVA_OPTS"] = "-Djava.util.prefs.userRoot=/workspace/cache/java"
trust_store = Path("/etc/ssl/certs/java/cacerts")
if trust_store.exists():
    env["JAVA_OPTS"] += " -Djavax.net.ssl.trustStore=" + str(trust_store)
command = [
    str(tools / "bin/sdkmanager"),
    "--sdk_root=" + str(sdk),
    "--install",
    "platform-tools",
    "platforms;android-36",
    "build-tools;35.0.0",
    "ndk;27.0.12077973",
]
proxy = urlparse(os.environ.get("HTTPS_PROXY", ""))
if proxy.hostname:
    command += [
        "--proxy=http",
        "--proxy_host=" + proxy.hostname,
        "--proxy_port=" + str(proxy.port or 80),
    ]
subprocess.run(command, input="y\n" * 100, text=True, env=env, check=True)
