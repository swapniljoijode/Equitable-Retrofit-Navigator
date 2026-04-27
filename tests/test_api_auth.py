from __future__ import annotations

import os

from fastapi.testclient import TestClient

from app.api import app


def test_run_requires_api_key():
    os.environ["API_AUTH_KEY"] = "unit-test-key"
    client = TestClient(app)
    res = client.post("/run", json={"source": "mock"})
    assert res.status_code == 401


def test_run_accepts_valid_api_key():
    os.environ["API_AUTH_KEY"] = "unit-test-key"
    client = TestClient(app)
    res = client.post("/run", headers={"X-API-Key": "unit-test-key"}, json={"source": "mock"})
    assert res.status_code == 200
    assert "X-Request-ID" in res.headers


def test_run_preserves_incoming_request_id():
    os.environ["API_AUTH_KEY"] = "unit-test-key"
    client = TestClient(app)
    res = client.post(
        "/run",
        headers={"X-API-Key": "unit-test-key", "X-Request-ID": "req-123"},
        json={"source": "mock"},
    )
    assert res.status_code == 200
    assert res.headers.get("X-Request-ID") == "req-123"
