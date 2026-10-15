"""Operator readiness/backup check. Prints no tokens, URLs, student data or database errors."""

import argparse
import json
from pathlib import Path
import ssl
import urllib.error
import urllib.parse
import urllib.request

from backup_postgres import backup_status


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def ready(url, ca_file=None):
    parsed = urllib.parse.urlsplit(url)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username
        or parsed.password
        or parsed.query
        or parsed.fragment
        or parsed.path not in ("/ready", "/api/ready")
    ):
        return False
    try:
        context = ssl.create_default_context(cafile=ca_file)
        opener = urllib.request.build_opener(
            NoRedirect(), urllib.request.HTTPSHandler(context=context)
        )
        with opener.open(url, timeout=5) as response:
            if response.status != 200:
                return False
            payload = response.read(1025)
            if len(payload) > 1024:
                return False
            value = json.loads(payload)
            return value.get("status") == "ok" and value.get("mode") in (
                "shared",
                "production",
            )
    except (OSError, ValueError, AttributeError, urllib.error.URLError):
        return False


def check(url, directory, max_age_hours=26, ca_file=None):
    readiness = ready(url, ca_file)
    backup = backup_status(directory, max_age_hours)
    return dict(
        status="ok" if readiness and backup == "fresh" else "attention",
        readiness="ok" if readiness else "unavailable",
        backup=backup,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True)
    parser.add_argument("--backup-directory", required=True, type=Path)
    parser.add_argument("--max-age-hours", type=int, default=26)
    parser.add_argument("--ca-file", type=Path)
    args = parser.parse_args()
    if not 1 <= args.max_age_hours <= 8760:
        parser.error("max-age-hours must be 1–8760")
    result = check(args.url, args.backup_directory, args.max_age_hours, args.ca_file)
    print(json.dumps(result))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
