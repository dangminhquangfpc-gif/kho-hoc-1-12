"""Provider behavior is simulated; these checks do not call or validate a paid model."""

import asyncio
import hashlib
import json
import os
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from datetime import datetime, timedelta, timezone

import httpx
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import select, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from khohoc.accounts import AccountService
from khohoc.ai_tutor import (
    AITutorConfig,
    QuotaExceeded,
    create_ai_tutor_router,
    reserve_quotas,
)
from khohoc.database import make_engine, migrate
from khohoc.models import (
    AccountAttempt,
    Attempt,
    AuditEvent,
    LearningRecord,
    LearningSession,
    LearningUser,
    RequestBudget,
)

KEY = "synthetic-key-for-mock-provider-ONLY"
PROMPT = "Nội dung riêng: hướng dẫn tính chu vi hình tròn."
AUTH = {"Authorization": "Bearer khs_synthetic-learner"}
BODY = {
    "grade": 5,
    "subject": "toan",
    "text": PROMPT,
    "consent": True,
    "expected_provider_host": "api.openai.com",
}
CONTENT = {
    "explanation": "Chu vi bằng đường kính nhân với 3,14.",
    "steps": ["Xác định bán kính.", "Lấy hai lần bán kính nhân với 3,14."],
    "uncertainties": [],
    "confidence": 0.9,
    "needs_review": False,
}


def provider_response(content=None, **kwargs):
    return {
        "choices": [
            {
                "finish_reason": "stop",
                "message": {
                    "content": json.dumps(content or CONTENT, ensure_ascii=False)
                },
            }
        ],
        "usage": {"prompt_tokens": 120, "completion_tokens": 80},
    } | kwargs


@pytest.fixture
def tutor(tmp_path):
    engine = make_engine("sqlite:///" + str(tmp_path / "tutor.db"))
    migrate(engine)
    key = tmp_path / "provider.key"
    key.write_text(KEY + "\n")
    key.chmod(0o600)
    config = AITutorConfig(enabled=True, model="gpt-4.1-mini", api_key_file=str(key))
    requests = []
    handler = [lambda request: httpx.Response(200, json=provider_response())]

    def mocked(request):
        requests.append(request)
        return handler[0](request)

    def db():
        with Session(engine) as session:
            yield session

    accounts = AccountService(db)
    with Session(engine) as session:
        for ident, token in (
            ("learner", "khs_synthetic-learner"),
            ("other", "khs_other"),
        ):
            session.add(
                LearningUser(
                    id=ident,
                    username=ident,
                    display_name="Học viên giả lập",
                    password_hash="not-a-real-hash",
                    role="student",
                )
            )
            session.add(
                LearningSession(
                    token_hash=hashlib.sha256(token.encode()).hexdigest(),
                    user_id=ident,
                    expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
                )
            )
        session.commit()

    def app_for(settings=config):
        app = FastAPI()
        app.include_router(
            create_ai_tutor_router(
                db=db,
                accounts=accounts,
                engine=engine,
                config=settings,
                client_factory=lambda: httpx.AsyncClient(
                    transport=httpx.MockTransport(mocked), follow_redirects=False
                ),
            )
        )
        return TestClient(app)

    yield app_for, engine, config, requests, handler, key
    engine.dispose()


def test_status_auth_disabled_and_missing_configuration(tutor):
    app_for, engine, config, requests, _, key = tutor
    with app_for(AITutorConfig()) as client:
        assert client.get("/ai/status").status_code == 401
        assert client.post("/ai/explain", json=BODY).status_code == 401
        assert client.get("/ai/status", headers=AUTH).json() == {
            "configured": False,
            "provider_host": "",
            "model": "",
            "daily_user_limit": 0,
            "daily_server_limit": 0,
        }
        assert client.post("/ai/explain", headers=AUTH, json=BODY).status_code == 503
    key.unlink()
    with app_for() as client:
        assert not client.get("/ai/status", headers=AUTH).json()["configured"]
        assert client.post("/ai/explain", headers=AUTH, json=BODY).status_code == 503
    assert requests == []
    with Session(engine) as db:
        assert list(db.scalars(select(RequestBudget))) == []


@pytest.mark.parametrize(
    "change",
    [
        {"consent": False},
        {"consent": 1},
        {"consent": "true"},
        {"grade": 0},
        {"grade": "5"},
        {"grade": True},
        {"subject": "vat_li"},
        {"text": "ab"},
        {"text": "a" * 6001},
        {"api_key": KEY},
        {"attempt_id": "missing"},
        {"question_id": "missing"},
    ],
)
def test_explicit_consent_input_and_subject_validation(tutor, change):
    app_for, _, _, requests, _, _ = tutor
    with app_for() as client:
        response = client.post("/ai/explain", headers=AUTH, json=BODY | change)
    assert response.status_code == 422
    assert PROMPT not in response.text and KEY not in response.text
    assert requests == []


def test_explanation_payload_and_provisional_result_no_stored_work(tutor):
    app_for, engine, _, requests, _, _ = tutor
    with app_for() as client:
        status = client.get("/ai/status", headers=AUTH).json()
        assert status["configured"] and status["model"] == "gpt-4.1-mini"
        assert KEY not in json.dumps(status)
        result = client.post("/ai/explain", headers=AUTH, json=BODY)
    assert result.status_code == 200
    assert result.json()["provisional"] and result.json()["needs_review"]
    assert result.json()["grounded"] is False
    assert result.json()["usage"] == {"input_tokens": 120, "output_tokens": 80}
    assert "score" not in result.json()
    assert requests[0].url == "https://api.openai.com/v1/chat/completions"
    assert requests[0].headers["authorization"] == "Bearer " + KEY
    payload = json.loads(requests[0].content)
    assert payload["model"] == "gpt-4.1-mini" and payload["max_tokens"] == 800
    assert payload["response_format"] == {"type": "json_object"}
    assert [m["role"] for m in payload["messages"]] == ["system", "user"]
    assert json.loads(payload["messages"][1]["content"])["text"] == PROMPT
    assert (
        "tools" not in payload
        and "completed_attempt_reference" not in payload["messages"][1]["content"]
    )
    with Session(engine) as db:
        audits = list(db.scalars(select(AuditEvent)))
        assert len(audits) == 1 and json.loads(audits[0].target)["outcome"] == "success"
        assert json.loads(audits[0].target)["usage"] == {
            "input_tokens": 120,
            "output_tokens": 80,
        }
        assert PROMPT not in audits[0].target and KEY not in audits[0].target
        assert CONTENT["explanation"] not in audits[0].target
        assert list(db.scalars(select(LearningRecord))) == []
        assert list(db.scalars(select(Attempt))) == []


def seed_attempt(engine, result=None, owner="learner"):
    with Session(engine) as db:
        db.add(
            Attempt(
                id="completed-work",
                token_hash="not-a-capability-token",
                snapshot={
                    "questions": [
                        {
                            "id": "circle",
                            "grade": 5,
                            "subject": "toan",
                            "question": "Tính chu vi hình tròn có bán kính 3 cm.",
                            "options": [],
                            "correct_answer": "18,84 cm",
                            "explanation": "3 × 2 × 3,14 = 18,84 (cm). Đáp số: 18,84 cm.",
                        }
                    ]
                },
                answers={"circle": "18,84 cm"},
                result=result,
            )
        )
        db.add(AccountAttempt(attempt_id="completed-work", user_id=owner))
        db.commit()


def test_grounded_reference_only_owned_submitted_work(tutor):
    app_for, engine, _, requests, _, _ = tutor
    official = {"score": 1, "max_score": 1}
    seed_attempt(engine, result=official)
    body = BODY | {"attempt_id": "completed-work", "question_id": "circle"}
    with app_for() as client:
        assert (
            client.post(
                "/ai/explain", headers={"Authorization": "Bearer khs_other"}, json=body
            ).status_code
            == 404
        )
        assert (
            client.post(
                "/ai/explain", headers=AUTH, json=body | {"grade": 4}
            ).status_code
            == 422
        )
        assert (
            client.post(
                "/ai/explain", headers=AUTH, json=body | {"question_id": "unknown"}
            ).status_code
            == 404
        )
        response = client.post("/ai/explain", headers=AUTH, json=body)
    assert response.status_code == 200 and response.json()["grounded"]
    payload = json.loads(requests[0].content)
    reference = json.loads(payload["messages"][1]["content"])[
        "completed_attempt_reference"
    ]
    assert reference["correct_answer"] == "18,84 cm"
    assert "Đáp số" in reference["explanation"]
    assert "answers" not in reference and "score" not in reference
    with Session(engine) as db:
        assert db.get(Attempt, "completed-work").result == official
        assert db.get(Attempt, "completed-work").answers == {"circle": "18,84 cm"}


def test_grounded_reference_does_not_leak_unsubmitted_answer(tutor):
    app_for, engine, _, requests, _, _ = tutor
    seed_attempt(engine)
    with app_for() as client:
        response = client.post(
            "/ai/explain",
            headers=AUTH,
            json=BODY
            | {
                "attempt_id": "completed-work",
                "question_id": "circle",
            },
        )
    assert response.status_code == 409 and "18,84" not in response.text
    assert requests == []


def test_oversize_grounded_reference_rejected_before_quota_or_outbound(tutor):
    app_for, engine, _, requests, _, _ = tutor
    seed_attempt(engine, result={"score": 1})
    with Session(engine) as db:
        attempt = db.get(Attempt, "completed-work")
        snapshot = json.loads(json.dumps(attempt.snapshot))
        snapshot["questions"][0]["correct_answer"] = "x" * 50000
        attempt.snapshot = snapshot
        db.commit()
    with app_for() as client:
        response = client.post(
            "/ai/explain",
            headers=AUTH,
            json=BODY
            | {
                "attempt_id": "completed-work",
                "question_id": "circle",
            },
        )
    assert response.status_code == 422
    assert requests == []
    with Session(engine) as db:
        assert list(db.scalars(select(RequestBudget))) == []


def test_provider_wait_releases_database_connection(tutor):
    app_for, engine, _, _, handler, _ = tutor

    def provider(request):
        assert engine.pool.checkedout() == 0
        return httpx.Response(200, json=provider_response())

    handler[0] = provider
    with app_for() as client:
        assert client.post("/ai/explain", headers=AUTH, json=BODY).status_code == 200


def test_consent_is_bound_to_the_disclosed_provider_host(tutor):
    app_for, engine, _, requests, _, _ = tutor
    with app_for() as client:
        response = client.post(
            "/ai/explain",
            headers=AUTH,
            json=BODY
            | {
                "expected_provider_host": "previous-provider.example.com",
            },
        )
    assert response.status_code == 409 and requests == []
    with Session(engine) as db:
        assert list(db.scalars(select(RequestBudget))) == []


@pytest.mark.parametrize(
    "url",
    [
        "http://api.openai.com/v1",
        "https://key@api.openai.com/v1",
        "https://api.openai.com/v1?token=secret",
        "https://api.openai.com/v1#fragment",
        "https://localhost/v1",
        "https://one.local/v1",
        "https://one.localhost/v1",
        "https://127.0.0.1/v1",
        "https://10.1.2.3/v1",
        "https://169.254.169.254/v1",
        "https://[::1]/v1",
        "https://192.168.1.10/v1",
        "https://api.openai.com:8080/v1",
        "https://api.openai.com/../secret",
        "https://api.openai.com/%2e/secret",
    ],
)
def test_provider_url_rejects_unsafe_configuration(tutor, url):
    _, _, config, _, _, _ = tutor
    assert replace(config, base_url=url).key() is None


def test_private_regular_key_file_and_environment_configuration(
    tutor, monkeypatch, tmp_path
):
    _, _, config, _, _, key = tutor
    assert config.key() == KEY and KEY not in repr(config)
    key.chmod(0o644)
    assert config.key() is None
    key.chmod(0o600)
    link = tmp_path / "symlink.key"
    link.symlink_to(key)
    assert replace(config, api_key_file=str(link)).key() is None
    assert replace(config, api_key_file=str(tmp_path)).key() is None
    fifo = tmp_path / "fifo.key"
    os.mkfifo(fifo, mode=0o600)
    assert replace(config, api_key_file=str(fifo)).key() is None
    monkeypatch.setenv("KHOHOC_AI_ENABLED", "true")
    monkeypatch.setenv("KHOHOC_AI_MODEL", "gpt-4.1-mini")
    monkeypatch.setenv("KHOHOC_AI_API_KEY_FILE", str(key))
    assert AITutorConfig.from_env().key() == KEY
    monkeypatch.setenv("KHOHOC_AI_DAILY_USER_LIMIT", "not-a-number")
    assert not AITutorConfig.from_env().enabled
    assert replace(config, daily_user_limit=51).key() is None
    assert replace(config, daily_server_limit=501).key() is None
    assert replace(config, output_tokens=1201).key() is None
    assert replace(config, model="secret\nmodel").key() is None


def test_secret_environment_injection_and_ambiguous_key_sources(tutor, monkeypatch):
    app_for, engine, config, requests, _, key = tutor
    monkeypatch.setenv("KHOHOC_AI_ENABLED", "true")
    monkeypatch.setenv("KHOHOC_AI_MODEL", "gpt-4.1-mini")
    monkeypatch.delenv("KHOHOC_AI_API_KEY_FILE", raising=False)
    monkeypatch.setenv("KHOHOC_AI_API_KEY", KEY)
    settings = AITutorConfig.from_env()
    assert settings.key() == KEY
    assert settings.api_key_file is None
    assert settings.api_key_env_name == "KHOHOC_AI_API_KEY"
    assert KEY not in repr(settings)
    assert KEY not in str(settings.__dict__)
    with app_for(settings) as client:
        status = client.get("/ai/status", headers=AUTH)
        assert status.json()["configured"] and KEY not in status.text
        assert client.post("/ai/explain", headers=AUTH, json=BODY).status_code == 200
    assert requests[0].headers["authorization"] == "Bearer " + KEY
    monkeypatch.setenv("KHOHOC_AI_API_KEY_FILE", str(key))
    ambiguous = AITutorConfig.from_env()
    assert ambiguous.key() is None
    with app_for(ambiguous) as client:
        assert not client.get("/ai/status", headers=AUTH).json()["configured"]
        assert client.post("/ai/explain", headers=AUTH, json=BODY).status_code == 503
    assert len(requests) == 1
    assert replace(config, api_key_file=None, api_key_env_name="PATH").key() is None
    monkeypatch.delenv("KHOHOC_AI_API_KEY_FILE")
    monkeypatch.setenv("KHOHOC_AI_API_KEY", "short")
    assert AITutorConfig.from_env().key() is None
    monkeypatch.setenv("KHOHOC_AI_API_KEY", KEY + "\nprivate text")
    assert AITutorConfig.from_env().key() is None
    monkeypatch.delenv("KHOHOC_AI_API_KEY")
    # A rotated/deleted runtime secret fails closed, rather than retaining a copy.
    assert settings.key() is None
    with Session(engine) as db:
        assert KEY not in "".join(
            item.target for item in db.scalars(select(AuditEvent))
        )


@pytest.mark.parametrize(
    "content",
    [
        CONTENT | {"confidence": 1.1},
        CONTENT | {"confidence": float("nan")},
        CONTENT | {"score": 10},
        CONTENT | {"needs_review": "false"},
        CONTENT | {"steps": []},
        CONTENT | {"steps": ["x"] * 9},
        CONTENT | {"explanation": "x" * 6001},
        CONTENT | {"explanation": "<script>alert('unsafe')</script>"},
        CONTENT | {"explanation": "javascript:run()"},
        CONTENT | {"uncertainties": ["x" * 501]},
        CONTENT | {"explanation": "text\x00hidden"},
    ],
)
def test_untrusted_model_content_is_bounded_and_strict(tutor, content):
    app_for, _, _, requests, handler, _ = tutor
    handler[0] = lambda request: httpx.Response(200, json=provider_response(content))
    with app_for() as client:
        response = client.post("/ai/explain", headers=AUTH, json=BODY)
    assert response.status_code == 502 and len(requests) == 1
    assert KEY not in response.text and PROMPT not in response.text


@pytest.mark.parametrize(
    "kind",
    [
        "unavailable",
        "redirect",
        "invalid-json",
        "deep-json",
        "oversize",
        "tool-call",
        "incomplete",
        "bad-usage",
        "duplicate-keys",
        "not-json",
    ],
)
def test_provider_failures_are_generic_and_consume_attempt_quota(tutor, kind):
    app_for, engine, config, requests, handler, _ = tutor
    response = provider_response()
    if kind == "unavailable":
        answer = httpx.Response(401, text=KEY + PROMPT)
    elif kind == "redirect":
        answer = httpx.Response(307, headers={"Location": "https://localhost/private"})
    elif kind == "invalid-json":
        answer = httpx.Response(
            200, content=b"not JSON", headers={"content-type": "application/json"}
        )
    elif kind == "deep-json":
        answer = httpx.Response(
            200,
            content=b"[" * 2000 + b"0" + b"]" * 2000,
            headers={"content-type": "application/json"},
        )
    elif kind == "oversize":
        answer = httpx.Response(
            200, content=b" " * 131073, headers={"content-type": "application/json"}
        )
    elif kind == "not-json":
        answer = httpx.Response(200, text="<html>" + KEY)
    else:
        if kind == "tool-call":
            response["choices"][0]["message"]["tool_calls"] = [{"name": "run"}]
        elif kind == "incomplete":
            response["choices"][0]["finish_reason"] = "length"
        elif kind == "bad-usage":
            response["usage"]["completion_tokens"] = config.output_tokens + 1
        elif kind == "duplicate-keys":
            response["choices"][0]["message"]["content"] = (
                '{"explanation":"first","explanation":"second"}'
            )
        answer = httpx.Response(200, json=response)
    handler[0] = lambda request: answer
    with app_for(replace(config, daily_user_limit=1)) as client:
        result = client.post("/ai/explain", headers=AUTH, json=BODY)
        assert result.status_code == 502
        assert KEY not in result.text and PROMPT not in result.text
        assert client.post("/ai/explain", headers=AUTH, json=BODY).status_code == 429
    assert len(requests) == 1
    with Session(engine) as db:
        audit = db.scalar(select(AuditEvent))
        assert json.loads(audit.target)["outcome"] == "provider_error"
        assert KEY not in audit.target and PROMPT not in audit.target


class SlowStream(httpx.AsyncByteStream):
    async def __aiter__(self):
        yield b"{"
        await asyncio.sleep(1)
        yield b"}"


def test_timeout_bounds_whole_request_not_just_one_chunk(tutor, monkeypatch):
    app_for, _, _, requests, handler, _ = tutor
    import khohoc.ai_tutor as module

    monkeypatch.setattr(module, "PROVIDER_TIMEOUT_SECONDS", 0.05)
    handler[0] = lambda request: httpx.Response(
        200, stream=SlowStream(), headers={"content-type": "application/json"}
    )
    started = time.monotonic()
    with app_for() as client:
        response = client.post("/ai/explain", headers=AUTH, json=BODY)
    assert response.status_code == 504
    assert time.monotonic() - started < 0.8 and len(requests) == 1


def test_daily_server_quota_across_users_and_window_rollover(tutor, monkeypatch):
    app_for, _, config, requests, _, _ = tutor
    clock = [2_000_000_000]
    monkeypatch.setattr("khohoc.ai_tutor.time.time", lambda: clock[0])
    with app_for(replace(config, daily_server_limit=1)) as client:
        assert client.post("/ai/explain", headers=AUTH, json=BODY).status_code == 200
        other = {"Authorization": "Bearer khs_other"}
        assert client.post("/ai/explain", headers=other, json=BODY).status_code == 429
        clock[0] += 86400
        assert client.post("/ai/explain", headers=other, json=BODY).status_code == 200
    assert len(requests) == 2


@pytest.fixture(params=["sqlite", "postgresql"])
def quota_engine(request, tmp_path):
    admin = None
    if request.param == "postgresql":
        if not os.getenv("KHOHOC_TEST_POSTGRES_URL"):
            pytest.skip("PostgreSQL integration requires local integration runner")
        admin = make_engine(os.environ["KHOHOC_TEST_POSTGRES_URL"])
        schema = "test_" + uuid.uuid4().hex
        with admin.begin() as connection:
            connection.execute(text(f"CREATE SCHEMA {schema}"))
        url = (
            make_url(os.environ["KHOHOC_TEST_POSTGRES_URL"])
            .update_query_dict({"options": "-csearch_path=" + schema})
            .render_as_string(hide_password=False)
        )
    else:
        url = "sqlite:///" + str(tmp_path / "quota.db")
    engine = make_engine(url)
    migrate(engine)
    yield engine
    engine.dispose()
    if admin:
        with admin.begin() as connection:
            connection.execute(text(f"DROP SCHEMA {schema} CASCADE"))
        admin.dispose()


def test_atomic_reservations_across_workers_all_or_nothing(quota_engine):
    config = AITutorConfig(daily_user_limit=1, daily_server_limit=1)

    def reserve(_):
        try:
            reserve_quotas(quota_engine, "same-learner", config)
            return True
        except QuotaExceeded:
            return False

    with ThreadPoolExecutor(max_workers=8) as pool:
        assert sum(pool.map(reserve, range(16))) == 1
    with Session(quota_engine) as db:
        assert sorted(db.scalars(select(RequestBudget.count))) == [1, 1, 1]


def test_short_window_caps_attempts_even_with_daily_capacity(tutor):
    app_for, _, _, requests, _, _ = tutor
    with app_for() as client:
        for _ in range(3):
            assert (
                client.post("/ai/explain", headers=AUTH, json=BODY).status_code == 200
            )
        assert client.post("/ai/explain", headers=AUTH, json=BODY).status_code == 429
    assert len(requests) == 3
