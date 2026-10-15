"""Prepare a new Neon PostgreSQL pilot without sending owner credentials to Render.

The default is a read-only plan. --apply is an explicit owner operation against a
new, empty database. No owner URL is accepted as a command-line argument or saved.
"""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import getpass
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import stat
import sys
import warnings

import certifi
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "services/api"))

from khohoc.accounts import ensure_manager  # noqa: E402
from khohoc.database import grant_runtime, migrate  # noqa: E402

RUNTIME_ROLE = "tuhoc_app"
RENDER_CA = "/etc/ssl/certs/ca-certificates.crt"
NEON_DIRECT_HOST = re.compile(
    r"ep-[a-z0-9-]+(?:\.c-[0-9]+)?\.[a-z0-9-]+\.aws\.neon\.tech"
)


class PreparationError(Exception):
    """Only fixed, credential-free explanations may reach the console."""


def normalize_owner_url(raw):
    """Accept only an AWS Neon direct endpoint; require verified TLS and CA trust."""
    try:
        url = make_url(raw.strip())
        if (
            url.drivername not in {"postgres", "postgresql", "postgresql+psycopg"}
            or not url.host
            or not NEON_DIRECT_HOST.fullmatch(url.host)
            or "-pooler" in url.host.split(".")[0]
            or url.port not in {None, 5432}
            or not url.username
            or not re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_]{0,62}", url.username)
            or url.username == RUNTIME_ROLE
            or not url.password
            or any(ord(char) < 32 or ord(char) == 127 for char in url.password)
            or not url.database
            or not re.fullmatch(r"[a-zA-Z0-9_.-]{1,63}", url.database)
            or set(url.query) - {"sslmode", "channel_binding"}
            or any(not isinstance(value, str) for value in url.query.values())
            or url.query.get("sslmode", "require") not in {"require", "verify-full"}
            or url.query.get("channel_binding", "require") not in {"require", "prefer"}
        ):
            raise ValueError
        return url.set(
            drivername="postgresql+psycopg",
            query={
                "sslmode": "verify-full",
                "sslrootcert": certifi.where(),
                "channel_binding": "require",
            },
        )
    except Exception:
        raise PreparationError(
            "Use the Neon AWS DIRECT owner connection string (not a pooler), "
            "with a password and the normal PostgreSQL port. Do not paste it into chat."
        ) from None


def read_owner_url(path=None):
    if path is not None:
        path = Path(path)
        if path.is_symlink() or not path.is_file():
            raise PreparationError("Owner URL input must be a private regular file.")
        if os.name != "nt" and stat.S_IMODE(path.stat().st_mode) & 0o077:
            raise PreparationError("Owner URL input file must have permissions 0600.")
        try:
            raw = path.read_text(encoding="utf-8-sig")
        except Exception:
            raise PreparationError(
                "Cannot read the private owner URL input file."
            ) from None
    else:
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("error", getpass.GetPassWarning)
                raw = getpass.getpass("Neon DIRECT owner URL (hidden; never saved): ")
        except (getpass.GetPassWarning, EOFError):
            raise PreparationError(
                "A private terminal is required for hidden input; alternatively use "
                "--owner-url-file with a private local file."
            ) from None
    return normalize_owner_url(raw)


def owner_engine(url):
    # SQL errors must not reveal bind parameters; the CLI also suppresses exception text.
    return create_engine(
        url,
        hide_parameters=True,
        pool_pre_ping=True,
        connect_args={
            "connect_timeout": 15,
            "options": "-cstatement_timeout=120000 -clock_timeout=10000",
        },
    )


def _inspect_connection(connection):
    if connection.dialect.name != "postgresql":
        raise PreparationError("This helper supports PostgreSQL only.")
    role = (
        connection.execute(
            text(
                "SELECT current_user AS owner_role, current_database() AS database_name, "
                "r.rolcreaterole OR r.rolsuper AS can_create_role, "
                "d.datdba = r.oid AS owns_database, "
                "has_schema_privilege(current_user, 'public', 'CREATE') AS can_create_schema "
                "FROM pg_roles r JOIN pg_database d ON d.datname = current_database() "
                "WHERE r.rolname = current_user"
            )
        )
        .mappings()
        .one()
    )
    if role["owner_role"] == RUNTIME_ROLE:
        raise PreparationError("Use the database owner, not the runtime role.")
    if not all(
        role[key] for key in ("can_create_role", "owns_database", "can_create_schema")
    ):
        raise PreparationError(
            "The owner must own this database and be allowed to create a role and public schema objects."
        )
    exists = connection.execute(
        text("SELECT EXISTS(SELECT 1 FROM pg_roles WHERE rolname = :role)"),
        {"role": RUNTIME_ROLE},
    ).scalar_one()
    if exists:
        raise PreparationError(
            "Runtime role tuhoc_app already exists. Refusing to reset its password or privileges; "
            "use the existing private configuration or a separate new pilot database/project."
        )
    relations = connection.execute(
        text(
            "SELECT COUNT(*) FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace "
            "WHERE n.nspname = 'public' AND c.relkind IN ('r','p','v','m','S','f')"
        )
    ).scalar_one()
    if relations:
        raise PreparationError(
            "The public schema is not empty. This first-run helper never replaces existing tables or data."
        )
    return {
        "database": role["database_name"],
        "runtime_role": RUNTIME_ROLE,
        "empty": True,
    }


def inspect_plan(engine):
    """Read-only preflight, usable by tests and setup packaging without any files."""
    with engine.connect() as connection:
        connection.execute(text("SET TRANSACTION READ ONLY"))
        return _inspect_connection(connection)


class _TransactionFacade:
    """Let existing explicit DDL helpers share one owner's actual transaction."""

    def __init__(self, connection):
        self.connection = connection
        self.dialect = connection.dialect

    @contextmanager
    def begin(self):
        yield self.connection

    @contextmanager
    def connect(self):
        yield self.connection


def _content_plan(path, expected_sha256, library_root):
    if path is None:
        if expected_sha256 is not None:
            raise PreparationError("--content-sha256 requires --content-archive.")
        return None
    if not expected_sha256 or not re.fullmatch(r"[a-f0-9]{64}", expected_sha256):
        raise PreparationError(
            "A content archive requires its reviewed --content-sha256."
        )
    from khohoc.content_transfer import MAX_ARCHIVE_BYTES, validate_archive

    try:
        with Path(path).open("rb") as handle:
            payload = handle.read(MAX_ARCHIVE_BYTES + 1)
        if hashlib.sha256(payload).hexdigest() != expected_sha256:
            raise PreparationError(
                "Content archive SHA256 differs from the reviewed value."
            )
        options = {"library_root": library_root} if library_root is not None else {}
        archive = validate_archive(payload, **options)
        return {"sha256": expected_sha256, "counts": archive["manifest"]["counts"]}
    except PreparationError:
        raise
    except Exception:
        raise PreparationError(
            "Content archive validation failed. Use the unchanged published setup package and its public PDFs."
        ) from None


def _new_private_directory(directory):
    path = Path(directory)
    # Refuse symlinks in every existing parent: never chmod or write through them.
    if any(parent.is_symlink() for parent in (path, *path.parents)):
        raise PreparationError("Private output path must not contain symbolic links.")
    if path.exists():
        raise PreparationError(
            "Private output directory already exists; refusing to overwrite credentials."
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.mkdir(mode=0o700)
    if os.name != "nt":
        path.chmod(0o700)
    return path


def _private_write(path, value):
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(value)


def runtime_database_url(owner_url, password):
    return owner_url.set(
        username=RUNTIME_ROLE,
        password=password,
        query={
            "sslmode": "verify-full",
            "sslrootcert": RENDER_CA,
            "channel_binding": "require",
        },
    ).render_as_string(hide_password=False)


def _create_runtime_role(connection, password):
    # PostgreSQL utility statements cannot bind a PASSWORD placeholder. Keep the
    # password in a bound, transaction-local setting, never interpolated SQL.
    connection.execute(
        text("SELECT set_config('tuhoc.bootstrap_password', :password, true)"),
        {"password": password},
    )
    connection.execute(
        text(
            "DO $tuhoc$ BEGIN EXECUTE format("
            "'CREATE ROLE tuhoc_app WITH LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE "
            "NOINHERIT NOREPLICATION NOBYPASSRLS PASSWORD %L', "
            "current_setting('tuhoc.bootstrap_password')); END $tuhoc$"
        )
    )
    connection.execute(text("SELECT set_config('tuhoc.bootstrap_password', '', true)"))


def prepare(
    engine,
    *,
    directory,
    content_archive=None,
    content_sha256=None,
    library_root=None,
    apply=False,
):
    """Plan by default; apply only to a fresh pilot and never persist the owner URL."""
    content = _content_plan(content_archive, content_sha256, library_root)
    plan = inspect_plan(engine)
    result = {"mode": "plan", **plan, "content": content}
    if not apply:
        return result
    private = _new_private_directory(directory)
    try:
        password = secrets.token_urlsafe(48)
        runtime_url = runtime_database_url(engine.url, password)
        with engine.begin() as connection:
            connection.execute(text("SELECT pg_advisory_xact_lock(11120261017)"))
            # Recheck after acquiring the owner-operation lock; no stale preflight.
            _inspect_connection(connection)
            _create_runtime_role(connection, password)
            facade = _TransactionFacade(connection)
            migrate(facade)
            ensure_manager(connection, private / "manager-credentials.txt")
            connection.execute(text("REVOKE CREATE ON SCHEMA public FROM PUBLIC"))
            # Fresh dedicated database: PUBLIC otherwise grants runtime roles
            # temporary-table DDL even when the application role owns no tables.
            database_identifier = (
                connection.dialect.identifier_preparer.quote_identifier(
                    plan["database"]
                )
            )
            connection.execute(
                text(
                    f"REVOKE CREATE, TEMPORARY ON DATABASE {database_identifier} FROM PUBLIC"
                )
            )
            grant_runtime(facade, RUNTIME_ROLE)
            if content_archive is not None:
                from khohoc.content_transfer import import_published_content

                options = (
                    {"library_root": library_root} if library_root is not None else {}
                )
                # A fresh schema has no conflicts. Still perform the real receiver's
                # dry-run validation before any public content is inserted.
                import_published_content(
                    connection,
                    content_archive,
                    expected_sha256=content_sha256,
                    **options,
                )
                import_published_content(
                    connection,
                    content_archive,
                    apply=True,
                    expected_sha256=content_sha256,
                    **options,
                )
            _private_write(
                private / "render-private.env",
                "KHOHOC_DATABASE_URL=" + runtime_url + "\n",
            )
            _private_write(
                private / "README-private.txt",
                "PRIVATE: Never upload this directory to GitHub or chat.\n"
                "render-private.env contains only the restricted runtime database URL.\n"
                "Paste that environment variable into Render's private Environment settings.\n"
                "Do not put the owner connection string on Render.\n"
                "manager-credentials.txt contains a temporary manager password; change it at first login.\n"
                "If setup failed, keep these files and inspect the owner database before retrying.\n"
                "On Windows, chmod does not enforce ACLs. Keep this directory in your own Windows profile;\n"
                "do not place it in shared/public/cloud-sync folders. Restrict its Security permissions.\n",
            )
    except Exception:
        raise PreparationError(
            "Setup did not finish. Database changes are transactional, but a lost connection can make "
            "commit status uncertain. Keep the private output directory; inspect the database before "
            "retrying. Existing roles and passwords will never be reset automatically. "
            "Connection details and database exception text were hidden."
        ) from None
    return {**result, "mode": "applied", "private_directory": str(private)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Explicitly initialize a NEW pilot database",
    )
    parser.add_argument(
        "--owner-url-file",
        type=Path,
        help="Private local input file; never printed or copied",
    )
    parser.add_argument(
        "--directory", type=Path, default=ROOT / "state/free-server-private"
    )
    parser.add_argument("--content-archive", type=Path)
    parser.add_argument("--content-sha256")
    parser.add_argument("--library-root", type=Path)
    args = parser.parse_args(argv)
    engine = None
    try:
        url = read_owner_url(args.owner_url_file)
        engine = owner_engine(url)
        result = prepare(
            engine,
            directory=args.directory,
            content_archive=args.content_archive,
            content_sha256=args.content_sha256,
            library_root=args.library_root,
            apply=args.apply,
        )
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        if not args.apply:
            print(
                "Read-only plan only. Review the content counts, then run explicitly with --apply to initialize."
            )
        else:
            print(
                "Prepared. Owner URL was not saved. Keep private files local; never upload them to Git or chat."
            )
            if os.name == "nt":
                print(
                    "Windows: protect this private directory with your user-only Security permissions; chmod is not an ACL."
                )
        return 0
    except KeyboardInterrupt:
        print("Cancelled. No connection details were displayed.", file=sys.stderr)
        return 1
    except PreparationError as error:
        print(str(error), file=sys.stderr)
        return 1
    except Exception:
        print(
            "Preparation failed. Check connectivity, the direct owner URL and database permissions locally. "
            "Connection details and database exception text were hidden.",
            file=sys.stderr,
        )
        return 1
    finally:
        if engine is not None:
            try:
                engine.dispose()
            except Exception:
                # Cleanup failures must not expose driver connection information.
                pass


if __name__ == "__main__":
    raise SystemExit(main())
