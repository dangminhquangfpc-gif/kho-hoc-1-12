"""Explicit schema initialization for shared servers; no automatic production DDL."""

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import make_url
from .models import Base

SCHEMA_VERSION = 2


def make_engine(url):
    if url.startswith("sqlite"):
        return create_engine(
            url, pool_pre_ping=True, connect_args={"check_same_thread": False}
        )
    options = str(make_url(url).query.get("options", ""))
    return create_engine(
        url,
        pool_pre_ping=True,
        pool_timeout=5,
        connect_args={
            "connect_timeout": 5,
            "options": options + " -cstatement_timeout=5000 -clock_timeout=3000",
        },
    )


def verify_columns(connection, skip=()):
    inspector = inspect(connection)
    for table in Base.metadata.sorted_tables:
        if table.name in skip:
            continue
        columns = {column["name"] for column in inspector.get_columns(table.name)}
        if not set(table.columns.keys()) <= columns:
            raise RuntimeError(
                "Schema columns differ; an explicit migration is required"
            )


def migrate(engine):
    # Import document models before computing metadata.
    from . import library, question_versions  # noqa: F401

    with engine.begin() as connection:
        if engine.dialect.name == "postgresql":
            connection.execute(text("SELECT pg_advisory_xact_lock(11120261015)"))
        connection.execute(
            text(
                "CREATE TABLE IF NOT EXISTS app_schema_version (version INTEGER PRIMARY KEY)"
            )
        )
        versions = (
            connection.execute(text("SELECT version FROM app_schema_version"))
            .scalars()
            .all()
        )
        if versions not in ([], [1], [SCHEMA_VERSION]):
            raise RuntimeError(
                "Unsupported schema version; explicit migration required"
            )
        if not versions:
            # Local v13 SQLite has no version table; preserve rows and add absent tables.
            Base.metadata.create_all(connection)
        elif versions == [1]:
            # Explicit additive 1 -> 2 migration. Refuse unrelated baseline drift.
            from .models import ContentReport

            verify_columns(connection, skip=(ContentReport.__tablename__,))
            ContentReport.__table__.create(connection, checkfirst=True)
        verify_columns(connection)
        if versions != [SCHEMA_VERSION]:
            connection.execute(text("DELETE FROM app_schema_version"))
            connection.execute(
                text("INSERT INTO app_schema_version (version) VALUES (:version)"),
                {"version": SCHEMA_VERSION},
            )


def verify_schema(engine):
    from . import library, question_versions  # noqa: F401

    with engine.connect() as connection:
        if "app_schema_version" not in inspect(connection).get_table_names():
            raise RuntimeError(
                "Run khohoc.server_admin migrate before starting shared server"
            )
        if connection.execute(
            text("SELECT version FROM app_schema_version")
        ).scalars().all() != [SCHEMA_VERSION]:
            raise RuntimeError("Unsupported database schema")
        if not set(Base.metadata.tables) <= set(inspect(connection).get_table_names()):
            raise RuntimeError("Incomplete database schema")
        verify_columns(connection)


def grant_runtime(engine, role, schema="public"):
    """Owner-only operation: API role gets data access, never schema/role administration."""
    import re

    verify_schema(engine)
    if not all(
        re.fullmatch(r"[a-z_][a-z0-9_]{0,62}", value) for value in (role, schema)
    ):
        raise ValueError("Invalid role or schema name")
    with engine.begin() as connection:
        connection.execute(text(f'GRANT USAGE ON SCHEMA "{schema}" TO "{role}"'))
        for table in Base.metadata.tables:
            connection.execute(
                text(
                    f'GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE "{schema}"."{table}" TO "{role}"'
                )
            )
        connection.execute(
            text(f'GRANT SELECT ON TABLE "{schema}".app_schema_version TO "{role}"')
        )
        connection.execute(
            text(
                f'GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA "{schema}" TO "{role}"'
            )
        )
