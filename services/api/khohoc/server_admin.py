"""Offline server maintenance. No public administration endpoints or secret output."""

import argparse
import sqlite3
import tempfile
from pathlib import Path
from sqlalchemy import select, text, inspect
from .app import Settings
from .database import make_engine, migrate, grant_runtime
from .accounts import ensure_manager
from .models import Base, LearningSession, RequestBudget


def copy_sqlite(source_path, target):
    if target.dialect.name != "postgresql":
        raise ValueError("Destination must be PostgreSQL")
    path = Path(source_path).resolve()
    if not path.is_file():
        raise ValueError("Missing SQLite source")
    snapshot_directory = tempfile.TemporaryDirectory(prefix="tuhoc-transfer-")
    snapshot = Path(snapshot_directory.name) / "snapshot.db"
    with sqlite3.connect(path.as_uri() + "?mode=ro", uri=True) as incoming:
        with sqlite3.connect(snapshot) as output:
            incoming.backup(output)
    source = make_engine("sqlite:///file:" + str(snapshot) + "?mode=ro&uri=true")
    excluded = {LearningSession.__table__.name, RequestBudget.__table__.name}
    try:
        with source.connect() as incoming, target.begin() as outgoing:
            # One transaction: failed transfer leaves target unchanged.
            for table in Base.metadata.sorted_tables:
                if outgoing.execute(select(table).limit(1)).first():
                    raise ValueError("Destination must be empty; never merge databases")
            for table in Base.metadata.sorted_tables:
                if table.name in excluded:
                    continue
                if not inspect(incoming).has_table(table.name):
                    if table.name in {"attempt_drafts", "content_reports"}:
                        continue
                    raise ValueError("Source schema incomplete")
                result = incoming.execute(select(table)).mappings()
                while batch := result.fetchmany(200):
                    outgoing.execute(table.insert(), [dict(row) for row in batch])
            outgoing.execute(
                text(
                    "SELECT setval(pg_get_serial_sequence('local_audit_events', 'id'), COALESCE((SELECT MAX(id) FROM local_audit_events), 1), EXISTS(SELECT 1 FROM local_audit_events))"
                )
            )
    finally:
        source.dispose()
        snapshot_directory.cleanup()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("migrate")
    grant = commands.add_parser("grant-runtime")
    grant.add_argument("--role", default="tuhoc_app")
    bootstrap = commands.add_parser("bootstrap-manager")
    bootstrap.add_argument("--credentials-file", required=True)
    transfer = commands.add_parser("import-sqlite")
    transfer.add_argument("--source", required=True)
    args = parser.parse_args()
    config = Settings()
    engine = make_engine(config.resolved_database_url())
    try:
        if args.command == "migrate":
            migrate(engine)
        elif args.command == "grant-runtime":
            grant_runtime(engine, args.role)
        elif args.command == "bootstrap-manager":
            from .database import verify_schema

            verify_schema(engine)
            ensure_manager(engine, args.credentials_file)
        else:
            from .database import verify_schema

            verify_schema(engine)
            copy_sqlite(args.source, engine)
    finally:
        engine.dispose()
    print("Hoàn tất. Không đưa tệp tài khoản hoặc thông tin kết nối lên Git.")


if __name__ == "__main__":
    main()
