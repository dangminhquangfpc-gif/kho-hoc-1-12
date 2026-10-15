"""Disposable HTTPS/Compose smoke test. Requires built shared image and Flutter web."""

import hashlib
import json
from pathlib import Path
import secrets
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
DOCKER = ["docker", "--host=unix:///var/run/docker.sock"]


def runtime_content_fixture():
    """Select a small real fixture set; never publish a whole development bank."""
    from khohoc.content_fixes import QUESTION_REPLACEMENTS
    from khohoc.library import DocumentInput, is_textbook_lesson
    from khohoc.schemas import ExamInput, Question

    def read(relative):
        return json.loads((ROOT / relative).read_text(encoding="utf-8"))

    book = next(
        book
        for book in read("data/seeds/textbook_units.json")["books"]
        if book["grade"] == 5 and book["subject"] == "toan"
    )
    guide = next(
        DocumentInput.model_validate(document).model_dump(mode="json")
        for document in read("data/library/curriculum_documents.json")["documents"]
        if document["grade"] == 5
        and document["subject"] == "toan"
        and is_textbook_lesson(document)
    )
    pairs = read("data/seeds/source_practice_map.json")["papers"]
    source = next(
        DocumentInput.model_validate(document).model_dump(mode="json")
        for document in read("data/library/external_documents.json")["documents"]
        if document["id"] in pairs
        and document["grade"] == 5
        and document["subject"] == "toan"
    )
    mapping = pairs[source["id"]]
    exam = next(
        ExamInput.model_validate(exam).model_dump(mode="json")
        for exam in read("data/seeds/source_practice_exams.json")
        if exam["id"] == mapping["exam_id"]
    )
    exam["question_ids"] = [
        QUESTION_REPLACEMENTS.get(qid, qid) for qid in exam["question_ids"]
    ]
    # This topic's display name comes from curriculum_exams.json, not a Python label.
    topic_exam = next(
        exam
        for exam in read("data/seeds/curriculum_exams.json")
        if exam["id"] == "kntt_math_1_dem_so"
    )
    needed = set(exam["question_ids"]) | {topic_exam["question_ids"][0]}
    questions = {}
    for filename in (
        "questions.json",
        "language_questions.json",
        "curriculum_questions.json",
        "subject_questions.json",
        "practice_questions.json",
        "extended_practice_questions.json",
        "multigrade_questions.json",
        "subject_practice_questions.json",
        "clean_questions.json",
    ):
        for question in read("data/seeds/" + filename)["questions"]:
            if question["id"] in needed:
                questions[question["id"]] = Question.model_validate(
                    question
                ).model_dump(mode="json")
    if set(questions) != needed:
        raise RuntimeError("Runtime smoke fixture is missing source-exam questions")
    return dict(
        guide=guide,
        source=source,
        mapping=mapping,
        exam=exam,
        questions=questions,
        unit_count=len(book["units"]),
        topic=dict(
            grade=topic_exam["grade"],
            subject=topic_exam["subject"],
            id=topic_exam["topic"],
            name=topic_exam["title"].split(" · ")[1],
        ),
    )


def add_runtime_content(db, fixture):
    """Only used by disposable smoke databases, never by deployment startup."""
    from khohoc.library import LibraryDocument
    from khohoc.models import ContentQuestion, Exam

    for question in fixture["questions"].values():
        if not db.get(ContentQuestion, question["id"]):
            db.add(
                ContentQuestion(
                    id=question["id"],
                    payload=question,
                    fingerprint=hashlib.sha256(question["id"].encode()).hexdigest(),
                    state="published",
                    rights_confirmed=True,
                )
            )
    for document in (fixture["guide"], fixture["source"]):
        db.add(
            LibraryDocument(
                id=document["id"],
                payload=document,
                fingerprint=hashlib.sha256(document["id"].encode()).hexdigest(),
                state="published",
                rights_confirmed=True,
            )
        )
    db.add(Exam(id=fixture["exam"]["id"], state="published", payload=fixture["exam"]))


def assert_runtime_resources(request, fixture):
    """Exercise metadata-dependent endpoints in the actual built API container."""
    guide, source, mapping = (fixture[key] for key in ("guide", "source", "mapping"))
    curriculum = request("/curriculum?grade=5&subject=toan")
    assert curriculum["unit_count"] == fixture["unit_count"]
    assert curriculum["authored_count"] == 1
    unit = next(
        unit for unit in curriculum["units"] if unit["id"] == guide["curriculum_unit_id"]
    )
    assert unit["document_id"] == guide["id"]
    lessons = request("/documents?grade=5&subject=toan&section=lessons")
    assert [document["id"] for document in lessons] == [guide["id"]]
    detail = request("/documents/" + guide["id"])
    assert detail["sections"] == guide["sections"]
    papers = request("/documents?grade=5&subject=toan&section=exams")
    assert [paper["id"] for paper in papers] == [source["id"]]
    assert papers[0]["practice_exam_id"] == mapping["exam_id"]
    assert papers[0]["title"] == mapping["title"]
    assert papers[0]["practice_notice"] == mapping["notice"]
    mapped_detail = request("/documents/" + source["id"])
    assert mapped_detail["reference_title"] == source["title"]
    assert mapped_detail["practice_exam_id"] == mapping["exam_id"]
    exam = request("/exams/" + mapping["exam_id"])
    assert len(exam["questions"]) == mapping["question_count"]
    assert [question["id"] for question in exam["questions"]] == fixture["exam"][
        "question_ids"
    ]
    assert all("correct_answer" not in question for question in exam["questions"])
    topic = fixture["topic"]
    options = request(
        f"/practice-options?grade={topic['grade']}&subject={topic['subject']}"
    )
    assert next(item for item in options["topics"] if item["id"] == topic["id"])[
        "name"
    ] == topic["name"]


def main():
    from sqlalchemy.orm import Session
    from khohoc.accounts import password_hash
    from khohoc.database import make_engine, migrate
    from khohoc.models import LearningUser, ContentQuestion, Exam
    from khohoc.schemas import Question
    from backup_postgres import PostgresDocker, backup, backup_status, keygen, restore

    project = "tuhoc-smoke-" + secrets.token_hex(4)
    domain = "study.test.edu.vn"
    password = secrets.token_urlsafe(24)
    runtime_fixture = runtime_content_fixture()
    with tempfile.TemporaryDirectory(prefix="tuhoc-https-") as directory:
        staging = Path(directory)
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts/prepare_shared.py"),
                "--domain",
                domain,
                "--email",
                "operator@test.edu.vn",
                "--directory",
                directory,
            ],
            check=True,
            stdout=subprocess.DEVNULL,
        )
        # The disposable test's private mount must be writable by container UID 10001.
        private = staging / "private"
        private.chmod(0o777)
        source = private / "import.db"
        engine = make_engine("sqlite:///" + str(source))
        migrate(engine)
        raw = json.loads((ROOT / "data/seeds/practice_questions.json").read_text())[
            "questions"
        ][0]
        question = Question.model_validate(raw).model_dump(mode="json")
        with Session(engine) as db:
            for user, role in [
                ("manager", "manager"),
                ("student", "student"),
                ("other", "student"),
            ]:
                db.add(
                    LearningUser(
                        id=user,
                        username=user,
                        display_name="Kiểm thử " + user,
                        role=role,
                        password_hash=password_hash(password),
                        manager_id=None if role == "manager" else "manager",
                    )
                )
            db.add(
                ContentQuestion(
                    id=question["id"],
                    payload=question,
                    fingerprint="https-smoke",
                    state="published",
                    rights_confirmed=True,
                )
            )
            db.add(
                Exam(
                    id="https-exam",
                    state="published",
                    payload=dict(
                        id="https-exam",
                        title="Đề kiểm thử HTTPS",
                        grade=question["grade"],
                        subject=question["subject"],
                        textbook="ket_noi_tri_thuc",
                        topic=question["topic"],
                        duration_minutes=15,
                        question_ids=[question["id"]],
                    ),
                )
            )
            db.flush()
            add_runtime_content(db, runtime_fixture)
            db.commit()
        engine.dispose()
        source.chmod(0o444)
        original = ROOT / "deploy/shared/compose.yaml"
        prefix = DOCKER + [
            "compose",
            "--project-name",
            project,
            "--profile",
            "maintenance",
            "--env-file",
            str(staging / ".env"),
        ]
        config = json.loads(
            subprocess.check_output(
                prefix + ["-f", str(original), "config", "--format", "json"], text=True
            )
        )
        config["services"]["api"].pop("build", None)
        for key in ["owner_password", "app_password"]:
            config["secrets"][key]["file"] = str(staging / "secrets" / key)
        config["services"]["maintenance"]["volumes"][0]["source"] = str(private)
        caddy = staging / "Caddyfile"
        caddy.write_text(
            (ROOT / "deploy/shared/Caddyfile")
            .read_text()
            .replace("{$TUHOC_DOMAIN} {", "{$TUHOC_DOMAIN} {\n    tls internal")
        )
        config["services"]["gateway"]["volumes"][0]["source"] = str(caddy)
        config["services"]["gateway"]["ports"] = [
            dict(target=443, published="0", host_ip="127.0.0.1", protocol="tcp")
        ]
        compose = staging / "compose.json"
        compose.write_text(json.dumps(config))
        command = prefix + ["-f", str(compose)]

        def run(*args):
            subprocess.run(command + list(args), check=True, stdout=subprocess.DEVNULL)

        try:
            run("up", "-d", "--wait", "db")
            run(
                "run",
                "--rm",
                "maintenance",
                "python",
                "-m",
                "khohoc.server_admin",
                "migrate",
            )
            run(
                "run",
                "--rm",
                "maintenance",
                "python",
                "-m",
                "khohoc.server_admin",
                "import-sqlite",
                "--source",
                "/maintenance/import.db",
            )
            run(
                "run",
                "--rm",
                "maintenance",
                "python",
                "-m",
                "khohoc.server_admin",
                "grant-runtime",
                "--role",
                "tuhoc_app",
            )
            run("up", "-d", "api", "gateway")
            certificate = staging / "root.crt"
            deadline = time.monotonic() + 45
            while True:
                result = subprocess.run(
                    command
                    + [
                        "exec",
                        "-T",
                        "gateway",
                        "cat",
                        "/data/caddy/pki/authorities/local/root.crt",
                    ],
                    capture_output=True,
                )
                if result.returncode == 0:
                    certificate.write_bytes(result.stdout)
                    break
                if time.monotonic() > deadline:
                    raise RuntimeError("Local CA unavailable")
                time.sleep(0.5)
            port = (
                subprocess.check_output(command + ["port", "gateway", "443"], text=True)
                .strip()
                .rsplit(":", 1)[1]
            )
            jars = [staging / "one.cookies", staging / "two.cookies"]
            for jar in jars:
                jar.touch(mode=0o600)

            def request(path, body=None, device=0, status=200, extra=None):
                args = [
                    "curl",
                    "--silent",
                    "--show-error",
                    "--max-time",
                    "10",
                    "--noproxy",
                    domain,
                    "--resolve",
                    f"{domain}:{port}:127.0.0.1",
                    "--cacert",
                    str(certificate),
                    "--cookie",
                    str(jars[device]),
                    "--cookie-jar",
                    str(jars[device]),
                    "-w",
                    "\n%{http_code}",
                ]
                if body is not None:
                    args += [
                        "--header",
                        "Content-Type: application/json",
                        "--data-binary",
                        json.dumps(body),
                    ]
                if extra:
                    args += extra
                result = subprocess.check_output(
                    args + [f"https://{domain}:{port}/api{path}"], text=True
                )
                data, code = result.rsplit("\n", 1)
                if int(code) != status:
                    raise RuntimeError(f"{path}: expected {status}, received {code}")
                return json.loads(data) if data else None

            deadline = time.monotonic() + 45
            while True:
                try:
                    assert request("/health")["mode"] == "shared"
                    break
                except (RuntimeError, subprocess.CalledProcessError):
                    if time.monotonic() > deadline:
                        raise
                    time.sleep(0.5)
            assert_runtime_resources(request, runtime_fixture)
            request("/ai/status", status=404)
            for device in [0, 1]:
                request(
                    "/auth/login",
                    {"username": "student", "password": password},
                    device=device,
                )
            request("/ai/status", status=404)
            request(
                "/ai/explain",
                {"text": "Giải thích cách làm bài toán này."},
                status=404,
            )
            # Assign a public source privately, then carry assignment progress through recovery.
            request(
                "/auth/login", {"username": "manager", "password": password}, device=1
            )
            group = request(
                "/classroom/groups", {"name": "Nhóm HTTPS"}, status=201, device=1
            )
            group_path = "/classroom/groups/" + group["id"]
            request(group_path + "/members", {"username": "student"}, device=1)
            assigned = request(
                group_path + "/assignments",
                {"exam_id": "https-exam"},
                status=201,
                device=1,
            )
            exam_id = assigned["exam_id"]
            request(
                "/auth/login", {"username": "student", "password": password}, device=1
            )
            assert request("/account/assignments")[0]["status"] == "not_started"
            attempt = request("/exams/" + exam_id + "/attempts", {}, status=201)
            path = "/account/attempts/" + attempt["id"]
            request(
                path + "/draft",
                {
                    "revision": 0,
                    "answers": {question["id"]: question["correct_answer"]},
                },
            )
            resumed = request(path, device=1)
            assert resumed["draft_revision"] == 1
            assert resumed["answers"][question["id"]] == question["correct_answer"]
            request(path + "/draft", {"revision": 0, "answers": {}}, status=409)
            submitted = request(
                "/attempts/" + attempt["id"] + "/submit",
                {"draft_revision": 1, "answers": resumed["answers"]},
                device=1,
            )
            assert submitted["score"] == float(question["max_score"])
            request(
                "/auth/login", {"username": "manager", "password": password}, device=1
            )
            progress = request(group_path + "/assignments/" + exam_id, device=1)
            assert progress["submitted_count"] == 1
            assert progress["students"][0]["latest_percent"] == 100

            assert request("/account/results")[0]["id"] == attempt["id"]
            feedback = request(
                "/content-reports",
                {
                    "target_kind": "question",
                    "target_id": question["id"],
                    "attempt_id": attempt["id"],
                    "category": "unclear",
                    "message": "Kiểm thử lưu phản hồi qua sao lưu và phục hồi.",
                },
                status=201,
            )

            request(
                "/auth/login", {"username": "other", "password": password}, device=1
            )
            request(path, device=1, status=404)
            assert request("/account/assignments", device=1) == []
            request("/exams/" + exam_id, device=1, status=404)
            request(
                "/auth/login",
                {"username": "student", "password": password},
                status=403,
                extra=["--header", "Origin: https://evil.example"],
            )
            request("/admin/questions", status=404)
            # Session and score survive both API workers restarting.
            run("restart", "api")
            deadline = time.monotonic() + 45
            while True:
                try:
                    assert request("/account/results")[0]["id"] == attempt["id"]
                    break
                except (RuntimeError, subprocess.CalledProcessError):
                    if time.monotonic() > deadline:
                        raise
                    time.sleep(0.5)
            # Confirm DB outages are reported as 503, then reconnect without replacing data.
            run("stop", "db")
            request("/ready", status=503)
            request("/grades", status=503)
            run("up", "-d", "--wait", "db")
            assert request("/ready")["status"] == "ok"
            key = staging / "postgres.backup-key"
            keygen(key)
            driver = PostgresDocker(
                compose_file=compose, env_file=staging / ".env", project=project
            )
            assert driver.configured_database() == "tuhoc"
            archive = backup(
                driver, driver.configured_database(), staging / "backups", key, 30
            )
            assert backup_status(staging / "backups") == "fresh"
            driver.sql("tuhoc", "DELETE FROM learning_records")
            assert request("/account/results") == []
            recovery = "recovery_smoke_" + secrets.token_hex(6)
            restore(driver, archive, recovery, key)
            owner_url = "postgresql+psycopg://tuhoc_owner@db:5432/" + recovery
            run(
                "run",
                "--rm",
                "-e",
                "KHOHOC_DATABASE_URL=" + owner_url,
                "maintenance",
                "python",
                "-m",
                "khohoc.server_admin",
                "grant-runtime",
                "--role",
                "tuhoc_app",
            )
            config["services"]["api"]["environment"]["KHOHOC_DATABASE_URL"] = (
                "postgresql+psycopg://tuhoc_app@db:5432/" + recovery
            )
            compose.write_text(json.dumps(config))
            assert driver.configured_database() == recovery
            run("up", "-d", "api")
            deadline = time.monotonic() + 45
            while True:
                try:
                    assert request("/ready")["status"] == "ok"
                    break
                except (RuntimeError, subprocess.CalledProcessError):
                    if time.monotonic() > deadline:
                        raise
                    time.sleep(0.5)
            request("/auth/me", status=401)  # Backup sessions must not be reactivated.
            request("/auth/login", {"username": "student", "password": password})
            restored = request("/account/results")
            assert restored[0]["id"] == attempt["id"]
            assert restored[0]["result"]["score"] == submitted["score"]
            assert driver.sql("tuhoc", "SELECT count(*) FROM learning_records") == b"0"
            assert request("/content-reports")[0]["id"] == feedback["id"]
            restored_assignments = request("/account/assignments")
            assert restored_assignments[0]["exam_id"] == exam_id
            assert restored_assignments[0]["status"] == "submitted"
            assert restored_assignments[0]["latest_percent"] == 100
            for service in ["api", "db"]:
                ident = subprocess.check_output(
                    command + ["ps", "-q", service], text=True
                ).strip()
                info = json.loads(
                    subprocess.check_output(DOCKER + ["inspect", ident], text=True)
                )[0]
                assert not info["HostConfig"]["PortBindings"]
                if service == "api":
                    assert info["HostConfig"]["ReadonlyRootfs"]
                    assert info["Config"]["User"] == "10001:10001"
            print(
                "PASS: verified local HTTPS, curriculum/guide/source-exam/topic runtime metadata, restricted API role, SQLite transfer, two-device drafts/results, isolation, restart persistence, DB outage 503, verified encrypted PostgreSQL restore with revoked sessions and private DB/API ports."
            )
        finally:
            subprocess.run(
                command + ["down", "--volumes", "--remove-orphans"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )


if __name__ == "__main__":
    main()
