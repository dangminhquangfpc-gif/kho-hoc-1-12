"""Shared-server configuration and atomic, database-backed request budgets."""

import hashlib
import ipaddress
import time
from urllib.parse import urlsplit
from sqlalchemy import delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session
from .models import RequestBudget


def validate_shared(config):
    origin = urlsplit(config.public_origin)
    if (
        origin.scheme != "https"
        or not origin.hostname
        or origin.username
        or origin.password
        or origin.path
        or origin.query
        or origin.fragment
        or origin.port not in (None, 443)
    ):
        raise ValueError(
            "Shared server requires an HTTPS public_origin without path or credentials"
        )
    host = origin.hostname
    if (
        host == "localhost"
        or host.endswith((".localhost", ".local", ".invalid", ".example"))
        or "." not in host
    ):
        raise ValueError("Shared server requires a public hostname")
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        pass
    else:
        if not ip.is_global:
            raise ValueError("Shared server requires a public host")
    if not config.database_url.startswith("postgresql+psycopg://"):
        raise ValueError("Shared server requires PostgreSQL with psycopg")
    if config.admin_token or config.manager_credentials_file:
        raise ValueError(
            "Bootstrap and content administration must run offline on shared server"
        )
    if config.cors_origins != [config.public_origin]:
        raise ValueError("Shared CORS origins must equal the public HTTPS origin")
    return host


def reserve(engine, key, limit, seconds):
    now = int(time.time())
    window = now // seconds
    digest = hashlib.sha256(f"{seconds}:{window}:{key}".encode()).hexdigest()
    # ON CONFLICT locks one counter across workers; denied requests do not increase it.
    statement = insert(RequestBudget).values(
        key=digest, count=1, expires_at=(window + 1) * seconds
    )
    statement = statement.on_conflict_do_update(
        index_elements=[RequestBudget.key],
        set_={"count": RequestBudget.count + 1},
        where=RequestBudget.count < limit,
    ).returning(RequestBudget.count)
    with Session(engine) as db:
        allowed = db.execute(statement).scalar_one_or_none() is not None
        db.execute(delete(RequestBudget).where(RequestBudget.expires_at < now))
        db.commit()
    return allowed
