"""Validate the small resource probe also exercised against the built shared image."""

import importlib.util
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from khohoc.app import Settings, create_app


def test_shared_smoke_runtime_endpoints(tmp_path):
    path = Path(__file__).parents[3] / "scripts/smoke_shared_stack.py"
    spec = importlib.util.spec_from_file_location("shared_runtime_smoke", path)
    smoke = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(smoke)
    fixture = smoke.runtime_content_fixture()
    app = create_app(Settings(database_url="sqlite:///" + str(tmp_path / "probe.db")))
    with TestClient(app) as client:
        with Session(app.state.engine) as db:
            smoke.add_runtime_content(db, fixture)
            db.commit()

        def request(path):
            response = client.get(path)
            assert response.status_code == 200, path
            return response.json()

        smoke.assert_runtime_resources(request, fixture)
