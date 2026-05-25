import pytest
from src.api import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


# ── POST /runs/ ───────────────────────────────────────────────────────────────

def test_create_run_returns_201(client):
    resp = client.post("/runs/", json={"run_name": "smoke", "scenario_name": "test"})
    assert resp.status_code == 201


def test_create_run_echoes_payload(client):
    payload = {"run_name": "r1", "scenario_name": "s1", "model_name": "m1", "provider": "p1"}
    resp = client.post("/runs/", json=payload)
    data = resp.get_json()
    assert data["run_name"] == "r1"
    assert data["scenario_name"] == "s1"


def test_create_run_content_type(client):
    resp = client.post("/runs/", json={})
    assert resp.content_type == "application/json"


def test_create_run_empty_body(client):
    # Empty JSON object is accepted by the stub (no validation yet)
    resp = client.post("/runs/", json={})
    assert resp.status_code == 201


def test_create_run_non_json_body(client):
    resp = client.post("/runs/", data="not-json", content_type="text/plain")
    # force=True in get_json means Flask parses anyway; stub echoes whatever it gets
    assert resp.status_code in (201, 400)


# ── GET /runs/ ────────────────────────────────────────────────────────────────

def test_list_runs_returns_200(client):
    resp = client.get("/runs/")
    assert resp.status_code == 200


def test_list_runs_returns_list(client):
    resp = client.get("/runs/")
    assert isinstance(resp.get_json(), list)


def test_list_runs_content_type(client):
    resp = client.get("/runs/")
    assert resp.content_type == "application/json"
