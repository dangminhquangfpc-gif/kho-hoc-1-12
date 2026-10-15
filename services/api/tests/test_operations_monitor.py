import importlib.util
from pathlib import Path
import ssl
import sys
import threading
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

ROOT = Path(__file__).parents[3]


def load(name):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(
        name, ROOT / "scripts" / (name + ".py")
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


load("backup_postgres")
monitor = load("monitor_shared")


@pytest.fixture
def tls_server(tmp_path):
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "localhost")])
    now = datetime.now(timezone.utc)
    certificate = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(minutes=1))
        .not_valid_after(now + timedelta(days=1))
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .add_extension(
            x509.SubjectAlternativeName([x509.DNSName("localhost")]), critical=False
        )
        .sign(key, hashes.SHA256())
    )
    cert_file, key_file = tmp_path / "cert.pem", tmp_path / "key.pem"
    cert_file.write_bytes(certificate.public_bytes(serialization.Encoding.PEM))
    key_file.write_bytes(
        key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )
    )

    class Handler(BaseHTTPRequestHandler):
        status = 200
        body = b'{"status":"ok","mode":"shared"}'

        def do_GET(self):
            self.send_response(self.status)
            self.send_header("Location", "http://localhost/ready")
            self.end_headers()
            self.wfile.write(self.body)

        def log_message(self, *args):
            pass

    server = HTTPServer(("127.0.0.1", 0), Handler)
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(cert_file, key_file)
    server.socket = context.wrap_socket(server.socket, server_side=True)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield (
            "https://localhost:" + str(server.server_port) + "/api/ready",
            cert_file,
            Handler,
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def test_monitor_requires_verified_https_and_matching_hostname(tls_server):
    url, ca, handler = tls_server
    assert not monitor.ready(url)  # Unknown self-signed CA must fail.
    assert monitor.ready(url, ca)
    assert not monitor.ready(url.replace("localhost", "127.0.0.1"), ca)
    assert not monitor.ready(url.replace("https:", "http:"), ca)


@pytest.mark.parametrize(
    "code,body",
    [
        (503, b'{"status":"unavailable","mode":"shared"}'),
        (302, b""),
        (200, b"<html>error</html>"),
        (200, b'{"status":"ok","mode":"development"}'),
        (200, b"x" * 1025),
    ],
)
def test_monitor_rejects_failure_redirects_invalid_or_development_responses(
    tls_server, code, body
):
    url, ca, handler = tls_server
    handler.status, handler.body = code, body
    assert not monitor.ready(url, ca)


def test_monitor_reports_missing_backup_even_when_server_is_ready(tls_server, tmp_path):
    url, ca, handler = tls_server
    result = monitor.check(url, tmp_path / "backups", ca_file=ca)
    assert result == {"status": "attention", "readiness": "ok", "backup": "missing"}
