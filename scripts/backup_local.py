"""Encrypted, consistent SQLite backups. Never restore over a running database."""

import argparse
import os
from pathlib import Path
import secrets
import sqlite3
import tempfile

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

MAGIC = b"TUHOC111-SQLITE-1\n"
MAX_BYTES = 512 * 1024 * 1024


def write_private(path: Path, payload: bytes):
    # Exclusive creation also rejects symlinks and existing destinations.
    with path.open("xb") as stream:
        os.chmod(path, 0o600)
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())


def read_key(path: Path):
    key = path.read_bytes()
    if len(key) != 32:
        raise ValueError("Khóa phải có đúng 32 byte.")
    return key


def check_database(path: Path):
    with sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True) as db:
        if db.execute("PRAGMA integrity_check").fetchall() != [("ok",)]:
            raise ValueError("Cơ sở dữ liệu không vượt qua kiểm tra toàn vẹn.")
        tables = {
            row[0]
            for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }
        if not {"learning_users", "learning_records", "local_attempts"} <= tables:
            raise ValueError("Không phải cơ sở dữ liệu học tập Tự học 111.")


def backup(database: Path, destination: Path, key_file: Path):
    key = read_key(key_file)
    with tempfile.TemporaryDirectory(prefix="tuhoc-backup-") as directory:
        snapshot = Path(directory) / "snapshot.db"
        # SQLite backup API includes committed WAL data while the app stays online.
        with sqlite3.connect(
            database.resolve().as_uri() + "?mode=ro", uri=True
        ) as source:
            with sqlite3.connect(snapshot) as target:
                source.backup(target)
        check_database(snapshot)
        if snapshot.stat().st_size > MAX_BYTES:
            raise ValueError("Bản local vượt giới hạn sao lưu 512 MiB.")
        nonce = secrets.token_bytes(12)
        encrypted = AESGCM(key).encrypt(nonce, snapshot.read_bytes(), MAGIC)
        write_private(destination, MAGIC + nonce + encrypted)


def restore(archive: Path, destination: Path, key_file: Path):
    key = read_key(key_file)
    if archive.stat().st_size > MAX_BYTES + 128:
        raise ValueError("Tệp sao lưu quá lớn.")
    payload = archive.read_bytes()
    if not payload.startswith(MAGIC):
        raise ValueError("Định dạng sao lưu không hợp lệ.")
    offset = len(MAGIC)
    data = AESGCM(key).decrypt(
        payload[offset : offset + 12], payload[offset + 12 :], MAGIC
    )
    # Validate before publishing; never overwrite existing DB/WAL/SHM files.
    if any(Path(str(destination) + suffix).exists() for suffix in ("", "-wal", "-shm")):
        raise FileExistsError("Chỉ khôi phục đến đường dẫn cơ sở dữ liệu mới.")
    with tempfile.TemporaryDirectory(prefix="tuhoc-restore-") as directory:
        candidate = Path(directory) / "candidate.db"
        candidate.write_bytes(data)
        check_database(candidate)
        write_private(destination, data)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    keygen = sub.add_parser("keygen")
    keygen.add_argument("--key-file", required=True, type=Path)
    for command in ("backup", "restore"):
        action = sub.add_parser(command)
        action.add_argument("--key-file", required=True, type=Path)
        action.add_argument("--database", required=True, type=Path)
        action.add_argument("--archive", required=True, type=Path)
    args = parser.parse_args()
    try:
        if args.command == "keygen":
            write_private(args.key_file, AESGCM.generate_key(bit_length=256))
        elif args.command == "backup":
            backup(args.database, args.archive, args.key_file)
        else:
            restore(args.archive, args.database, args.key_file)
    except Exception:
        parser.exit(
            1,
            "Không hoàn tất. Kiểm tra khóa, tệp đầu vào, quyền ghi và dùng đường dẫn đích mới.\n",
        )
    print("Hoàn tất. Giữ khóa riêng biệt với bản sao lưu.")


if __name__ == "__main__":
    main()
