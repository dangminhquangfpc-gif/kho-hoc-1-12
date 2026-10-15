"""Route Java/Gradle through the existing platform proxy without extracting credentials."""

import os
from pathlib import Path
from urllib.parse import urlparse

proxy = urlparse(os.environ.get("HTTPS_PROXY", ""))
path = Path("/workspace/cache/gradle/gradle.properties")
if path.exists():
    content = path.read_text()
else:
    content = (
        "org.gradle.workers.max=2\norg.gradle.parallel=false\norg.gradle.daemon=false\n"
    )
if proxy.hostname:
    values = {
        "systemProp.http.proxyHost": proxy.hostname,
        "systemProp.https.proxyHost": proxy.hostname,
        "systemProp.http.proxyPort": str(proxy.port or 80),
        "systemProp.https.proxyPort": str(proxy.port or 80),
        "systemProp.http.nonProxyHosts": "localhost|127.*|[::1]",
    }
    lines = [
        line
        for line in content.splitlines()
        if not any(line.startswith(k + "=") for k in values)
    ]
    content = "\n".join(lines + [(k + "=" + v) for k, v in values.items()]) + "\n"
if "kotlin.compiler.execution.strategy=" not in content:
    content += "kotlin.compiler.execution.strategy=in-process\n"
trust = Path("/etc/ssl/certs/java/cacerts")
if trust.exists() and "systemProp.javax.net.ssl.trustStore=" not in content:
    content += "systemProp.javax.net.ssl.trustStore=" + str(trust) + "\n"
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(content)
