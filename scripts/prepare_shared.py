"""Create private deployment files on the server, without displaying credentials."""

import argparse
import os
from pathlib import Path
import re
import secrets


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--domain", required=True)
    parser.add_argument("--email", required=True)
    parser.add_argument(
        "--directory",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "deploy/shared",
    )
    args = parser.parse_args()
    if (
        not re.fullmatch(r"[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?", args.domain)
        or "." not in args.domain
    ):
        parser.error("Domain must be a hostname without scheme, path or port")
    if not re.fullmatch(r"[^\s=@]+@[^\s=@]+\.[^\s=@]+", args.email):
        parser.error("Invalid email")
    root = args.directory
    secret_dir = root / "secrets"
    private = root / "private"
    destinations = [
        secret_dir / "owner_password",
        secret_dir / "app_password",
        root / ".env",
    ]
    if any(path.exists() or path.is_symlink() for path in destinations):
        parser.error("Deployment files already exist; refusing to overwrite")
    root.mkdir(parents=True, exist_ok=True)
    secret_dir.mkdir(mode=0o700, exist_ok=True)
    private.mkdir(mode=0o700, exist_ok=True)
    # Parent directory protects secrets on host. Read-only secret mounts are readable by API UID 10001.
    os.chmod(secret_dir, 0o700)
    for path in destinations[:2]:
        with path.open("x") as stream:
            os.chmod(path, 0o444)
            stream.write(secrets.token_urlsafe(48) + "\n")
    with destinations[2].open("x") as stream:
        os.chmod(destinations[2], 0o600)
        stream.write(f"TUHOC_DOMAIN={args.domain}\nTUHOC_ACME_EMAIL={args.email}\n")
    print("Created private deployment files. Credentials were not displayed.")


if __name__ == "__main__":
    main()
